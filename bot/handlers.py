import logging
import sys
from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from core.config import settings
from core.menus import (
    MenuMainCB, MenuJadwalShiftCB, MenuFormCB, MenuLinkCB,
    menu_main, menu_jadwal_shift, menu_form, menu_link
)
from core.account import check_account
from core.db.database import get_session
from core.db.repository import log_telegram_event
from core.jadwal_shift import get_jadwal_tgl, get_jadwal_tgl_aktif, get_jadwal_saya
from core.telegram import safe_delete_message, handle_exception

from bot.forms.states import (
    FormBackupRestore, FormRestoreData,
    FormStartPOSReplikasi, FormTutupPOSReplikasi,
    FormStartPOSSiaga, FormTutupPOSSiaga
)
from bot.forms.handlers.handler_backup_restore import txt_form as txt_backuprestore
from bot.forms.handlers.handler_restore_data import txt_form as txt_restore_data
from bot.forms.handlers.handler_start_posreplikasi import txt_form as txt_startposreplikasi
from bot.forms.handlers.handler_tutup_posreplikasi import txt_form as txt_tutupposreplikasi
from bot.forms.handlers.handler_start_possiaga import txt_form as txt_startpossiaga
from bot.forms.handlers.handler_tutup_possiaga import txt_form as txt_tutuppossiaga

from bot.forms.questions import (
    BaseFormQuestion,
    BackupRestoreFormQuestion,
    RestoreDataFormQuestion,
    StartPOSReplikasiFormQuestion,
    StartPOSSiagaFormQuestion
)


async def _safe_edit_or_reply(session_db, callback, text_message, reply_markup):
    """Coba edit pesan, fallback ke answer jika gagal"""
    try:
        msg = await callback.message.edit_text(text_message, reply_markup=reply_markup)
        await log_telegram_event(session_db, msg)
    except Exception:
        msg = await callback.message.answer(text_message, reply_markup=reply_markup)
        await log_telegram_event(session_db, msg)


async def send_menu_main(session_db, event):
    """Tampilkan menu utama"""
    text = "🏠 <b>Main Menu</b>"

    if isinstance(event, CallbackQuery):
        await event.answer(reply_markup=ReplyKeyboardRemove())
        try:
            msg = await event.message.edit_text(text, reply_markup=menu_main())
            await log_telegram_event(session_db, msg)
        except Exception:
            msg = await event.message.answer(text, reply_markup=menu_main())
            await log_telegram_event(session_db, msg)
        return

    if isinstance(event, Message):
        await safe_delete_message(event)
        temp_msg = await event.answer(text="🌎", reply_markup=ReplyKeyboardRemove())
        await log_telegram_event(session_db, temp_msg)
        await safe_delete_message(temp_msg)
        temp_msg2 = await event.answer(text, reply_markup=menu_main())
        await log_telegram_event(session_db, temp_msg2)
        return


router = Router()


# ------------------ Handlers ------------------ #

@router.message(F.chat.type == "private", CommandStart())
async def command_start(message: Message, bot: Bot, state: FSMContext):
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)
            user_id = await check_account(session_db, message, state)
            if not user_id:
                return
            await send_menu_main(session_db, message)
    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(F.chat.type == "private")
async def private_any(message: Message, bot: Bot, state: FSMContext):
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)
            user_id = await check_account(session_db, message, state)
            if not user_id:
                return
            await send_menu_main(session_db, message)
    except Exception as e:
        await handle_exception(message, bot, e)


# ------------------ Callback Handlers ------------------ #

@router.callback_query(F.chat.type == "private", MenuMainCB.filter())
async def menu_main_handler(callback: CallbackQuery, callback_data: MenuMainCB, bot: Bot, state: FSMContext):
    await callback.answer()
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, callback)
            user_id = await check_account(session_db, callback, state)
            if not user_id:
                return

            menu = callback_data.menu

            if menu == "menu_main":
                await send_menu_main(session_db, callback)

            elif menu == "menu_jadwal_shift":
                text_message = await get_jadwal_tgl_aktif(session_db)
                await _safe_edit_or_reply(session_db, callback, text_message, menu_jadwal_shift())

            elif menu == "menu_form":
                await _safe_edit_or_reply(session_db, callback, "📝 <b>Form Laporan</b>", menu_form())

            elif menu == "pw_mysqladmin":
                today_date = datetime.now().strftime("%Y%m%d")
                dd = datetime.now().strftime("%d")
                xor_result = (int(today_date) * int(dd)) ^ 987654321
                await _safe_edit_or_reply(
                    session_db, callback,
                    f"🏠 <b>Main Menu</b>\n\n🔐 <code>{xor_result}</code> {datetime.now().strftime('%S%M%H')}",
                    menu_main()
                )

            elif menu == "profile":
                profile_txt = (
                    "<pre>\n"
                    f"{'Nama'.ljust(15)}: {user_id.get('nama_lengkap')}\n"
                    f"{'NIK'.ljust(15)}: {user_id.get('nik')}\n"
                    f"{'Telegram ID'.ljust(15)}: {user_id.get('telegram_id')}\n"
                    f"{'Name'.ljust(15)}: {user_id.get('first_name', '')}"
                    f"{' ' + user_id.get('last_name') if user_id.get('last_name') else ''}\n"
                    f"{'Username'.ljust(15)}: {user_id.get('username') or ''}\n"
                    f"{'Last Verify'.ljust(15)}: {user_id.get('verified_at', '')}\n\n"
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"{sys.version}\n"
                    "</pre>"
                )
                await _safe_edit_or_reply(session_db, callback, f"👤 <b>Profile Saya</b>\n\n{profile_txt}", menu_main())

            elif menu == "menu_link":
                await _safe_edit_or_reply(session_db, callback, "📝 <b>Links</b>", menu_link())

            elif menu == "exit":
                await safe_delete_message(callback.message)

            else:
                await send_menu_main(session_db, callback)
    except Exception as e:
        await handle_exception(callback.message, bot, e)


