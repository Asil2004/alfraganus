import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.json"

VOICE_PROFILES = {
    # Erkak profillari
    "katta_erkak": {"voice": "Charon", "desc": "Salobatli, vazmin katta yoshli erkak (Jarvis) ovozi"},
    "vazmin": {"voice": "Charon", "desc": "Salobatli, vazmin erkak ovozi"},
    "jarvis": {"voice": "Charon", "desc": "Salobatli, vazmin erkak (Jarvis) ovozi"},
    "erkak": {"voice": "Charon", "desc": "Salobatli erkak ovozi"},
    "ota": {"voice": "Charon", "desc": "Katta yoshli, vazmin ota/ustoz ovozi"},
    
    "yosh_yigit": {"voice": "Puck", "desc": "Yosh, chaqqon va do'stona yigit ovozi"},
    "yigit": {"voice": "Puck", "desc": "Yosh, chaqqon yigit ovozi"},
    "yosh": {"voice": "Puck", "desc": "Yosh yigit ovozi"},
    "bola": {"voice": "Puck", "desc": "Yosh yigit/o'smir ovozi"},
    "ogil": {"voice": "Puck", "desc": "Yosh yigit ovozi"},
    
    "kuchli_erkak": {"voice": "Fenrir", "desc": "Kuchli, qat'iyatli bariton erkak ovozi"},
    "bariton": {"voice": "Fenrir", "desc": "Kuchli bariton erkak ovozi"},

    # Ayol profillari
    "ayol": {"voice": "Aoede", "desc": "Mayin, muloyim va madaniyatli ayol ovozi"},
    "mayin_ayol": {"voice": "Aoede", "desc": "Mayin, muloyim ayol ovozi"},
    "katta_ayol": {"voice": "Aoede", "desc": "Katta yoshli, vazmin ayol ovozi"},
    "ona": {"voice": "Aoede", "desc": "Mehribon, muloyim ona ovozi"},
    
    "yosh_qiz": {"voice": "Kore", "desc": "Yosh, xotirjam va samimiy qiz ovozi"},
    "qiz": {"voice": "Kore", "desc": "Yosh, samimiy qiz ovozi"},
    "singil": {"voice": "Kore", "desc": "Yosh qiz ovozi"}
}


def get_current_voice() -> str:
    """Hozirgi faol ovoz modelini qaytaradi"""
    try:
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("voice_name", "Charon")
        return "Charon"
    except Exception:
        return "Charon"


def list_voice_personas() -> dict:
    """Mavjud barcha ovoz profillarini qaytaradi"""
    return VOICE_PROFILES


def change_voice_persona(persona: str) -> str:
    """Yosh va jinsga qarab Alfraganus ovoz profilini o'zgartiradi"""
    p_clean = persona.lower().strip()
    
    matched = None
    
    # 1. Qiz bola / Singil profili (Kore) - birinchi o'rinda tekshiriladi
    if any(w in p_clean for w in ["qiz", "singil", "kore", "yosh_qiz", "qizaloq"]):
        matched = VOICE_PROFILES["yosh_qiz"]

    # 2. Ayol / Ona profili (Aoede)
    elif any(w in p_clean for w in ["ayol", "ona", "xotin", "mayin", "aoede"]):
        matched = VOICE_PROFILES["ayol"]

    # 3. Kuchli bariton / Jangovar erkak profili (Fenrir)
    elif any(w in p_clean for w in ["bariton", "kuchli", "fenrir", "jangovar"]):
        matched = VOICE_PROFILES["kuchli_erkak"]

    # 4. Yosh yigit / O'spirin / Bola profili (Puck)
    elif any(w in p_clean for w in ["yigit", "bola", "ospirin", "o'spirin", "puck", "yosh_yigit"]):
        matched = VOICE_PROFILES["yosh_yigit"]

    # 5. Salobatli katta yoshli erkak / Jarvis / Ota (Charon)
    elif any(w in p_clean for w in ["katta", "erkak", "ota", "bobo", "charon", "jarvis", "vazmin"]):
        matched = VOICE_PROFILES["katta_erkak"]

    # 6. Lug'at bo'yicha uzunlikka ko'ra qidirish (uzun kalitlar birinchi)
    else:
        sorted_keys = sorted(VOICE_PROFILES.keys(), key=len, reverse=True)
        for k in sorted_keys:
            if k in p_clean:
                matched = VOICE_PROFILES[k]
                break

    if not matched:
        matched = VOICE_PROFILES["katta_erkak"]

    try:
        settings = {}
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
        settings["voice_name"] = matched["voice"]
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            
        return f"Ovoz muvaffaqiyatli o'zgartirildi: {matched['desc']} (Model: {matched['voice']}). Yangi ovoz keyingi javobdan boshlab yangraydi."
    except Exception as e:
        return f"Ovozni saqlashda xatolik: {e}"
