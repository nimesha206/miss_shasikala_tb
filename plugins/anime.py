"""
Plugin: Anime & Reaction Images
Commands: neko, waifu, hug, pat, kiss, slap, punch, cry, dance, wink
"""

import aiohttp
import io

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode, ChatAction

import config
from helpers import footer, auto_delete

NEKOS_API = "https://nekos.best/api/v2/{}"
SOME_RANDOM_API = "https://some-random-api.com/animal/{}"


async def _fetch_img(category: str) -> str | None:
    """Fetch image URL from nekos.best API."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.get(NEKOS_API.format(category)) as r:
                d = await r.json()
                results = d.get("results", [])
                if results:
                    return results[0].get("url")
    except Exception:
        pass
    return None


async def _send_reaction(update: Update, ctx: ContextTypes.DEFAULT_TYPE, category: str, caption: str):
    await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    url = await _fetch_img(category)
    if url:
        try:
            await update.message.reply_photo(
                photo=url,
                caption=caption + footer(),
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        except Exception:
            pass
    # fallback
    msg = await update.message.reply_text(f"❌ {category} image ගැනීමට නොහැකිය!" + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


async def neko(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_reaction(update, ctx, "neko", "🐱 *Neko!*")

async def waifu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_reaction(update, ctx, "waifu", "💕 *Waifu!*")

async def hug(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "someone"
    await _send_reaction(update, ctx, "hug", f"🤗 *{user}* hugged *{target}*!")

async def pat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "someone"
    await _send_reaction(update, ctx, "pat", f"👋 *{user}* patted *{target}*!")

async def kiss(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "someone"
    await _send_reaction(update, ctx, "kiss", f"💋 *{user}* kissed *{target}*!")

async def slap(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "someone"
    await _send_reaction(update, ctx, "slap", f"👋 *{user}* slapped *{target}*!")

async def punch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "someone"
    await _send_reaction(update, ctx, "punch", f"👊 *{user}* punched *{target}*!")

async def cry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_reaction(update, ctx, "cry", "😢 *Crying...*")

async def dance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_reaction(update, ctx, "dance", "💃 *Dancing!*")

async def wink(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await _send_reaction(update, ctx, "wink", "😉 *Wink!*")


def register(app: Application):
    app.add_handler(CommandHandler("neko", neko))
    app.add_handler(CommandHandler("waifu", waifu))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("pat", pat))
    app.add_handler(CommandHandler("kiss", kiss))
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("punch", punch))
    app.add_handler(CommandHandler("cry", cry))
    app.add_handler(CommandHandler("dance", dance))
    app.add_handler(CommandHandler("wink", wink))
