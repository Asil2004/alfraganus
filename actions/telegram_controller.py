import time
import subprocess
import pyautogui
import pyperclip

from actions.open_app import focus_app, open_app


def focus_or_open_telegram():
    res = focus_app("Telegram")
    if "topilmadi" in res:
        open_app("Telegram")
        time.sleep(1.2)
        focus_app("Telegram")
    time.sleep(0.3)


def open_telegram_chat(chat_name: str) -> str:
    """Telegramda qidiruv orqali kontakt/guruh/kanalni topib ochadi"""
    try:
        focus_or_open_telegram()
        
        # 1. Oldingi qidiruv yoki holatdan chiqish
        pyautogui.press("esc")
        time.sleep(0.1)
        pyautogui.press("esc")
        time.sleep(0.1)
        
        # 2. Qidiruv maydonini ochish (Ctrl+F)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.25)
        
        # 3. Nomni buferga olib yozish (barcha o'zbek/kirill/lotin harflari uchun xavfsiz)
        pyperclip.copy(chat_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.6)  # Qidiruv natijalari yuklanishini kutish
        
        # 4. Natijani tanlash va chatni ochish
        pyautogui.press("down")
        time.sleep(0.15)
        pyautogui.press("enter")
        time.sleep(0.3)
        
        return f"Telegramda '{chat_name}' chati ochildi."
    except Exception as e:
        return f"Telegram chatini ochishda xatolik: {e}"


def send_telegram_message(recipient: str, message: str) -> str:
    """Telegramda ko'rsatilgan kontakt/chatni ochib, xabar yozadi va Enter bilan yuboradi"""
    try:
        # 1. Avval chatni ochish
        open_res = open_telegram_chat(recipient)
        time.sleep(0.4)
        
        # 2. Xabarni kiritish maydoniga joylash
        if message:
            pyperclip.copy(message)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)
            # 3. Yuborish (Enter)
            pyautogui.press("enter")
            return f"Telegramda '{recipient}' chatiga xabar muvaffaqiyatli jo'natildi: \"{message}\""
        else:
            return f"Telegramda '{recipient}' chati ochildi (xabar matni berilmagan)."
    except Exception as e:
        return f"Telegramga xabar yuborishda xatolik: {e}"
