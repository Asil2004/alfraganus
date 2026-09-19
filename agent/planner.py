import json
from pathlib import Path
from google import genai

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"


def plan_task(task_goal: str) -> list:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            api_key = json.load(f)["gemini_api_key"]

        client = genai.Client(api_key=api_key)
        prompt = f"""Foydalanuvchi murakkab vazifa berdi: "{task_goal}".
Ushbu vazifani bajarish uchun mavjud vositalar (tools) ketma-ketligini JSON formatda rejalashtiring.

Mavjud vositalar:
- open_app (app_name)
- browser_control (action, query, url)
- computer_control (action, x, y, text, key, shortcut)
- computer_settings (command, value)
- file_controller (action, path, content)
- terminal_execute (command)
- weather_action (city)
- youtube_video (query)

Format:
[
  {{"step": 1, "tool": "tool_name", "args": {{...}}, "description": "qisqa izoh"}},
  ...
]
Faqat to'g'ridan-to'g'ri JSON massiv qaytaring.
"""
        for m in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception:
                continue
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        return json.loads(raw_text.strip())
    except Exception as e:
        return [{"step": 1, "tool": "unknown", "args": {}, "description": f"Reja tuzishda xatolik: {e}"}]
