"""
Plugin: Fun Commands
Commands: joke, quote, fact, 8ball, compliment, insult, flirt, ship, hack, shayari, goodnight
"""

import random
import asyncio
import aiohttp

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode

import config
from helpers import footer, auto_delete


async def _fetch(url: str, timeout=8) -> dict | None:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as s:
            async with s.get(url) as r:
                return await r.json()
    except Exception:
        return None


# ══════════════════════════════════════════
# /joke
# ══════════════════════════════════════════
async def joke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("😂 *Joke ගනිමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _fetch("https://v2.jokeapi.dev/joke/Any?type=twopart&blacklistFlags=nsfw,racist,sexist")
    if d and d.get("setup"):
        text = f"😂 *{d['setup']}*\n\n_{d['delivery']}_"
    else:
        d2 = await _fetch("https://official-joke-api.appspot.com/jokes/random")
        text = f"😂 *{d2['setup']}*\n\n_{d2['punchline']}_" if d2 else "❌ Joke ලබා ගැනීමට නොහැකිය"
    await wait.edit_text(text + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /quote
# ══════════════════════════════════════════
async def quote(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("💬 *Quote ගනිමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _fetch("https://zenquotes.io/api/random")
    if d and d[0].get("q"):
        text = f'💬 *"{d[0]["q"]}"*\n\n— _{d[0]["a"]}_'
    else:
        d2 = await _fetch("https://api.quotable.io/random")
        text = f'💬 *"{d2["content"]}"*\n\n— _{d2["author"]}_' if d2 else "❌ Quote ලබා ගැනීමට නොහැකිය"
    await wait.edit_text(text + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /fact
# ══════════════════════════════════════════
async def fact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("💡 *Fact ගනිමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _fetch("https://uselessfacts.jsph.pl/random.json?language=en")
    text = d.get("text") if d else None
    if not text:
        d2 = await _fetch("https://catfact.ninja/fact")
        text = d2.get("fact") if d2 else "❌ Fact ලබා ගැනීමට නොහැකිය"
    await wait.edit_text(
        f"💡 *Interesting Fact!*\n━━━━━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /8ball
# ══════════════════════════════════════════
BALL_ANSWERS = [
    "✅ ඔව්, නිසැකයි!", "✅ නිශ්චිතවම!", "✅ හොඳ ලකුණු ඇත.", "✅ ඔව් :D",
    "⚠️ ප්‍රතිඵල අපැහැදිලියි", "⚠️ දැනට නොකිව හැකිය", "⚠️ නොකිව නොහැකිය",
    "❌ නෑ!", "❌ නිශ්චිතවම නෑ!", "❌ ඒකට කිසිවිටෙකත් හැකි නෑ",
]

async def eightball(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = " ".join(ctx.args)
    if not q:
        await update.message.reply_text(
            f"⚠️ ප්‍රශ්නයක් ඇතුළත් කරන්න!\n`{config.PREFIX}8ball Will I be rich?`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return
    answer = random.choice(BALL_ANSWERS)
    msg = await update.message.reply_text(
        f"🎱 *Magic 8 Ball*\n━━━━━━━━━━━━━━━━━━━━━━\n❓ *{q}*\n\n🎱 {answer}\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /compliment  /insult  /flirt
# ══════════════════════════════════════════
COMPLIMENTS = [
    "ඔබ සූර්යාලෝකය වගේ ❤️", "ඔබේ සිනහව ලෝකය ආලෝකවත් කරයි ✨",
    "ඔබ ඇදහිය නොහැකි පුද්ගලයෙකි 💕", "ඔබ ගේ presence alone positive vibes දෙනවා 🌸",
    "ඔබ සෑම කෙනෙකුගේම හදවතේ ඉඩ ඇති 💖",
]
INSULTS = [
    "ඔයා WiFi signal වගේ — දුරින් හිටිය හොඳයි 😂",
    "ඔයා calendar වගේ — ඔයාගේ දවස් ගණන් ගිහිල්ල 😅",
    "ඔයා dictionary වගේ — boring ❄️",
]
FLIRTS = [
    "ඔබ Google Maps නෙමේද? ඔබ නැතිව මං ගමනක් යන්නෙ නෑ 💕",
    "WiFi password හොයනවාද? ඒ ගොඩ — ඔබ ළඟ connection automatic 💘",
    "ඔබේ කෙස් රන්රේ — ඔබ perfect 😍",
]

async def compliment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"💕 *Compliment*\n━━━━━━━━━━━━━━━━━━━━━━\n{random.choice(COMPLIMENTS)}\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))

async def insult(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"😂 *Playful Insult*\n━━━━━━━━━━━━━━━━━━━━━━\n{random.choice(INSULTS)}\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))

async def flirt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"💘 *Flirt*\n━━━━━━━━━━━━━━━━━━━━━━\n{random.choice(FLIRTS)}\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /ship
# ══════════════════════════════════════════
async def ship(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    user = update.effective_user.first_name
    target = " ".join(args) if args else "Someone Special"
    percent = random.randint(1, 100)
    bar_filled = int(percent / 10)
    bar = "💗" * bar_filled + "🖤" * (10 - bar_filled)
    msg = await update.message.reply_text(
        f"💑 *Ship Meter*\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💕 *{user}* ❤️ *{target}*\n\n"
        f"{bar}\n"
        f"💯 *{percent}% Compatible!*\n━━━━━━━━━━━━━━━━━━━━━━"
        + footer(), parse_mode=ParseMode.MARKDOWN
    )
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /hack
# ══════════════════════════════════════════
async def hack(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    target = " ".join(ctx.args) or "Target"
    steps = [
        f"🔍 Scanning {target}...",
        f"🔓 Bypassing firewall...",
        f"💻 Accessing database...",
        f"📂 Downloading files...",
        f"✅ *{target} Hacked Successfully!* 😈",
    ]
    msg = await update.message.reply_text(f"⚡ *Hacking {target}...*", parse_mode=ParseMode.MARKDOWN)
    for step in steps:
        await asyncio.sleep(1.2)
        await msg.edit_text(step, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


# ══════════════════════════════════════════
# /goodnight
# ══════════════════════════════════════════
async def goodnight(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msgs = [
        "🌙 *සුභ රාත්‍රියක් !* 😴\nඅලූත් සිහිනයන් දකිනු ලැබේ ✨",
        "🌟 *Good Night!* 🌙\nRest well and dream big 💫",
        "🌙 *இனிய இரவு!* ✨\nSweet dreams 💕",
    ]
    msg = await update.message.reply_text(random.choice(msgs) + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(msg))


def register(app: Application):
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("8ball", eightball))
    app.add_handler(CommandHandler("compliment", compliment))
    app.add_handler(CommandHandler("insult", insult))
    app.add_handler(CommandHandler("flirt", flirt))
    app.add_handler(CommandHandler("ship", ship))
    app.add_handler(CommandHandler("hack", hack))
    app.add_handler(CommandHandler("goodnight", goodnight))
