from typing import Any, BinaryIO, List, Optional, Tuple

from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from telegram.request import HTTPXRequest

try:
    from telegram import FSInputFile  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    FSInputFile = None  # type: ignore[assignment]

from .config import settings

_bot: Optional[Bot] = None
_bot_token: Optional[str] = None
_request: Optional[HTTPXRequest] = None


def _get_request() -> HTTPXRequest:
    global _request
    if _request is None:
        _request = HTTPXRequest(
            connect_timeout=20.0,
            read_timeout=60.0,
            write_timeout=60.0,
            pool_timeout=30.0,
            connection_pool_size=20,
        )
    return _request


def get_bot(token: Optional[str] = None) -> Bot:
    global _bot, _bot_token
    desired = token or settings.TELEGRAM_BOT_TOKEN
    if _bot is None or (_bot_token != desired):
        _bot = Bot(token=desired, request=_get_request())
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


def _wrap_file(path: str) -> Tuple[Any, Optional[BinaryIO]]:
    if FSInputFile is not None:
        return FSInputFile(path), None
    file_handle = open(path, "rb")
    return file_handle, file_handle


def _cleanup_files(files: List[BinaryIO]) -> None:
    for file in files:
        try:
            file.close()
        except Exception:
            pass


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
        cleanup: List[BinaryIO] = []
        try:
            for item in attachments:
                path = item["path"]
                file_obj, to_close = _wrap_file(path)
                if to_close is not None:
                    cleanup.append(to_close)
                media_type = item.get("type")
                if media_type == "photo":
                    media_group.append(InputMediaPhoto(media=file_obj))
                elif media_type == "video":
                    media_group.append(InputMediaVideo(media=file_obj))
                else:
                    media_group.append(InputMediaDocument(media=file_obj))
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
        finally:
            _cleanup_files(cleanup)

    if len(attachments) == 1:
        item = attachments[0]
        path = item["path"]
        media_type = item.get("type")
        file_obj, to_close = _wrap_file(path)
        caption = text or None

        try:
            if media_type == "photo":
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=file_obj,
                    caption=caption,
                    reply_markup=reply_markup,
                )
                return
            if media_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=file_obj,
                    caption=caption,
                    reply_markup=reply_markup,
                )
                return
            if media_type == "document":
                await bot.send_document(
                    chat_id=chat_id,
                    document=file_obj,
                    caption=caption,
                    reply_markup=reply_markup,
                )
                return
        finally:
            if to_close is not None:
                _cleanup_files([to_close])

    await bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )