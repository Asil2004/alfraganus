import os
import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def build_executable():
    print("====================================================")
    print("  🔨 ALFRAGANUS AI — STANDALONE EXE YARATISH")
    print("====================================================")

    pyinstaller_exe = Path(r"C:\Program Files (x86)\JarvisMarkXXXV\python_env\Scripts\pyinstaller.exe")
    if not pyinstaller_exe.exists():
        pyinstaller_exe = "pyinstaller"

    # Clean old build dirs
    dist_dir = BASE_DIR / "dist"
    build_dir = BASE_DIR / "build"
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except Exception:
            pass
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception:
            pass

    cmd = [
        str(pyinstaller_exe),
        "--noconfirm",
        "--onedir",
        "--name", "Alfraganus",
        "--add-data", f"{BASE_DIR / 'core'};core",
        "--add-data", f"{BASE_DIR / 'config'};config",
        "--add-data", f"{BASE_DIR / 'server'};server",
        "--add-data", f"{BASE_DIR / 'gestures'};gestures",
        "--add-data", f"{BASE_DIR / 'actions'};actions",
        "--hidden-import", "google.genai",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "websockets",
        "--hidden-import", "sounddevice",
        "--hidden-import", "mediapipe",
        "--hidden-import", "pyautogui",
        "--hidden-import", "psutil",
        "--hidden-import", "actions.phone_controller",
        "--hidden-import", "actions.voice_persona",
        str(BASE_DIR / "main.py")
    ]

    print("PyInstaller ishga tushmoqda...")
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    if res.returncode == 0:
        exe_path = BASE_DIR / "dist" / "Alfraganus" / "Alfraganus.exe"
        print("====================================================")
        print(f"  ✅ EXE MUVAFFAQIYATLI YARATILDI:\n  {exe_path}")
        print("====================================================")
    else:
        print("❌ EXE yaratishda xatolik yuz berdi.")

if __name__ == "__main__":
    build_executable()
