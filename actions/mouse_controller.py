import time
import math
import ctypes
from ctypes import wintypes
from pathlib import Path
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.005


def get_cursor_telemetry() -> dict:
    """Sichqoncha kursorining aniq koordinatalari, piksel rangi, ekran hududi va oyna nomini qaytaradi"""
    x, y = pyautogui.position()
    screen_w, screen_h = pyautogui.size()
    
    # Ekran hududini aniqlash
    h_pos = "Chap" if x < screen_w / 3 else ("O'rta" if x < 2 * screen_w / 3 else "O'ng")
    v_pos = "Yuqori" if y < screen_h / 3 else ("Markaz" if y < 2 * screen_h / 3 else "Pastki")
    region = f"{v_pos}-{h_pos}"
    if y >= screen_h - 45:
        region = "Vazifalar paneli (Taskbar)"
    elif y <= 35:
        region = "Sarlavha paneli (Titlebar / Top bar)"

    # Kursor ostidagi piksel rangi
    try:
        pixel = pyautogui.pixel(x, y)
        hex_color = f"#{pixel[0]:02X}{pixel[1]:02X}{pixel[2]:02X}"
        rgb_color = f"RGB({pixel[0]}, {pixel[1]}, {pixel[2]})"
    except Exception:
        hex_color = "#000000"
        rgb_color = "RGB(0, 0, 0)"

    # Kursor ostidagi oyna sarlavhasini aniqlash (Windows API)
    window_title = "Ish stoli (Desktop)"
    try:
        user32 = ctypes.windll.user32
        pt = wintypes.POINT(x, y)
        hwnd = user32.WindowFromPoint(pt)
        if hwnd:
            root_hwnd = user32.GetAncestor(hwnd, 2)  # GA_ROOT = 2
            length = user32.GetWindowTextLengthW(root_hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(root_hwnd, buf, length + 1)
                if buf.value.strip():
                    window_title = buf.value.strip()
    except Exception:
        pass

    return {
        "x": x,
        "y": y,
        "screen_w": screen_w,
        "screen_h": screen_h,
        "region": region,
        "hex_color": hex_color,
        "rgb_color": rgb_color,
        "window_title": window_title,
        "norm_x": round(x / max(1, screen_w) * 1000),
        "norm_y": round(y / max(1, screen_h) * 1000)
    }


def smooth_move_to(target_x: int, target_y: int, steps: int = 15, duration: float = 0.25):
    """Kursorni insoniy silliq harakat (Interpolatsiya) bilan ko'chiradi"""
    start_x, start_y = pyautogui.position()
    if start_x == target_x and start_y == target_y:
        return

    delay = duration / max(1, steps)
    for i in range(1, steps + 1):
        t = i / steps
        # S-curve (Smoothstep easing)
        ease_t = t * t * (3 - 2 * t)
        curr_x = int(start_x + (target_x - start_x) * ease_t)
        curr_y = int(start_y + (target_y - start_y) * ease_t)
        pyautogui.moveTo(curr_x, curr_y)
        time.sleep(delay)
    pyautogui.moveTo(target_x, target_y)


def circle_around(cx: int, cy: int, radius: int = 40, points: int = 16):
    """Belgilangan nuqta atrofida kursorni aylanma harakatlantirib ko'rsatadi"""
    for i in range(points + 1):
        angle = 2 * math.pi * (i / points)
        px = int(cx + radius * math.cos(angle))
        py = int(cy + radius * math.sin(angle))
        pyautogui.moveTo(px, py)
        time.sleep(0.01)
    pyautogui.moveTo(cx, cy)


def mouse_control(
    action: str,
    x: int = None,
    y: int = None,
    dx: int = 0,
    dy: int = 0,
    button: str = "left",
    clicks: int = 1,
    direction: str = "down",
    amount: int = 3,
    duration: float = 0.25,
    target: str = ""
) -> str:
    """
    Sichqonchaning barcha imkoniyatlarini to'liq boshqarish va koordinatalarni aniqlash funksiyasi:
    action turlari:
      - 'get_position' / 'info': Kursor koordinatasi, rangi, joylashgan oynasi va ekrandagi o'rnini qaytaradi
      - 'move': Koordinataga silliq ko'chirish
      - 'move_rel': Nisbiy siljitish (dx, dy)
      - 'click': Bir marta bosish (left, right, middle)
      - 'double_click': Ikki marta tez bosish (Double click)
      - 'triple_click': Uch marta tez bosish
      - 'right_click': O'ng tugma (Context menu)
      - 'middle_click': O'rta tugma (G'ildirakcha bosish)
      - 'mouse_down': Sichqoncha tugmasini bosib turish
      - 'mouse_up': Sichqoncha tugmasini qo'yib yuborish
      - 'drag': Belgilangan joyga sudrab olib borish (Drag and Drop)
      - 'scroll': Yuqoriga/pastga/yonboshga aylantirish
      - 'hover': Kursor bilan borib to'xtash
      - 'circle_highlight': Obyekt atrofida aylanib ko'rsatish
      - 'click_target': Ekranni sun'iy intellekt (Vision) bilan ko'rib, element ustiga borib 2 marta yoki 1 marta bosish
    """
    act = (action or "info").lower().strip()
    btn = (button or "left").lower().strip()

    try:
        if act in ("get_position", "info", "position", "where"):
            info = get_cursor_telemetry()
            return (
                f"Sichqoncha kursorining aniq holati:\n"
                f"• Koordinata: X={info['x']}, Y={info['y']} (Ekran: {info['screen_w']}x{info['screen_h']})\n"
                f"• Joylashuvi: {info['region']}\n"
                f"• Faol Oyna: {info['window_title']}\n"
                f"• Kursor ostidagi rang: {info['hex_color']} ({info['rgb_color']})"
            )

        elif act == "move":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=duration)
                return f"Kursor silliq harakat bilan ({x}, {y}) koordinatasiga o'tkazildi."
            return "Ko'chirish uchun X va Y koordinatalari ko'rsatilmadi."

        elif act == "move_rel":
            cur_x, cur_y = pyautogui.position()
            target_x = cur_x + dx
            target_y = cur_y + dy
            smooth_move_to(target_x, target_y, duration=duration)
            return f"Kursor ({dx}, {dy}) masofaga siljitildi -> Yangi o'rni: ({target_x}, {target_y})."

        elif act == "click":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=0.15)
            pyautogui.click(button=btn, clicks=clicks)
            pos = pyautogui.position()
            return f"Sichqoncha ({pos.x}, {pos.y}) nuqtasida {btn} tugmasi bilan {clicks} marta bosildi."

        elif act == "double_click":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=0.15)
            pyautogui.doubleClick(button=btn)
            pos = pyautogui.position()
            return f"Sichqoncha ({pos.x}, {pos.y}) nuqtasida 2 marta tez bosildi (Double Click)."

        elif act == "triple_click":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=0.15)
            pyautogui.tripleClick(button=btn)
            pos = pyautogui.position()
            return f"Sichqoncha ({pos.x}, {pos.y}) nuqtasida 3 marta tez bosildi."

        elif act == "right_click":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=0.15)
            pyautogui.rightClick()
            pos = pyautogui.position()
            return f"Sichqonchaning o'ng tugmasi ({pos.x}, {pos.y}) da bosildi."

        elif act == "middle_click":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=0.15)
            pyautogui.middleClick()
            pos = pyautogui.position()
            return f"Sichqonchaning o'rta (g'ildirakcha) tugmasi bosildi."

        elif act == "mouse_down":
            pyautogui.mouseDown(button=btn)
            return f"Sichqonchaning {btn} tugmasi bosib turildi."

        elif act == "mouse_up":
            pyautogui.mouseUp(button=btn)
            return f"Sichqonchaning {btn} tugmasi qo'yib yuborildi."

        elif act == "drag":
            if x is not None and y is not None:
                pyautogui.dragTo(x, y, duration=duration, button=btn)
                return f"Obyekt ({x}, {y}) koordinatasiga sudrab olib borildi."
            return "Sudrash uchun yakuniy X va Y koordinatalari berilmadi."

        elif act == "scroll":
            scroll_dir = direction.lower().strip()
            units = amount if scroll_dir in ("up", "yuqoriga") else -amount
            pyautogui.scroll(units * 100)
            return f"Sichqoncha g'ildirakchasi {scroll_dir} yo'nalishida {amount} birlik aylantirildi."

        elif act == "hover":
            if x is not None and y is not None:
                smooth_move_to(x, y, duration=duration)
                time.sleep(0.3)
                return f"Kursor ({x}, {y}) ustiga olib borib ushlab turildi (Hover)."
            return "Hover uchun koordinata berilmadi."

        elif act == "circle_highlight":
            cx = x if x is not None else pyautogui.position().x
            cy = y if y is not None else pyautogui.position().y
            circle_around(cx, cy)
            return f"Kursor ({cx}, {cy}) nuqtasi atrofida aylanib ko'rsatildi."

        elif act == "click_target":
            from actions.screen_processor import screen_click
            c_type = "double_click" if clicks >= 2 else "click"
            return screen_click(target=target or "target element", click_type=c_type)

        else:
            return f"Noma'lum sichqoncha amali: '{action}'."

    except Exception as e:
        return f"Sichqoncha harakatida xatolik: {e}"
