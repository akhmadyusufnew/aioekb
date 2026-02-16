import json
from datetime import datetime

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlmodel import select

from core.account import check_account
from core.config import settings
from core.db.database import get_session
from core.db.models import TelegramIDDB
from core.menus import menu_main
from core.telegram import handle_exception

from bot.forms.states import FormRegistrasiAccount


router = Router()


@router.message(FormRegistrasiAccount.nik)
async def input_nik(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        if not message.text:
            await message.answer("🔆 Balasan harus berupa NIK.")
            return

        nik = message.text.strip()

        if not nik.isdigit() or len(nik) != 10:
            await message.answer("🔆 NIK tidak sesuai format.")
            return

        await state.update_data(nik=nik)
        await state.set_state(FormRegistrasiAccount.nama_lengkap)

        await message.answer("🔆 Masukan NAMA LENGKAP sesuai ESS...")

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormRegistrasiAccount.nama_lengkap)
async def input_nama_lengkap(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        if not message.text:
            await message.answer("🔆 Balasan tidak sesuai format ...")
            return

        await state.update_data(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            nama_lengkap=message.text.strip().upper(),
            )

        data_state = await state.get_data()

        stmt = select(TelegramIDDB).where(
            TelegramIDDB.telegram_id == data_state.get("telegram_id"),
            TelegramIDDB.nik == data_state.get("nik"),
            TelegramIDDB.nama_lengkap == data_state.get("nama_lengkap")
            )

        async with get_session() as session_db:
            user = (await session_db.execute(stmt)).scalar_one_or_none()

            if not user:
                await message.reply("🫢 Verifikasi gagal. Pastikan NIK dan NAMA LENGKAP yang di kirim sesuai.")
                await state.set_state(FormRegistrasiAccount.nik)
                await message.answer("🔆 Masukkan NIK Anda ...")

                stmt2 = select(
                    TelegramIDDB.telegram_id,
                    TelegramIDDB.nik,
                    TelegramIDDB.nama_lengkap,
                    ).where(
                        TelegramIDDB.telegram_id == data_state.get("telegram_id")
                    )
                result = await session_db.execute(stmt2)
                user_dict = dict(result.mappings().first() or {})

                admin_text = (
                    f"📌 Verifikasi ulang gagal"
                    f"\n\n"
                    f"Data registrasi ulang\n<pre>{json.dumps(data_state, indent=4)}</pre>"
                    f"\n\n"
                    f"Data pada system\n<pre>{json.dumps(user_dict, indent=4, ensure_ascii=False)}</pre>"
                )
                await bot.send_message(chat_id=settings.ADMIN_ID, text=admin_text)
                return

            user.first_name = data_state.get("first_name")
            user.last_name = data_state.get("last_name")
            user.username = data_state.get("username")
            user.nama_lengkap = data_state.get("nama_lengkap")
            user.verified_at = datetime.now()
            session_db.add(user)

            await state.clear()

            user_id = await check_account(session_db, message, state)
            if user_id:          
                await message.answer(
                    text="✅ Verifikasi ulang berhasil.",
                    reply_markup=menu_main(user_id)
                )
            
            else:
                await message.answer(
                    text=f"⚠️ Verifikasi ulang gagal, hubungi <a href='tg://user?id={settings.ADMIN_ID}'>Admin</a>.",
                )

    except Exception as e:
        await handle_exception(message, bot, e)
