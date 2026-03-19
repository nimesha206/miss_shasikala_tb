"""
Plugin: AI Commands
Commands: ai, gpt, gemini, llama3, imagine
"""

import asyncio
import aiohttp
import google.generativeai as genai

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode, ChatAction

import config
from helpers import footer, auto_delete, is_owner

# Gemini setup
genai.configure(api_key=config.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Conversation history per user (gemini)
_history: dict = {}


async def _gemini_ask(uid: int, question: str) -> str:
    """Ask Gemini with per-user history."""
    if uid not in _history:
        _history[uid] = []
    _history[uid].append({"role": "user", "parts": [question]})
    # Keep last 20 turns
    if len(_history[uid]) > 40:
        _history[uid] = _history[uid][-40:]
    try:
        chat = gemini_model.start_chat(history=_history[uid][:-1])
        resp = await asyncio.to_thread(chat.send_message, question)
        answer = resp.text
        _history[uid].append({"role": "model", "parts": [answer]})
        return answer
    except Exception as e:
        return f"❌ Gemini Error: {e}"


async def _free_ai(question: str) -> str:
    """Fallback free AI APIs."""
    apis = [
        f"https://api.paxsenix.biz.id/ai/gpt4?text={aiohttp.helpers.requote_uri(question)}",
        f"https://api.openai.com/v1/chat/completions",  # needs key; skip silently
    ]
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
        try:
            async with s.get(f"https://api.paxsenix.biz.id/ai/gpt4?text={question}") as r:
                d = await r.json()
                return d.get("message") or d.get("result") or d.get("text") or "❌ No answer"
        except Exception:
            pass
    return "❌ AI service unavailable right now"


# ══════════════════════════════════════════
# /ai  /gpt  /gemini  /llama3
# ══════════════════════════════════════════
async def ai_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = " ".join(ctx.args)
    if not q:
        msg = await update.message.reply_text(
            f"⚠️ ප්‍රශ්නයක් ඇතුළත් කරන්න!\n"
            f"*උදාහරණ:* `{config.PREFIX}ai What is love?`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    await update.effective_chat.send_action(ChatAction.TYPING)
    wait = await update.message.reply_text(
        f"🤖 *AI සිතමින්...*\n⏳ රැඳෙන්න...", parse_mode=ParseMode.MARKDOWN
    )

    uid = update.effective_user.id
    answer = await _gemini_ask(uid, q)

    text = (
        f"🤖 *AI Answer*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"❓ *Question:* {q}\n\n"
        f"💬 *Answer:*\n{answer}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
        + footer()
    )
    await wait.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /clearai  — clear conversation history
# ══════════════════════════════════════════
async def clearai(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _history.pop(uid, None)
    msg = await update.message.reply_text(
        "🧹 *AI History cleared!*" + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /imagine  — AI image generation
# ══════════════════════════════════════════
async def imagine(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(ctx.args)
    if not prompt:
        msg = await update.message.reply_text(
            f"⚠️ Prompt ඇතුළත් කරන්න!\n"
            f"*උදාහරණ:* `{config.PREFIX}imagine a beautiful sunset in Sri Lanka`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    wait = await update.message.reply_text(
        f"🎨 *Image generate කරමින්...*\n⏳ රැඳෙන්න...", parse_mode=ParseMode.MARKDOWN
    )

    # Try multiple free image APIs
    img_url = None
    apis = [
        f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true",
        f"https://api.paxsenix.biz.id/ai/flux?prompt={prompt}",
    ]

    # pollinations.ai is free & reliable — use directly
    img_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"

    try:
        await update.message.reply_photo(
            photo=img_url,
            caption=f"🎨 *AI Generated Image*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 *Prompt:* {prompt}"
                    + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
        await wait.delete()
    except Exception as e:
        await wait.edit_text(f"❌ Image generate කිරීමට නොහැකිය: {e}" + footer(),
                             parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


def register(app: Application):
    app.add_handler(CommandHandler(["ai", "gpt", "gemini", "llama3", "chatai"], ai_cmd))
    app.add_handler(CommandHandler("clearai", clearai))
    app.add_handler(CommandHandler(["imagine", "flux", "sora"], imagine))
