from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Union, Optional

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlmodel import select

from core.db.database import get_session
from core.db.models import TelegramIDDB
from bot.forms.states.registrasi_account import FormRegistrasiAccount


async def get_user_id(session_db, chat_id: int) -> dict:
    stmt = select(TelegramIDDB).where(TelegramIDDB.telegram_id == chat_id)
    result = await session_db.execute(stmt)
    user = result.scalars().one_or_none()
    return user.dict() if user else {}


async def check_account(session_db, event: Union[Message, CallbackQuery], state: FSMContext) -> Optional[dict]:
    if not getattr(event, "from_user", None):
        return None

    telegram_id = event.from_user.id
    user_data = await get_user_id(session_db, telegram_id)
    if not user_data:
        return None

    now = datetime.now()
    time_threshold = now - relativedelta(months=3)
    if user_data.get("verified_at") and user_data["verified_at"] > time_threshold:
        return user_data

    await state.update_data(
        telegram_id=telegram_id,
        first_name=event.from_user.first_name,
        last_name=event.from_user.last_name,
        username=event.from_user.username
    )
    await state.set_state(FormRegistrasiAccount.nik)

    nik_question=(
        "Bot memerlukan verifikasi akun setiap 3 bulan.\n"
        "Hanya 2 langkah untuk verifikasi.\n\n"
        "🔆 Masukkan NIK Anda ..."
    )

    if isinstance(event, CallbackQuery):
        try:
            await event.message.delete()
        except Exception:
            pass

        await event.bot.send_message(chat_id=event.from_user.id, text=nik_question)
    else:
        await event.answer(nik_question)
