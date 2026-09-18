import time
import subprocess
import psutil
import pyautogui

from actions.open_app import focus_app

GUI_APPS_MAP = {
    'telegram.exe': 'Telegram',
    'chrome.exe': 'Google Chrome',
    'msedge.exe': 'Microsoft Edge',
    'brave.exe': 'Brave Browser',
    'code.exe': 'Visual Studio Code',
    'notepad.exe': 'Notepad (Bloknot)',
    'calc.exe': 'Kalkulyator',
    'calculatorapp.exe': 'Kalkulyator',
    'explorer.exe': 'Fayl Menejeri (Explorer)',
    'antigravity.exe': 'Antigravity IDE',
    'arduino.exe': 'Arduino IDE',
    'lasergrbl.exe': 'LaserGRBL',
    'winword.exe': 'Microsoft Word',
    'excel.exe': 'Microsoft Excel',
    'powerpnt.exe': 'Microsoft PowerPoint',
    'spotify.exe': 'Spotify',
    'vncviewer.exe': 'RealVNC Viewer',
    'rdb tokarlik.exe': 'RDB Tokarlik CNC',
    'whatsapp.exe': 'WhatsApp'
}


def get_open_apps() -> str:
    """Hozirda kompyuterda ochiq bo'lgan barcha asosiy ilovalarni aniqlaydi"""
    detected = {}
    for p in psutil.process_iter(['name', 'pid']):
        try:
            pname = p.info['name'].lower()
            if pname in GUI_APPS_MAP:
                app_title = GUI_APPS_MAP[pname]
                detected[app_title] = pname
        except Exception:
            pass

    if detected:
        lines = [f"? {title} ({exe})" for title, exe in detected.items()]
        return "Ekranda ochiq bo'lgan ilovalar:\n" + "\n".join(lines)
    return "Hozirda faol foydalanuvchi ilovalari topilmadi."


import pyperclip


def interact_with_app(app_name: str, action: str, text: str = "", key: str = "", shortcut: str = "") -> str:
    """Ochiq ilovani faollashtirib, uning ichida amallarni bajaradi (matn yozish, chat ochish, qidirish, saqlash, yuborish)"""
    act = action.lower().strip()
    
    # Telegram uchun maxsus aniq navigatsiya
    if "telegram" in app_name.lower():
        from actions.telegram_controller import open_telegram_chat, send_telegram_message
        if act in ["open_chat", "find_chat", "search"]:
            return open_telegram_chat(text)
        elif act in ["send_message", "send"]:
            # If text has both recipient and message or only message
            return send_telegram_message(recipient=text, message=key or text)

    # 1. Avval ilovani oldinga chiqarish
    focus_res = focus_app(app_name)
    time.sleep(0.35)
    
    try:
        if act in ["open_chat", "find_chat"]:
            pyautogui.press("esc")
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.2)
            if text:
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)
                pyautogui.press("down")
                time.sleep(0.1)
                pyautogui.press("enter")
                time.sleep(0.2)
            return f"'{app_name}' ilovasida '{text}' chati ochildi."

        elif act == "type":
            if text:
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                return f"'{app_name}' ilovasida '{text}' matni yozildi."
            return "Matn berilmadi."

        elif act in ["send_message", "enter"]:
            if text:
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.15)
            pyautogui.press("enter")
            return f"'{app_name}' ga xabar/buyruq yuborildi (Enter)."

        elif act == "search":
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.2)
            if text:
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.2)
                pyautogui.press("enter")
            return f"'{app_name}' da qidiruv amalga oshirildi."

        elif act == "hotkey":
            if shortcut:
                keys = [k.strip().lower() for k in shortcut.split("+")]
                pyautogui.hotkey(*keys)
                return f"'{app_name}' ichida '{shortcut}' kombinatsiyasi bajarildi."
            return "Kombinatsiya berilmadi."

        elif act == "save":
            pyautogui.hotkey("ctrl", "s")
            return f"'{app_name}' da saqlandi (Ctrl+S)."

        elif act == "new":
            pyautogui.hotkey("ctrl", "n")
            return f"'{app_name}' da yangi oyna/hujjat ochildi (Ctrl+N)."

        elif act == "close":
            pyautogui.hotkey("alt", "f4")
            return f"'{app_name}' oynasi yopildi (Alt+F4)."

        else:
            return f"'{app_name}' uchun noma'lum amal: {act}"

    except Exception as e:
        return f"Ilova bilan ishlashda xatolik: {e}"
