"""
Plugin: Group Management
Commands: kick, ban, unban, mute, unmute, promote, demote,
          welcome, goodbye, setwelcome, setleave,
          antilink, antispam, groupinfo, admins
Events: welcome/goodbye auto-messages
"""

import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import (
    CommandHandler, ChatMemberHandler, MessageHandler,
    ContextTypes, Application, filters,
)
from telegram.constants import ParseMode

import config
from database import db
from helpers import footer, auto_delete, is_owner


def _is_admin(member) -> bool:
    from telegram import ChatMember
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)


async def _require_admin(update: Update) -> bool:
    """Return True if caller is admin."""
    member = await update.effective_chat.get_member(update.effective_user.id)
    if not _is_admin(member):
        msg = await update.message.reply_text(
            "❌ *Admin permission required!*" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return False
    return True


# ══════════════════════════════════════════
# /kick
# ══════════════════════════════════════════
async def kick(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව kick කරන්න!", parse_mode=ParseMode.MARKDOWN)
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(target.id)
        await update.effective_chat.unban_member(target.id)
        msg = await update.message.reply_text(
            f"👢 *{target.first_name}* kicked!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════
# /ban  /unban
# ══════════════════════════════════════════
async def ban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව ban කරන්න!", parse_mode=ParseMode.MARKDOWN)
        return
    target = update.message.reply_to_message.from_user
    reason = " ".join(ctx.args) or "No reason"
    try:
        await update.effective_chat.ban_member(target.id)
        msg = await update.message.reply_text(
            f"🔨 *{target.first_name}* banned!\n*Reason:* {reason}" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def unban(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව unban කරන්න!", parse_mode=ParseMode.MARKDOWN)
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.unban_member(target.id)
        msg = await update.message.reply_text(
            f"✅ *{target.first_name}* unbanned!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ══════════════════════════════════════════
# /mute  /unmute
# ══════════════════════════════════════════
async def mute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව mute කරන්න!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(target.id, ChatPermissions(can_send_messages=False))
        msg = await update.message.reply_text(
            f"🔇 *{target.first_name}* muted!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def unmute(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව unmute කරන්න!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(target.id, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        ))
        msg = await update.message.reply_text(
            f"🔊 *{target.first_name}* unmuted!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ══════════════════════════════════════════
# /promote  /demote
# ══════════════════════════════════════════
async def promote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව promote කරන්න!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.promote_member(target.id,
            can_manage_chat=True, can_delete_messages=True,
            can_restrict_members=True, can_pin_messages=True,
        )
        msg = await update.message.reply_text(
            f"👑 *{target.first_name}* promoted to Admin!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def demote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply කරන user ව demote කරන්න!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.promote_member(target.id,
            can_manage_chat=False, can_delete_messages=False,
            can_restrict_members=False, can_pin_messages=False,
        )
        msg = await update.message.reply_text(
            f"📉 *{target.first_name}* demoted!" + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ══════════════════════════════════════════
# /welcome  /setwelcome
# ══════════════════════════════════════════
async def welcome_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    cid = update.effective_chat.id
    g = db.get_group(cid)
    sub = ctx.args[0].lower() if ctx.args else None
    if sub == "on":
        db.set_group(cid, "welcome", True)
        msg = await update.message.reply_text("✅ *Welcome message ON!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    elif sub == "off":
        db.set_group(cid, "welcome", False)
        msg = await update.message.reply_text("❌ *Welcome message OFF!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    else:
        msg = await update.message.reply_text(
            f"📌 *Welcome Command*\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ ON: `/welcome on`\n❌ OFF: `/welcome off`\n✏️ Custom: `/setwelcome [text]`\n\n"
            f"*Status:* {'🟢 ON' if g.get('welcome') else '🔴 OFF'}" + footer(),
            parse_mode=ParseMode.MARKDOWN
        )
    ctx.application.create_task(auto_delete(msg))


async def setwelcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    text = " ".join(ctx.args)
    if not text:
        await update.message.reply_text("⚠️ Custom welcome text ඇතුළත් කරන්න!")
        return
    db.set_group(update.effective_chat.id, "welcome_text", text)
    msg = await update.message.reply_text("✅ *Custom Welcome Message saved!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


async def goodbye_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    cid = update.effective_chat.id
    g = db.get_group(cid)
    sub = ctx.args[0].lower() if ctx.args else None
    if sub == "on":
        db.set_group(cid, "goodbye", True)
        msg = await update.message.reply_text("✅ *Goodbye message ON!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    elif sub == "off":
        db.set_group(cid, "goodbye", False)
        msg = await update.message.reply_text("❌ *Goodbye message OFF!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    else:
        msg = await update.message.reply_text(
            f"*Status:* {'🟢 ON' if g.get('goodbye') else '🔴 OFF'}" + footer(), parse_mode=ParseMode.MARKDOWN
        )
    ctx.application.create_task(auto_delete(msg))


async def setleave(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    text = " ".join(ctx.args)
    if not text:
        await update.message.reply_text("⚠️ Custom leave text ඇතුළත් කරන්න!")
        return
    db.set_group(update.effective_chat.id, "goodbye_text", text)
    msg = await update.message.reply_text("✅ *Custom Goodbye Message saved!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /antilink
# ══════════════════════════════════════════
async def antilink(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await _require_admin(update): return
    cid = update.effective_chat.id
    sub = ctx.args[0].lower() if ctx.args else None
    if sub == "on":
        db.set_group(cid, "antilink", True)
        msg = await update.message.reply_text("🔗 *Antilink ON!*\nLinks automatically deleted." + footer(), parse_mode=ParseMode.MARKDOWN)
    elif sub == "off":
        db.set_group(cid, "antilink", False)
        msg = await update.message.reply_text("✅ *Antilink OFF!*" + footer(), parse_mode=ParseMode.MARKDOWN)
    else:
        g = db.get_group(cid)
        msg = await update.message.reply_text(
            f"🔗 *Antilink Status:* {'🟢 ON' if g.get('antilink') else '🔴 OFF'}\n`/antilink on` or `/antilink off`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /groupinfo
# ══════════════════════════════════════════
async def groupinfo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("❌ Group command පමණයි!")
        return
    cnt = await chat.get_member_count()
    admins = await chat.get_administrators()
    text = (
        f"👥 *Group Information*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Name:* {chat.title}\n"
        f"🆔 *ID:* `{chat.id}`\n"
        f"👥 *Members:* {cnt}\n"
        f"👮 *Admins:* {len(admins)}\n"
        f"🔗 *Link:* {chat.invite_link or 'N/A'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /admins
# ══════════════════════════════════════════
async def admins_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        await update.message.reply_text("❌ Group command පමණයි!")
        return
    admins = await chat.get_administrators()
    lines = [f"👮 *Group Admins ({len(admins)})*\n━━━━━━━━━━━━━━━━━━━━━━"]
    for a in admins:
        name = a.user.first_name
        role = "🔰 Creator" if a.status == "creator" else "👮 Admin"
        lines.append(f"{role}: [{name}](tg://user?id={a.user.id})")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━" + footer())
    msg = await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# Auto Welcome / Goodbye handler
# ══════════════════════════════════════════
async def member_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member: return
    cid = update.effective_chat.id
    g = db.get_group(cid)
    new = update.chat_member.new_chat_member
    old = update.chat_member.old_chat_member

    from telegram import ChatMember
    joined = new.status == ChatMember.MEMBER and old.status in (ChatMember.LEFT, ChatMember.BANNED)
    left   = new.status in (ChatMember.LEFT, ChatMember.BANNED) and old.status == ChatMember.MEMBER

    user = update.chat_member.new_chat_member.user

    if joined and g.get("welcome"):
        wtext = g.get("welcome_text") or (
            f"╔══════════════════════╗\n"
            f"║  🌸 *{update.effective_chat.title}* 🌸  ║\n"
            f"╚══════════════════════╝\n\n"
            f"🇱🇰 *සාදරයෙන් පිළිගනිමු* [{user.first_name}](tg://user?id={user.id}) 🙏\n"
            f"🇬🇧 *Welcome* [{user.first_name}](tg://user?id={user.id}) 🙏\n\n"
            f"💚 Please follow group rules!\n━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await update.effective_chat.send_message(wtext, parse_mode=ParseMode.MARKDOWN)

    elif left and g.get("goodbye"):
        ltext = g.get("goodbye_text") or (
            f"👋 *[{user.first_name}](tg://user?id={user.id})* left the group!\n"
            f"_Goodbye, come back soon_ 💕"
            + footer()
        )
        await update.effective_chat.send_message(ltext, parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════
# Anti-link message handler
# ══════════════════════════════════════════
async def antilink_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    cid = update.effective_chat.id
    g = db.get_group(cid)
    if not g.get("antilink"): return

    import re
    text = update.message.text
    if re.search(r"(https?://|t\.me/|telegram\.me/)", text, re.I):
        # Check if user is admin
        member = await update.effective_chat.get_member(update.effective_user.id)
        if not _is_admin(member):
            try:
                await update.message.delete()
                warn = await update.effective_chat.send_message(
                    f"🚫 [{update.effective_user.first_name}](tg://user?id={update.effective_user.id}) — Links not allowed!"
                    + footer(), parse_mode=ParseMode.MARKDOWN
                )
                ctx.application.create_task(auto_delete(warn, 10))
            except Exception:
                pass


def register(app: Application):
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("welcome", welcome_cmd))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("goodbye", goodbye_cmd))
    app.add_handler(CommandHandler("setleave", setleave))
    app.add_handler(CommandHandler("antilink", antilink))
    app.add_handler(CommandHandler(["groupinfo", "ginfo"], groupinfo))
    app.add_handler(CommandHandler(["admins", "staff"], admins_cmd))
    app.add_handler(ChatMemberHandler(member_update, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, antilink_handler), group=10)
