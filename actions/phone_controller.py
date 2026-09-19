import os
import sys
import time
import subprocess
import shutil
import json
import io
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)


def get_adb_path() -> Optional[str]:
    """Tizimdan ADB (Android Debug Bridge) dasturini avtomatik aniqlaydi"""
    # 1. Standart PATH
    adb_in_path = shutil.which("adb")
    if adb_in_path:
        return adb_in_path

    # 2. Odatdagi Windows Android SDK va maxsus yo'llar
    candidates = [
        r"C:\Users\MSI\AppData\Local\Android\Sdk\platform-tools\adb.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
        r"C:\platform-tools\adb.exe",
        r"C:\adb\adb.exe",
        r"D:\platform-tools\adb.exe",
    ]

    for p in candidates:
        if os.path.exists(p):
            return p

    return None


def run_adb(args: List[str], timeout: int = 15) -> subprocess.CompletedProcess:
    """ADB buyrug'ini xavfsiz ishga tushiradi"""
    adb_path = get_adb_path()
    if not adb_path:
        raise FileNotFoundError(
            "ADB dasturi topilmadi. Iltimos, Android SDK platform-tools o'rnatilganini tekshiring."
        )

    cmd = [adb_path] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )


def get_connected_devices() -> List[Dict[str, str]]:
    """Kompyuterga ulangan Android qurilmalar ro'yxatini qaytaradi"""
    try:
        res = run_adb(["devices", "-l"])
        lines = res.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                dev_id = parts[0]
                status = parts[1]
                model = "Noma'lum"
                for p in parts[2:]:
                    if p.startswith("model:"):
                        model = p.split(":", 1)[1]
                devices.append({"id": dev_id, "status": status, "model": model, "raw": line})
        return devices
    except Exception:
        return []


def connect_wifi(ip_address: str, port: int = 5555) -> str:
    """Telefonni Wi-Fi orqali simsiz ulash (Wireless Debugging)"""
    try:
        target = ip_address.strip()
        if ":" not in target:
            target = f"{target}:{port}"
        res = run_adb(["connect", target])
        out = res.stdout.strip() or res.stderr.strip()
        if "connected" in out.lower():
            return f"✅ Telefon Wi-Fi orqali muvaffaqiyatli ulandi ({target})."
        return f"Ulanish natijasi: {out}"
    except Exception as e:
        return f"Wi-Fi orqali ulanishda xatolik: {e}"


def pair_wifi(ip_address: str, port: int, pairing_code: str) -> str:
    """Android 11+ uchun simsiz juftlash (Pairing Code)"""
    try:
        target = f"{ip_address.strip()}:{port}"
        res = run_adb(["pair", target, str(pairing_code).strip()])
        return f"Juftlash natijasi: {res.stdout.strip() or res.stderr.strip()}"
    except Exception as e:
        return f"Juftlashda xatolik: {e}"


# Ommabop Android ilovalari to'plami
POPULAR_APPS = {
    "youtube": "com.google.android.youtube",
    "telegram": "org.telegram.messenger",
    "telegram plus": "org.telegram.plus",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "camera": "com.android.camera",
    "kamera": "com.android.camera",
    "gallery": "com.google.android.apps.photos",
    "galereya": "com.google.android.apps.photos",
    "rasmlar": "com.google.android.apps.photos",
    "chrome": "com.android.chrome",
    "brauzer": "com.android.chrome",
    "tiktok": "com.zhiliaoapp.musically",
    "settings": "com.android.settings",
    "sozlamalar": "com.android.settings",
    "calculator": "com.google.android.calculator",
    "kalkulyator": "com.google.android.calculator",
    "phone": "com.google.android.dialer",
    "telefon": "com.google.android.dialer",
    "qo'ng'iroq": "com.google.android.dialer",
    "messages": "com.google.android.apps.messaging",
    "sms": "com.google.android.apps.messaging",
    "xabarlar": "com.google.android.apps.messaging",
    "maps": "com.google.android.apps.maps",
    "xarita": "com.google.android.apps.maps",
    "clock": "com.google.android.deskclock",
    "soat": "com.google.android.deskclock",
    "budilnik": "com.google.android.deskclock",
    "spotify": "com.spotify.music",
    "yandex music": "ru.yandex.music",
    "yandex": "com.yandex.browser",
    "play store": "com.android.vending",
    "market": "com.android.vending",
    "gmail": "com.google.android.gm",
    "pochta": "com.google.android.gm",
    "notes": "com.google.android.keep",
    "eslatmalar": "com.google.android.keep",
    "file manager": "com.google.android.apps.nbu.files",
    "fayllar": "com.google.android.apps.nbu.files",
}


