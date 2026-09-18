import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from actions.system_monitor import system_monitor
from actions.voice_persona import get_current_voice, list_voice_personas, change_voice_persona
from actions.phone_controller import phone_controller
from actions.device_controller import device_controller
from actions.computer_settings import computer_settings

app = FastAPI(
    title="Alfraganus AI Cloud Gateway",
    description="Markaziy Alfraganus AI Serveri, WebSocket Gateway va Web Dashboard",
    version="2.5.0"
)

# Enable CORS for web and mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected Web Dashboards and Local Daemons
active_dashboards: List[WebSocket] = []
active_clients: Dict[str, WebSocket] = {}

DASHBOARD_HTML_PATH = BASE_DIR / "server" / "web_dashboard.html"


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Web Dashboard interfeysini taqdim etadi"""
    if DASHBOARD_HTML_PATH.exists():
        with open(DASHBOARD_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Alfraganus Cloud Gateway ishlamoqda. Dashboard topilmadi.</h1>")


@app.get("/api/status")
async def get_system_status():
    """Server va tizim telemetriyasini qaytaradi"""
    try:
        telemetry = system_monitor()
        current_voice = get_current_voice()
        all_voices = list_voice_personas()
        return {
            "status": "online",
            "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "voice_name": current_voice,
            "available_voices": list(all_voices.keys()),
            "connected_clients": len(active_clients),
            "telemetry_raw": telemetry
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/voice")
async def set_voice_persona(data: dict = Body(...)):
    """Ovoz profilini o'zgartiradi (katta_erkak, yosh_qiz, ayol, yosh_yigit, bariton)"""
    persona = data.get("persona", "katta_erkak")
    res = change_voice_persona(persona)
    # Broadcast to all dashboards
    await broadcast_to_dashboards({"type": "voice_change", "persona": persona, "message": res})
    return {"status": "success", "result": res}


@app.post("/api/execute")
async def execute_command(data: dict = Body(...)):
    """Buyruqni bajaradi (Serverda yoki ulangan lokal mijozda)"""
    action = data.get("action", "")
    target = data.get("target", "")
    text = data.get("text", "")
    command = data.get("command", "")

    try:
        if action == "system_monitor":
            return {"result": system_monitor()}
        elif action == "computer_settings":
            return {"result": computer_settings(command or target or "status")}
        elif action == "device_controller":
            return {"result": device_controller(action=target or "scan_network", text=text, command=command)}
        elif action == "phone_control":
            return {"result": phone_controller(action=target or "status", app_name=text, text=text, query=command)}
        elif action == "open_app":
            from actions.open_app import open_app
            return {"result": open_app(target or text or command)}
        elif action == "close_app":
            from actions.open_app import close_app
            return {"result": close_app(target or text or command)}
        elif action == "telegram_notify":
            from actions.telegram_bot_bridge import send_bot_message
            return {"result": send_bot_message(text or command or "Alfraganus Cloud bildirishnomasi")}
        else:
            return {"result": f"Buyruq qabul qilindi: {action} ({target})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phone")
async def phone_api(data: dict = Body(...)):
    """Telefonni boshqarish bo'yicha maxsus API"""
    act = data.get("action", "status")
    app_name = data.get("app_name", "")
    text = data.get("text", "")
    phone_number = data.get("phone_number", "")
    ip = data.get("ip", "")
    query = data.get("query", "")
    
    res = phone_controller(
        action=act,
        app_name=app_name,
        text=text,
        phone_number=phone_number,
        ip=ip,
        query=query
    )
    return {"status": "success", "action": act, "result": res}


# ==========================================
# WebSocket Gateway
# ==========================================

async def broadcast_to_dashboards(message: dict):
    """Barcha ochiq Web Dashboardlarga xabar yuborish"""
    for ws in list(active_dashboards):
        try:
            await ws.send_json(message)
        except Exception:
            if ws in active_dashboards:
                active_dashboards.remove(ws)


@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """Web Dashboard uchun real-vaqtli WebSocket oqimi"""
    await websocket.accept()
    active_dashboards.append(websocket)
    try:
        # Initial status
        await websocket.send_json({
            "type": "init",
            "voice": get_current_voice(),
            "telemetry": system_monitor()
        })
        
        while True:
            data = await websocket.receive_json()
            # Handle dashboard actions
            if data.get("type") == "voice_change":
                res = change_voice_persona(data.get("persona", "katta_erkak"))
                await websocket.send_json({"type": "voice_updated", "result": res})
            elif data.get("type") == "command":
                res = phone_controller(action=data.get("action", "status"), app_name=data.get("app_name", ""))
                await websocket.send_json({"type": "command_result", "result": res})
    except WebSocketDisconnect:
        if websocket in active_dashboards:
            active_dashboards.remove(websocket)


@app.websocket("/ws/client/{client_id}")
async def websocket_client(websocket: WebSocket, client_id: str):
    """Mahalliy Kompyuter Agentlari (Client Daemons) uchun WebSocket"""
    await websocket.accept()
    active_clients[client_id] = websocket
    await broadcast_to_dashboards({
        "type": "client_connected",
        "client_id": client_id,
        "time": time.strftime("%H:%M:%S")
    })

    try:
        while True:
            msg = await websocket.receive_json()
            # Forward telemetry and responses to dashboards
            await broadcast_to_dashboards({
                "type": "client_message",
                "client_id": client_id,
                "data": msg
            })
    except WebSocketDisconnect:
        if client_id in active_clients:
            del active_clients[client_id]
        await broadcast_to_dashboards({
            "type": "client_disconnected",
            "client_id": client_id
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Alfraganus Cloud Gateway ishga tushmoqda: http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
