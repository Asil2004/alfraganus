import json
from pathlib import Path

MEM_FILE = Path(__file__).resolve().parent / "user_memory.json"


def load_memory() -> dict:
    if not MEM_FILE.exists():
        return {
            "user_name": "Xo'jayin",
            "preferences": {},
            "recent_actions": []
        }
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"user_name": "Xo'jayin", "preferences": {}, "recent_actions": []}


def save_memory(mem: dict):
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def update_memory(key: str, value: str):
    mem = load_memory()
    mem["preferences"][key] = value
    save_memory(mem)
    return f"Xotiraga saqlandi: {key} = {value}"


def add_recent_action(action_desc: str):
    mem = load_memory()
    actions = mem.get("recent_actions", [])
    actions.append(action_desc)
    if len(actions) > 20:
        actions = actions[-20:]
    mem["recent_actions"] = actions
    save_memory(mem)


def format_memory_for_prompt() -> str:
    mem = load_memory()
    lines = [f"Foydalanuvchi: {mem.get('user_name', 'Foydalanuvchi')}"]
    prefs = mem.get("preferences", {})
    if prefs:
        lines.append("Foydalanuvchi xohishlari:")
        for k, v in prefs.items():
            lines.append(f" - {k}: {v}")
    return "\n".join(lines)
