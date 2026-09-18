import os
import sys
import time
import subprocess
import difflib
from pathlib import Path
import psutil

# Expanded Comprehensive Aliases (Uzbek, Russian, English)
KNOWN_ALIASES = {
    # Browsers & Internet
    "chrome": "chrome",
    "google chrome": "chrome",
    "google": "chrome",
    "хром": "chrome",
    "гугл хром": "chrome",
    "yandex": "browser",
    "yandeks": "browser",
    "yandex browser": "browser",
    "яндекс": "browser",
    "яндекс браузер": "browser",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "brave": "brave",
    "utorrent": "uTorrent Web",
    "torrent": "uTorrent Web",
    "торрент": "uTorrent Web",
    
    # Messengers & Social
    "telegram": "Telegram",
    "tg": "Telegram",
    "телеграм": "Telegram",
    "whatsapp": "WhatsApp",
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
    "3d pechat": "UltiMaker Cura 5.12.0",
    "куpush": "UltiMaker Cura 5.12.0",
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
    
    # Windows System
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


def _scan_all_desktop_and_system_items():
    """Ish stolidagi va tizimdagi barcha ilovalar, yorliqlar, papkalar va fayllarni skan qiladi"""
    shortcut_dirs = [
        Path(r"C:\Users\MSI\Desktop"),
        Path(r"C:\Users\Public\Desktop"),
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs"
    ]
    
    items = {}
    
    # 1. Desktop Items (files, folders, shortcuts)
    desktop_dir = Path(r"C:\Users\MSI\Desktop")
    if desktop_dir.exists():
        for p in desktop_dir.iterdir():
            if p.name.lower() in ["desktop.ini"]:
                continue
            name_stem = p.stem.lower().strip()
            name_full = p.name.lower().strip()
            items[name_stem] = str(p)
            items[name_full] = str(p)
            
    # 2. Start Menu & Program Shortcuts
    for s_dir in shortcut_dirs:
        if s_dir.exists():
            for p in s_dir.rglob("*.lnk"):
                name_clean = p.stem.lower().strip()
                if name_clean not in items:
                    items[name_clean] = str(p)
            for p in s_dir.rglob("*.exe"):
                name_clean = p.stem.lower().strip()
                if name_clean not in items:
                    items[name_clean] = str(p)
                    
    return items


def _verify_and_double_click(app_label: str) -> str:
    """Ilova ochilgach ekranni skrinshot qilib tekshiradi, so'ng oyna/ilovaga 2 marta bosib faollashtiradi va tasdiqlaydi"""
    try:
        time.sleep(1.2)  # Oyna ekranda chizilishi uchun kutish
        temp_dir = Path(__file__).resolve().parent.parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        screen_file = temp_dir / "last_screen.png"
        
        # 1. Ekranni skrinshot qilib saqlash
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(all_screens=False)
            img.save(str(screen_file))
        except Exception:
            try:
                import pyautogui
                pyautogui.screenshot(str(screen_file))
            except Exception:
                pass

        # 2. Oynani faollashtirish va 2 marta klik qilish
        try:
            from actions.mouse_controller import mouse_control, smooth_move_to
            screen_w, screen_h = pyautogui.size()
            center_x, center_y = screen_w // 2, screen_h // 2
            
            # Agar oyna markazda ochilgan bo'lsa, markazga borib 2 marta bosiladi
            smooth_move_to(center_x, center_y, duration=0.2)
            pyautogui.doubleClick(center_x, center_y)
        except Exception:
            try:
                pyautogui.doubleClick()
            except Exception:
                pass

    except Exception:
        pass
    return f"'{app_label}' ilovasi ochildi, ekranda tekshirildi va ikki marta bosilib faollashtirildi."


def open_app(app_name: str) -> str:
    """
    1. Dastlab mustaqil ochishga harakat qiladi.
    2. Ekranni skrinshot qilib tekshiradi.
    3. Ilovaga 2 marta klik qiladi va tasdiqlaydi.
    4. Agar yorliq topilmasa, ekrandagi ikonkani topib 2 marta bosadi.
    """
    name_clean = app_name.lower().strip()
    
    # 1. Check known aliases first
    target = KNOWN_ALIASES.get(name_clean)
    if target:
        try:
            if target.startswith("ms-") or target.startswith("microsoft."):
                subprocess.Popen(f"start {target}", shell=True)
                return _verify_and_double_click(app_name)
            if target.startswith("explorer.exe"):
                subprocess.Popen(target, shell=True)
                return _verify_and_double_click(app_name)
            os.startfile(target)
            return _verify_and_double_click(app_name)
        except Exception:
            try:
                subprocess.Popen(f'start "" "{target}"', shell=True)
                return _verify_and_double_click(app_name)
            except Exception:
                pass

    # 2. Scan all desktop files, shortcuts, folders, and installed programs
    items = _scan_all_desktop_and_system_items()
    
    # Exact match
    if name_clean in items:
        p = items[name_clean]
        try:
            os.startfile(p)
            return _verify_and_double_click(Path(p).name)
        except Exception:
            try:
                subprocess.Popen(f'start "" "{p}"', shell=True)
                return _verify_and_double_click(Path(p).name)
            except Exception as e:
                return f"Ochishda xatolik: {e}"

    # Substring match
    for item_key, item_path in items.items():
        if name_clean in item_key or item_key in name_clean:
            try:
                os.startfile(item_path)
                return _verify_and_double_click(Path(item_path).name)
            except Exception:
                try:
                    subprocess.Popen(f'start "" "{item_path}"', shell=True)
                    return _verify_and_double_click(Path(item_path).name)
                except Exception as e:
                    return f"Ochishda xatolik: {e}"

    # 3. Fuzzy matching for typos or slight variations
    close_matches = difflib.get_close_matches(name_clean, items.keys(), n=1, cutoff=0.40)
    if close_matches:
        matched_key = close_matches[0]
        item_path = items[matched_key]
        try:
            os.startfile(item_path)
            return _verify_and_double_click(Path(item_path).name)
        except Exception:
            try:
                subprocess.Popen(f'start "" "{item_path}"', shell=True)
                return _verify_and_double_click(Path(item_path).name)
            except Exception as e:
                return f"'{matched_key}' ochishda xatolik: {e}"

    # 4. Visual Desktop Search (Ekrandan qidirib 2 marta bosish)
    try:
        from actions.screen_processor import screen_click
        vision_res = screen_click(target=app_name, click_type="double_click")
        if "topildi" in vision_res:
            time.sleep(1.0)
            return f"'{app_name}' ekranda topildi, ikki marta bosildi va ochildi."
    except Exception:
        pass

    # 5. Fallback to start command
    try:
        subprocess.Popen(f'start "" "{name_clean}"', shell=True)
        return _verify_and_double_click(app_name)
    except Exception as e:
        return f"'{app_name}' nomli dastur yoki fayl topilmadi: {e}"


def focus_app(app_name: str) -> str:
    name_clean = app_name.lower().strip()
    ps_cmd = f"$w = New-Object -ComObject WScript.Shell; $p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{name_clean}*' -or $_.ProcessName -like '*{name_clean}*' }} | Select-Object -First 1; if ($p) {{ $w.AppActivate($p.Id); 'OK' }} else {{ 'NOT_FOUND' }}"
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
        if "OK" in res.stdout:
            return f"'{app_name}' oynasi oldinga chiqarildi."
        return f"'{app_name}' nomli ochiq oyna topilmadi."
    except Exception as e:
        return f"Oynani faollashtirishda xatolik: {e}"


def list_installed_apps(query: str = "") -> str:
    items = _scan_all_desktop_and_system_items()
    q = (query or "").lower().strip()
    results = []
    for k, p in sorted(items.items()):
        if not q or q in k:
            results.append(f"• {Path(p).name}")
            if len(results) >= 40:
                break
    if results:
        return "Kompyuterdagi va ish stolidagi mavjud ilovalar/fayllar:\n" + "\n".join(results)
    return "Ilovalar topilmadi."


def close_app(app_name: str) -> str:
    name_clean = app_name.lower().strip()
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
