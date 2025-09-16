import asyncio
from typing import List, Optional
from telegram import Bot, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup
from .config import settings

_bot: Optional[Bot] = None

def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    return _bot

async def send_post(text: Optional[str], buttons: Optional[List[dict]], media: Optional[List[dict]], chat_id: str):
    bot = get_bot()

    # Build inline keyboard
    reply_markup = None
    if buttons:
        keyboard = [[InlineKeyboardButton(b["title"], url=b["url"]) for b in buttons]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # Decide how to send based on media count
    if media and len(media) > 1:
        group = []
        for m in media:
            if m["type"] == "photo":
                group.append(InputMediaPhoto(media=open(m["path"], "rb"), caption=None))
            elif m["type"] == "video":
                group.append(InputMediaVideo(media=open(m["path"], "rb"), caption=None))
        # Telegram forbids buttons on media groups; we optionally send text after.
        await asyncio.to_thread(bot.send_media_group, chat_id=chat_id, media=group)
        if text or buttons:
            await asyncio.to_thread(bot.send_message, chat_id=chat_id, text=text or "", reply_markup=reply_markup, disable_web_page_preview=True)
    elif media and len(media) == 1:
        m = media[0]
        if m["type"] == "photo":
            await asyncio.to_thread(bot.send_photo, chat_id=chat_id, photo=open(m["path"], "rb"), caption=text or None, reply_markup=reply_markup)
        elif m["type"] == "video":
            await asyncio.to_thread(bot.send_video, chat_id=chat_id, video=open(m["path"], "rb"), caption=text or None, reply_markup=reply_markup)
        elif m["type"] == "document":
            await asyncio.to_thread(bot.send_document, chat_id=chat_id, document=open(m["path"], "rb"), caption=text or None, reply_markup=reply_markup)
        else:
            await asyncio.to_thread(bot.send_message, chat_id=chat_id, text=text or "", reply_markup=reply_markup)
    else:
        await asyncio.to_thread(bot.send_message, chat_id=chat_id, text=text or "", reply_markup=reply_markup, disable_web_page_preview=True)
