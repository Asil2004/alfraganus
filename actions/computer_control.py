import time
import pyautogui

pyautogui.FAILSAFE = False


def computer_control(action: str, x: int = None, y: int = None, text: str = "", key: str = "", shortcut: str = "", clicks: int = 1, direction: str = "down", amount: int = 3):
    action = action.lower().strip()
    try:
        if action == "move":
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.2)
                return f"Kursor ({x}, {y}) koordinatasiga o'tkazildi."
            return "Koordinatalar ko'rsatilmadi."

        elif action == "click":
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks)
                return f"({x}, {y}) nuqtasiga {clicks} marta bosildi."
            pyautogui.click(clicks=clicks)
            return f"Sichqoncha {clicks} marta bosildi."

        elif action == "right_click":
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
                return f"({x}, {y}) nuqtasida o'ng tugma bosildi."
            pyautogui.rightClick()
            return "Sichqonchaning o'ng tugmasi bosildi."

        elif action == "double_click":
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y)
                return f"({x}, {y}) nuqtasida ikki marta bosildi."
            pyautogui.doubleClick()
            return "Ikki marta tez bosildi."

        elif action == "drag":
            if x is not None and y is not None:
                pyautogui.dragTo(x, y, duration=0.4)
                return f"Obyekt ({x}, {y}) ga surildi."
            return "Surish koordinatasi berilmadi."

        elif action == "scroll":
            scroll_units = amount if direction == "up" else -amount
            pyautogui.scroll(scroll_units * 100)
            return f"{direction} yo'nalishida {amount} birlik aylantirildi."

        elif action == "type":
            if text:
                pyautogui.write(text, interval=0.02)
                return f"'{text}' matni yozildi."
            return "Yozish uchun matn berilmadi."

        elif action == "press":
            if key:
                pyautogui.press(key)
                return f"'{key}' tugmasi bosildi."
            return "Tugma nomi ko'rsatilmadi."

        elif action == "hotkey":
            if shortcut:
                keys = [k.strip().lower() for k in shortcut.split("+")]
                pyautogui.hotkey(*keys)
                return f"'{shortcut}' kombinatsiyasi bajarildi."
            return "Kombinatsiya ko'rsatilmadi."

        else:
            return f"Noma'lum amal: {action}"

    except Exception as e:
        return f"Xatolik: {e}"
