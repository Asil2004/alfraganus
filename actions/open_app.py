import os
import sys
import time
import json
import difflib
import subprocess
import shutil
from pathlib import Path
import psutil

# Expanded Comprehensive Aliases (Uzbek, Russian, English)
KNOWN_ALIASES = {
    # Browsers & Internet
    "chrome": "chrome",
    "google chrome": "chrome",
    "google": "chrome",
    "gugl": "chrome",
    "хром": "chrome",
    "гугл хром": "chrome",
    "гугл": "chrome",
    "yandex": "browser",
    "yandeks": "browser",
    "yandex browser": "browser",
    "яндекс": "browser",
    "яндекс браузер": "browser",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "brave": "brave",
    "opera": "opera",
    "firefox": "firefox",
    "utorrent": "uTorrent Web",
    "torrent": "uTorrent Web",
    "торрент": "uTorrent Web",
    
    # Messengers & Social
    "telegram": "Telegram",
    "tg": "Telegram",
    "telefram": "Telegram",
    "telegran": "Telegram",
    "телеграм": "Telegram",
    "тг": "Telegram",
    "whatsapp": "WhatsApp",
    "vatsap": "WhatsApp",
    "ватсап": "WhatsApp",
    "instagram": "Instagram",
    "insta": "Instagram",
    "инстаграм": "Instagram",
    
    # 3D CAD & Engineering Software
    "kompas": "КОМПАС-3D v21",
    "kompas 3d": "КОМПАС-3D v21",
    "kompas3d": "КОМПАС-3D v21",
    "компас": "КОМПАС-3D v21",
    "компас 3д": "КОМПАС-3D v21",
    "компас-3d": "КОМПАС-3D v21",
    "coreldraw": "CorelDRAW 2025",
    "corel": "CorelDRAW 2025",
    "korel": "CorelDRAW 2025",
    "корел": "CorelDRAW 2025",
    "корел дро": "CorelDRAW 2025",
    "solidworks": "SOLIDWORKS",
    "solid": "SOLIDWORKS",
    "солид": "SOLIDWORKS",
    "солидворкс": "SOLIDWORKS",
    "lasergrbl": "LaserGRBL",
    "lazer": "LaserGRBL",
    "лазер": "LaserGRBL",
    "tokarlik": "RDB Tokarlik CNC",
    "rdb tokarlik": "RDB Tokarlik CNC",
    "cnc": "RDB Tokarlik CNC",
    "токарлик": "RDB Tokarlik CNC",
    "cura": "UltiMaker Cura 5.12.0",
    "ultimaker cura": "UltiMaker Cura 5.12.0",
    "ultimaker": "UltiMaker Cura 5.12.0",
    "3d pechat": "UltiMaker Cura 5.12.0",
    "3d printer": "UltiMaker Cura 5.12.0",
    "k40": "K40 Whisperer",
    "k40 whisperer": "K40 Whisperer",
    "crealityscan": "CrealityScan",
    "creality scan": "CrealityScan",
    "3d skaner": "CrealityScan",
    "inkscape": "Inkscape",
    "инкскейп": "Inkscape",
    "paint.net": "paint.net",
    "paint net": "paint.net",
    "пейнт нет": "paint.net",
    "autocad": "acad",
    "avtokad": "acad",
    "автокад": "acad",
    "blender": "blender",
    "блендер": "blender",
    "photoshop": "photoshop",
    "fotoshop": "photoshop",
    "фотошоп": "photoshop",
    
    # Medical & Custom Kiosk
    "medlife": "MedLife",
    "medlife kiosk": "MedLife",
    "tibbiyot kiosk": "MedLife",
    "медлайф": "MedLife",
    "intelectual property": "Intelectual Property App",
    "intellectual property": "Intelectual Property App",
    
    # Office & Productivity
    "word": "winword",
    "vord": "winword",
    "ворд": "winword",
    "microsoft word": "winword",
    "excel": "excel",
    "eksel": "excel",
    "эксель": "excel",
    "microsoft excel": "excel",
    "powerpoint": "powerpnt",
    "prezentatsiya": "powerpnt",
    "поверпоинт": "powerpnt",
    "foxit": "Foxit PDF Reader",
    "foxit reader": "Foxit PDF Reader",
    "pdf reader": "Foxit PDF Reader",
    "фоксит": "Foxit PDF Reader",
    "abbyy": "ABBYY FineReader PDF",
    "finereader": "ABBYY FineReader PDF",
    "файнридер": "ABBYY FineReader PDF",
    "total commander": "Total Commander x64",
    "total": "Total Commander x64",
    "тотал коммандер": "Total Commander x64",
    "aimp": "AIMP",
    "muzika": "AIMP",
    "аимп": "AIMP",
    "potplayer": "PotPlayer (64-bit)",
    "video pleyer": "PotPlayer (64-bit)",
    "потплеер": "PotPlayer (64-bit)",
    "notepad": "notepad",
    "bloknot": "notepad",
    "блокнот": "notepad",
    "calculator": "calc",
    "kalkulyator": "calc",
    "калькулятор": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "peynt": "mspaint",
    "пейнт": "mspaint",
    "snipping tool": "snippingtool",
    "qaychi": "snippingtool",
    "ножницы": "snippingtool",
    "task manager": "taskmgr",
    "dispetcher zadach": "taskmgr",
    "диспетчер задач": "taskmgr",
    
    # Developer & AI
    "antigravity": "Antigravity",
    "claude": "Claude",
    "клод": "Claude",
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "arduino": "Arduino IDE",
    "arduino ide": "Arduino IDE",
    "ардуино": "Arduino IDE",
    "raspberry pi": "Raspberry Pi Imager",
    "raspberry imager": "Raspberry Pi Imager",
    "scratch": "scratch",
    "vnc": "RealVNC Connect Viewer",
    "realvnc": "RealVNC Connect Viewer",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    
    # Windows System & AppsFolder
    "settings": "ms-settings:",
    "sozlamalar": "ms-settings:",
    "настройки": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "kamera": "microsoft.windows.camera:",
    "камера": "microsoft.windows.camera:",
    "store": "ms-windows-store:",
    "microsoft store": "ms-windows-store:",
    "control panel": "control",
    "boshqaruv paneli": "control",
    "панель управления": "control",
    "this pc": "explorer.exe shell:MyComputerFolder",
    "mening kompyuterim": "explorer.exe shell:MyComputerFolder",
    "kompyuterim": "explorer.exe shell:MyComputerFolder",
    "мой компьютер": "explorer.exe shell:MyComputerFolder",
    "recycle bin": "explorer.exe shell:RecycleBinFolder",
    "savat": "explorer.exe shell:RecycleBinFolder",
    "korzina": "explorer.exe shell:RecycleBinFolder",
    "корзина": "explorer.exe shell:RecycleBinFolder",
    "file explorer": "explorer",
    "explorer": "explorer",
    "fayllar": "explorer",
    "проводник": "explorer"
}

