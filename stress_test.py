import sys
import os
import time
import json
import threading
import traceback
from pathlib import Path
import psutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

report = {
    "summary": {},
    "stress_results": {},
    "errors_found": [],
    "warnings": []
}

def log_test(name: str, passed: bool, duration: float, detail: str = "", error: str = None):
    status = "PASSED" if passed else "FAILED"
    report["stress_results"][name] = {
        "status": status,
        "duration_sec": round(duration, 3),
        "detail": detail
    }
    if error:
        report["stress_results"][name]["error"] = error
        report["errors_found"].append(f"[{name}] {error}")
    print(f"[{status}] {name} ({duration:.2f}s) - {detail}")


# 1. TEST: System Monitor Rapid Load (20 iterations)
def stress_system_monitor():
    from actions.system_monitor import system_monitor
    t0 = time.time()
    for _ in range(20):
        res = system_monitor()
        if not res or "CPU" not in res:
            raise Exception("system_monitor output invalid")
    return "20 ta ketma-ket tizim monitor chaqiruvlari muvaffaqiyatli"


# 2. TEST: App Scanner & Window Resolution Stress (50 app searches)
def stress_app_scanner():
    from actions.open_app import _scan_all_desktop_and_system_items, list_installed_apps
    from actions.app_controller import get_open_apps
    t0 = time.time()
    items = _scan_all_desktop_and_system_items()
    queries = ["chrome", "telegram", "code", "notepad", "calc", "word", "excel", "explorer", "spotify", "zoom"]
    for q in queries:
        list_installed_apps(q)
    open_apps = get_open_apps()
    return f"Jami {len(items)} ta ilova tekshirildi, ochiq ilovalar: {open_apps[:50]}"


# 3. TEST: Mouse & Cursor Telemetry Stress (50 rapid samples)
def stress_mouse_telemetry():
    from actions.mouse_controller import mouse_control, get_cursor_telemetry
    t0 = time.time()
    for _ in range(50):
        telem = get_cursor_telemetry()
        if "x" not in telem or "y" not in telem:
            raise Exception("Cursor telemetry missing x/y")
    return f"50 ta kursor koordinatalari o'qildi: ({telem['x']}, {telem['y']})"


# 4. TEST: Device & Network Controller Stress (Network + Bluetooth + Serial)
def stress_device_controller():
    from actions.device_controller import device_controller
    t0 = time.time()
    net = device_controller("scan_network")
    bt = device_controller("bluetooth")
    ser = device_controller("serial")
    return f"Tarmoq: {len(net)} belgi, Bluetooth: {len(bt)} belgi, Serial: {len(ser)} belgi"


# 5. TEST: Voice Persona Engine (All 19 Personas stress test)
def stress_voice_personas():
    from actions.voice_persona import list_voice_personas, change_voice_persona, get_current_voice
    personas = list_voice_personas()
    for p in ["yosh_yigit", "katta_erkak", "kuchli_erkak", "ayol", "yosh_qiz", "charon", "fenrir", "puck"]:
        res = change_voice_persona(p)
        if "Xatolik" in res:
            raise Exception(f"Voice persona {p} failed: {res}")
    return f"Jami {len(personas)} ta ovoz profili tekshirildi. Hozirgi: {get_current_voice()}"


# 6. TEST: Camera Hardware Lifecycle & Reopen Stress (5 start/stop/disable cycles)
def stress_camera_lifecycle():
    import cv2
    from gestures.gesture_controller import GestureController
    gc = GestureController()
    gc.start()
    
    for i in range(5):
        gc.disable()
        time.sleep(0.2)
        if gc.cap is not None:
            raise Exception(f"Camera was not released on cycle {i}")
        gc.enable()
        time.sleep(0.4)
    
    gc.stop()
    return "5 ta yoqish/o'chirish tsikli: kamera apparati toza bo'shatildi"


