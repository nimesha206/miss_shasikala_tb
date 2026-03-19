"""
Plugin: Sticker & Image
Commands: sticker/s, attp, removebg, simage
"""

import io
import asyncio
import aiohttp

from telegram import Update, Sticker
from telegram.ext import CommandHandler, ContextTypes, Application
from telegram.constants import ParseMode, ChatAction

import config
from helpers import footer, auto_delete


async def _download(url: str) -> bytes | None:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as s:
            async with s.get(url) as r:
                return await r.read()
    except Exception:
        return None


# ══════════════════════════════════════════
# /sticker  /s  — Image to Sticker
# ══════════════════════════════════════════
async def sticker_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from PIL import Image

    # Get image — from reply or direct photo
    photo = None
    if update.message.reply_to_message:
        if update.message.reply_to_message.photo:
            photo = update.message.reply_to_message.photo[-1]
        elif update.message.reply_to_message.sticker and not update.message.reply_to_message.sticker.is_animated:
            # sticker to image to sticker
            photo = update.message.reply_to_message.sticker
    elif update.message.photo:
        photo = update.message.photo[-1]

    if not photo:
        msg = await update.message.reply_text(
            f"⚠️ ෆොටෝ එකක් reply කරන්න හෝ ෆොටෝ සමඟ `{config.PREFIX}s` ලියන්න!"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    await update.effective_chat.send_action(ChatAction.CHOOSE_STICKER)
    wait = await update.message.reply_text("🎨 *Sticker හදමින்...*", parse_mode=ParseMode.MARKDOWN)

    try:
        file = await ctx.bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await file.download_to_memory(buf)
        buf.seek(0)

        # Resize to 512x512
        img = Image.open(buf).convert("RGBA")
        img.thumbnail((512, 512))
        out = io.BytesIO()
        img.save(out, format="WEBP")
        out.seek(0)

        await wait.delete()
        await update.message.reply_sticker(sticker=out)
    except Exception as e:
        await wait.edit_text(f"❌ Sticker create ව්‍යර්ථ: {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════
# /attp  — Text to Sticker (animated text art)
# ══════════════════════════════════════════
async def attp(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from PIL import Image, ImageDraw, ImageFont
    import colorsys, math

    text = " ".join(ctx.args)
    if not text:
        msg = await update.message.reply_text(
            f"⚠️ Text ඇතුළත් කරන්න!\n`{config.PREFIX}attp Hello World`"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    wait = await update.message.reply_text("✨ *Text sticker හදමින்...*", parse_mode=ParseMode.MARKDOWN)

    try:
        # Create colorful text image
        W, H = 512, 512
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to use a nice font, fallback to default
        font_size = max(40, int(W * 0.12))
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2
        y = (H - th) // 2

        # Gradient rainbow letters
        colors = ["#FF6B6B", "#FFE66D", "#4ECDC4", "#A8E6CF", "#FF8B94", "#AA96DA"]
        for i, ch in enumerate(text):
            color = colors[i % len(colors)]
            cbbox = draw.textbbox((0, 0), ch, font=font)
            cw = cbbox[2] - cbbox[0]
            draw.text((x, y), ch, font=font, fill=color, stroke_width=3, stroke_fill="black")
            x += cw

        out = io.BytesIO()
        img.save(out, format="WEBP")
        out.seek(0)
        await wait.delete()
        await update.message.reply_sticker(sticker=out)
    except Exception as e:
        await wait.edit_text(f"❌ ATTP ව්‍යර්ථ: {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


# ══════════════════════════════════════════
# /removebg  — Remove Background
# ══════════════════════════════════════════
async def removebg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    photo = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1]
    elif update.message.photo:
        photo = update.message.photo[-1]

    if not photo:
        msg = await update.message.reply_text(
            f"⚠️ ෆොටෝ reply කරන්න හෝ ෆොටෝ සමඟ `{config.PREFIX}removebg` ලියන්න!"
            + footer(), parse_mode=ParseMode.MARKDOWN
        )
        ctx.application.create_task(auto_delete(msg))
        return

    wait = await update.message.reply_text("✂️ *Background remove කරමින்...*", parse_mode=ParseMode.MARKDOWN)

    try:
        from rembg import remove
        from PIL import Image

        file = await ctx.bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await file.download_to_memory(buf)
        buf.seek(0)

        result = await asyncio.to_thread(remove, buf.read())
        out = io.BytesIO(result)
        out.name = "nobg.png"

        await wait.delete()
        await update.message.reply_document(
            document=out,
            caption=f"✅ *Background Removed!*" + footer(),
            parse_mode=ParseMode.MARKDOWN,
        )
    except ImportError:
        # rembg not installed — use free API
        try:
            file = await ctx.bot.get_file(photo.file_id)
            buf = io.BytesIO()
            await file.download_to_memory(buf)
            buf.seek(0)

            async with aiohttp.ClientSession() as s:
                form = aiohttp.FormData()
                form.add_field("image_file", buf, filename="img.png", content_type="image/png")
                async with s.post("https://api.remove.bg/v1.0/removebg", data=form,
                                  headers={"X-Api-Key": "free_trial"}, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status == 200:
                        data = await r.read()
                        out = io.BytesIO(data)
                        out.name = "nobg.png"
                        await wait.delete()
                        await update.message.reply_document(document=out,
                            caption="✅ *Background Removed!*" + footer(), parse_mode=ParseMode.MARKDOWN)
                    else:
                        await wait.edit_text("❌ Remove.bg API limit. `pip install rembg` install කරන්න!" + footer(),
                                            parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await wait.edit_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await wait.edit_text(f"❌ {e}" + footer(), parse_mode=ParseMode.MARKDOWN)


def register(app: Application):
    app.add_handler(CommandHandler(["sticker", "s"], sticker_cmd))
    app.add_handler(CommandHandler("attp", attp))
    app.add_handler(CommandHandler(["removebg", "rmbg"], removebg))
