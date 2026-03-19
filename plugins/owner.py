"""
Plugin: Owner Commands
Commands: addpremium, delpremium, banuser, unbanuser, broadcast, stats
"""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode

import config
from database import db
from helpers import footer, auto_delete, is_owner, get_runtime


def _owner_only(func):
    """Decorator: owner only commands."""
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not is_owner(update.effective_user.id):
            msg = await update.message.reply_text(
                "❌ *Owner only command!*" + footer(), parse_mode=ParseMode.MARKDOWN
            )
            ctx.application.create_task(auto_delete(msg))
            return
        return await func(update, ctx)
    return wrapper


# ══════════════════════════════════════════
# /addpremium  /delpremium
# ══════════════════════════════════════════
@_owner_only
async def addpremium(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව premium කරන්න!")
        return
    uid = update.message.reply_to_message.from_user.id
    name = update.message.reply_to_message.from_user.first_name
    db.add_premium(uid)
    msg = await update.message.reply_text(
        f"⭐ *{name}* added to Premium!" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


@_owner_only
async def delpremium(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව premium remove කරන්න!")
        return
    uid = update.message.reply_to_message.from_user.id
    name = update.message.reply_to_message.from_user.first_name
    db.remove_premium(uid)
    msg = await update.message.reply_text(
        f"❌ *{name}* removed from Premium!" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /banuser  /unbanuser
# ══════════════════════════════════════════
@_owner_only
async def banuser(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව ban කරන්න!")
        return
    uid = update.message.reply_to_message.from_user.id
    name = update.message.reply_to_message.from_user.first_name
    db.ban_user(uid)
    msg = await update.message.reply_text(
        f"🔨 *{name}* bot banned!" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


@_owner_only
async def unbanuser(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව unban කරන්න!")
        return
    uid = update.message.reply_to_message.from_user.id
    name = update.message.reply_to_message.from_user.first_name
    db.unban_user(uid)
    msg = await update.message.reply_text(
        f"✅ *{name}* bot unbanned!" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /broadcast  — Send message to all users
# ══════════════════════════════════════════
@_owner_only
async def broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = " ".join(ctx.args)
    if not text:
        await update.message.reply_text("⚠️ Message ඇතුළත් කරන්න!\n`/broadcast Hello everyone!`", parse_mode=ParseMode.MARKDOWN)
        return

    users = db._data.get("users", {})
    sent = 0
    failed = 0
    for uid in users:
        try:
            await ctx.bot.send_message(
                int(uid),
                f"📢 *Broadcast from {config.BOT_NAME}*\n━━━━━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━━━━━"
                + footer(), parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except Exception:
            failed += 1

    msg = await update.message.reply_text(
        f"📢 *Broadcast Done!*\n✅ Sent: {sent}\n❌ Failed: {failed}" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /stats  — Bot statistics
# ══════════════════════════════════════════
@_owner_only
async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = len(db._data.get("users", {}))
    groups = len(db._data.get("groups", {}))
    premium = len(db._data.get("premium", []))
    banned = len(db._data.get("banned", []))
    msg = await update.message.reply_text(
        f"📊 *Bot Statistics*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Users:* {users}\n"
        f"👫 *Groups:* {groups}\n"
        f"⭐ *Premium:* {premium}\n"
        f"🔨 *Banned:* {banned}\n"
        f"⏱️ *Uptime:* `{get_runtime()}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


def register(app: Application):
    app.add_handler(CommandHandler("addpremium", addpremium))
    app.add_handler(CommandHandler("delpremium", delpremium))
    app.add_handler(CommandHandler("banuser", banuser))
    app.add_handler(CommandHandler("unbanuser", unbanuser))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
