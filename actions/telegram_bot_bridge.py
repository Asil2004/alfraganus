import io
import os
import json
import time
import threading
import requests
from pathlib import Path
from PIL import ImageGrab

from actions.open_app import open_app, close_app, focus_app
from actions.computer_settings import computer_settings
from actions.system_monitor import system_monitor

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"


def get_bot_token() -> str:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("telegram_bot_token", "")
    except Exception:
        return ""


def get_admin_chat_id() -> str:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return str(data.get("admin_chat_id", ""))
    except Exception:
        return ""


def save_admin_chat_id(chat_id: str):
    try:
        data = {}
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["admin_chat_id"] = str(chat_id)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def send_bot_message(text: str, chat_id: str = None) -> str:
    token = get_bot_token()
    cid = chat_id or get_admin_chat_id()
    if not token:
        return "Telegram Bot Token topilmadi."
    if not cid:
        return "Iltimos, avval Telegramda @al_pc_bot ga /start buyrug'ini yuboring."

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": cid, "text": text, "parse_mode": "HTML"}, timeout=10)
        if resp.status_code == 200:
            return f"Xabar Telegramga muvaffaqiyatli yuborildi."
        return f"Xatolik: {resp.text}"
    except Exception as e:
        return f"Telegramga yuborishda xatolik: {e}"


def send_bot_screenshot(caption: str = "🖥️ Kompyuter ekrani skrinshoti", chat_id: str = None) -> str:
    token = get_bot_token()
    cid = chat_id or get_admin_chat_id()
    if not token or not cid:
        return "Telegram Bot yoki Chat ID sozlanmagan."

    try:
        screenshot = ImageGrab.grab()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format="JPEG", quality=85)
        img_bytes.seek(0)

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": ("screenshot.jpg", img_bytes, "image/jpeg")}
        data = {"chat_id": cid, "caption": caption}
        resp = requests.post(url, data=data, files=files, timeout=15)
        if resp.status_code == 200:
            return "Ekran rasmi Telegramga jo'natildi."
        return f"Rasm yuborishda xatolik: {resp.text}"
    except Exception as e:
        return f"Skrinshot yuborishda xatolik: {e}"


def send_bot_file(file_path: str, caption: str = "", chat_id: str = None) -> str:
    token = get_bot_token()
    cid = chat_id or get_admin_chat_id()
    p = Path(file_path)
    if not p.exists():
        return f"Fayl topilmadi: {file_path}"
    if not token or not cid:
        return "Telegram sozlamalari topilmadi."

    try:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        with open(p, "rb") as f:
            files = {"document": (p.name, f)}
            data = {"chat_id": cid, "caption": caption or p.name}
            resp = requests.post(url, data=data, files=files, timeout=30)
            if resp.status_code == 200:
                return f"'{p.name}' fayli Telegramga jo'natildi."
            return f"Fayl yuborishda xatolik: {resp.text}"
    except Exception as e:
        return f"Fayl yuborishda xatolik: {e}"


class TelegramBotListener:
    def __init__(self, engine=None):
        self.engine = engine
        self.is_running = False
        self.thread = None
        self.last_update_id = 0

    def start(self):
        token = get_bot_token()
        if not token:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def _poll_loop(self):
        token = get_bot_token()
        while self.is_running:
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates?offset={self.last_update_id + 1}&timeout=15"
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    for upd in data.get("result", []):
                        self.last_update_id = upd["update_id"]
                        msg = upd.get("message", {})
                        text = msg.get("text", "").strip()
                        chat_id = str(msg.get("chat", {}).get("id", ""))
                        user_name = msg.get("from", {}).get("first_name", "Foydalanuvchi")

                        if chat_id:
                            save_admin_chat_id(chat_id)

                        if text:
                            self._handle_command(chat_id, user_name, text)
            except Exception:
                time.sleep(3)
            time.sleep(0.5)

    def _handle_command(self, chat_id: str, user_name: str, text: str):
        low = text.lower()
        if low in ["/start", "salom", "start"]:
            welcome = (
                f"Assalomu alaykum, <b>{user_name}</b>!\n\n"
                f"🌌 <b>ALFRAGANUS AI</b> kompyuteringizga muvaffaqiyatli ulandi!\n\n"
                f"Siz ushbu bot orqali kompyuteringizni masofadan to'liq boshqarishingiz mumkin:\n\n"
                f"📸 /screen yoki <code>ekran</code> — Ekran skrinshotini olish\n"
                f"📊 /status — Tizim holati va internet tezligi\n"
                f"🔒 /lock — Kompyuterni qulflash\n"
                f"🚀 /open [ilova] — Dasturni ochish (masalan: <code>/open telegram</code>)\n"
                f"💬 Yoki oddiy o'zbekcha yozing (masalan: <i>Chrome ni och</i>, <i>Ovozni 50 ga qo'y</i>)"
            )
            send_bot_message(welcome, chat_id)

        elif low in ["/screen", "/screenshot", "ekran", "skrinshot", "ekranni ko'rsat"]:
            send_bot_screenshot("🖥️ Kompyuteringizning ayni damdagi ekrani:", chat_id)

        elif low in ["/status", "status", "holat", "tizim holati"]:
            rep = system_monitor()
            send_bot_message(f"📊 <b>Tizim Telemetriyasi:</b>\n\n{rep}", chat_id)

        elif low in ["/lock", "qulfla", "kompyuterni qulfla"]:
            res = computer_settings("lock")
            send_bot_message(f"🔒 {res}", chat_id)

        elif low.startswith("/open "):
            app = text[6:].strip()
            res = open_app(app)
            send_bot_message(f"🚀 {res}", chat_id)

        elif low.startswith("/close "):
            app = text[7:].strip()
            res = close_app(app)
            send_bot_message(f"🛑 {res}", chat_id)

        else:
            # Universal command via engine or direct app
            if "telegram" in low and ("och" in low or "xabar" in low):
                from actions.telegram_controller import open_telegram_chat
                open_telegram_chat("Telegram")
                send_bot_message(f"✅ Telegram ilovasi kompyuterda ochildi.", chat_id)
            else:
                from actions.open_app import open_app
                res = open_app(text)
                send_bot_message(f"🤖 Buyruq bajarildi: {res}", chat_id)
