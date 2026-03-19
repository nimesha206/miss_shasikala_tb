"""
Plugin: Callback Query Handler (Inline Button Responses)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes, Application
from telegram.constants import ParseMode

import config
from helpers import get_runtime, footer


async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "alive":
        from datetime import datetime
        now = datetime.now()
        text = (
            f"✅ *Bot Online!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ *Uptime:* `{get_runtime()}`\n"
            f"🕐 *Time:* {now.strftime('%H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))

    elif data == "ping":
        import time
        start = time.time()
        ms = int((time.time() - start) * 1000 + 50)
        await query.edit_message_text(
            f"🏓 *Pong!* `{ms}ms`" + footer(), parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="menu")]]))

    elif data == "menu":
        p = config.PREFIX
        text = (
            f"╔══════════════════════════╗\n"
            f"║   📋 *MISS SHASIKALA MENU* 📋  ║\n"
            f"╚══════════════════════════╝\n\n"
            f"🤖 `{p}ai` • `{p}gemini` • `{p}imagine`\n"
            f"🎵 `{p}play` • `{p}video` • `{p}lyrics`\n"
            f"🌤️ `{p}weather` • `{p}news` • `{p}tts`\n"
            f"😂 `{p}joke` • `{p}quote` • `{p}fact`\n"
            f"🎨 `{p}sticker` • `{p}attp` • `{p}removebg`\n"
            f"👥 `{p}kick` • `{p}ban` • `{p}mute`\n\n"
            f"📋 Full list: `/help`"
            + footer()
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Alive", callback_data="alive"),
             InlineKeyboardButton("⚡ Ping", callback_data="ping")],
            [InlineKeyboardButton("🌐 Group", url=config.GROUP_LINK),
             InlineKeyboardButton("👑 Owner", url=config.OWNER_CONTACT)],
        ])
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


def register(app: Application):
    app.add_handler(CallbackQueryHandler(callback_handler))
