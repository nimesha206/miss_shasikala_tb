"""
Plugin: Bot Mother Commands
Owner number ගෙන් commands දෙනකොට bot execute කරනවා

Commands (owner only):
  .leave [group_id or @username]  — bot group leave කරනවා
  .block [user_id or @username]   — user ignore list දානවා
  .unblock [user_id or @username] — ignore list ගෙන් ඉවත් කරනවා
  .blocklist                      — blocked users list
  .joingroup [link]               — bot group join කරනවා
  .pin                            — reply msg pin කරනවා
  .unpin                          — unpin all
  .del / .delete                  — reply msg delete කරනවා
  .purge [n]                      — last n messages delete
  .setname [name]                 — bot name change
  .setbio [text]                  — bot bio change
  .setphoto                       — bot photo change (reply to image)
  .grouplist                      — bot ඉන්න groups list
"""

import asyncio
from telegram import Update, Chat
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, Application, filters
from telegram.constants import ParseMode

import config
from database import db
from helpers import footer, auto_delete, is_owner

# ── In-memory blocked set (also persisted in db) ─
_blocked: set = set()


def _load_blocked():
    global _blocked
    _blocked = set(db._data.get("bot_blocked", []))


def _save_blocked():
    db._data["bot_blocked"] = list(_blocked)
    db.save()


_load_blocked()


