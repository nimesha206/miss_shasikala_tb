"""
Plugin: Info & Tools
Commands: weather, news, translate, tts, define, cinfo, ss
"""

import asyncio
import aiohttp
import io

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode, ChatAction

import config
from helpers import footer, auto_delete


async def _get(url, timeout=10, **kwargs):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as s:
            async with s.get(url, **kwargs) as r:
                return await r.json()
    except Exception:
        return None


async def _get_bytes(url, timeout=20):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as s:
            async with s.get(url) as r:
                return await r.read()
    except Exception:
        return None


# ══════════════════════════════════════════
# /weather
# ══════════════════════════════════════════
async def weather(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    city = " ".join(ctx.args)
    if not city:
        await update.message.reply_text(
            f"⚠️ නගරයේ නම ඇතුළත් කරන්න!\n`{config.PREFIX}weather Colombo`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    wait = await update.message.reply_text("🌤️ *කාලගුණය සොයමින்...*", parse_mode=ParseMode.MARKDOWN)

    d = await _get(f"https://wttr.in/{city}?format=j1")
    if d and "current_condition" in d:
        c = d["current_condition"][0]
        area = d["nearest_area"][0]
        aname = area["areaName"][0]["value"]
        country = area["country"][0]["value"]
        desc = c["weatherDesc"][0]["value"]
        temp_c = c["temp_C"]
        temp_f = c["temp_F"]
        humidity = c["humidity"]
        wind = c["windspeedKmph"]
        feels = c["FeelsLikeC"]
        uv = c.get("uvIndex", "N/A")
        text = (
            f"🌤️ *Weather — {aname}, {country}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"☁️ *Condition:* {desc}\n"
            f"🌡️ *Temp:* {temp_c}°C / {temp_f}°F\n"
            f"🌡️ *Feels Like:* {feels}°C\n"
            f"💧 *Humidity:* {humidity}%\n"
            f"💨 *Wind:* {wind} km/h\n"
            f"☀️ *UV Index:* {uv}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
    else:
        text = f"❌ '{city}' සඳහා කාලගුණ තොරතුරු ලබා ගැනීමට නොහැකිය!" + footer()

    await wait.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /news
# ══════════════════════════════════════════
async def news(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    wait = await update.message.reply_text("📰 *News ගනිමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _get("https://saurav.tech/NewsAPI/top-headlines/category/general/us.json")
    if d and d.get("articles"):
        arts = d["articles"][:5]
        lines = ["📰 *Latest News*\n━━━━━━━━━━━━━━━━━━━━━━"]
        for i, a in enumerate(arts, 1):
            lines.append(f"{i}. *{a['title']}*\n   _{a.get('source', {}).get('name', '')}_ | [Read]({a.get('url', '#')})\n")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━" + footer())
        text = "\n".join(lines)
    else:
        text = "❌ News ලබා ගැනීමට නොහැකිය!" + footer()
    await wait.edit_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /translate  /trt
# ══════════════════════════════════════════
async def translate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text(
            f"⚠️ Format: `{config.PREFIX}translate [lang] [text]`\n"
            f"*උදාහරණ:* `{config.PREFIX}translate si Hello World`\n"
            f"_Codes: si=Sinhala, en=English, ta=Tamil, hi=Hindi_"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    lang = args[0]
    text = " ".join(args[1:])
    wait = await update.message.reply_text("🌍 *Translating...*", parse_mode=ParseMode.MARKDOWN)

    d = await _get(f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|{lang}")
    if d and d.get("responseData", {}).get("translatedText"):
        result = d["responseData"]["translatedText"]
        out = (
            f"🌍 *Translation*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Original:* {text}\n"
            f"🔤 *Translated ({lang}):* {result}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
    else:
        out = "❌ Translate ව්‍යර්ථ විය!" + footer()
    await wait.edit_text(out, parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /tts  — Text to Speech
# ══════════════════════════════════════════
async def tts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = " ".join(ctx.args)
    if not text:
        await update.message.reply_text(
            f"⚠️ Text ඇතුළත් කරන්න!\n`{config.PREFIX}tts ආයුබෝවන්`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    await update.effective_chat.send_action(ChatAction.RECORD_VOICE)
    wait = await update.message.reply_text("🔊 *TTS generate කරමින்...*", parse_mode=ParseMode.MARKDOWN)

    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl=si&client=tw-ob"
    headers = {"User-Agent": "Mozilla/5.0"}
    audio = await _get_bytes(url)

    if audio:
        await wait.delete()
        await update.message.reply_voice(
            voice=io.BytesIO(audio),
            caption=f"🔊 *TTS:* _{text}_" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await wait.edit_text("❌ TTS generate ව්‍යර්ථ විය!" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════
# /define  — Dictionary
# ══════════════════════════════════════════
async def define(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    word = " ".join(ctx.args)
    if not word:
        await update.message.reply_text(
            f"⚠️ වචනයක් ඇතුළත් කරන්න!\n`{config.PREFIX}define love`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    wait = await update.message.reply_text("📖 *සොයමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")

    if d and isinstance(d, list):
        entry = d[0]
        wrd = entry["word"]
        meanings = entry.get("meanings", [])
        lines = [f"📖 *{wrd}*\n━━━━━━━━━━━━━━━━━━━━━━"]
        for m in meanings[:2]:
            pos = m.get("partOfSpeech", "")
            defn = m.get("definitions", [{}])[0].get("definition", "")
            ex = m.get("definitions", [{}])[0].get("example", "")
            lines.append(f"*{pos}:* {defn}")
            if ex:
                lines.append(f"_Example: {ex}_")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━" + footer())
        await wait.edit_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)
    else:
        await wait.edit_text(f"❌ '{word}' හමු නොවිණී!" + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /cinfo  — Country Info
# ══════════════════════════════════════════
async def cinfo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    country = " ".join(ctx.args)
    if not country:
        await update.message.reply_text(
            f"⚠️ රටේ නම ඇතුළත් කරන්න!\n`{config.PREFIX}cinfo Sri Lanka`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    wait = await update.message.reply_text("🌍 *Country info සොයමින்...*", parse_mode=ParseMode.MARKDOWN)
    d = await _get(f"https://restcountries.com/v3.1/name/{country}")

    if d and isinstance(d, list):
        c = d[0]
        name = c["name"]["common"]
        capital = c.get("capital", ["N/A"])[0]
        region = c.get("region", "N/A")
        pop = f"{c.get('population', 0):,}"
        langs = ", ".join(c.get("languages", {}).values()) or "N/A"
        flag = c.get("flag", "")
        currencies = ", ".join(v["name"] for v in c.get("currencies", {}).values()) or "N/A"
        text = (
            f"{flag} *{name}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏛️ *Capital:* {capital}\n"
            f"🌍 *Region:* {region}\n"
            f"👥 *Population:* {pop}\n"
            f"🗣️ *Languages:* {langs}\n"
            f"💰 *Currency:* {currencies}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
            + footer()
        )
        await wait.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await wait.edit_text(f"❌ '{country}' සොයා ගැනීමට නොහැකිය!" + footer(), parse_mode=ParseMode.MARKDOWN)
    ctx.application.create_task(auto_delete(wait))


# ══════════════════════════════════════════
# /ss  — Website Screenshot
# ══════════════════════════════════════════
async def screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = " ".join(ctx.args)
    if not url or not url.startswith("http"):
        await update.message.reply_text(
            f"⚠️ URL ඇතුළත් කරන්න!\n`{config.PREFIX}ss https://google.com`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        return

    await update.effective_chat.send_action(ChatAction.UPLOAD_PHOTO)
    wait = await update.message.reply_text("📸 *Screenshot ගනිමින்...*", parse_mode=ParseMode.MARKDOWN)

    ss_url = f"https://image.thum.io/get/width/1280/crop/800/{url}"
    data = await _get_bytes(ss_url)

    if data:
        await wait.delete()
        await update.message.reply_photo(
            photo=io.BytesIO(data),
            caption=f"📸 *Screenshot:* `{url}`" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await wait.edit_text("❌ Screenshot ගැනීමට නොහැකිය!" + footer(), parse_mode=ParseMode.MARKDOWN)


def register(app: Application):
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler(["translate", "trt"], translate))
    app.add_handler(CommandHandler("tts", tts))
    app.add_handler(CommandHandler("define", define))
    app.add_handler(CommandHandler("cinfo", cinfo))
    app.add_handler(CommandHandler(["ss", "screenshot"], screenshot))
