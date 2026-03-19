"""
╔══════════════════════════════════════════╗
║   🌸 MISS SHASIKALA TELEGRAM BOT 🌸     ║
║   👑 Created by: Nimesha Madhushan      ║
╚══════════════════════════════════════════╝
"""

import os, sys, subprocess, time

# ══════════════════════════════════════════
# 🔧 STEP 1 — pip upgrade
# ══════════════════════════════════════════
print("🔄 pip upgrading...", flush=True)
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
    check=False,
)

# ══════════════════════════════════════════
# 🔧 STEP 2 — platform detect → pip flags
# ══════════════════════════════════════════
_flags = []
if os.path.exists("/data/data/com.termux"):   # Termux
    _flags = ["--break-system-packages"]
elif os.environ.get("REPL_ID"):               # Replit
    _flags = ["--user"]

# ══════════════════════════════════════════
# 🔧 STEP 3 — install / upgrade ALL packages
# ══════════════════════════════════════════
PACKAGES = [
    "python-telegram-bot[job-queue]==21.6",
    "aiohttp==3.9.5",
    "Pillow==10.4.0",
    "google-generativeai==0.7.2",
    "requests==2.31.0",
    "yt-dlp",
    "rembg",
]

print(f"📦 Installing/upgrading {len(PACKAGES)} packages...", flush=True)
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet"] + _flags + PACKAGES,
    check=False,
)
print("✅ Packages ready!", flush=True)

# ══════════════════════════════════════════
# 🔧 STEP 4 — ffmpeg (Linux only)
# ══════════════════════════════════════════
if sys.platform.startswith("linux"):
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        print("🔧 Installing ffmpeg...", flush=True)
        subprocess.run(
            ["apt-get", "install", "-y", "--no-install-recommends", "ffmpeg"],
            capture_output=True,
            env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"},
            check=False,
        )
        print("✅ ffmpeg ready!", flush=True)

# ══════════════════════════════════════════
# 🚀 STEP 5 — Start Bot
# ══════════════════════════════════════════
import asyncio, logging, importlib

from telegram import Update
from telegram.ext import Application

import config
from database import db

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("miss_shasikala.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)
START_TIME = time.time()


def load_plugins(app: Application) -> int:
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    loaded = 0
    for fname in sorted(os.listdir(plugins_dir)):
        if fname.endswith(".py") and not fname.startswith("_"):
            try:
                mod = importlib.import_module(f"plugins.{fname[:-3]}")
                if hasattr(mod, "register"):
                    mod.register(app)
                loaded += 1
                logger.info(f"✅ Plugin: {fname}")
            except Exception as exc:
                logger.error(f"❌ Plugin FAILED {fname}: {exc}")
    return loaded


def main() -> None:
    print("""
╔══════════════════════════════════════════════╗
║   🌸 MISS SHASIKALA TELEGRAM BOT 🌸         ║
║   👑 Created by : Nimesha Madhushan          ║
║   🔗 GitHub    : github.com/nimesha206/nimabt║
║   📞 Owner     : +94726800969               ║
║   🌐 Group     : t.me/mjsicgroupsl          ║
╚══════════════════════════════════════════════╝
    """)

    if not config.BOT_TOKEN:
        print("❌  config.py හි BOT_TOKEN දමන්න! (@BotFather)")
        sys.exit(1)

    if config.OWNER_ID == 0:
        print("⚠️  config.py හි OWNER_ID දමන්න! (https://t.me/userinfobot)")

    app = Application.builder().token(config.BOT_TOKEN).build()
    total = load_plugins(app)
    print(f"📦 Plugins loaded : {total}")
    print(f"🤖 Bot is running ! Prefix: {config.PREFIX}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
