import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def check_and_update():
    print("====================================================")
    print("  🌌 ALFRAGANUS AI — TIZIMNI TEKSHIRISH VA YANGILASH")
    print("====================================================")
    
    # 1. Check API Key configuration
    config_file = BASE_DIR / "config" / "api_keys.json"
    example_file = BASE_DIR / "config" / "api_keys.example.json"
    if not config_file.exists():
        print("[!] config/api_keys.json topilmadi, shablon yaratilmoqda...")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        if example_file.exists():
            import shutil
            shutil.copy(example_file, config_file)
        else:
            config_file.write_text('{\n  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",\n  "telegram_bot_token": ""\n}', encoding="utf-8")
    print("✓ Konfiguratsiya tekshirildi.")

    # 2. Check MediaPipe Task Model
    model_file = BASE_DIR / "gestures" / "hand_landmarker.task"
    if not model_file.exists() or model_file.stat().st_size < 1000000:
        print("[!] MediaPipe modeli yangilanmoqda...")
        import urllib.request
        url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
        urllib.request.urlretrieve(url, model_file)
    print("✅ MediaPipe 21 Landmarks modeli tayyor.")

    # 3. Ensure Desktop Shortcut exists
    desktop_shortcut = Path(r"C:\Users\MSI\Desktop\Alfraganus AI.lnk")
    if not desktop_shortcut.exists():
        try:
            ps_cmd = f"$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('{str(desktop_shortcut)}'); $s.TargetPath = '{str(BASE_DIR / 'run_alfraganus.bat')}'; $s.WorkingDirectory = '{str(BASE_DIR)}'; $s.Description = 'Alfraganus AI - Autonomous PC Agent'; $s.Save()"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            print("✅ Ish stolidagi (Desktop) yorliq yangilandi.")
        except Exception:
            pass
    else:
        print("✅ Ish stolidagi yorliq faol holatda.")

    print("====================================================")
    print("  🚀 TIZIM TAYYOR — DASTUR ISHGA TUSHMOQDA...")
    print("====================================================\n")

if __name__ == "__main__":
    check_and_update()
