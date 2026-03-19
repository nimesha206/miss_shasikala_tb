"""
Helper utilities for Miss Shasikala Bot
"""

import asyncio
import time
from datetime import timedelta
from telegram import Message
import config

# Module-level start time — imported by all plugins
START_TIME = time.time()


def get_runtime() -> str:
    """Bot uptime as readable string."""
    secs = int(time.time() - START_TIME)
    td = timedelta(seconds=secs)
    d = td.days
    h, rem = divmod(td.seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def is_owner(uid: int) -> bool:
    return uid == config.OWNER_ID or uid in config.SUDO_USERS


async def auto_delete(message: Message, delay: int = None):
    """Delete a message after delay seconds."""
    delay = delay or config.AUTO_DELETE
    if delay > 0:
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass


def footer() -> str:
    return f"\n\n🌸 *{config.BOT_NAME}* | 👑 _{config.OWNER_NAME}_"


def hbytes(size: float) -> str:
    """Human-readable file size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