# Cache for StartApps (Name -> AppID mapping)
_START_APPS_CACHE = {}
_LAST_CACHE_TIME = 0


def _clean_app_query(raw_query: str) -> str:
    """O'zbekcha va ruscha qo'shimchalarni tozalab, ilova asosiy nomini ajratadi"""
    q = raw_query.lower().strip()
    
    # Qo'shimchalar va fe'llar
    removals = [
        "ni ochib ber", "ni ishga tushir", "ni ishlat", "ni yoq", "ni boshla", "ni och",
        "ochib ber", "ishga tushir", "ishlat", "yoq", "boshla", "och", "yurgiz",
        "dasturini", "ilovasini", "programmasini", "programmani", "ilovasi", "dasturi",
        "ni", "ga", "da", "dan", "da och", "ni och"
    ]
    
    for r in removals:
        if q.endswith(" " + r):
            q = q[:-len(" " + r)].strip()
        elif q.endswith(r) and len(q) > len(r) + 2:
            q = q[:-len(r)].strip()
            
    return q.strip()


def _get_start_apps() -> dict:
    """Windows Get-StartApps orqali barcha rasmiy ilovalar (Win32 + UWP/Store) ro'yxatini oladi"""
    global _START_APPS_CACHE, _LAST_CACHE_TIME
    now = time.time()
    if _START_APPS_CACHE and (now - _LAST_CACHE_TIME < 300):
        return _START_APPS_CACHE
        
    apps = {}
    try:
        ps_cmd = "Get-StartApps | Select-Object Name, AppID | ConvertTo-Json"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=8)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                n = str(item.get("Name", "")).strip()
                aid = str(item.get("AppID", "")).strip()
                if n and aid:
                    apps[n.lower()] = {"name": n, "appid": aid}
    except Exception:
        pass
        
    _START_APPS_CACHE = apps
    _LAST_CACHE_TIME = now
    return apps