def open_phone_app(app_name: str) -> str:
    """Telefonda dasturni ochadi"""
    app_key = app_name.lower().strip()
    pkg = POPULAR_APPS.get(app_key, app_name)
    
    try:
        # Monkey orqali asosiy Launch Intentni ishga tushirish
        res = run_adb(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
        if res.returncode == 0:
            return f"Telefonda '{app_name}' ilovasi ochildi."
        
        # Fallback: am start
        res2 = run_adb(["shell", "monkey", "-p", pkg, "1"])
        if res2.returncode == 0:
            return f"Telefonda '{app_name}' ilovasi ochildi."
        
        return f"Telefonda ochish natijasi: {res.stdout.strip() or res.stderr.strip()}"
    except Exception as e:
        return f"Telefonda ilovani ochishda xatolik: {e}"


def close_phone_app(app_name: str) -> str:
    """Telefonda ilovani to'xtatadi (Force Stop)"""
    app_key = app_name.lower().strip()
    pkg = POPULAR_APPS.get(app_key, app_name)
    try:
        run_adb(["shell", "am", "force-stop", pkg])
        return f"Telefonda '{app_name}' ilovasi to'xtatildi."
    except Exception as e:
        return f"Ilovani to'xtatishda xatolik: {e}"


def phone_tap(x: int, y: int) -> str:
    """Telefon ekranining (X, Y) koordinatasiga bosadi"""
    try:
        run_adb(["shell", "input", "tap", str(x), str(y)])
        return f"Telefon ekranida ({x}, {y}) nuqtasi bosildi."
    except Exception as e:
        return f"Ekranga bosishda xatolik: {e}"


def phone_swipe(direction: str = "up", distance: int = 600) -> str:
    """Telefon ekranini suradi / skroll qiladi (up, down, left, right)"""
    try:
        # Odatdagi ekran o'lchami 1080x2400 deb olinadi
        cx, cy = 540, 1200
        d = int(distance)
        
        if direction.lower() in ["up", "yuqoriga", "pastdan_tepaga"]:
            x1, y1, x2, y2 = cx, cy + d // 2, cx, cy - d // 2
        elif direction.lower() in ["down", "pastga", "tepadan_pastga"]:
            x1, y1, x2, y2 = cx, cy - d // 2, cx, cy + d // 2
        elif direction.lower() in ["left", "chapga"]:
            x1, y1, x2, y2 = cx + d // 2, cy, cx - d // 2, cy
        elif direction.lower() in ["right", "o'ngga", "ongga"]:
            x1, y1, x2, y2 = cx - d // 2, cy, cx + d // 2, cy
        else:
            x1, y1, x2, y2 = cx, cy + 300, cx, cy - 300

        run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), "300"])
        return f"Telefon ekrani {direction} yo'nalishida surildi."
    except Exception as e:
        return f"Ekranni surishda xatolik: {e}"


def phone_type_text(text: str) -> str:
    """Telefonda matn yozadi"""
    try:
        # Bo'shliqlarni va maxsus belgilarni to'g'ri uzatish
        escaped_text = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
        run_adb(["shell", "input", "text", escaped_text])
        return f"Telefonga '{text}' matni yozildi."
    except Exception as e:
        return f"Matn yozishda xatolik: {e}"


