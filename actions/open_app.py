import os
import sys
import time
import json
import difflib
import subprocess
import shutil
import webbrowser
from pathlib import Path
import psutil
import ctypes
import win32gui
import win32con
import win32process

USER_HOME = Path(os.environ.get("USERPROFILE", r"C:\Users\MSI"))

# Well-known System Standard Folders
STANDARD_FOLDERS = {
    "c": "C:\\",
    "c disk": "C:\\",
    "c: ": "C:\\",
    "d": "D:\\",
    "d disk": "D:\\",
    "d: ": "D:\\",
    "antigravity": "D:\\antigravity",
    "antigravity papkasi": "D:\\antigravity",
    "alfraganus": "D:\\antigravity\\alfraganus",
    "alfraganus papkasi": "D:\\antigravity\\alfraganus",
    "terminal": "D:\\antigravity\\terminal",
    "terminal papkasi": "D:\\antigravity\\terminal",
    "cnc": "D:\\antigravity\\cnc",
    "cnc papkasi": "D:\\antigravity\\cnc",
    "set print": "D:\\antigravity\\set print",
    "telegram bot": "D:\\antigravity\\telegram bot",
    "yuklamalar": str(USER_HOME / "Downloads"),
    "downloads": str(USER_HOME / "Downloads"),
    "zagruzki": str(USER_HOME / "Downloads"),
    "hujjatlar": str(USER_HOME / "Documents"),
    "documents": str(USER_HOME / "Documents"),
    "dokumenti": str(USER_HOME / "Documents"),
    "ish stoli": str(USER_HOME / "Desktop"),
    "desktop": str(USER_HOME / "Desktop"),
    "rabochiy stol": str(USER_HOME / "Desktop"),
    "rasmlar": str(USER_HOME / "Pictures"),
    "pictures": str(USER_HOME / "Pictures"),
    "foto": str(USER_HOME / "Pictures"),
    "musiqalar": str(USER_HOME / "Music"),
    "music": str(USER_HOME / "Music"),
    "videolar": str(USER_HOME / "Videos"),
    "videos": str(USER_HOME / "Videos"),
    "video": str(USER_HOME / "Videos"),
}