def _scan_all_desktop_and_system_items() -> dict:
    """Ish stoli, Start Menyu, AppData va WindowsApps papkalarini skan qiladi"""
    user_home = Path(os.environ.get("USERPROFILE", r"C:\Users\MSI"))
    shortcut_dirs = [
        user_home / "Desktop",
        Path(r"C:\Users\Public\Desktop"),
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        user_home / "AppData" / "Local" / "Microsoft" / "WindowsApps"
    ]
    
    items = {}
    
    # 1. Desktop Items
    desktop_dir = user_home / "Desktop"
    if desktop_dir.exists():
        for p in desktop_dir.iterdir():
            if p.name.lower() in ["desktop.ini"]:
                continue
            name_stem = p.stem.lower().strip()
            name_full = p.name.lower().strip()
            items[name_stem] = str(p)
            items[name_full] = str(p)
            
    # 2. Shortcuts and Executables
    for s_dir in shortcut_dirs:
        if s_dir.exists():
            try:
                for p in s_dir.rglob("*.lnk"):
                    name_clean = p.stem.lower().strip()
                    if name_clean not in items:
                        items[name_clean] = str(p)
                for p in s_dir.rglob("*.exe"):
                    name_clean = p.stem.lower().strip()
                    if name_clean not in items:
                        items[name_clean] = str(p)
            except Exception:
                pass
                
    return items


def _launch_target(target: str, display_name: str) -> bool:
    """Har qanday manzil (AppID, URI, .lnk, .exe, System path) bo'yicha ilovani ishga tushiradi"""
    # 1. Windows UWP / Store AppID
    if "!" in target or target.startswith("Microsoft.") or target.startswith("{") or target.startswith("electron."):
        try:
            subprocess.Popen(f'explorer.exe "shell:AppsFolder\\{target}"', shell=True)
            return True
        except Exception:
            pass

    # 2. URI Protocol (ms-settings:, microsoft.windows.camera:, etc.)
    if ":" in target and not Path(target).is_absolute():
        try:
            subprocess.Popen(f'start {target}', shell=True)
            return True
        except Exception:
            pass

    # 3. Direct File / Shortcut Execution
    p = Path(target)
    if p.exists():
        try:
            os.startfile(str(p))
            return True
        except Exception:
            try:
                subprocess.Popen(f'start "" "{str(p)}"', shell=True)
                return True
            except Exception:
                pass

    # 4. PATH / Command Launch
    try:
        subprocess.Popen(f'start "" "{target}"', shell=True)
        return True
    except Exception:
        pass

    return False