def phone_press_key(key: str) -> str:
    """Telefondagi apparat yoki tizim tugmalarini bosadi"""
    key_map = {
        "home": "3",
        "back": "4",
        "orqaga": "4",
        "call": "5",
        "end_call": "6",
        "power": "26",
        "qulflash": "26",
        "ekranni_yoqish": "26",
        "volume_up": "24",
        "ovoz_baland": "24",
        "volume_down": "25",
        "ovoz_past": "25",
        "mute": "164",
        "camera": "27",
        "enter": "66",
        "delete": "67",
        "backspace": "67",
        "recents": "187",
        "app_switch": "187",
        "barcha_ilovalar": "187",
        "play_pause": "85",
        "screenshot": "120"
    }
    
    k = key.lower().strip()
    code = key_map.get(k, k)
    try:
        run_adb(["shell", "input", "keyevent", code])
        return f"Telefonda '{key}' tugmasi bosildi."
    except Exception as e:
        return f"Tugmani bosishda xatolik: {e}"


def phone_make_call(phone_number: str) -> str:
    """Telefonda raqam terish yoki to'g'ridan-to'g'ri qo'ng'iroq qilish"""
    try:
        clean_num = "".join([c for c in phone_number if c.isdigit() or c == "+"])
        if not clean_num:
            return "Telefon raqami noto'g'ri ko'rsatildi."
        
        # Dial intent (foydalanuvchi ekranda tasdiqlashi yoki to'g'ridan-to'g'ri terish)
        run_adb(["shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{clean_num}"])
        return f"Telefonda {clean_num} raqamiga qo'ng'iroq boshlandi."
    except Exception as e:
        return f"Qo'ng'iroq qilishda xatolik: {e}"


def phone_send_sms(phone_number: str, message: str) -> str:
    """Telefonda SMS xabar yuborish"""
    try:
        clean_num = "".join([c for c in phone_number if c.isdigit() or c == "+"])
        run_adb(["shell", "am", "start", "-a", "android.intent.action.SENDTO", "-d", f"smsto:{clean_num}", "--es", "sms_body", message])
        # SMS dasturida yuborish tugmasi
        time.sleep(1)
        run_adb(["shell", "input", "keyevent", "66"])
        return f"Telefonda {clean_num} raqamiga '{message}' SMS xabari tayyorlandi va yuborildi."
    except Exception as e:
        return f"SMS yuborishda xatolik: {e}"


def phone_battery_status() -> str:
    """Telefon batareya holati va quvvat foizini oladi"""
    try:
        res = run_adb(["shell", "dumpsys", "battery"])
        out = res.stdout.strip()
        if not out:
            return "Telefon batareya ma'lumotlarini olib bo'lmadi. Telefon ulanganini tekshiring."

        level = "Noma'lum"
        status = "Noma'lum"
        temp = "Noma'lum"
        
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("level:"):
                level = line.split(":", 1)[1].strip() + "%"
            elif line.startswith("status:"):
                st_code = line.split(":", 1)[1].strip()
                status = "Zaryadlanmoqda" if st_code == "2" else "Batareyadan ishlamoqda"
            elif line.startswith("temperature:"):
                try:
                    temp_val = float(line.split(":", 1)[1].strip()) / 10.0
                    temp = f"{temp_val}°C"
                except Exception:
                    pass

        return f"🔋 Telefon batareyasi: {level}\n⚡ Holati: {status}\n🌡️ Harorati: {temp}"
    except Exception as e:
        return f"Batareyani tekshirishda xatolik: {e}"


