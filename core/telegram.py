import logging

from typing import Optional

from aiogram import Bot
from aiogram.types import Message, ContentType

from core.config import settings


def extract_file_id(message: Message) -> Optional[str]:
    if message.content_type == ContentType.PHOTO:
        return message.photo[-1].file_id

    if message.content_type == ContentType.DOCUMENT:
        return message.document.file_id

    if message.content_type == ContentType.VIDEO:
        return message.video.file_id
    
    return None


async def safe_delete_message(
    message: Message | None = None,
    *,
    bot: Bot | None = None,
    chat_id: int | None = None,
    message_id: int | None = None,
):
    try:
        if message:
            await message.delete()
        elif bot and chat_id and message_id:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

async def handle_exception(message: Message, bot, e: Exception):
    logging.exception("Unhandled exception")

    try:
        await bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=str(e)
        )
    except Exception:
        logging.exception("Failed to notify admin")

    await message.answer("server gagal memproses, silakan kirim ulang command /start")