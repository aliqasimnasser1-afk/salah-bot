<div align="center">

# 🕌 Salah Bot | بوت مواقيت الصلاة

**A fast, bilingual Telegram bot for prayer times, reminders, daily adhkar and Qibla.**
**بوت تيليجرام سريع بلغتين: مواقيت الصلاة، تنبيهات، أذكار الصباح والمساء، واتجاه القبلة.**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-74_passing-3fb950?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-b30012?style=for-the-badge)

</div>

---

## ✨ Features | المميزات

| | English | العربية |
|---|---|---|
| 🕋 | Daily prayer times with the Hijri date; the main menu always shows the next prayer and its countdown | مواقيت اليوم مع التاريخ الهجري، والقائمة الرئيسية تعرض دائمًا الصلاة القادمة والوقت المتبقي |
| 🔔 | Reminder before each prayer (0 / 5 / 10 / 15 / 30 min) and an alert when it begins | تنبيه قبل كل صلاة (اختياري) وعند دخول وقتها |
| 📿 | Morning and evening adhkar sent automatically after Fajr and Asr | أذكار الصباح والمساء تُرسل تلقائيًا بعد الفجر والعصر |
| 📖 | Adhkar browsed one card at a time with Previous / Next buttons, edited in place (no scrolling) | تصفح الأذكار بطاقة بطاقة بأزرار السابق والتالي في نفس الرسالة بدون تمرير |
| 🧭 | Qibla bearing and distance to the Kaaba, computed locally | زاوية القبلة والمسافة إلى الكعبة، تُحسب محليًا |
| 🇸🇦 | First-run setup: pick your Saudi region and city from a menu (13 regions, 60+ cities) | إعداد أولي: اختر منطقتك ومدينتك في السعودية من قائمة (13 منطقة وأكثر من 60 مدينة) |
| 📍 | Share a location or type a city (Arabic or English); the bot shows the city it found and lets you correct it | أرسل موقعك أو اكتب مدينتك؛ يعرض البوت المدينة التي فهمها ويتيح لك تصحيحها |
| 📐 | Six calculation methods (Umm Al-Qura by default) | ست طرق حساب (أم القرى افتراضيًا) |
| 🌐 | Full Arabic and English interface, switchable per user | واجهة عربية وإنجليزية كاملة لكل مستخدم |
| 🌍 | Correct time zone per user, anywhere in the world | المنطقة الزمنية الصحيحة لكل مستخدم في أي مكان |

## 🚀 Quick start | تشغيل سريع

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
   أنشئ بوتًا من BotFather وانسخ التوكن.
2. Configure:

```bash
cp .env.example .env      # then put your token in BOT_TOKEN
```

3. Run it, either way:

```bash
# Docker (recommended)
docker compose up -d --build

# or plain Python 3.11+
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m bot
```

Open your bot in Telegram and send `/start`.

## ⚙️ Configuration | الإعدادات

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | required | Token from @BotFather |
| `DB_PATH` | `data/salah.db` | SQLite file (a Docker volume holds it) |
| `DEFAULT_METHOD` | `4` | Calculation method for new users (4 = Umm Al-Qura) |
| `PORT` | `8080` | Health-check port (`/health`) |
| `ADMIN_IDS` | empty | Comma-separated Telegram IDs allowed to run `/stats` |

## 🤖 Commands | الأوامر

`/start` `/times` `/next` `/qibla` `/morning` `/evening` `/settings` `/help`

## 🏗 How it works

```
Telegram ──► aiogram handlers ──► SQLite (users, sent notifications)
                  │
                  ├──► Aladhan API ──► prayer times + Hijri date + time zone
                  ├──► Nominatim / Open-Meteo ──► city name → coordinates
                  └──► qibla.py ──► bearing + distance (pure math)

ReminderService (every 30 s)
   └─ events.due_events()  pure function: which notifications are due now
   └─ db.mark_sent()       INSERT OR IGNORE, so each one is sent exactly once
```

- **Exactly-once delivery:** each notification has a unique key per user per day; the key is written before sending, so a restart or overlapping tick never duplicates a message.
- **Resilient:** a failing prayer-times service skips that tick and retries on the next one. Users who block the bot are removed automatically. Telegram rate limits are respected.
- **Efficient:** timings are cached per rounded location, so thousands of users in the same city cost one API call.
- **Private by design:** only a Telegram ID, a language, coordinates and settings are stored. No messages are logged.

```
bot/
  main.py         startup, polling, graceful shutdown
  handlers.py     commands, buttons, location input
  reminders.py    background notification loop
  events.py       pure scheduling logic
  aladhan.py      prayer-times client + cache
  geocode.py      city name to coordinates
  regions.py      Saudi regions and cities for the setup menu
  qibla.py        great-circle bearing and distance
  adhkar.py       morning / evening adhkar
  texts.py        Arabic and English strings
  keyboards.py    inline keyboards
  db.py           async SQLite layer
  health.py       /health endpoint
tests/            74 tests, including real handler flows with a fake Telegram session
```

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers Qibla math, API parsing, the scheduling window, exactly-once delivery, the database, geocoder parsing, and end-to-end handler flows (location → times → settings) without touching the network.

## ☁️ Hosting

The bot uses long polling, so it needs a process that stays running.

- **VPS / Oracle Cloud Always Free:** `docker compose up -d` — no sleeping, recommended.
- **Render free tier:** the instance sleeps after 15 minutes without inbound HTTP traffic. Ping `/health` every 5 minutes (a scheduled GitHub Actions workflow works) to keep it awake.
  The free tier also has an **ephemeral disk**: the SQLite file is wiped on every restart or redeploy, so users would have to set their city again. For persistent data use a VPS (or a paid Render disk).
  `render.yaml` is included: *New > Blueprint*, pick this repo, and paste `BOT_TOKEN` when asked.

## 📌 Notes

- Prayer times come from the [Aladhan API](https://aladhan.com/prayer-times-api). Always verify against your local mosque or authority, especially near the start of Ramadan or in extreme latitudes.
- City lookup uses OpenStreetMap Nominatim (rate-limited to one request per second, as its policy requires) with Open-Meteo as a fallback. For an ambiguous city name the bot shows what it found; sharing your location is always exact.
- The adhkar are a short selection. For the complete collection see *Hisn al-Muslim*.

## 📄 License

MIT © Ali Qasim
