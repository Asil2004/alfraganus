import io
import os
import json
import time
import threading
import requests
from pathlib import Path
from PIL import Image, ImageGrab

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


def get_gemini_api_key() -> str:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("gemini_api_key", "")
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
            return "Xabar Telegramga muvaffaqiyatli yuborildi."
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


def send_bot_camera_photo(caption: str = "📷 Noutbuk kamerasi surati", chat_id: str = None) -> str:
    token = get_bot_token()
    cid = chat_id or get_admin_chat_id()
    if not token or not cid:
        return "Telegram Bot yoki Chat ID sozlanmagan."

    cap = None
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Kamera ochilmadi yoki boshqa dastur tomonidan band."
        
        # Olingan bir nechta kadrlarni o'tkazib yuborish (avto-fokus va yorug'lik moslashuvi)
        for _ in range(5):
            cap.read()
        
        ret, frame = cap.read()
        cap.release()
        cap = None

        if not ret or frame is None:
            return "Kameradan tasvir olinmadi."

        ret, encoded_img = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if not ret:
            return "Tasvirni formatlashda xatolik."

        img_bytes = io.BytesIO(encoded_img.tobytes())
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": ("camera_capture.jpg", img_bytes, "image/jpeg")}
        data = {"chat_id": cid, "caption": caption}
        resp = requests.post(url, data=data, files=files, timeout=15)
        if resp.status_code == 200:
            return "Kamera surati Telegramga jo'natildi."
        return f"Kamera rasmini yuborishda xatolik: {resp.text}"
    except Exception as e:
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
        return f"Kameradan surat olishda xatolik: {e}"