@router.callback_query(F.chat.type == "private", MenuJadwalShiftCB.filter())
async def menu_jadwal_shift_handler(callback: CallbackQuery, callback_data: MenuJadwalShiftCB, bot: Bot, state: FSMContext):
    await callback.answer()
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, callback)
            user_id = await check_account(session_db, callback, state)
            if not user_id:
                return

            menu = callback_data.menu
            now = datetime.now()
            tanggal_mapping = {
                "hari_ini": 0,
                "besok": 1,
                "lusa": 2,
                "lusa_1": 4,
                "kemarin": -1,
                "kemarin_1": -2
            }

            if menu == "on_shift":
                text_message = await get_jadwal_tgl_aktif(session_db)
            elif menu == "saya":
                text_message = await get_jadwal_saya(session_db, user_id.get("nik"))
            elif menu in tanggal_mapping:
                tanggal = now + timedelta(days=tanggal_mapping[menu])
                label = "Jadwal Shift" if "lusa_1" in menu or "kemarin_1" in menu else f"Jadwal {menu.replace('_', ' ').title()}"
                text_message = await get_jadwal_tgl(session_db, tanggal, label)
            elif menu == "menu_main":
                await send_menu_main(session_db, callback)
                return
            else:
                await send_menu_main(session_db, callback)
                return

            await _safe_edit_or_reply(session_db, callback, text_message, menu_jadwal_shift())
    except Exception as e:
        await handle_exception(callback.message, bot, e)


@router.callback_query(F.chat.type == "private", MenuFormCB.filter())
async def menu_form_handler(callback: CallbackQuery, callback_data: MenuFormCB, bot: Bot, state: FSMContext):
    await callback.answer()
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, callback)
            user_id = await check_account(session_db, callback, state)
            if not user_id:
                return

            menu = callback_data.menu
            form_mapping = {
                "backup_restore": (FormBackupRestore, txt_backuprestore, BackupRestoreFormQuestion),
                "restore_data": (FormRestoreData, txt_restore_data, RestoreDataFormQuestion),
                "start_pos_replikasi": (FormStartPOSReplikasi, txt_startposreplikasi, StartPOSReplikasiFormQuestion),
                "tutup_pos_replikasi": (FormTutupPOSReplikasi, txt_tutupposreplikasi, BaseFormQuestion),
                "start_pos_siaga": (FormStartPOSSiaga, txt_startpossiaga, StartPOSSiagaFormQuestion),
                "tutup_pos_siaga": (FormTutupPOSSiaga, txt_tutuppossiaga, BaseFormQuestion)
            }

            if menu in form_mapping:
                await safe_delete_message(callback.message)

                form_state, txt_func, question_cls = form_mapping[menu]
                await state.set_state(form_state.kdtk)

                text_message = await txt_func(state)
                msg = await callback.message.answer(text_message)
                await log_telegram_event(session_db, msg)

                await state.update_data(
                    pelaksana_nik=user_id.get("nik", ""),
                    pelaksana_nama=user_id.get("nama_lengkap", ""),
                    form_view_message_id=msg.message_id
                )

                await question_cls(bot, state, session_db).q_kdtk(callback.message)
            elif menu == "menu_main":
                await send_menu_main(session_db, callback)
            else:
                await send_menu_main(session_db, callback)
    except Exception as e:
        await handle_exception(callback.message, bot, e)


@router.callback_query(F.chat.type == "private", MenuLinkCB.filter())
async def menu_link_handler(callback: CallbackQuery, callback_data: MenuLinkCB, bot: Bot, state: FSMContext):
    await callback.answer()
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, callback)
            user_id = await check_account(session_db, callback, state)
            if not user_id:
                return
            await send_menu_main(session_db, callback)
    except Exception as e:
        await handle_exception(callback.message, bot, e)