def phone_device_info() -> str:
    """Telefon modeli, Android versiyasi va texnik holatini aniqlaydi"""
    try:
        devices = get_connected_devices()
        if not devices:
            return (
                "📱 Hozirda ulangan telefon topilmadi.\n\n"
                "Ulash yo'llari:\n"
                "1. USB kabeli orqali ulab, telefonda 'USB orqali tuzatish (USB Debugging)'ni yoqing;\n"
                "2. Yoki Wi-Fi orqali: 'Telefonga Wi-Fi orqali ulan: [Telefon_IP_manzili]:5555' deb buyruq bering;\n"
                "3. Yoki Windows rasmiy 'Telefon bilan aloqa (Phone Link)' dasturini ochishni so'rang."
            )

        model = run_adb(["shell", "getprop", "ro.product.model"]).stdout.strip()
        brand = run_adb(["shell", "getprop", "ro.product.brand"]).stdout.strip()
        android_ver = run_adb(["shell", "getprop", "ro.build.version.release"]).stdout.strip()
        battery = phone_battery_status()

        return (
            f"📱 Ulangan Telefon: {brand.upper()} {model}\n"
            f"🤖 Android Versiyasi: {android_ver}\n"
            f"{battery}\n"
            f"✅ ADB aloqasi to'liq faol."
        )
    except Exception as e:
        return f"Telefon ma'lumotlarini olishda xatolik: {e}"


def capture_phone_screenshot() -> Optional[Path]:
    """Telefon ekrani skrinshotini oladi va fayl sifatida saqlaydi"""
    try:
        screen_file = TEMP_DIR / "phone_screen.png"
        adb_path = get_adb_path()
        if not adb_path:
            return None

        # To'g'ridan-to'g'ri binary oqim orqali skrinshot olish (juda tez)
        with open(screen_file, "wb") as f:
            cmd = [adb_path, "exec-out", "screencap", "-p"]
            subprocess.run(cmd, stdout=f, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

        if screen_file.exists() and screen_file.stat().st_size > 1000:
            return screen_file
        return None
    except Exception:
        return None


def phone_screen_vision(query: str = "Telefon ekranida nima ko'rsatilgan? Asosiy ma'lumotlarni o'zbek tilida aytib ber.") -> str:
    """Telefon ekranini rasmga olib, Gemini Vision orqali tahlil qiladi va foydalanuvchiga aytib beradi"""
    try:
        screen_path = capture_phone_screenshot()
        if not screen_path:
            return "Telefon ekranini rasmga olib bo'lmadi. Telefon USB yoki Wi-Fi orqali ulanganini tekshiring."

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                api_key = json.load(f)["gemini_api_key"]
        except Exception:
            return "Gemini API kaliti topilmadi."

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
        with open(screen_path, "rb") as f:
            image_bytes = f.read()

        prompt = f"""Siz Alfraganus AI assistentisiz. Foydalanuvchining smartfoni ekrani tasviri berilgan.
Savol/Vazifa: {query}

Ko'rsatmalar:
- Telefon ekranidagi ilovalar, xabarlar, bildirishnomalar yoki kontentni tahlil qiling.
- O'zbek tilida juda aniq, qisqa va lo'nda tushuntiring.
"""
        response = None
        for m in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        prompt
                    ]
                )
                if response and response.text:
                    break
            except Exception:
                continue
        return response.text.strip() if response else "Tahlil qilib bo'lmadi."
    except Exception as e:
        return f"Telefon ekranini tahlil qilishda xatolik: {e}"


def open_windows_phone_link() -> str:
    """Windows'ning rasmiy Telefon bilan aloqa (Phone Link) dasturini ochadi"""
    try:
        subprocess.run(["powershell", "-Command", "Start-Process 'ms-phone:'"], check=False)
        return "Windows 'Telefon bilan aloqa' (Phone Link) dasturi ochildi."
    except Exception as e:
        return f"Phone Link ochishda xatolik: {e}"