def open_app(app_name: str) -> str:
    """
    Universal Ko'p Bosqichli Ilova Ishga Tushiruvchi:
    1. So'rovni tozalash va leksik tahlil (Uzbek Suffix Stripper).
    2. Maxsus Aliaslar jadvalidan tekshirish.
    3. Windows Get-StartApps (Barcha Win32 va Microsoft Store/UWP ilovalari).
    4. Ish stoli, Start Menu va AppData yorliqlarini to'liq tekshirish.
    5. PATH muhit o'zgaruvchilari (shutil.which).
    6. Noaniq qidiruv (Fuzzy Matching).
    7. Vizual sun'iy intellekt orqali ekrandan qidirib ochish (Visual Grounding).
    """
    raw_query = app_name.strip()
    cleaned = _clean_app_query(raw_query)
    
    # 1. Check Known Aliases
    target_alias = KNOWN_ALIASES.get(cleaned) or KNOWN_ALIASES.get(raw_query.lower())
    if target_alias:
        if _launch_target(target_alias, app_name):
            focus_app(cleaned)
            return f"✅ '{app_name}' muvaffaqiyatli ishga tushirildi."

    # 2. Check Windows Get-StartApps Database
    start_apps = _get_start_apps()
    
    # Aniq moslik
    if cleaned in start_apps:
        item = start_apps[cleaned]
        if _launch_target(item["appid"], item["name"]):
            focus_app(cleaned)
            return f"✅ '{item['name']}' dasturi ishga tushirildi."

    # Substring moslik
    for app_k, app_info in start_apps.items():
        if cleaned in app_k or app_k in cleaned:
            if _launch_target(app_info["appid"], app_info["name"]):
                focus_app(cleaned)
                return f"✅ '{app_info['name']}' dasturi ishga tushirildi."

    # 3. Check Desktop & System Shortcuts Directory
    items = _scan_all_desktop_and_system_items()
    if cleaned in items:
        p_str = items[cleaned]
        if _launch_target(p_str, Path(p_str).stem):
            focus_app(cleaned)
            return f"✅ '{Path(p_str).name}' ishga tushirildi."

    for item_key, item_path in items.items():
        if cleaned in item_key or item_key in cleaned:
            if _launch_target(item_path, Path(item_path).stem):
                focus_app(cleaned)
                return f"✅ '{Path(item_path).name}' ishga tushirildi."

    # 4. Check System Executables in PATH
    which_path = shutil.which(cleaned)
    if which_path:
        if _launch_target(which_path, cleaned):
            focus_app(cleaned)
            return f"✅ '{cleaned}' tizim buyrug'i ishga tushirildi."

    # 5. Fuzzy Match across StartApps and Shortcuts
    all_keys = list(set(list(start_apps.keys()) + list(items.keys()) + list(KNOWN_ALIASES.keys())))
    close_matches = difflib.get_close_matches(cleaned, all_keys, n=1, cutoff=0.35)
    if close_matches:
        matched_key = close_matches[0]
        if matched_key in start_apps:
            item = start_apps[matched_key]
            if _launch_target(item["appid"], item["name"]):
                focus_app(cleaned)
                return f"✅ '{item['name']}' topildi va ishga tushirildi."
        elif matched_key in items:
            p_str = items[matched_key]
            if _launch_target(p_str, Path(p_str).stem):
                focus_app(cleaned)
                return f"✅ '{Path(p_str).name}' topildi va ishga tushirildi."
        elif matched_key in KNOWN_ALIASES:
            alias_tgt = KNOWN_ALIASES[matched_key]
            if _launch_target(alias_tgt, matched_key):
                focus_app(cleaned)
                return f"✅ '{matched_key}' ochildi."

    # 6. Visual Desktop / Screen Grounding Search (AI Vision)
    try:
        from actions.screen_processor import screen_click
        vision_res = screen_click(target=app_name, click_type="double_click")
        if "topildi" in vision_res:
            time.sleep(0.8)
            return f"✅ '{app_name}' ekranda topildi va ikki marta bosilib ochildi."
    except Exception:
        pass

    # 7. Fallback Direct Start Attempt
    try:
        subprocess.Popen(f'start "" "{cleaned}"', shell=True)
        return f"✅ '{app_name}' buyrug'i tizimga yuborildi."
    except Exception as e:
        return f"⚠️ '{app_name}' nomli dastur yoki fayl topilmadi: {e}"


def focus_app(app_name: str) -> str:
    name_clean = _clean_app_query(app_name)
    ps_cmd = f"$w = New-Object -ComObject WScript.Shell; $p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{name_clean}*' -or $_.ProcessName -like '*{name_clean}*' }} | Select-Object -First 1; if ($p) {{ $w.AppActivate($p.Id); 'OK' }} else {{ 'NOT_FOUND' }}"
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
        if "OK" in res.stdout:
            return f"'{app_name}' oynasi oldinga chiqarildi."
        return f"'{app_name}' nomli ochiq oyna topilmadi."
    except Exception as e:
        return f"Oynani faollashtirishda xatolik: {e}"


def list_installed_apps(query: str = "") -> str:
    start_apps = _get_start_apps()
    items = _scan_all_desktop_and_system_items()
    q = (query or "").lower().strip()
    
    unique_names = set()
    for k, v in start_apps.items():
        unique_names.add(v["name"])
    for k, p in items.items():
        unique_names.add(Path(p).stem)
        
    results = []
    for name in sorted(unique_names):
        if not q or q in name.lower():
            results.append(f"• {name}")
            if len(results) >= 50:
                break
                
    if results:
        return f"Kompyuterdagi barcha mavjud dasturlar ({len(unique_names)} ta):\n" + "\n".join(results)
    return "Ilovalar topilmadi."


def close_app(app_name: str) -> str:
    name_clean = _clean_app_query(app_name)
    closed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            p_name = proc.info['name'].lower()
            if name_clean in p_name:
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    if closed_count > 0:
        return f"'{app_name}' ga oid {closed_count} ta jarayon yopildi."
    return f"'{app_name}' nomli ishlayotgan dastur topilmadi."
