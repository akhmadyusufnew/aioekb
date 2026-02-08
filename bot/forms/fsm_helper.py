import logging
import secrets
import string
from datetime import datetime

from pathlib import Path
from typing import Optional

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.config import settings
from core.menus import menu_main

from core.telegram import safe_delete_message


def generate_id_work(data_state: dict, prefix: str = "Z") -> str:
    cabang = str(data_state.get("cabang") or "G000")
    station = data_state.get("station")

    str2 = cabang[1:4].ljust(3, "X")
    str3 = data_state.get("kdtk")
    str4 = (
        data_state["datetime_start"].strftime("%y%m%d%H%M")
        if data_state.get("datetime_start")
        else data_state["datetime_end"].strftime("%y%m%d%H%M")
        if data_state.get("datetime_end")
        else datetime.now().strftime("%y%m%d%H%M")
    )
    str5 = f"{int(station):02d}" if str(station).isdigit() else "00"
    str6 = "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(2)
    )

    return f"{prefix}{str2}{str3}{str4}{str5}{str6}"



async def delete_file(file_path: Path):
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        logging.exception("Failed to delete file %s", file_path)


async def send_file_preview(bot: Bot, message: Message, file_id: str, reply_to_message_id: Optional[int]) -> Message:
    try:
        if message.content_type == ContentType.PHOTO:
            return await bot.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
                reply_to_message_id=reply_to_message_id,
            )
        
        return await bot.send_document(
            chat_id=message.chat.id,
            document=file_id,
            reply_to_message_id=reply_to_message_id,
        )
    except TelegramAPIError:
        if message.content_type == ContentType.PHOTO:
            return await bot.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
            )
        
        return await bot.send_document(
            chat_id=message.chat.id,
            document=file_id,
        )


async def download_and_save_file(bot: Bot, file_id: str, save_path: Path) -> Path:
    # Pastikan folder ada
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Ambil info file dari Telegram
    tg_file = await bot.get_file(file_id)
    tg_file_path = tg_file.file_path

    # Ambil ekstensi asli
    file_ext = Path(tg_file_path).suffix or ""

    # Nama file akhir (id_work_num.ext)
    final_path = save_path.with_suffix(file_ext)

    # Download file
    await bot.download_file(
        tg_file_path,
        destination=final_path
    )

    return final_path


async def handle_cancel_form(message: Message, bot: Bot, state: FSMContext):
    data_state = await state.get_data()

    for item in data_state.get("files", []):
        msg_id = item.get("message_id")
        if msg_id:
            await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=msg_id)
        
    for key in ("form_view_message_id", "form_write_message_id"):
        if data_state.get(key):
            await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=data_state[key])
    
    await state.clear()
    await message.answer("🗑 Di batalkan.", reply_markup=menu_main())
