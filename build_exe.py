import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("   ALFRAGANUS AI — STANDALONE EXE YARATISH (BUILD)")
    print("=" * 60)

    base_dir = Path(__file__).resolve().parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"

    # PyInstaller buyrug'ini tayyorlash
    python_exe = sys.executable
    print(f"Python muhiti: {python_exe}")

    cmd = [
        python_exe,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "Alfraganus",
        "--add-data", f"{base_dir / 'config'};config",
        "--add-data", f"{base_dir / 'core'};core",
        "--add-data", f"{base_dir / 'actions'};actions",
        "--add-data", f"{base_dir / 'gestures'};gestures",
        "--add-data", f"{base_dir / 'agent'};agent",
        "--collect-all", "mediapipe",
        "--collect-all", "google.genai",
        "--collect-all", "google.generativeai",
        "--collect-all", "sounddevice",
        "--collect-all", "cv2",
        "--collect-all", "pyautogui",
        "--collect-all", "PIL",
        "--hidden-import", "comtypes",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32con",
        "--hidden-import", "win32process",
        "--hidden-import", "psutil",
        "--hidden-import", "requests",
        "--hidden-import", "websockets",
        "--hidden-import", "numpy",
        str(base_dir / "main.py")
    ]

    print("\nPyInstaller ishga tushirilmoqda...")
    print(" ".join(cmd[:10]), "...\n")

    res = subprocess.run(cmd, cwd=base_dir)

    if res.returncode == 0:
        exe_path = dist_dir / "Alfraganus" / "Alfraganus.exe"
        print("\n" + "=" * 60)
        print("✅ ALFRAGANUS EXE MUVAFFAQIYATLI YARATILDI!")
        print(f"📁 EXE manzili: {exe_path}")
        print("=" * 60)
    else:
        print(f"\n❌ Xatolik yuz berdi. Returncode: {res.returncode}")

if __name__ == "__main__":
    main()
