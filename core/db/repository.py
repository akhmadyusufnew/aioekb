from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Union

from aiogram.types import Message, CallbackQuery, ContentType, ChatMemberUpdated

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, Session
from sqlalchemy.orm.exc import MultipleResultsFound

from .database import get_session
from .models import LogChatDB, TelegramIDDB, JadwalShiftDB


from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Union
from aiogram.types import Message, CallbackQuery, ContentType


async def log_telegram_event(session, event):
    log = LogChatDB()

    if isinstance(event, Message):
        telegram_date = event.edit_date or event.date
        if isinstance(telegram_date, (int, float)):
            log.telegram_date = datetime.fromtimestamp(telegram_date)
        else:
            log.telegram_date = telegram_date

        log.chat_type = event.chat.type
        log.chat_title = event.chat.title
        log.chat_id = event.chat.id
        log.message_id = event.message_id

        if event.from_user:
            log.from_id = event.from_user.id
            log.from_first_name = event.from_user.first_name
            log.from_last_name = event.from_user.last_name
            log.from_username = event.from_user.username

        log.message_text = event.text or event.caption

        if event.photo:
            best_photo = max(event.photo, key=lambda x: x.file_size or 0)
            log.content_type = "photo"
            log.file_id = best_photo.file_id
        elif event.document:
            log.content_type = "document"
            log.file_id = event.document.file_id
        elif event.audio:
            log.content_type = "audio"
            log.file_id = event.audio.file_id
        elif event.video:
            log.content_type = "video"
            log.file_id = event.video.file_id
        elif event.sticker:
            log.content_type = "sticker"
            log.file_id = event.sticker.file_id
        elif event.voice:
            log.content_type = "voice"
            log.file_id = event.voice.file_id
        else:
            log.content_type = "text"

    elif isinstance(event, CallbackQuery):
        telegram_date = getattr(event, "date", None) or (event.message.date if event.message else None)
        if isinstance(telegram_date, (int, float)):
            log.telegram_date = datetime.fromtimestamp(telegram_date)
        else:
            log.telegram_date = telegram_date

        log.chat_type = event.message.chat.type if event.message else None
        log.chat_id = event.message.chat.id if event.message else None
        log.message_id = event.message.message_id if event.message else None

        if event.from_user:
            log.from_id = event.from_user.id
            log.from_first_name = event.from_user.first_name
            log.from_last_name = event.from_user.last_name
            log.from_username = event.from_user.username

        log.message_text = event.data
        log.content_type = "CallbackQuery"

    elif isinstance(event, ChatMemberUpdated):
        log.telegram_date = event.date

        log.chat_type = event.chat.type
        log.chat_title = event.chat.title
        log.chat_id = event.chat.id

        if event.from_user:
            log.from_id = event.from_user.id
            log.from_first_name = event.from_user.first_name
            log.from_last_name = event.from_user.last_name
            log.from_username = event.from_user.username

        log.message_text = f"new_chat_member (id: {event.new_chat_member.user.id}, first_name: {event.new_chat_member.user.first_name}, last_name: {event.new_chat_member.user.last_name}, username: {event.new_chat_member.user.username})"

        log.content_type = "ChatMemberUpdated"

    session.add(log)
    await session.commit()


# ------------------- GET USER NIK -------------------
async def get_user_nik(nik: int):
    """
    Ambil user dari TelegramIDDB berdasarkan NIK.
    """
    stmt = select(TelegramIDDB).where(TelegramIDDB.nik == nik)

    async with get_session() as db:
        result = await db.execute(stmt)
        try:
            user = result.scalar_one_or_none()
        except MultipleResultsFound:
            return {}

        return user.dict() if user else {}


# ------------------- JADWAL SHIFT SAYA -------------------
async def get_jadwal_shift_saya(session_db, nik: str):
    """
    Ambil jadwal shift untuk user tertentu berdasarkan NIK (periode bulan ini).
    """
    periode = datetime.now().strftime("%y%m")

    stmt = (
        select(JadwalShiftDB)
        .where(JadwalShiftDB.nik == nik, JadwalShiftDB.periode == periode)
        .limit(1)
    )

    result = await session_db.execute(stmt)
    user = result.scalars().first()
    return user.dict() if user else {}


# ------------------- JADWAL SHIFT PER TANGGAL -------------------
async def get_jadwal_shift_tgl(session_db, yymmdd: str):
    periode = yymmdd[:4]
    day = yymmdd[4:].zfill(2)
    column_day = f"s_{day}"

    stmt = (
        select(
            JadwalShiftDB.nama_personil,
            JadwalShiftDB.kd_div,
            getattr(JadwalShiftDB, column_day)
        )
        .where(JadwalShiftDB.periode == periode)
        .order_by(
            getattr(JadwalShiftDB, column_day),
            JadwalShiftDB.jabatan,
            JadwalShiftDB.nama_personil
        )
    )
    result = await session_db.execute(stmt)
    return result.mappings().all()