def send_bot_live_combo(caption: str = "🖥️📹 Kompyuter ekrani va noutbuk kamerasi (Live Combo)", chat_id: str = None) -> str:
    """Ekran va kamera tasvirini bir vaqtning o'zida bitta suratda (Picture-in-Picture) yuboradi"""
    token = get_bot_token()
    cid = chat_id or get_admin_chat_id()
    if not token or not cid:
        return "Telegram Bot yoki Chat ID sozlanmagan."

    cap = None
    try:
        import cv2
        import numpy as np

        # 1. Ekranni suratga olish
        screenshot = ImageGrab.grab()
        screen_np = np.array(screenshot)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 2. Kameradan kadr olish
        cap = cv2.VideoCapture(0)
        cam_frame = None
        if cap.isOpened():
            for _ in range(4):
                cap.read()
            ret, cam_frame = cap.read()
            cap.release()
            cap = None

        # 3. Kamerani ekranga o'rnatish (Picture-in-Picture)
        if cam_frame is not None:
            sh, sw, _ = screen_bgr.shape
            pip_w = int(sw * 0.28)
            pip_h = int(pip_w * 0.75)
            cam_resized = cv2.resize(cam_frame, (pip_w, pip_h))

            x_off = sw - pip_w - 25
            y_off = sh - pip_h - 25
            if x_off > 0 and y_off > 0:
                # Oltin/Neon ramka chizish
                cv2.rectangle(screen_bgr, (x_off - 4, y_off - 4), (x_off + pip_w + 4, y_off + pip_h + 4), (0, 240, 255), 3)
                screen_bgr[y_off:y_off+pip_h, x_off:x_off+pip_w] = cam_resized
                cv2.putText(screen_bgr, "KAMERA (LIVE)", (x_off + 10, y_off + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 163), 2)

        ret, encoded_img = cv2.imencode('.jpg', screen_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
        if not ret:
            return "Tasvirni formatlashda xatolik."

        img_bytes = io.BytesIO(encoded_img.tobytes())
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": ("live_combo.jpg", img_bytes, "image/jpeg")}
        data = {"chat_id": cid, "caption": caption}
        resp = requests.post(url, data=data, files=files, timeout=15)
        if resp.status_code == 200:
            return "Ekran va kamera kombinatsiyasi Telegramga jo'natildi."
        return f"Xatolik: {resp.text}"
    except Exception as e:
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
        return f"Live tasvir yaratishda xatolik: {e}"


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
                        chat_id = str(msg.get("chat", {}).get("id", ""))
                        user_name = msg.get("from", {}).get("first_name", "Foydalanuvchi")

                        if chat_id:
                            save_admin_chat_id(chat_id)

                        text = msg.get("text", "").strip()
                        voice_info = msg.get("voice") or msg.get("audio")

                        if voice_info:
                            file_id = voice_info.get("file_id")
                            if file_id:
                                threading.Thread(
                                    target=self._handle_voice_message,
                                    args=(chat_id, user_name, file_id),
                                    daemon=True
                                ).start()
                        elif text:
                            self._handle_command(chat_id, user_name, text)
            except Exception:
                time.sleep(3)
            time.sleep(0.5)

    def _handle_voice_message(self, chat_id: str, user_name: str, file_id: str):
        token = get_bot_token()
        api_key = get_gemini_api_key()
        if not token or not api_key:
            send_bot_message("⚠️ Ovozni tahlil qilish uchun API sozlamalari topilmadi.", chat_id)
            return

        try:
            send_bot_message("🎙️ <i>Ovozli xabar qabul qilindi, Alfraganus AI tahlil qilmoqda...</i>", chat_id)

            # 1. Telegramdan ovoz faylini yuklab olish
            file_info_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
            resp = requests.get(file_info_url, timeout=15)
            if resp.status_code != 200:
                send_bot_message("⚠️ Ovoz faylini yuklab olishda xatolik bo'ldi.", chat_id)
                return

            file_path = resp.json().get("result", {}).get("file_path", "")
            download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
            audio_bytes = requests.get(download_url, timeout=20).content

            # 2. Gemini bilan transkripsiya va buyruqni anglash
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = (
                "Siz Alfraganus AI - kompyuterni boshqaruvchi kiber-assistent tizimisiz. "
                "Foydalanuvchi audio ovozli xabar yubordi.\n"
                "Quyidagi vazifalarni bajaring:\n"
                "1. Foydalanuvchi ovozini o'zbek tilida aniq matnga o'giring (transkripsiya).\n"
                "2. Foydalanuvchining niyatini/buyrug'ini tushunib, do'stona va aniq javob bering.\n\n"
                "Javobingizni quyidagi JSON formatda qaytaring (faqat JSON bo'lsin):\n"
                "{\n"
                '  "transcript": "Foydalanuvchi aytgan so\'zlar",\n'
                '  "action_type": "live | camera | screenshot | status | lock | open_app | chat",\n'
                '  "target": "ochilishi kerak bo\'lgan ilova nomi yoki bo\'sh",\n'
                '  "reply": "Foydalanuvchiga do\'stona o\'zbekcha javob matni"\n'
                "}"
            )

            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")
            
            # Model nomlari fallback zanjiri (eng so'nggi va faol modellar)
            candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash-native-audio-latest", "gemini-2.0-flash"]
            ai_res = None
            last_err = None

            for model_name in candidate_models:
                try:
                    ai_res = client.models.generate_content(
                        model=model_name,
                        contents=[audio_part, prompt]
                    )
                    if ai_res and ai_res.text:
                        break
                except Exception as ex:
                    last_err = ex
                    continue

            if not ai_res or not ai_res.text:
                raise Exception(f"AI model javob bermadi: {last_err}")

            raw_txt = ai_res.text.strip()
            if raw_txt.startswith("```json"):
                raw_txt = raw_txt[7:]
            if raw_txt.startswith("```"):
                raw_txt = raw_txt[3:]
            if raw_txt.endswith("```"):
                raw_txt = raw_txt[:-3]

            parsed = {}
            try:
                parsed = json.loads(raw_txt.strip())
            except Exception:
                parsed = {
                    "transcript": "Ovoz qabul qilindi",
                    "action_type": "chat",
                    "reply": raw_txt
                }

            transcript = parsed.get("transcript", "")
            action_type = parsed.get("action_type", "chat")
            target = parsed.get("target", "")
            reply = parsed.get("reply", "Buyruq bajarildi.")

            msg_out = f"🎙️ <b>Siz:</b> <i>«{transcript}»</i>\n\n🤖 <b>Alfraganus:</b> {reply}"
            send_bot_message(msg_out, chat_id)

            # Amallarni ijro etish
            act_low = action_type.lower()
            trans_low = transcript.lower()

            if act_low == "live" or ("ekran" in trans_low and "kamera" in trans_low):
                send_bot_live_combo("🖥️📹 Kompyuter ekrani va noutbuk kamerasi live tasviri:", chat_id)
            elif act_low == "camera" or "kamera" in trans_low or "surat" in trans_low:
                send_bot_camera_photo("📷 Noutbuk kamerasi orqali olingan surat:", chat_id)
            elif act_low == "screenshot" or "ekran" in trans_low or "skrinshot" in trans_low:
                send_bot_screenshot("🖥️ Kompyuteringizning ayni damdagi ekrani:", chat_id)
            elif act_low == "status" or "holat" in trans_low or "tizim" in trans_low:
                rep = system_monitor()
                send_bot_message(f"📊 <b>Tizim Holati:</b>\n\n{rep}", chat_id)
            elif act_low == "lock" or "qulfla" in trans_low:
                computer_settings("lock")
            elif act_low == "open_app" or target:
                app_name = target or transcript
                open_app(app_name)

        except Exception as e:
            send_bot_message(f"⚠️ Ovozli xabarni qayta ishlashda xatolik: {e}", chat_id)

    def _handle_command(self, chat_id: str, user_name: str, text: str):
        low = text.lower().strip()
        if low in ["/start", "salom", "start", "/help", "yordam"]:
            welcome = (
                f"Assalomu alaykum, <b>{user_name}</b>!\n\n"
                f"🌌 <b>ALFRAGANUS AI</b> kompyuteringizga muvaffaqiyatli ulandi!\n\n"
                f"Siz ushbu bot orqali kompyuteringizni masofadan to'liq boshqarishingiz mumkin:\n\n"
                f"🎙️ <b>Ovozli xabar:</b> Menga to'g'ridan-to'g'ri ovozli xabar (voice) yuboring — Alfraganus uni tushunib, darhol kompyuteringizda bajaradi!\n\n"
                f"🖥️📹 /live yoki <code>combo</code> — Ekran va kamera tasvirini birgalikda (Picture-in-Picture) olish\n"
                f"📷 /cam yoki <code>kamera</code> — Noutbuk kamerasidan surat olish\n"
                f"🖥️ /screen yoki <code>ekran</code> — Kompyuter ekranini live skrinshot qilish\n"
                f"📊 /status — Tizim telemetriyasi va yuklamalar\n"
                f"🔒 /lock — Kompyuterni qulflash\n"
                f"🚀 /open [ilova] — Dasturni ochish (masalan: <code>/open telegram</code>)\n"
                f"🛑 /close [ilova] — Dasturni yopish\n"
                f"💬 Yoki oddiy o'zbekcha yozing (masalan: <i>Kamera va ekranni ko'rsat</i>, <i>Youtube ni och</i>, <i>Ovozni 50 ga qo'y</i>)"
            )
            send_bot_message(welcome, chat_id)

        elif low in ["/live", "/combo", "live", "combo", "ekran va kamera", "kamera va ekran", "live ekran", "ekran kamera"]:
            send_bot_live_combo("🖥️📹 Kompyuter ekrani va noutbuk kamerasi (Live Combo):", chat_id)

        elif low in ["/cam", "/camera", "kamera", "surat", "rasm", "kamera surat", "kamera rasm", "suratga ol"]:
            send_bot_camera_photo("📷 Noutbuk kamerasi orqali olingan surat:", chat_id)

        elif low in ["/screen", "/screenshot", "ekran", "skrinshot", "ekranni ko'rsat"]:
            send_bot_screenshot("🖥️ Kompyuteringizning ayni damdagi ekrani:", chat_id)

        elif low in ["/status", "status", "holat", "tizim holati", "telemetriya"]:
            rep = system_monitor()
            send_bot_message(f"📊 <b>Tizim Telemetriyasi:</b>\n\n{rep}", chat_id)

        elif low in ["/lock", "qulfla", "kompyuterni qulfla", "bloklash"]:
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
            if "kamera" in low and "ekran" in low:
                send_bot_live_combo("🖥️📹 Kompyuter ekrani va noutbuk kamerasi live tasviri:", chat_id)
            elif "kamera" in low or "surat" in low:
                send_bot_camera_photo("📷 Noutbuk kamerasi orqali olingan surat:", chat_id)
            elif "ekran" in low or "skrinshot" in low:
                send_bot_screenshot("🖥️ Kompyuteringizning ayni damdagi ekrani:", chat_id)
            elif "telegram" in low and ("och" in low or "xabar" in low):
                from actions.telegram_controller import open_telegram_chat
                open_telegram_chat("Telegram")
                send_bot_message("✅ Telegram ilovasi kompyuterda ochildi.", chat_id)
            else:
                res = open_app(text)
                send_bot_message(f"🤖 Buyruq bajarildi: {res}", chat_id)