# ══════════════════════════════════════════════════
# Middleware — block filtered messages globally
# ══════════════════════════════════════════════════
async def block_filter(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Silently ignore messages from blocked users."""
    if update.effective_user and update.effective_user.id in _blocked:
        return  # ignored


# ══════════════════════════════════════════════════
# Owner check helper
# ══════════════════════════════════════════════════
async def _check_owner(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    if not is_owner(update.effective_user.id):
        msg = await update.message.reply_text(
            "❌ *Bot Mother commands — Owner only!*" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg, 10))
        return False
    return True


# ══════════════════════════════════════════════════
# /leave — bot group leave කරනවා
# ══════════════════════════════════════════════════
async def leave_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    # target: argument දෙනවා නැතිනම් current chat
    target = ctx.args[0] if ctx.args else None

    try:
        if target:
            # numeric ID or @username
            chat_id = int(target) if target.lstrip("-").isdigit() else target
            await ctx.bot.leave_chat(chat_id)
            msg = await update.message.reply_text(
                f"✅ *Bot left:* `{target}`" + footer(),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            # leave current group
            if update.effective_chat.type == "private":
                msg = await update.message.reply_text(
                    "⚠️ Group ID හෝ @username ඇතුළත් කරන්න!\n"
                    f"`/leave -1001234567890`\n`/leave @groupusername`"
                    + footer(), parse_mode=ParseMode.MARKDOWN,
                )
            else:
                chat_title = update.effective_chat.title
                await update.message.reply_text(
                    f"👋 *Leaving {chat_title}...*" + footer(),
                    parse_mode=ParseMode.MARKDOWN,
                )
                await asyncio.sleep(1)
                await ctx.bot.leave_chat(update.effective_chat.id)
                return

        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        msg = await update.message.reply_text(
            f"❌ Leave ව්‍යර්ථ: `{e}`" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════════════
# /block — user bot ignore list ට දානවා
# ══════════════════════════════════════════════════
async def block_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    # From reply or argument
    target_id = None
    target_name = None

    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = update.message.reply_to_message.from_user.first_name
    elif ctx.args:
        arg = ctx.args[0].replace("+", "").replace(" ", "")
        if arg.lstrip("-").isdigit():
            target_id = int(arg)
            target_name = str(target_id)
        else:
            try:
                user = await ctx.bot.get_chat(arg)
                target_id = user.id
                target_name = user.first_name or arg
            except Exception:
                pass

    if not target_id:
        msg = await update.message.reply_text(
            f"⚠️ User reply කරන්න හෝ ID/username ඇතුළත් කරන්න!\n"
            f"`/block @username`\n`/block 94712345678`"
            + footer(), parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))
        return

    if target_id == config.OWNER_ID:
        msg = await update.message.reply_text("❌ Owner block කරන්න බෑ! 😄" + footer(), parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(msg, 5))
        return

    _blocked.add(target_id)
    _save_blocked()

    msg = await update.message.reply_text(
        f"🚫 *Blocked!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *User:* {target_name}\n"
        f"🆔 *ID:* `{target_id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"_Bot ඔවුන්ගේ commands ignore කරනු ලැබේ_"
        + footer(), parse_mode=ParseMode.MARKDOWN,
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════════════
# /unblock
# ══════════════════════════════════════════════════
async def unblock_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    target_id = None
    target_name = None

    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = update.message.reply_to_message.from_user.first_name
    elif ctx.args:
        arg = ctx.args[0].replace("+", "").replace(" ", "")
        if arg.lstrip("-").isdigit():
            target_id = int(arg)
            target_name = str(target_id)

    if not target_id:
        msg = await update.message.reply_text(
            f"⚠️ User reply කරන්න හෝ ID ඇතුළත් කරන්න!" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))
        return

    if target_id in _blocked:
        _blocked.discard(target_id)
        _save_blocked()
        msg = await update.message.reply_text(
            f"✅ *Unblocked!* — `{target_name or target_id}`" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        msg = await update.message.reply_text(
            f"⚠️ `{target_name or target_id}` blocked list හි නෑ!" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════════════
# /blocklist
# ══════════════════════════════════════════════════
async def blocklist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    if not _blocked:
        msg = await update.message.reply_text(
            "✅ *Blocked list හිස්!*" + footer(), parse_mode=ParseMode.MARKDOWN
        )
    else:
        lines = [f"🚫 *Blocked Users ({len(_blocked)})*\n━━━━━━━━━━━━━━━━━━━━━━"]
        for uid in _blocked:
            lines.append(f"• `{uid}`")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━" + footer())
        msg = await update.message.reply_text(
            "\n".join(lines), parse_mode=ParseMode.MARKDOWN
        )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════════════
# /del  /delete — reply message delete
# ══════════════════════════════════════════════════
async def delete_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    try:
        if update.message.reply_to_message:
            await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        msg = await update.message.reply_text(f"❌ Delete ව්‍යර්ථ: `{e}`" + footer(), parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(msg, 5))


# ══════════════════════════════════════════════════
# /purge [n] — last n messages delete
# ══════════════════════════════════════════════════
async def purge_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    n = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() else 10
    n = min(n, 100)  # max 100

    wait = await update.message.reply_text(f"🗑️ *{n} messages delete කරමින்...*", parse_mode=ParseMode.MARKDOWN)

    deleted = 0
    # Telegram Bot API allows deleting recent messages only
    msg_id = update.message.message_id
    for i in range(msg_id, max(msg_id - n - 1, 0), -1):
        try:
            await ctx.bot.delete_message(update.effective_chat.id, i)
            deleted += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    try:
        await wait.delete()
    except Exception:
        pass

    done = await update.effective_chat.send_message(
        f"✅ *{deleted} messages deleted!*" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(done, 5))


# ══════════════════════════════════════════════════
# /pin — reply msg pin
# ══════════════════════════════════════════════════
async def pin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Pin කළ message reply කරන්න!", parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(msg))
        return
    try:
        await ctx.bot.pin_chat_message(
            update.effective_chat.id,
            update.message.reply_to_message.message_id,
            disable_notification=False,
        )
        msg = await update.message.reply_text("📌 *Message pinned!*" + footer(), parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ Pin ව්‍යර්ථ: `{e}`" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════════
# /unpin
# ══════════════════════════════════════════════════
async def unpin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return
    try:
        await ctx.bot.unpin_all_chat_messages(update.effective_chat.id)
        msg = await update.message.reply_text("✅ *All messages unpinned!*" + footer(), parse_mode=ParseMode.MARKDOWN)
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════════
# /grouplist — bot ඉන්න groups
# ══════════════════════════════════════════════════
async def grouplist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    groups = db._data.get("groups", {})
    if not groups:
        msg = await update.message.reply_text(
            "📭 *Bot කිසිම group හි නෑ!*" + footer(), parse_mode=ParseMode.MARKDOWN
        )
    else:
        lines = [f"👥 *Bot Groups ({len(groups)})*\n━━━━━━━━━━━━━━━━━━━━━━"]
        for gid in list(groups.keys())[:20]:
            try:
                chat = await ctx.bot.get_chat(int(gid))
                lines.append(f"• *{chat.title}* — `{gid}`")
            except Exception:
                lines.append(f"• `{gid}`")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━" + footer())
        msg = await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════════════
# /setname — bot display name change
# ══════════════════════════════════════════════════
async def setname_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return
    name = " ".join(ctx.args)
    if not name:
        msg = await update.message.reply_text(
            f"⚠️ Name ඇතුළත් කරන්න!\n`/setname Miss Shasikala`" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))
        return
    try:
        await ctx.bot.set_my_name(name)
        msg = await update.message.reply_text(
            f"✅ *Bot name changed to:* {name}" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════════
# /setbio — bot bio change
# ══════════════════════════════════════════════════
async def setbio_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return
    bio = " ".join(ctx.args)
    if not bio:
        msg = await update.message.reply_text(
            f"⚠️ Bio ඇතුළත් කරන්න!\n`/setbio 🌸 Sinhala Telegram Bot`" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))
        return
    try:
        await ctx.bot.set_my_description(bio)
        msg = await update.message.reply_text(
            f"✅ *Bot bio updated!*" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════════
# /setphoto — bot profile photo change
# ══════════════════════════════════════════════════
async def setphoto_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _check_owner(update, ctx): return

    photo = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]
    elif update.message.photo:
        photo = update.message.photo[-1]

    if not photo:
        msg = await update.message.reply_text(
            "⚠️ Photo reply කරන්න හෝ photo සමඟ `/setphoto` ලියන්න!" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        ctx.application.create_task(auto_delete(msg))
        return

    try:
        import io
        file = await ctx.bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await file.download_to_memory(buf)
        buf.seek(0)
        await ctx.bot.set_my_photo(buf)
        msg = await update.message.reply_text(
            "✅ *Bot photo updated!*" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════════════
# Register
# ══════════════════════════════════════════════════
def register(app: Application):
    # Block filter — runs on all messages first (group 0)
    app.add_handler(
        MessageHandler(filters.ALL, block_filter),
        group=-999,
    )

    app.add_handler(CommandHandler("leave", leave_cmd))
    app.add_handler(CommandHandler(["block", "ignore"], block_cmd))
    app.add_handler(CommandHandler(["unblock", "unignore"], unblock_cmd))
    app.add_handler(CommandHandler("blocklist", blocklist_cmd))
    app.add_handler(CommandHandler(["del", "delete"], delete_cmd))
    app.add_handler(CommandHandler("purge", purge_cmd))
    app.add_handler(CommandHandler("pin", pin_cmd))
    app.add_handler(CommandHandler("unpin", unpin_cmd))
    app.add_handler(CommandHandler("grouplist", grouplist_cmd))
    app.add_handler(CommandHandler("setname", setname_cmd))
    app.add_handler(CommandHandler("setbio", setbio_cmd))
    app.add_handler(CommandHandler("setphoto", setphoto_cmd))
