<h1 align="center">🦅 GOLDEN EAGLE BOT — ULTIMATE EDITION</h1>

<p align="center">
  <b>The most powerful Telegram Uploader / Downloader bot.</b><br>
  Smooth like butter · Futuristic · Professional · DRM &amp; Non-DRM — A to Z.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Pyrogram-2.0-orange?logo=telegram&logoColor=white">
  <img src="https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb&logoColor=white">
  <img src="https://img.shields.io/badge/Deploy-Heroku%20%7C%20Render-purple?logo=heroku&logoColor=white">
</p>

---

## ✨ Features

| Category | What it does |
|----------|--------------|
| 📄 **TXT Leech** | Extract & upload every video / pdf link from a `.txt` file |
| 🔐 **DRM Decrypt** | Widevine / ClearKey DRM streams via `mp4decrypt` (Bento4) |
| 🎞️ **Non-DRM** | HLS (`m3u8`), MPD, direct MP4, YouTube, and more |
| 🎬 **YouTube** | `/y2t` (YT → txt), `/ytm` (YT → mp3), cookies support |
| 📝 **Converters** | `/t2t` (text → txt), `/t2h` (txt → html) |
| 💧 **Watermark** | Custom video watermark text overlay |
| 🎚️ **Quality** | 144p → 1080p selectable per session |
| 👥 **Premium System** | `/add`, `/remove`, `/users`, `/plan` with expiry tracking |
| 📢 **Broadcast** | `/broadcast` text/photo/video/doc to all users |
| 📊 **Live Health** | Futuristic auto-refreshing status dashboard |

---

## 🤖 Commands

**Users**
```
/start    Bot status check & welcome
/y2t      YouTube → .txt converter
/ytm      YouTube → .mp3 downloader
/t2t      Text → .txt generator
/t2h      .txt → .html converter
/stop     Cancel running task
/cookies  Update YT cookies
/id       Get chat / user ID
/info     User details
/logs     View bot activity
```

**Owner / Admin**
```
/add <id> <days>   Grant premium access
/remove <id>       Revoke access
/users             List all premium users
/broadcast         Reply to a msg to broadcast it
/broadusers        List all broadcasting users
/reset             Reset & re-register commands
```

---

## ⚙️ Environment Variables

Copy `.env.example` → `.env` and fill in:

| Variable | Required | Description |
|----------|:--------:|-------------|
| `API_ID` | ✅ | From https://my.telegram.org |
| `API_HASH` | ✅ | From https://my.telegram.org |
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `OWNER` / `OWNER_ID` | ✅ | Your numeric Telegram ID |
| `OWNER_ID2` | ⬜ | Second admin ID |
| `MONGO_URL` | ✅ | MongoDB Atlas connection string |
| `DATABASE_NAME` | ⬜ | Default: `eagle` |
| `CREDIT` / `CREDIT_LINK` | ⬜ | Branding |

---

## 🚀 Deployment

### Heroku (recommended — worker dyno, runs 24/7)
1. Create app → set **stack** to `container`
2. Add all env vars above
3. Deploy this repo, then **scale the worker dyno**:
   ```bash
   heroku stack:set container -a your-app
   git push heroku main
   heroku ps:scale worker=1 -a your-app
   ```

### Render
- Use the included `render.yaml` (Docker-based web service).

### Local
```bash
pip install -r sainibots.txt
cp .env.example .env      # fill in values
python3 modules/main.py
```

---

## 🩺 Health Dashboard

Once deployed, open your app URL to see a live, glassmorphic status page:
- ✅ green = bot connected (shows username, ID, uptime)
- ⏳ amber = still starting
- ❌ red = connection error (with reason)

`GET /health` returns JSON for uptime monitors.

---

## 🛠️ Architecture

```
modules/
├── main.py            ← entry point, all command/callback handlers
├── auth.py            ← premium user management
├── broadcast.py       ← broadcast engine
├── db.py (root)       ← MongoDB layer
├── drm_handler.py     ← DRM decrypt engine (Widevine/ClearKey)
├── saini.py           ← core download/upload helper
├── html_handler.py    ← .txt → .html
├── youtube_handler.py ← YouTube/cookies
├── text_handler.py    ← text → .txt
├── topic_handler.py   ← topic-in-caption logic
├── utils.py           ← progress bar & helpers
└── vars.py            ← config & message templates
```

---

<p align="center"><b>🦅 Built for speed. Tuned for power. Smooth like butter.</b></p>
