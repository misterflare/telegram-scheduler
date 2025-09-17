from typing import List, Optional

from telegram import (
    Bot,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)

from .config import settings

_bot: Optional[Bot] = None
_bot_token: Optional[str] = None


def get_bot(token: Optional[str] = None) -> Bot:
    global _bot, _bot_token
    desired = token or settings.TELEGRAM_BOT_TOKEN
    if _bot is None or (_bot_token != desired):
        _bot = Bot(token=desired)
        _bot_token = desired
    return _bot


def _build_keyboard(buttons: Optional[List[dict]]) -> Optional[InlineKeyboardMarkup]:
    if not buttons:
        return None
    row = [
        InlineKeyboardButton(btn["title"], url=btn["url"])
        for btn in buttons
        if btn.get("title") and btn.get("url")
    ]
    if not row:
        return None
    return InlineKeyboardMarkup([row])


async def send_post(
    text: Optional[str],
    buttons: Optional[List[dict]],
    media: Optional[List[dict]],
    chat_id: str,
    token: Optional[str] = None,
) -> None:
    bot = get_bot(token)
    reply_markup = _build_keyboard(buttons)
    message_text = text if text else (" " if reply_markup else "")

    attachments = [item for item in media or [] if item.get("path")]

    if len(attachments) > 1:
        media_group = []
        for item in attachments:
            path = item["path"]
            file = FSInputFile(path)
            media_type = item.get("type")
            if media_type == "photo":
                media_group.append(InputMediaPhoto(media=file))
            elif media_type == "video":
                media_group.append(InputMediaVideo(media=file))
            else:
                media_group.append(InputMediaDocument(media=file))
        if media_group:
            await bot.send_media_group(chat_id=chat_id, media=media_group)
            if message_text or reply_markup:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
        return

    if len(attachments) == 1:
        item = attachments[0]
        path = item["path"]
        media_type = item.get("type")
        file = FSInputFile(path)
        caption = text or None

        if media_type == "photo":
            await bot.send_photo(
                chat_id=chat_id,
                photo=file,
                caption=caption,
                reply_markup=reply_markup,
            )
            return
        if media_type == "video":
            await bot.send_video(
                chat_id=chat_id,
                video=file,
                caption=caption,
                reply_markup=reply_markup,
            )
            return
        if media_type == "document":
            await bot.send_document(
                chat_id=chat_id,
                document=file,
                caption=caption,
                reply_markup=reply_markup,
            )
            return

    await bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
