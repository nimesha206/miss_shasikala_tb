"""
Plugin: General Commands
Commands: start, alive, ping, uptime, info, help, menu, owner, id
"""

import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode

import config
from helpers import get_runtime, is_owner, footer, auto_delete


# ══════════════════════════════════════════
# /start
# ══════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"╔══════════════════════════╗\n"
        f"║   🌸 *MISS SHASIKALA BOT* 🌸   ║\n"
        f"╚══════════════════════════╝\n\n"
        f"👋 *ආයුබෝවන් {user.first_name}!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 *Bot:* {config.BOT_NAME}\n"
        f"👑 *Owner:* {config.OWNER_NAME}\n"
        f"🔧 *Prefix:* `{config.PREFIX}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Commands ලැයිස්තුව සඳහා `/help` ටයිප් කරන්න\n"
        + footer()
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Menu", callback_data="menu"),
         InlineKeyboardButton("👑 Owner", url=config.OWNER_CONTACT)],
        [InlineKeyboardButton("🌐 Group", url=config.GROUP_LINK),
         InlineKeyboardButton("⭐ GitHub", url=config.GITHUB)],
    ])
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /alive  /bot
# ══════════════════════════════════════════
async def alive(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime
    now = datetime.now()
    text = (
        f"╔══════════════════════════╗\n"
        f"║   🌸 *MISS SHASIKALA BOT* 🌸   ║\n"
        f"╚══════════════════════════╝\n\n"
        f"✅ *Bot ක්‍රියාත්මකයි!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 *දිනය:* {now.strftime('%Y-%m-%d')}\n"
        f"🕐 *වෙලාව:* {now.strftime('%H:%M:%S')}\n"
        f"⏱️ *Uptime:* `{get_runtime()}`\n"
        f"🤖 *Bot:* {config.BOT_NAME}\n"
        f"👑 *Owner:* {config.OWNER_NAME}\n"
        f"🔧 *Prefix:* `{config.PREFIX}`\n"
        f"📡 *Status:* Online ✅\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Ping", callback_data="ping"),
         InlineKeyboardButton("📋 Menu", callback_data="menu")],
        [InlineKeyboardButton("🌐 Group", url=config.GROUP_LINK)],
    ])
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /ping
# ══════════════════════════════════════════
async def ping(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 *Ping...*", parse_mode=ParseMode.MARKDOWN)
    ms = int((time.time() - start) * 1000)
    status = "🟢 Excellent" if ms < 500 else "🟡 Good" if ms < 1000 else "🔴 Slow"
    text = (
        f"🏓 *PONG!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *Response:* `{ms}ms`\n"
        f"📡 *Status:* {status}\n"
        f"⏱️ *Uptime:* `{get_runtime()}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /uptime  /runtime
# ══════════════════════════════════════════
async def uptime(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        f"⏱️ *BOT RUNTIME*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 *ක්‍රියාත්මක වූ කාලය:*\n"
        f"`{get_runtime()}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /info  /owner  /dev
# ══════════════════════════════════════════
async def info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        f"╔══════════════════════════╗\n"
        f"║   🌸 *BOT INFORMATION* 🌸   ║\n"
        f"╚══════════════════════════╝\n\n"
        f"🤖 *Bot Name:* {config.BOT_NAME}\n"
        f"👑 *Owner:* {config.OWNER_NAME}\n"
        f"📱 *Platform:* Telegram\n"
        f"🔧 *Prefix:* `{config.PREFIX}`\n"
        f"⏱️ *Uptime:* `{get_runtime()}`\n"
        f"🌐 *GitHub:* {config.GITHUB}\n"
        f"📞 *Contact:* {config.OWNER_CONTACT}\n"
        f"👥 *Group:* {config.GROUP_LINK}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Contact Owner", url=config.OWNER_CONTACT)],
        [InlineKeyboardButton("🌐 Join Group", url=config.GROUP_LINK),
         InlineKeyboardButton("⭐ GitHub", url=config.GITHUB)],
    ])
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /id
# ══════════════════════════════════════════
async def get_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    lines = [
        f"🪪 *ID Information*",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"👤 *Your ID:* `{user.id}`",
        f"💬 *Chat ID:* `{chat.id}`",
    ]
    if update.message.reply_to_message:
        r = update.message.reply_to_message.from_user
        lines.append(f"🎯 *Replied User ID:* `{r.id}`")
    lines.append(footer())
    msg = await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /help  /menu
# ══════════════════════════════════════════
async def help_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    p = config.PREFIX
    text = (
        f"╔══════════════════════════╗\n"
        f"║   📋 *MISS SHASIKALA MENU* 📋  ║\n"
        f"╚══════════════════════════╝\n\n"
        f"🤖 *AI & CHAT*\n"
        f"  `{p}ai` , `{p}gpt` , `{p}gemini` — AI Chat\n"
        f"  `{p}imagine` — AI Image Generate\n\n"
        f"🎵 *MUSIC & VIDEO*\n"
        f"  `{p}play` / `{p}song` / `{p}mp3` — Music Download\n"
        f"  `{p}video` / `{p}mp4` — Video Download\n"
        f"  `{p}lyrics` — Lyrics Search\n\n"
        f"🎨 *STICKER & IMAGE*\n"
        f"  `{p}sticker` / `{p}s` — Image → Sticker\n"
        f"  `{p}attp` — Text → Sticker\n"
        f"  `{p}removebg` — BG Remove\n"
        f"  `{p}ss` — Website Screenshot\n\n"
        f"🌍 *INFO & TOOLS*\n"
        f"  `{p}weather` — Weather Info\n"
        f"  `{p}news` — Latest News\n"
        f"  `{p}translate` — Translate Text\n"
        f"  `{p}tts` — Text to Speech\n"
        f"  `{p}define` — Dictionary\n"
        f"  `{p}cinfo` — Country Info\n"
        f"  `{p}8ball` — Magic 8 Ball\n\n"
        f"😂 *FUN*\n"
        f"  `{p}joke` `{p}quote` `{p}fact`\n"
        f"  `{p}compliment` `{p}insult` `{p}flirt`\n"
        f"  `{p}ship` `{p}wasted` `{p}jail`\n"
        f"  `{p}neko` `{p}waifu` `{p}hug` `{p}pat`\n\n"
        f"👥 *GROUP MANAGEMENT*\n"
        f"  `{p}kick` `{p}ban` `{p}unban`\n"
        f"  `{p}mute` `{p}unmute`\n"
        f"  `{p}promote` `{p}demote`\n"
        f"  `{p}welcome` `{p}goodbye`\n"
        f"  `{p}antilink` `{p}antispam`\n"
        f"  `{p}groupinfo` `{p}admins`\n\n"
        f"👑 *OWNER ONLY*\n"
        f"  `{p}addpremium` `{p}delpremium`\n"
        f"  `{p}banuser` `{p}unbanuser`\n"
        f"  `{p}broadcast`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Alive", callback_data="alive"),
         InlineKeyboardButton("⚡ Ping", callback_data="ping")],
        [InlineKeyboardButton("🌐 Join Group", url=config.GROUP_LINK),
         InlineKeyboardButton("👑 Owner", url=config.OWNER_CONTACT)],
        [InlineKeyboardButton("⭐ GitHub", url=config.GITHUB)],
    ])
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# Register
# ══════════════════════════════════════════
def register(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["alive", "bot"], alive))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler(["uptime", "runtime"], uptime))
    app.add_handler(CommandHandler(["info", "owner", "dev"], info))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler(["help", "menu"], help_menu))
