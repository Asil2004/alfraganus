import io
import re
import json
import base64
import time
from pathlib import Path
from PIL import ImageGrab
import pyautogui
from google import genai
from google.genai import types

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"


def _get_api_key():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["gemini_api_key"]
    except Exception:
        return ""


def _capture_screen():
    try:
        screenshot = ImageGrab.grab(all_screens=False)
        return screenshot
    except Exception:
        import pyautogui
        return pyautogui.screenshot()


def screen_process(query: str = "Ekranda nima ko'rsatilgan? Asosiy ma'lumotlarni o'zbek tilida qisqa tushuntir.") -> str:
    """Ekranni tahlil qilib, foydalanuvchining savoliga o'zbek tilida javob beradi (Vision)"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return "Gemini API kaliti topilmadi."

        client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

        screenshot = _capture_screen()
        screenshot.thumbnail((1920, 1080))

        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG', quality=85)
        image_bytes = img_byte_arr.getvalue()

        prompt = f"""Siz Alfraganus AI tizimisiz. Foydalanuvchi kompyuter ekraniga qarab quyidagi savol/buyruqni berdi:
Savol: {query}

Ko'rsatmalar:
- Ekrandagi ma'lumotlarni diqqat bilan tahlil qiling.
- O'zbek tilida juda aniq, qisqa va lo'nda javob bering.
- Agar biror xatolik oynasi, tugma yoki dastur ochiq bo'lsa, uni aniq tushuntiring.
"""
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
        except Exception:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
        return response.text.strip()
    except Exception as e:
        return f"Ekranni tahlil qilishda xatolik yuz berdi: {e}"


def screen_click(target: str, click_type: str = "click") -> str:
    """Ekrandagi kerakli tugma, belgi, yozuv yoki elementni ko'rib (Vision), kursor bilan borib bosadi (Click/Double Click/Right Click)"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return "Gemini API kaliti topilmadi."

        client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})

        screenshot = _capture_screen()
        screen_w, screen_h = pyautogui.size()

        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG', quality=85)
        image_bytes = img_byte_arr.getvalue()

        prompt = f"""You are a GUI grounding model. The user wants to click on the following UI element on screen:
Target: "{target}"

Analyze the image carefully. Return the normalized center coordinates of "{target}" (on a 0 to 1000 scale, where (0,0) is top-left, and (1000,1000) is bottom-right).
Return ONLY a JSON object:
{{"found": true, "x": <0-1000>, "y": <0-1000>, "description": "<element description>"}}
If the target is not visible on screen, return:
{{"found": false, "reason": "<why not found>"}}
"""
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
        except Exception:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )

        raw = response.text.strip()
        # JSON tozalash
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        data = json.loads(raw)
        if data.get("found"):
            norm_x = data["x"]
            norm_y = data["y"]
            target_x = int(norm_x * screen_w / 1000.0)
            target_y = int(norm_y * screen_h / 1000.0)

            pyautogui.moveTo(target_x, target_y, duration=0.35)
            time.sleep(0.1)

            c_type = click_type.lower().strip()
            if c_type == "double_click":
                pyautogui.doubleClick()
                action_name = "ikki marta bosildi"
            elif c_type == "right_click":
                pyautogui.rightClick()
                action_name = "o'ng tugma bosildi"
            else:
                pyautogui.click()
                action_name = "bosildi (Click)"

            return f"Ekrandagi '{target}' elementi ({target_x}, {target_y}) nuqtasida topildi va {action_name}."
        else:
            return f"Ekrandan '{target}' topilmadi: {data.get('reason', 'Element koʻrinmadi')}."

    except Exception as e:
        return f"Ekrandan elementni bosishda xatolik: {e}"


def screen_type(target: str, text: str) -> str:
    """Ekrandagi kiritish maydonini (Input box) ko'rib, unga bosadi va matn yozadi"""
    try:
        click_res = screen_click(target, "click")
        if "topildi" in click_res:
            time.sleep(0.2)
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyautogui.press("enter")
            return f"'{target}' maydoniga '{text}' matni kiritildi."
        return click_res
    except Exception as e:
        return f"Matn kiritishda xatolik: {e}"