def phone_controller(
    action: str = "status",
    app_name: str = "",
    text: str = "",
    phone_number: str = "",
    ip: str = "",
    port: int = 5555,
    pairing_code: str = "",
    x: int = 0,
    y: int = 0,
    direction: str = "up",
    key: str = "home",
    query: str = ""
) -> str:
    """
    Telefon va smartfonlarni to'liq boshqarish:
    - status / info: Qurilma va batareya holatini ko'rish
    - open_app: Telefonda ilovani ochish (YouTube, Telegram, Instagram, Kamera, Galereya, Sozlamalar va b.)
    - close_app: Telefonda ilovani to'xtatish
    - tap: Ekranning (X, Y) nuqtasiga bosish
    - swipe / scroll: Ekranni surish (up, down, left, right)
    - type_text: Telefonga matn yozish
    - press_key: Home, Back, Recents, Power, Volume_up, Volume_down tugmalarini bosish
    - call: Qo'ng'iroq qilish
    - send_sms: SMS yuborish
    - screen_vision / screen_process: Telefon ekranini ko'rish va Gemini Vision orqali tahlil qilish
    - connect_wifi: Simsiz Wi-Fi (ADB) orqali ulanish
    - pair_wifi: Simsiz tuzatish juftlash kodi bilan ulash
    - phone_link: Windows Telefon bilan aloqa dasturini ochish
    - notify: Telegram orqali telefonga xabar/skrinshot yuborish
    """
    act = (action or "status").lower().strip()

    if act in ["status", "info", "device_info", "qurilma", "holat"]:
        return phone_device_info()

    elif act in ["battery", "battery_status", "batareya", "quvvat"]:
        return phone_battery_status()

    elif act in ["open_app", "open", "launch", "ilovani_och", "och"]:
        target_app = app_name or text or query
        if not target_app:
            return "Ochilishi kerak bo'lgan ilova nomi ko'rsatilmadi."
        return open_phone_app(target_app)

    elif act in ["close_app", "close", "stop", "yop", "toxtat"]:
        target_app = app_name or text or query
        return close_phone_app(target_app)

    elif act in ["tap", "click", "bos", "ekranga_bos"]:
        return phone_tap(x, y)

    elif act in ["swipe", "scroll", "surish", "ekranni_sur", "sur"]:
        return phone_swipe(direction=direction or "up")

    elif act in ["type", "type_text", "text", "yoz", "matn_yoz"]:
        input_text = text or query
        return phone_type_text(input_text)

    elif act in ["press_key", "key", "button", "tugma", "home", "back", "power", "volume_up", "volume_down"]:
        target_key = key if act in ["press_key", "key", "button", "tugma"] else act
        return phone_press_key(target_key)

    elif act in ["call", "qongiroq", "telefon_qil", "terish"]:
        target_num = phone_number or text or query
        return phone_make_call(target_num)

    elif act in ["sms", "send_sms", "xabar_yubor"]:
        target_num = phone_number or text
        msg = query or text
        return phone_send_sms(target_num, msg)

    elif act in ["screen_vision", "screen_process", "ekranga_qara", "ekran_tahlili", "screenshot", "ko'rish"]:
        prompt_query = query or text or "Telefon ekranida nima ko'rsatilgan?"
        return phone_screen_vision(prompt_query)

    elif act in ["connect_wifi", "wifi_connect", "simsiz_ulan"]:
        target_ip = ip or text or query
        return connect_wifi(target_ip, port=port or 5555)

    elif act in ["pair_wifi", "pair"]:
        target_ip = ip or text
        return pair_wifi(target_ip, port=port or 5555, pairing_code=pairing_code)

    elif act in ["phone_link", "windows_link", "telefon_bilan_aloqa"]:
        return open_windows_phone_link()

    elif act in ["notify", "send_notification", "telegram_notify"]:
        from actions.telegram_bot_bridge import send_bot_message
        msg = text or query or "Alfraganus AI bildirishnomasi"
        return send_bot_message(f"📱 <b>TELEFON BILDIRISHNOMASI:</b>\n{msg}")

    else:
        # Fallback to device info or general handler
        return phone_device_info()
