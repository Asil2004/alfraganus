import os
import sys
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
API_KEYS_PATH = CONFIG_DIR / "api_keys.json"
SETTINGS_PATH = CONFIG_DIR / "settings.json"

# Palette
C_BG = "#060a14"
C_PANEL = "#0b1424"
C_CARD = "#101d33"
C_CARD_SELECTED = "#1a2c4e"
C_CYAN = "#00f0ff"
C_PURPLE = "#a855f7"
C_GREEN = "#10b981"
C_TEXT = "#f1f5f9"
C_MUTED = "#94a3b8"
C_BORDER = "#1e3a5f"


def is_setup_needed() -> bool:
    """Tekshiradi: API kaliti mavjudmi yoki kiritish kerakmi"""
    if not API_KEYS_PATH.exists():
        return True
    try:
        with open(API_KEYS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            key = data.get("gemini_api_key", "").strip()
            if not key or "YOUR_GEMINI" in key or len(key) < 15:
                return True
        return False
    except Exception:
        return True


class SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ALFRAGANUS AI — Dastlabki Sozlash Ustasi")
        self.root.geometry("680x740")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        self.selected_persona = "katta_erkak"
        self.selected_voice = "Charon"
        self.setup_completed = False

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=C_PANEL, height=80, highlightbackground=C_CYAN, highlightthickness=1)
        header.pack(fill="x", side="top", padx=15, pady=12)

        lbl_title = tk.Label(
            header,
            text="🌌 ALFRAGANUS AI — O'RNATISH VA SOZLASH",
            font=("Segoe UI", 15, "bold"),
            fg=C_CYAN,
            bg=C_PANEL
        )
        lbl_title.pack(anchor="w", padx=18, pady=(12, 2))

        lbl_sub = tk.Label(
            header,
            text="Tizimni ishga tushirish uchun Gemini API kaliti va ovoz profilini tanlang",
            font=("Segoe UI", 9),
            fg=C_MUTED,
            bg=C_PANEL
        )
        lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        # Main Scrollable / Stack Frame
        container = tk.Frame(self.root, bg=C_BG)
        container.pack(fill="both", expand=True, padx=15, pady=5)

        # 1. API KEY SECTION
        sec_api = tk.Frame(container, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        sec_api.pack(fill="x", pady=8, padx=5)

        lbl_sec1 = tk.Label(sec_api, text="1. GOOGLE GEMINI API KALITI (Majburiy)", font=("Segoe UI", 11, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl_sec1.pack(anchor="w", padx=14, pady=(10, 4))

        lbl_help = tk.Label(sec_api, text="Google AI Studio'dan bepul API kalit oling (https://aistudio.google.com/apikey)", font=("Segoe UI", 8), fg=C_MUTED, bg=C_PANEL)
        lbl_help.pack(anchor="w", padx=14, pady=(0, 6))

        box_input = tk.Frame(sec_api, bg=C_PANEL)
        box_input.pack(fill="x", padx=14, pady=(0, 10))

        self.entry_api_key = tk.Entry(
            box_input,
            font=("Consolas", 11),
            bg="#050811",
            fg="#38bdf8",
            insertbackground="#38bdf8",
            relief="solid",
            highlightbackground=C_BORDER,
            highlightthickness=1
        )
        self.entry_api_key.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        btn_get_key = tk.Button(
            box_input,
            text="Kalit Olish ↗",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg=C_CYAN,
            relief="flat",
            padx=10,
            command=lambda: webbrowser.open("https://aistudio.google.com/apikey")
        )
        btn_get_key.pack(side="right")

        # 2. VOICE PERSONA SELECTION
        sec_voice = tk.Frame(container, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        sec_voice.pack(fill="x", pady=8, padx=5)

        lbl_sec2 = tk.Label(sec_voice, text="2. DASTLABKI OVOZ PROFILINI TANLANG", font=("Segoe UI", 11, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl_sec2.pack(anchor="w", padx=14, pady=(10, 8))

        self.persona_buttons = {}
        personas = [
            ("katta_erkak", "Charon", "🧔 Katta Erkak (Jarvis)", "Salobatli, jiddiy va vazmin professional erkak ovozi"),
            ("yosh_qiz", "Kore", "👧 Yosh Qiz", "Samimiy, chaqqon va xotirjam yosh qiz ovozi"),
            ("ayol", "Aoede", "👩 Mayin Ayol", "Mayin, muloyim va madaniyatli ayol ovozi"),
            ("yosh_yigit", "Puck", "👦 Yosh Yigit", "Quvnoq, chaqqon va do'stona yigit ovozi"),
            ("bariton", "Fenrir", "⚔️ Kuchli Bariton", "Chuqur, jangovar va qat'iyatli erkak ovozi"),
        ]

        for p_id, v_model, p_name, p_desc in personas:
            card = tk.Frame(sec_voice, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1, cursor="hand2")
            card.pack(fill="x", padx=14, pady=3)

            lbl_pname = tk.Label(card, text=f"{p_name}  —  [{v_model}]", font=("Segoe UI", 10, "bold"), fg=C_TEXT, bg=C_CARD)
            lbl_pname.pack(anchor="w", padx=12, pady=(4, 0))

            lbl_pdesc = tk.Label(card, text=p_desc, font=("Segoe UI", 8), fg=C_MUTED, bg=C_CARD)
            lbl_pdesc.pack(anchor="w", padx=12, pady=(0, 4))

            # Bind click
            card.bind("<Button-1>", lambda e, pid=p_id, vmod=v_model: self._select_persona(pid, vmod))
            lbl_pname.bind("<Button-1>", lambda e, pid=p_id, vmod=v_model: self._select_persona(pid, vmod))
            lbl_pdesc.bind("<Button-1>", lambda e, pid=p_id, vmod=v_model: self._select_persona(pid, vmod))

            self.persona_buttons[p_id] = (card, lbl_pname, lbl_pdesc)

        self._select_persona("katta_erkak", "Charon")

        # 3. TELEGRAM BOT (Optional)
        sec_tg = tk.Frame(container, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        sec_tg.pack(fill="x", pady=8, padx=5)

        lbl_sec3 = tk.Label(sec_tg, text="3. TELEGRAM BOT TOKENI (Ixtiyoriy masofaviy boshqaruv)", font=("Segoe UI", 10, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl_sec3.pack(anchor="w", padx=14, pady=(8, 2))

        self.entry_tg_token = tk.Entry(
            sec_tg,
            font=("Consolas", 10),
            bg="#050811",
            fg="#a7f3d0",
            insertbackground="#a7f3d0",
            relief="solid",
            highlightbackground=C_BORDER,
            highlightthickness=1
        )
        self.entry_tg_token.pack(fill="x", padx=14, pady=(2, 10), ipady=4)

        # 4. START BUTTON
        btn_start = tk.Button(
            self.root,
            text="🚀 SAQLASH VA ALFRAGANUS'NI ISHGA TUSHIRISH",
            font=("Segoe UI", 12, "bold"),
            bg="#00b4d8",
            fg="#000",
            activebackground=C_CYAN,
            relief="flat",
            pady=10,
            cursor="hand2",
            command=self._save_and_start
        )
        btn_start.pack(fill="x", side="bottom", padx=20, pady=16)

    def _select_persona(self, persona_id: str, voice_model: str):
        self.selected_persona = persona_id
        self.selected_voice = voice_model

        for pid, (card, lbl_title, lbl_desc) in self.persona_buttons.items():
            if pid == persona_id:
                card.config(bg=C_CARD_SELECTED, highlightbackground=C_CYAN, highlightthickness=2)
                lbl_title.config(bg=C_CARD_SELECTED, fg=C_CYAN)
                lbl_desc.config(bg=C_CARD_SELECTED, fg="#e2e8f0")
            else:
                card.config(bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
                lbl_title.config(bg=C_CARD, fg=C_TEXT)
                lbl_desc.config(bg=C_CARD, fg=C_MUTED)

    def _save_and_start(self):
        api_key = self.entry_api_key.value = self.entry_api_key.get().strip()
        tg_token = self.entry_tg_token.get().strip()

        if not api_key:
            messagebox.showwarning(
                "API Kalit kiritilmadi",
                "Iltimos, Alfraganus AI ishlashi uchun Google Gemini API kalitini kiriting."
            )
            return

        try:
            CONFIG_DIR.mkdir(exist_ok=True, parents=True)

            # 1. Save API keys
            api_data = {
                "gemini_api_key": api_key,
                "telegram_bot_token": tg_token
            }
            with open(API_KEYS_PATH, "w", encoding="utf-8") as f:
                json.dump(api_data, f, indent=2)

            # 2. Save Settings with initial voice persona
            settings_data = {}
            if SETTINGS_PATH.exists():
                try:
                    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                        settings_data = json.load(f)
                except Exception:
                    pass

            settings_data["voice_name"] = self.selected_voice
            settings_data["voice_persona"] = self.selected_persona

            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            self.setup_completed = True
            messagebox.showinfo(
                "Sozlash Muvaffaqiyatli",
                f"Sozlamalar saqlandi!\nTanlangan ovoz: {self.selected_persona.upper()} ({self.selected_voice})\nAlfraganus ishga tushmoqda..."
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Xatolik", f"Sozlamalarni saqlashda xatolik: {e}")

    def run(self):
        self.root.mainloop()
        return self.setup_completed


def ensure_setup():
    """Agar sozlash kerak bo'lsa, oynani ochadi va to'ldirilishini kutadi"""
    if is_setup_needed():
        wizard = SetupWizard()
        return wizard.run()
    return True


if __name__ == "__main__":
    ensure_setup()
