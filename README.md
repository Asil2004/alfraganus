# 🌌 ALFRAGANUS (Ahmad al-Farg'oniy) — Autonomous Multimodal AI Core

<p align="center">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%20Live%20Multimodal-00f0ff?style=for-the-badge" alt="Gemini Live">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Android%20ADB-10b981?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Language-100%25%20Pure%20Uzbek-orange?style=for-the-badge" alt="Uzbek">
</p>

---

## 🇺🇿 O'zbekcha Tavsif

**Alfraganus (Al-Farg'oniy)** — bu kompyuter, smartfon va aqlli qurilmalarni to'liq avtonom boshqaruvchi, Google Gemini Live ko'p modalli sun'iy intellektiga asoslangan zamonaviy shaxsiy assistentdir.

### 🌟 Asosiy Imkoniyatlar:

1. **🎙️ Sof Gemini Live Audio & Ovoz Profillari (Voice Personas):**
   - Hech qanday tashqi robotik sintezatorsiz, to'g'ridan-to'g'ri Gemini Live sof audio oqimi.
   - Yosh va jinsga qarab 5 ta tabiiy profil:
     - 🧔 **Katta Erkak / Jarvis (`Charon`):** Salobatli, vazmin, professional erkak ovozi.
     - 👧 **Yosh Qiz (`Kore`):** Samimiy, xotirjam va muloyim yosh qiz ovozi.
     - 👩 **Mayin Ayol (`Aoede`):** Mayin, madaniyatli ayol ovozi.
     - 👦 **Yosh Yigit (`Puck`):** Chaqqon, do'stona yigit ovozi.
     - ⚔️ **Kuchli Bariton (`Fenrir`):** Chuqur, jangovar va qat'iyatli bariton ovozi.

2. **📱 Smartfonni To'liq Boshqarish (ADB over USB & Wi-Fi):**
   - Ilovalarni ochish (YouTube, Telegram, WhatsApp, Instagram, Kamera, Galereya, Sozlamalar va b.).
   - Ekranni bosish (`tap`), surish (`swipe`), matn yozish (`type_text`), apparat tugmalari (`home`, `back`, `volume`, `power`).
   - Qo'ng'iroq qilish va SMS yuborish.
   - **Gemini Vision** orqali telefon ekranini skrinshot qilib, undagi ma'lumotlarni o'qib berish.
   - Batareya quvvati, harorati va texnik holatini tekshirish.

3. **🖐️ Ikki Qo'lli Imo-ishoralar (Dual-Hand Vision Gestures):**
   - MediaPipe orqali ikkala qo'lni 60 FPS tezlikda kuzatish.
   - Musht qilib ushlaganda oynani ekranning istalgan joyiga surish (Window drag & drop).
   - Ikki qo'lni kengaytirish orqali oynani kattalashtirish (`Win+Up`), yaqinlashtirganda kichraytirish (`Win+Down`), ikkala musht bilan ish stolini ochish (`Win+D`).

4. **👁️ Gemini Vision & Visual Grounding:**
   - Kompyuter ekranidagi xatoliklar, rasmlar va dasturlarni ko'rib tahlil qilish.
   - Ekrandagi har qanday tugma yoki belgini ko'rib, kursor bilan borib bosish (`screen_click`).

5. **✈️ Telegram Masofaviy Nazorati:**
   - Telegram bot (`@al_pc_bot`) orqali kompyuterni masofadan boshqarish va skrinshot olish.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Repozitoriyni klonlash:
```bash
git clone https://github.com/Asil2004/alfraganus.git
cd alfraganus
```

### 2. Virtual muhit va kutubxonalarni o'rnatish:
```bash
python -m venv env
# Windows:
.\env\Scripts\activate
# Linux/Mac:
source env/bin/activate

pip install -r requirements.txt
```

### 3. API Kalitlarni sozlash:
`config/api_keys.example.json` faylidan nusxa olib, `config/api_keys.json` yarating:
```json
{
  "gemini_api_key": "SIZNING_GEMINI_API_KALITINGIZ",
  "telegram_bot_token": "SIZNING_TELEGRAM_BOT_TOKENINGIZ"
}
```

### 4. Dasturni ishga tushirish:
```bash
python main.py
```
*Yoki `run_alfraganus.bat` faylini ishga tushiring.*

---

## 🏛️ Tizim Fayl Tuzilishi

```
alfraganus/
├── actions/                  # Barcha avtonom amallar va boshqaruv modullari
│   ├── app_controller.py     # Dasturlar va jarayonlar menejeri
│   ├── browser_control.py    # Brauzer avtomatizatsiyasi
│   ├── computer_control.py   # Kursor va klaviatura simulyatori
│   ├── computer_settings.py  # Windows ovoz, yorug'lik va quvvat boshqaruvi
│   ├── device_controller.py  # Tarmoq, Bluetooth, COM portlar, WoL
│   ├── file_controller.py    # Fayllar bilan ishlash
│   ├── mouse_controller.py   # Kursor telemetriyasi va harakati
│   ├── open_app.py           # 280+ ta tizim va ish stoli ilovalari indeksi
│   ├── phone_controller.py   # ADB, Wi-Fi, Ilovalar, Qo'ng'iroq, SMS, Vision
│   ├── screen_processor.py   # Gemini Vision & Visual Grounding
│   ├── system_monitor.py     # CPU, RAM, Disk, Tarmoq telemetriyasi
│   ├── telegram_bot_bridge.py# 24/7 Telegram masofaviy aloqa boti
│   ├── voice_persona.py      # Yosh va jinsga qarab ovoz profillari
│   ├── weather_report.py     # Ob-havo ma'lumotlari
│   └── youtube_video.py      # YouTube video va musiqa qidiruvi
├── config/                   # Sozlamalar va konfiguratsiyalar
├── core/                     # Tizim prompti va Gemini sozlamalari
├── gestures/                 # MediaPipe 2-qo'l kuzatuvi va harakatlar
├── ui.py                     # Cyberpunk uslubidagi Desktop GUI
├── main.py                   # Asosiy Gemini Live dvigateli
├── test_suite.py             # 10 ta modul bo'yicha diagnostika
├── updater.py                # Ishga tushirishdan oldingi tekshiruvchi
├── requirements.txt          # Kerakli Python kutubxonalari
└── run_alfraganus.bat        # Windows ishga tushirish skripti
```

---

## 📄 Litsenziya

MIT License © 2026 Alfraganus AI System.