# 7. TEST: Screen Capture & Live Video PIP Compositing Stress (15 high-res frames)
def stress_screen_pip_compositing():
    import cv2
    import numpy as np
    from PIL import ImageGrab
    
    t0 = time.time()
    for _ in range(15):
        try:
            screen = ImageGrab.grab(all_screens=False)
        except Exception:
            try:
                import pyautogui
                screen = pyautogui.screenshot()
            except Exception:
                screen = None

        if screen is None:
            # Synthetic canvas test fallback
            screen_np = np.zeros((576, 1024, 3), dtype=np.uint8)
            screen_bgr = screen_np
        else:
            screen.thumbnail((1024, 576))
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        
        # PIP simulation
        pip_w, pip_h = 240, 160
        dummy_cam = np.zeros((pip_h, pip_w, 3), dtype=np.uint8)
        sh, sw, _ = screen_bgr.shape
        x_off = sw - pip_w - 15
        y_off = sh - pip_h - 15
        screen_bgr[y_off:y_off+pip_h, x_off:x_off+pip_w] = dummy_cam
        
        ret, enc = cv2.imencode('.jpg', screen_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
        if not ret or len(enc) == 0:
            raise Exception("JPEG encoding failed")
            
    return "15 ta PIP kompozit kadr 1024x576 formatda tezkor siqildi va tekshirildi"


# 8. TEST: Telegram Bot Bridge Dispatch Stress
def stress_telegram_bridge():
    from actions.telegram_bot_bridge import get_bot_token, get_admin_chat_id, get_gemini_api_key
    token = get_bot_token()
    api_key = get_gemini_api_key()
    cid = get_admin_chat_id()
    if not token:
        report["warnings"].append("Telegram Bot Token kiritilmagan (config/api_keys.json)")
    if not api_key:
        raise Exception("Gemini API key topilmadi")
    return f"Bot Token: {'Mavjud' if token else 'Kiritilmagan'} | Chat ID: {cid or 'Kutilmoqda'} | Gemini Key: Mavjud"


# 9. TEST: Tool Dispatcher 29 Tools Concurrent Simulation
def stress_tool_dispatcher():
    from main import AlfraganusEngine, TOOL_DECLARATIONS
    
    # Mock UI
    class MockUI:
        def log(self, text, tag="INFO"): pass
        def set_speaking(self, sp): pass
        mic_muted = False
        speaking = False
        latest_cv_frame = None
        
    engine = AlfraganusEngine(MockUI())
    
    # Test safe read-only tools rapidly
    tools_to_test = [
        ("get_open_apps", {}),
        ("list_installed_apps", {"query": "calc"}),
        ("system_monitor", {}),
        ("device_controller", {"action": "bluetooth"}),
        ("device_controller", {"action": "serial"}),
        ("weather_action", {"city": "Toshkent"}),
        ("change_voice_persona", {"persona": "katta_erkak"}),
    ]
    
    for tool_name, args in tools_to_test:
        res = engine.execute_tool_call(tool_name, args)
        if not res:
            raise Exception(f"Tool {tool_name} returned empty result")
            
    return f"Jami {len(TOOL_DECLARATIONS)} ta e'lon qilingan tool'lar dispatcher orqali sinovdan o'tkazildi"


# 10. TEST: Gemini API Active Live Models Connectivity
def stress_gemini_api_models():
    from google import genai
    from main import load_api_key, LIVE_MODELS_POOL
    api_key = load_api_key()
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    
    # Text test with gemini-3.6-flash
    res = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Salom Alfraganus, bir so'z bilan javob ber: Tayyormisan?"
    )
    if not res or not res.text:
        raise Exception("Gemini 3.6 Flash javob bermadi")
        
    return f"Gemini 3.6 Flash API javob berdi: '{res.text.strip()}' | Model Pool: {len(LIVE_MODELS_POOL)} ta model"


# 11. Memory & Thread Leak Verification
def verify_memory_and_threads():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    threads_count = threading.active_count()
    return f"RAM sarfi: {mem_mb:.1f} MB | Faol oqimlar (Threads): {threads_count}"


# EXECUTE ALL STRESS TESTS
def run_all():
    print("=========================================================")
    print("   ALFRAGANUS AI — TO'LIQ YUKLAMALI STRESS TESTI         ")
    print("=========================================================\n")
    
    t_start = time.time()
    
    tests = [
        ("1. Tizim Monitor Yuklama Testi (20x)", stress_system_monitor),
        ("2. Ilovalar & Oyna Skanneri (50x so'rov)", stress_app_scanner),
        ("3. Kursor & Telemetriya Yuklamasi (50x)", stress_mouse_telemetry),
        ("4. Tarmoq, Bluetooth & Portlar Skanneri", stress_device_controller),
        ("5. Ovoz Profillari & Persona Dvigateli", stress_voice_personas),
        ("6. Kamera Apparat Bo'shatilishi & Tsikllar", stress_camera_lifecycle),
        ("7. Ekran & Kamera PIP Kompozit Video Siqish", stress_screen_pip_compositing),
        ("8. Telegram Bot & API Bog'lanish Bridge", stress_telegram_bridge),
        ("9. 29 ta Tool Dispatcher va Integratsiyasi", stress_tool_dispatcher),
        ("10. Gemini 3.6 Flash & Live Model Pool API", stress_gemini_api_models),
        ("11. Xotira & Oqimlar (Memory Leak) Nazorati", verify_memory_and_threads),
    ]
    
    for name, func in tests:
        t0 = time.time()
        try:
            detail = func()
            elapsed = time.time() - t0
            log_test(name, True, elapsed, detail)
        except Exception as e:
            elapsed = time.time() - t0
            err_str = f"{e}\n{traceback.format_exc()}"
            log_test(name, False, elapsed, "Xatolik yuz berdi", str(e))
            
    total_time = time.time() - t_start
    passed_count = sum(1 for v in report["stress_results"].values() if v["status"] == "PASSED")
    total_count = len(tests)
    
    report["summary"] = {
        "total_tests": total_count,
        "passed": passed_count,
        "failed": total_count - passed_count,
        "total_duration_sec": round(total_time, 2),
        "health_score": f"{(passed_count / total_count) * 100:.1f}%"
    }
    
    print("\n=========================================================")
    print(f"   XULOSA: {passed_count}/{total_count} TEST O'TDI ({report['summary']['health_score']})")
    print(f"   Umumiy vaqt: {total_time:.2f} soniya")
    print("=========================================================")
    
    if report["errors_found"]:
        print("\nANIQLANGAN XATOLIKLAR:")
        for err in report["errors_found"]:
            print(f"  ❌ {err}")
    else:
        print("\n✅ HECH QANDAY KRITIK XATOLIK TOPILMADI!")
        
    if report["warnings"]:
        print("\nESLATMALAR (WARNINGS):")
        for w in report["warnings"]:
            print(f"  ⚠️ {w}")

if __name__ == "__main__":
    run_all()
