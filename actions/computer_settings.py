import os
import subprocess
import pyautogui


def computer_settings(command: str, value: int = None):
    cmd = command.lower().strip()
    try:
        if cmd == "volume_up":
            steps = value if value else 5
            for _ in range(steps):
                pyautogui.press("volumeup")
            return f"Ovoz balandligi oshirildi (+{steps * 2}%)."

        elif cmd == "volume_down":
            steps = value if value else 5
            for _ in range(steps):
                pyautogui.press("volumedown")
            return f"Ovoz balandligi pasaytirildi (-{steps * 2}%)."

        elif cmd == "mute" or cmd == "unmute":
            pyautogui.press("volumemute")
            return "Ovoz yoqildi/o'chirildi."

        elif cmd == "brightness_up":
            # PowerShell WmiMonitorBrightnessMethods
            val = value if value else 10
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [Math]::Min(100, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness + {val}))"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            return "Ekran yorug'ligi oshirildi."

        elif cmd == "brightness_down":
            val = value if value else 10
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [Math]::Max(0, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness - {val}))"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            return "Ekran yorug'ligi pasaytirildi."

        elif cmd == "set_brightness":
            val = max(0, min(100, value if value is not None else 50))
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {val})"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            return f"Ekran yorug'ligi {val}% ga o'rnatildi."

        elif cmd == "lock":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Kompyuter ekrani qulflFactoryandi."

        elif cmd == "sleep":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "Kompyuter uyqu rejimiga o'tkazildi."

        elif cmd == "restart":
            subprocess.run(["shutdown", "/r", "/t", "10"])
            return "Kompyuter 10 soniyadan so'ng qayta yuklanadi."

        elif cmd == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "10"])
            return "Kompyuter 10 soniyadan so'ng o'chiriladi."

        elif cmd == "cancel_shutdown":
            subprocess.run(["shutdown", "/a"])
            return "O'chirish bekor qilindi."

        elif cmd in ["minimize_all", "show_desktop"]:
            pyautogui.hotkey("win", "d")
            return "Barcha oynalar kichraytirildi (Ish stoli ko'rsatildi)."

        elif cmd == "task_manager":
            pyautogui.hotkey("ctrl", "shift", "esc")
            return "Vazifalar menejeri (Task Manager) ochildi."

        else:
            return f"Noma'lum sozlama buyrug'i: {cmd}"

    except Exception as e:
        return f"Sozlamalarni o'zgartirishda xatolik: {e}"
