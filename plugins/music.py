"""
Plugin: Music & Video Download
Commands: play, song, mp3, video, mp4, ytmp4, lyrics
"""

import asyncio
import os
import re
import subprocess
import tempfile

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode, ChatAction

import config
from helpers import footer, auto_delete, hbytes

YT_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"


async def _yt_search(query: str) -> dict | None:
    """Search YouTube and return first result info."""
    try:
        import yt_dlp
        ydl_opts = {"quiet": True, "no_warnings": True, "default_search": "ytsearch1"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, query, download=False)
            if "entries" in info:
                return info["entries"][0]
            return info
    except Exception:
        return None


async def _download_audio(url: str, out_dir: str) -> str | None:
    """Download audio as MP3 using yt-dlp."""
    try:
        import yt_dlp
        out_tmpl = os.path.join(out_dir, "%(title)s.%(ext)s")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_tmpl,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}],
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        files = [f for f in os.listdir(out_dir) if f.endswith(".mp3")]
        return os.path.join(out_dir, files[0]) if files else None
    except Exception:
        return None


async def _download_video(url: str, out_dir: str, quality="360") -> str | None:
    """Download video using yt-dlp."""
    try:
        import yt_dlp
        fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        out_tmpl = os.path.join(out_dir, "%(title)s.%(ext)s")
        ydl_opts = {"format": fmt, "outtmpl": out_tmpl, "quiet": True, "merge_output_format": "mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
        files = [f for f in os.listdir(out_dir) if f.endswith(".mp4")]
        return os.path.join(out_dir, files[0]) if files else None
    except Exception:
        return None


# ══════════════════════════════════════════
# /play  /song  /mp3
# ══════════════════════════════════════════
async def play_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args)
    if not query:
        msg = await update.message.reply_text(
            f"⚠️ ගීත නාමය ඇතුළත් කරන්න!\n"
            f"*උදාහරණ:*\n`{config.PREFIX}play Shape of You`\n`{config.PREFIX}play https://youtu.be/...`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_AUDIO)
    wait = await update.message.reply_text(
        f"🔍 *සොයමින්...*\n🎵 *ඉල්ලුම:* {query}\n⏳ YouTube හි සොයමින்...", parse_mode=ParseMode.MARKDOWN
    )

    info = await _yt_search(query)
    if not info:
        await wait.edit_text("❌ ගීතය සොයා ගැනීමට නොහැකිය!" + footer(), parse_mode=ParseMode.MARKDOWN)
        return

    title = info.get("title", query)
    url = info.get("webpage_url") or info.get("url")
    duration = info.get("duration", 0)
    dur_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
    thumb = info.get("thumbnail", "")

    await wait.edit_text(
        f"⬇️ *Download කරමින்...*\n🎵 *{title}*\n⏱️ Duration: {dur_str}", parse_mode=ParseMode.MARKDOWN
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = await _download_audio(url, tmp)
        if not path:
            await wait.edit_text("❌ Download ව්‍යර්ථ විය!" + footer(), parse_mode=ParseMode.MARKDOWN)
            return

        size = hbytes(os.path.getsize(path))
        caption = (
            f"🎵 *{title}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ *Duration:* {dur_str}\n"
            f"📦 *Size:* {size}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await wait.delete()
        await update.message.reply_audio(
            audio=open(path, "rb"),
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            title=title,
            performer=config.BOT_NAME,
        )


# ══════════════════════════════════════════
# /video  /mp4  /ytmp4
# ══════════════════════════════════════════
async def video_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args)
    if not query:
        msg = await update.message.reply_text(
            f"⚠️ වීඩියෝ නාමය ඇතුළත් කරන්න!\n`{config.PREFIX}video Avengers`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)
    wait = await update.message.reply_text(
        f"🔍 *සොයමින்...*\n🎬 *ඉල්ලුම:* {query}", parse_mode=ParseMode.MARKDOWN
    )

    info = await _yt_search(query)
    if not info:
        await wait.edit_text("❌ වීඩියෝ සොයා ගැනීමට නොහැකිය!" + footer(), parse_mode=ParseMode.MARKDOWN)
        return

    title = info.get("title", query)
    url = info.get("webpage_url") or info.get("url")
    duration = info.get("duration", 0)
    dur_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"

    await wait.edit_text(
        f"⬇️ *Download කරමින්...*\n🎬 *{title}*\n⏱️ Duration: {dur_str}\n📺 Quality: 360p", parse_mode=ParseMode.MARKDOWN
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = await _download_video(url, tmp, "360")
        if not path:
            await wait.edit_text("❌ Download ව්‍යර්ථ විය! (Video too large?)" + footer(), parse_mode=ParseMode.MARKDOWN)
            return

        size = hbytes(os.path.getsize(path))
        caption = (
            f"🎬 *{title}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ *Duration:* {dur_str}\n"
            f"📦 *Size:* {size}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await wait.delete()
        await update.message.reply_video(
            video=open(path, "rb"),
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            supports_streaming=True,
        )


# ══════════════════════════════════════════
# /lyrics
# ══════════════════════════════════════════
async def lyrics_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    import aiohttp
    query = " ".join(ctx.args)
    if not query:
        msg = await update.message.reply_text(
            f"⚠️ ගීත නාමය ඇතුළත් කරන්න!\n`{config.PREFIX}lyrics Shape of You`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    wait = await update.message.reply_text("🎵 *Lyrics සොයමින්...*", parse_mode=ParseMode.MARKDOWN)

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.get(f"https://some-random-api.com/lyrics?title={query}") as r:
                data = await r.json()

        title = data.get("title", query)
        author = data.get("author", "Unknown")
        lyr = data.get("lyrics", "")[:3500]

        text = (
            f"🎵 *{title}*\n"
            f"🎤 *Artist:* {author}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{lyr}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await wait.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(wait))
    except Exception as e:
        await wait.edit_text(f"❌ Lyrics ලබා ගැනීමට නොහැකිය!\n{e}" + footer(), parse_mode=ParseMode.MARKDOWN)


def register(app: Application):
    app.add_handler(CommandHandler(["play", "song", "mp3", "ytmp3"], play_cmd))
    app.add_handler(CommandHandler(["video", "mp4", "ytmp4", "ytvideo"], video_cmd))
    app.add_handler(CommandHandler("lyrics", lyrics_cmd))