# Dedicated Explicit Executables and Aliases (Priority mappings)
KNOWN_ALIASES = {
    # Official Telegram Desktop (Must NOT be Unigram)
    "telegram": str(USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"),
    "telegram desktop": str(USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"),
    "tg": str(USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"),
    "telefram": str(USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"),
    "телеграм": str(USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"),
    "unigram": "38833FF26BA1D.UnigramPreview_g9c9v27vpyspw!App",
    "юниграм": "38833FF26BA1D.UnigramPreview_g9c9v27vpyspw!App",
    
    # Browsers & Internet
    "chrome": "chrome",
    "google chrome": "chrome",
    "google": "chrome",
    "gugl": "chrome",
    "хром": "chrome",
    "гугл хром": "chrome",
    "yandex": r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
    "yandex browser": r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
    "yandeks": r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
    "яндекс": r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "brave": "brave",
    "opera": "opera",
    "firefox": "firefox",
    
    # Social & Messengers
    "whatsapp": "WhatsApp",
    "vatsap": "WhatsApp",
    "ватсап": "WhatsApp",
    "instagram": str(USER_HOME / "Desktop" / "Instagram.lnk"),
    "insta": str(USER_HOME / "Desktop" / "Instagram.lnk"),
    "инстаграм": str(USER_HOME / "Desktop" / "Instagram.lnk"),
    "youtube": "https://www.youtube.com",
    "yutub": "https://www.youtube.com",
    "ютуб": "https://www.youtube.com",
    
    # 3D CAD & Engineering Software
    "kompas": "КОМПАС-3D v21",
    "kompas 3d": "КОМПАС-3D v21",
    "kompas3d": "КОМПАС-3D v21",
    "компас": "КОМПАС-3D v21",
    "компас 3д": "КОМПАС-3D v21",
    "coreldraw": "CorelDRAW 2025",
    "corel": "CorelDRAW 2025",
    "korel": "CorelDRAW 2025",
    "корел": "CorelDRAW 2025",
    "solidworks": "SOLIDWORKS",
    "solid": "SOLIDWORKS",
    "солид": "SOLIDWORKS",
    "lasergrbl": "LaserGRBL",
    "lazer": "LaserGRBL",
    "лазер": "LaserGRBL",
    "tokarlik": "RDB Tokarlik CNC",
    "rdb tokarlik": "RDB Tokarlik CNC",
    "cnc": "RDB Tokarlik CNC",
    "cura": "UltiMaker Cura 5.12.0",
    "ultimaker cura": "UltiMaker Cura 5.12.0",
    "3d pechat": "UltiMaker Cura 5.12.0",
    "k40": "K40 Whisperer",
    "k40 whisperer": "K40 Whisperer",
    "crealityscan": "CrealityScan",
    "creality scan": "CrealityScan",
    "inkscape": "Inkscape",
    "paint.net": "paint.net",
    "paint net": "paint.net",
    
    # Office & Media
    "word": "winword",
    "vord": "winword",
    "ворд": "winword",
    "excel": "excel",
    "eksel": "excel",
    "эксель": "excel",
    "powerpoint": "powerpnt",
    "prezentatsiya": "powerpnt",
    "foxit": "Foxit PDF Reader",
    "abbyy": "ABBYY FineReader PDF",
    "total commander": "Total Commander x64",
    "total": "Total Commander x64",
    "aimp": "AIMP",
    "muzika": "AIMP",
    "potplayer": "PotPlayer (64-bit)",
    "notepad": "notepad",
    "bloknot": "notepad",
    "блокнот": "notepad",
    "calculator": "calc",
    "kalkulyator": "calc",
    "калькулятор": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "qaychi": "snippingtool",
    "task manager": "taskmgr",
    "dispetcher zadach": "taskmgr",
    
    # Developer & AI
    "antigravity": "Antigravity",
    "claude": "Claude",
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "arduino": "Arduino IDE",
    "raspberry pi": "Raspberry Pi Imager",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    
    # System Protocols
    "settings": "ms-settings:",
    "sozlamalar": "ms-settings:",
    "kamera": "microsoft.windows.camera:",
    "camera": "microsoft.windows.camera:",
    "store": "ms-windows-store:",
    "control panel": "control",
    "boshqaruv paneli": "control",
    "this pc": "explorer.exe shell:MyComputerFolder",
    "kompyuterim": "explorer.exe shell:MyComputerFolder",
    "savat": "explorer.exe shell:RecycleBinFolder",
    "recycle bin": "explorer.exe shell:RecycleBinFolder",
    "korzina": "explorer.exe shell:RecycleBinFolder",
    "file explorer": "explorer",
    "explorer": "explorer",
    "fayllar": "explorer"
}

_START_APPS_CACHE = {}
_LAST_CACHE_TIME = 0


def _clean_app_query(raw_query: str) -> str:
    """O'zbekcha va ruscha qo'shimchalarni tozalab, toza nomni ajratadi"""
    q = raw_query.lower().strip()
    
    removals = [
        "ni ochib ber", "ni ishga tushir", "ni ishlat", "ni yoq", "ni boshla", "ni och",
        "ochib ber", "ishga tushir", "ishlat", "yoq", "boshla", "och", "yurgiz", "kir",
        "ga kir", "ga o't", "ni ko'rsat", "ko'rsat",
        "dasturini", "ilovasini", "programmasini", "programmani", "ilovasi", "dasturi",
        "papkasi", "papkasini", "papka", "papkani", "fayli", "faylini",
        "ni", "ga", "da", "dan"
    ]
    
    for r in removals:
        if q.endswith(" " + r):
            q = q[:-len(" " + r)].strip()
        elif q.endswith(r) and len(q) > len(r) + 2:
            q = q[:-len(r)].strip()
            
    return q.strip()


def restore_and_focus_window(app_name: str) -> bool:
    """
    Agar ilova taskbarda minimayz bo'lib turgan yoki orqa fonda ochiq bo'lsa:
    Uni yangidan ochmasdan, taskbardagi oynani TIKLAYDI (Restore) va oldinga chiqaradi.
    """
    cleaned = _clean_app_query(app_name).lower()
    
    # Maxsus nomlar xaritasi
    target_procs = []
    if "telegram" in cleaned:
        target_procs = ["telegram.exe"]
    elif "chrome" in cleaned or "google" in cleaned or "xrom" in cleaned:
        target_procs = ["chrome.exe"]
    elif "yandex" in cleaned or "yandeks" in cleaned:
        target_procs = ["browser.exe", "yandex.exe"]
    elif "word" in cleaned or "vord" in cleaned:
        target_procs = ["winword.exe"]
    elif "excel" in cleaned or "eksel" in cleaned:
        target_procs = ["excel.exe"]
    elif "code" in cleaned or "vscode" in cleaned:
        target_procs = ["code.exe"]
    elif "kompas" in cleaned:
        target_procs = ["kompas.exe"]
    elif "corel" in cleaned:
        target_procs = ["coreldrw.exe"]
    elif "explorer" in cleaned or "fayl" in cleaned:
        target_procs = ["explorer.exe"]
    elif "calc" in cleaned or "kalkulyator" in cleaned:
        target_procs = ["calculatorapp.exe", "calc.exe"]
    elif "notepad" in cleaned or "bloknot" in cleaned:
        target_procs = ["notepad.exe"]
    else:
        target_procs = [cleaned + ".exe", cleaned]

    found_hwnd = None
    found_title = ""

    def _enum_window_callback(hwnd, extra):
        nonlocal found_hwnd, found_title
        if not win32gui.IsWindow(hwnd):
            return True
        
        # Oyna matni va jarayon nomini olish
        title = win32gui.GetWindowText(hwnd).strip()
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            p = psutil.Process(pid)
            pname = p.name().lower()
        except Exception:
            pname = ""

        # Antigravity IDE oynasini o'zimiz ochmagan bo'lsak e'tiborsiz qoldirish
        if "antigravity" in pname and "antigravity" not in cleaned:
            return True

        # Jarayon yoki oyna sarlavhasi bo'yicha qidirish
        is_match = False
        for tp in target_procs:
            if tp in pname or pname.startswith(tp):
                is_match = True
                break
        if not is_match and title and (cleaned in title.lower()):
            is_match = True

        if is_match and (win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd)):
            # Asosiy katta oynalarni tanlash (0x0 bo'lmagan)
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w > 100 or h > 100 or win32gui.IsIconic(hwnd):
                found_hwnd = hwnd
                found_title = title or pname
                return False  # To'xtatish
        return True

    try:
        win32gui.EnumWindows(_enum_window_callback, None)
    except Exception:
        pass

    if found_hwnd:
        try:
            # 1. Agar minimayz bo'lsa, tiklash (SW_RESTORE = 9)
            if win32gui.IsIconic(found_hwnd):
                win32gui.ShowWindow(found_hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(found_hwnd, win32con.SW_SHOW)

            # 2. Windows API orqali oldinga chiqarish (Foreground Force)
            cur_thread = win32process.GetCurrentThreadId()
            target_thread, _ = win32process.GetWindowThreadProcessId(found_hwnd)
            ctypes.windll.user32.AttachThreadInput(cur_thread, target_thread, True)
            
            win32gui.SetForegroundWindow(found_hwnd)
            win32gui.BringWindowToTop(found_hwnd)
            
            ctypes.windll.user32.AttachThreadInput(cur_thread, target_thread, False)
            return True
        except Exception:
            try:
                ctypes.windll.user32.ShowWindow(found_hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(found_hwnd)
                return True
            except Exception:
                pass

    return False


def _get_start_apps() -> dict:
    """Windows Get-StartApps ro'yxatini kesh bilan qaytaradi"""
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
    shortcut_dirs = [
        USER_HOME / "Desktop",
        Path(r"C:\Users\Public\Desktop"),
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        USER_HOME / "AppData" / "Local" / "Microsoft" / "WindowsApps"
    ]
    
    items = {}
    desktop_dir = USER_HOME / "Desktop"
    if desktop_dir.exists():
        for p in desktop_dir.iterdir():
            if p.name.lower() not in ["desktop.ini"]:
                items[p.stem.lower().strip()] = str(p)
                items[p.name.lower().strip()] = str(p)
                
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


def _launch_target(target: str) -> bool:
    """Nishonni (AppID, URI, Web URL, .lnk, .exe, Fayl/Papka) ishga tushiradi"""
    # 0. URL Web manzil
    if target.startswith("http://") or target.startswith("https://"):
        try:
            webbrowser.open(target)
            return True
        except Exception:
            pass

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

    # 3. Direct File / Shortcut / Folder
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


def find_and_open_user_file(file_query: str) -> str | None:
    """
    Foydalanuvchi kompyuteridan faylni (PDF, DOCX, XLSX, PPTX, TXT, PY, MP4 va h.k.)
    nomi yoki kengaytmasi bo'yicha qidirib, standart dasturida ochadi.
    """
    q = file_query.strip().strip('"').strip("'")
    if not q:
        return None
    
    # 1. To'g'ridan-to'g'ri mavjud yo'l
    direct_p = Path(q)
    if direct_p.exists():
        if direct_p.is_file():
            try:
                os.startfile(str(direct_p))
                return f"✅ '{direct_p.name}' fayli tizimda ochildi ({direct_p})."
            except Exception:
                subprocess.Popen(f'start "" "{direct_p}"', shell=True)
                return f"✅ '{direct_p.name}' fayli ochildi."
        elif direct_p.is_dir():
            _launch_target(str(direct_p))
            return f"✅ '{direct_p.name}' papkasi ochildi."

    # 2. Qidiruv kalit so'zlarini tozalash
    search_term = q.lower()
    for prefix in ["fayl ", "fayli ", "hujjat ", "hujjati "]:
        if search_term.startswith(prefix):
            search_term = search_term[len(prefix):].strip()
    for suffix in [" fayli", " faylini", " fayl", " hujjati", " hujjatini", " hujjat", " och", " ochib ber"]:
        if search_term.endswith(suffix):
            search_term = search_term[:-len(suffix)].strip()

    if not search_term:
        search_term = q.lower()

    # 3. Asosiy foydalanuvchi kataloglari (tezkor qidiruv)
    search_dirs = [
        USER_HOME / "Desktop",
        USER_HOME / "Downloads",
        USER_HOME / "Documents",
        USER_HOME / "Pictures",
        USER_HOME / "Videos",
        USER_HOME / "Music",
        Path(r"D:\antigravity"),
        Path(r"D:\antigravity\alfraganus"),
        Path(r"D:\antigravity\cnc"),
        Path(r"D:\antigravity\terminal"),
        Path(r"D:\antigravity\set print"),
        Path(r"D:\antigravity\telegram bot"),
        USER_HOME,
    ]

    # Qidiruv 1: Aniq nom mosligi (Exact name match yoki stem match)
    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        try:
            for item in s_dir.iterdir():
                if item.is_file():
                    if item.name.lower() == search_term or item.stem.lower() == search_term:
                        try:
                            os.startfile(str(item))
                            return f"✅ '{item.name}' fayli tizimda ochildi ({item})."
                        except Exception:
                            subprocess.Popen(f'start "" "{item}"', shell=True)
                            return f"✅ '{item.name}' fayli ochildi."
        except Exception:
            continue

    # Qidiruv 2: Substring moslik (ichki papkalar bo'yicha cheklangan chuqurlikda)
    candidate_matches = []
    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        try:
            for root, dirs, files in os.walk(s_dir):
                rel = os.path.relpath(root, s_dir)
                depth = len(rel.split(os.sep)) if rel != "." else 0
                if depth > 2:
                    dirs.clear()
                    continue
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__", "AppData")]
                
                for f in files:
                    f_lower = f.lower()
                    if search_term in f_lower:
                        full_p = Path(root) / f
                        if full_p.stem.lower() == search_term or f_lower == search_term:
                            try:
                                os.startfile(str(full_p))
                                return f"✅ '{full_p.name}' fayli tizimda ochildi ({full_p})."
                            except Exception:
                                subprocess.Popen(f'start "" "{full_p}"', shell=True)
                                return f"✅ '{full_p.name}' fayli ochildi."
                        candidate_matches.append(full_p)
        except Exception:
            continue

    if candidate_matches:
        best = min(candidate_matches, key=lambda p: len(p.name))
        try:
            os.startfile(str(best))
            return f"✅ '{best.name}' fayli topildi va ochildi ({best})."
        except Exception:
            subprocess.Popen(f'start "" "{best}"', shell=True)
            return f"✅ '{best.name}' fayli ochildi."

    return None


def open_app(app_name: str) -> str:
    """
    Universal Ko'p Bosqichli Ilova, Fayl & Papka Ishga Tushiruvchi:
    1. Taskbarda minimayz bo'lgan oynani tekshirish va oldinga chiqarish (yangidan ochmaslik).
    2. Fayllarni qidirish va ochish (PDF, DOCX, XLSX, PPTX, TXT, PY, MP4 va b.).
    3. Papkalar va disklarni (D:, C:, Downloads, Desktop, Alfraganus) ochish.
    4. Maxsus Aliaslar (Official Telegram Desktop, Yandex, Chrome, Instagram).
    5. Windows Get-StartApps (Barcha Win32 va Microsoft Store/UWP ilovalari).
    6. Ish stoli va Start Menyu yorliqlari.
    7. Veb-ilova fallback (Instagram, Yandex, YouTube uchun brauzerda ochish).
    8. Noaniq qidiruv va Vizual Screen Grounding.
    """
    raw_query = app_name.strip()
    cleaned = _clean_app_query(raw_query)
    
    # 1. TASKBARDAGI MINIMAYZ BO'LGAN OYNALARNI TIKLASH
    if restore_and_focus_window(cleaned):
        return f"✅ '{app_name}' oynasi taskbardan tiklandi va oldinga chiqarildi."

    # 2. FAYLLARNI TEKSHIRISH (Agar so'rov fayl bo'lsa yoki kengaytmaga ega bo'lsa)
    is_explicit_file = any(w in raw_query.lower() for w in ["fayl", "fayli", "faylini", "hujjat", "file", ".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".py", ".mp4", ".png", ".jpg", ".zip"])
    if is_explicit_file:
        file_res = find_and_open_user_file(cleaned) or find_and_open_user_file(raw_query)
        if file_res:
            return file_res

    # 3. MAXSUS ALIASLAR VA RASMIY TELEGRAM DESKTOP (Ilovalar ustuvor)
    target_alias = KNOWN_ALIASES.get(cleaned) or KNOWN_ALIASES.get(raw_query.lower())
    if target_alias:
        # Agar Telegram bo'lsa, rasmiy Telegram Desktop .exe mavjudligini tekshirish
        if "telegram" in cleaned:
            tg_exe = USER_HOME / "AppData" / "Roaming" / "Telegram Desktop" / "Telegram.exe"
            tg_lnk = USER_HOME / "Desktop" / "Telegram.lnk"
            if tg_exe.exists():
                target_alias = str(tg_exe)
            elif tg_lnk.exists():
                target_alias = str(tg_lnk)

        # Agar Instagram bo'lsa va ilova ochilmasa, veb-saytga o'tish
        if "instagram" in cleaned:
            insta_lnk = USER_HOME / "Desktop" / "Instagram.lnk"
            if insta_lnk.exists():
                _launch_target(str(insta_lnk))
                return "✅ Instagram ilovasi ochildi."
            else:
                webbrowser.open("https://www.instagram.com")
                return "✅ Instagram veb-sayti brauzerda ochildi."

        if _launch_target(target_alias):
            return f"✅ '{app_name}' muvaffaqiyatli ishga tushirildi."

    # 4. PAPKA VA DISKLARNI TEKSHIRISH (Folder & Drive Navigator)
    if cleaned in STANDARD_FOLDERS:
        folder_path = STANDARD_FOLDERS[cleaned]
        if Path(folder_path).exists():
            _launch_target(folder_path)
            return f"✅ '{cleaned.title()}' papkasi Explorerda ochildi ({folder_path})."

    # Agar so'rov disk yoki papka bo'lsa (masalan: "D:\antigravity\cnc" yoki "C:\")
    if Path(cleaned).exists() and Path(cleaned).is_dir():
        _launch_target(cleaned)
        return f"✅ '{cleaned}' papkasi ochildi."

    # Maxsus antigravity ichidagi papkalarni qidirish (agar "papka" aytilgan bo'lsa yoki boshqa ilova topilmasa)
    is_folder_query = any(w in raw_query.lower() for w in ["papka", "papkasi", "folder", "disk"])
    if is_folder_query:
        ag_folder = Path(r"D:\antigravity")
        if ag_folder.exists():
            for sub in ag_folder.iterdir():
                if sub.is_dir() and (cleaned in sub.name.lower() or sub.name.lower() in cleaned):
                    _launch_target(str(sub))
                    return f"✅ '{sub.name}' papkasi Explorerda ochildi ({sub})."

    # 4. WINDOWS GET-STARTAPPS DATABASE
    start_apps = _get_start_apps()
    
    # Telegram so'ralganda Unigramni emas, faqat haqiqiy Telegramni tanlash
    if "telegram" in cleaned:
        if "telegram" in start_apps and "unigram" not in start_apps["telegram"]["name"].lower():
            item = start_apps["telegram"]
            if _launch_target(item["appid"]):
                return f"✅ Telegram Desktop dasturi ishga tushirildi."
    elif cleaned in start_apps:
        item = start_apps[cleaned]
        if _launch_target(item["appid"]):
            return f"✅ '{item['name']}' dasturi ishga tushirildi."

    # Substring moslik (Unigramni chetlab o'tish bilan)
    for app_k, app_info in start_apps.items():
        if cleaned in app_k or app_k in cleaned:
            if "telegram" in cleaned and "unigram" in app_k:
                continue
            if _launch_target(app_info["appid"]):
                return f"✅ '{app_info['name']}' dasturi ishga tushirildi."

    # 5. ISH STOLI VA START MENYU YORLIQLARI
    items = _scan_all_desktop_and_system_items()
    if cleaned in items:
        p_str = items[cleaned]
        if _launch_target(p_str):
            return f"✅ '{Path(p_str).name}' ishga tushirildi."

    for item_key, item_path in items.items():
        if cleaned in item_key or item_key in cleaned:
            if "telegram" in cleaned and "unigram" in item_key:
                continue
            if _launch_target(item_path):
                return f"✅ '{Path(item_path).name}' ishga tushirildi."

    # 6. VEB-ILOVA FALLBACK (Instagram, Yandex, YouTube)
    if "yandex" in cleaned or "yandeks" in cleaned:
        yandex_exe = Path(r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe")
        if yandex_exe.exists():
            _launch_target(str(yandex_exe))
            return f"✅ Yandex Browser ishga tushirildi."
        else:
            webbrowser.open("https://ya.ru")
            return f"✅ Yandex qidiruv tizimi brauzerda ochildi."

    # 7. FUZZY MATCH
    all_keys = list(set(list(start_apps.keys()) + list(items.keys()) + list(KNOWN_ALIASES.keys())))
    close_matches = difflib.get_close_matches(cleaned, all_keys, n=1, cutoff=0.38)
    if close_matches:
        matched_key = close_matches[0]
        if "telegram" in cleaned and "unigram" in matched_key:
            pass
        else:
            if matched_key in KNOWN_ALIASES:
                if _launch_target(KNOWN_ALIASES[matched_key]):
                    return f"✅ '{matched_key}' ochildi."
            elif matched_key in start_apps:
                if _launch_target(start_apps[matched_key]["appid"]):
                    return f"✅ '{start_apps[matched_key]['name']}' topildi va ochildi."
            elif matched_key in items:
                if _launch_target(items[matched_key]):
                    return f"✅ '{Path(items[matched_key]).name}' topildi va ochildi."

    # 8. VIZUAL SCREEN GROUNDING (AI Vision)
    try:
        from actions.screen_processor import screen_click
        vision_res = screen_click(target=app_name, click_type="double_click")
        if "topildi" in vision_res:
            time.sleep(0.8)
            return f"✅ '{app_name}' ekranda topildi va ochildi."
    except Exception:
        pass

    # 9. FAYLLAR VA HUJJATLAR (Agar foydalanuvchi biror fayl nomini aytgan bo'lsa)
    file_fallback = find_and_open_user_file(cleaned) or find_and_open_user_file(raw_query)
    if file_fallback:
        return file_fallback

    # 10. Topilmagan holatda aniq va rostgo'y xabar qaytarish (Yolg'on tasdiqlamaslik uchun)
    return f"⚠️ '{app_name}' nomli dastur, fayl yoki papka kompyuterdan topilmadi."


def focus_app(app_name: str) -> str:
    if restore_and_focus_window(app_name):
        return f"'{app_name}' oynasi oldinga chiqarildi."
    return f"'{app_name}' nomli ochiq oyna topilmadi."


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
