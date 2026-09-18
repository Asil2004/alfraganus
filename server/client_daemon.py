import os
import sys
import json
import time
import asyncio
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import websockets
from actions.system_monitor import system_monitor
from actions.phone_controller import phone_controller
from actions.device_controller import device_controller
from actions.computer_settings import computer_settings
from actions.open_app import open_app, close_app

SERVER_URL = os.environ.get("ALFRAGANUS_SERVER_URL", "ws://localhost:8000/ws/client/local_agent")


async def run_client_daemon():
    """Mahalliy kompyuterda ishlaydigan Agent daemon"""
    print(f"🔗 Alfraganus Serveriga ulanmoqda: {SERVER_URL}")

    while True:
        try:
            async with websockets.connect(SERVER_URL) as ws:
                print("✅ Alfraganus Cloud Serveriga ulandi!")
                
                # Send initial telemetry
                await ws.send(json.dumps({
                    "type": "telemetry",
                    "payload": system_monitor()
                }))

                while True:
                    msg_raw = await ws.receive()
                    msg = json.loads(msg_raw)
                    cmd = msg.get("command", "")
                    action = msg.get("action", "")
                    args = msg.get("args", {})

                    print(f"📥 Serverdan buyruq keldi: {action} ({args})")

                    # Execute local action
                    result = "Noma'lum buyruq"
                    try:
                        if action == "open_app":
                            result = open_app(args.get("app_name", cmd))
                        elif action == "close_app":
                            result = close_app(args.get("app_name", cmd))
                        elif action == "settings":
                            result = computer_settings(args.get("command", "status"))
                        elif action == "phone":
                            result = phone_controller(**args)
                        elif action == "device":
                            result = device_controller(**args)
                        elif action == "telemetry":
                            result = system_monitor()
                    except Exception as e:
                        result = f"Xatolik yuz berdi: {e}"

                    # Send result back to server
                    await ws.send(json.dumps({
                        "type": "result",
                        "request_id": msg.get("request_id"),
                        "result": result
                    }))

        except Exception as e:
            print(f"⚠️ Ulanishda uzilish ({e}). 5 soniyadan so'ng qayta ulanadi...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_client_daemon())
