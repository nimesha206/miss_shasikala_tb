# 🌸 Miss Shasikala Telegram Bot

> 👑 Created by: **Nimesha Madhushan**
> 🔗 GitHub: https://github.com/nimesha206/nimabt
> 📞 Contact: https://t.me/+94726800969
> 🌐 Group: https://t.me/mjsicgroupsl

---

## ✅ Step 1 — Bot Token ගන්නා ආකාරය

1. Telegram හි **@BotFather** ට යන්න
2. `/newbot` ටයිප් කරන්න
3. Bot name: `Miss Shasikala Bot`
4. Username: `miss_shasikala_bot` (unique name)
5. **Token** copy කරගන්න → `config.py` හි `BOT_TOKEN` ට දමන්න

## ✅ Step 2 — Owner ID ගන්නා ආකාරය

1. Telegram හි **@userinfobot** ට `/start` කරන්න
2. ලැබෙන **ID** copy කරගන්න → `config.py` හි `OWNER_ID` ට දමන්න

## ✅ Step 3 — config.py සකස් කරන්න

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather ගෙන්
OWNER_ID  = 1234567890              # @userinfobot ගෙන්
```

## ✅ Step 4 — Python & Dependencies Install

```bash
# Python 3.10+ required
sudo apt update
sudo apt install python3 python3-pip ffmpeg -y

# Install requirements
pip3 install -r requirements.txt
```

## ✅ Step 5 — Bot Run කරන්නා ආකාරය

```bash
python3 bot.py
```

---

## 🚀 VPS / Server Deploy (24/7 run)

### PM2 (Recommended):
```bash
npm install -g pm2
pm2 start bot.py --name "miss_shasikala" --interpreter python3
pm2 save
pm2 startup
```

### Screen:
```bash
screen -S shasikala
python3 bot.py
# Ctrl+A then D to detach
```

### Systemd Service:
```ini
# /etc/systemd/system/shasikala.service
[Unit]
Description=Miss Shasikala Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/miss_shasikala_telegram
ExecStart=/usr/bin/python3 bot.py
Restart=always
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable shasikala
sudo systemctl start shasikala
```

### Railway / Render (Free Cloud):
1. GitHub repo create කරන්න
2. Files upload කරන්න
3. **railway.app** හෝ **render.com** deploy කරන්න

### Heroku:
```
# Procfile already included
web: python3 bot.py
```

---

## 📋 Commands List

| Category | Commands |
|---|---|
| 🤖 AI | `/ai`, `/gpt`, `/gemini`, `/imagine` |
| 🎵 Music | `/play`, `/song`, `/mp3`, `/lyrics` |
| 🎬 Video | `/video`, `/mp4`, `/ytmp4` |
| 🌤️ Info | `/weather`, `/news`, `/define`, `/cinfo` |
| 🌍 Tools | `/translate`, `/tts`, `/ss` |
| 😂 Fun | `/joke`, `/quote`, `/fact`, `/8ball` |
| 💕 Fun+ | `/compliment`, `/flirt`, `/ship`, `/hack` |
| 🎨 Sticker | `/sticker`, `/attp`, `/removebg` |
| 🐱 Anime | `/neko`, `/waifu`, `/hug`, `/pat`, `/kiss` |
| 👥 Group | `/kick`, `/ban`, `/mute`, `/promote` |
| 👥 Group+ | `/welcome`, `/goodbye`, `/antilink`, `/admins` |
| 👑 Owner | `/addpremium`, `/broadcast`, `/stats` |
| ℹ️ General | `/start`, `/alive`, `/ping`, `/help`, `/id` |

---

## 📁 File Structure

```
miss_shasikala_telegram/
├── bot.py           — Main runner
├── config.py        — ⚙️ Setup here!
├── database.py      — Data storage
├── helpers.py       — Utilities
├── requirements.txt — Dependencies
├── database/
│   └── db.json      — Auto created
└── plugins/
    ├── general.py   — Basic commands
    ├── ai.py        — AI commands
    ├── music.py     — Music/Video
    ├── tools.py     — Info tools
    ├── fun.py       — Fun commands
    ├── group.py     — Group management
    ├── sticker.py   — Sticker tools
    ├── anime.py     — Anime images
    ├── owner.py     — Owner commands
    └── callbacks.py — Button handlers
```

---

## 💬 Support

- 📞 Owner: https://t.me/+94726800969
- 🌐 Group: https://t.me/mjsicgroupsl
- ⭐ GitHub: https://github.com/nimesha206/nimabt

---

*🌸 Miss Shasikala Bot — Made with ❤️ by Nimesha Madhushan*
