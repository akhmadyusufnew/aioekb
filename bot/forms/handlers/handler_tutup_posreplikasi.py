import logging
import string

from pathlib import Path
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType, FSInputFile, Message

from core.config import settings
from core.db.database import get_session
from core.db.models import SiagadanReplikasiDB
from core.db.repository import log_telegram_event
from core.menus import menu_main

from core.telegram import safe_delete_message, extract_file_id, handle_exception
from bot.forms.validators import verify_kdtk, verify_datetime
from bot.forms.fsm_helper import handle_cancel_form, generate_id_work, send_file_preview, delete_file, download_and_save_file

from bot.forms.states import FormTutupPOSReplikasi
from bot.forms.questions import TutupPOSReplikasiFormQuestion


async def txt_form(state: FSMContext) -> str:
    data_state = await state.get_data()

    cabang = data_state.get('cabang')
    datetime_start = data_state.get('datetime_start')
    datetime_end = data_state.get('datetime_end')

    if not cabang:
        cabang = "G000"

    if datetime_start:
        datetime_start = datetime_start.strftime("%d-%b-%Y ± %H:%M")
    else:
        datetime_start = '-'

    if datetime_end:
        datetime_end = datetime_end.strftime("%d-%b-%Y ± %H:%M")
    else:
        datetime_end = '-'

    string  = f"🍏 #TUTUPREPLIKASI #{cabang[:4]} #{data_state.get('kdtk', '')}\n"
    string += "<pre><code>"
    string += "Pengembalian POS Replikasi\n"
    string += "------------------------------------\n\n"
    string += "No. CO".ljust(12) + f": {data_state.get('nomor_co', '-')}\n"
    string += "Toko".ljust(12) + f": {data_state.get('kdtk', '')}{' - ' + data_state.get('nama_toko') if data_state.get('nama_toko') else ''}\n"
    string += "Cabang".ljust(12) + f": {data_state.get('cabang', '-')}\n"
    string += "Time Selesai".ljust(12) + f": {datetime_end}\n"
    string += "Status".ljust(12) + f": {data_state.get('status', '-')}\n"
    string += "Keterangan".ljust(12) + f": {data_state.get('keterangan', '-')}\n"
    string += "\n"
    string += f"{data_state.get('pelaksana_nama', '-')}\n"
    string += f"{data_state.get('id_work', '-')}\n"
    string += "------------------------------------\n"
    string += f"{datetime.now().replace(microsecond=0)}"
    string += "</code></pre>"
    return string


async def send_txt_form(bot, session_db, message, state):
    text_message = await txt_form(state)

    data_state = await state.get_data()
    form_view_message_id = data_state.get("form_view_message_id")

    if form_view_message_id:
        try:
            msg = await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=form_view_message_id,
                text=text_message
            )
            await log_telegram_event(session_db, msg)

        except Exception:
            msg = await message.answer(text_message)
            await state.update_data(form_view_message_id=msg.message_id)
            await log_telegram_event(session_db, msg)
    else:
        msg = await message.answer(text_message)
        await state.update_data(form_view_message_id=msg.message_id)
        await log_telegram_event(session_db, msg)


router = Router()


@router.message(StateFilter(FormTutupPOSReplikasi), F.text.lower() == "/batal")
async def cancel_form(message: Message, bot: Bot, state: FSMContext):
    await safe_delete_message(message)

    async with get_session() as session_db:
        await log_telegram_event(session_db, message)

    await handle_cancel_form(message, bot, state)


@router.message(FormTutupPOSReplikasi.kdtk)
async def input_kdtk(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            data = await verify_kdtk(message)
            if not data:
                return

            await state.update_data(**data)
            await state.set_state(FormTutupPOSReplikasi.nomor_co)

            await send_txt_form(bot, session_db, message, state)
            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_nomor_co(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.nomor_co)
async def input_nomor_co(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormTutupPOSReplikasi.kdtk)
                await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_kdtk(message)
                return

            if text == "/tidak_ada_nomor_co":
                nomor_co = "-"
            elif raw_text.startswith("2") and len(raw_text) == 10:
                nomor_co = raw_text
            else:
                return

            await state.update_data(nomor_co=nomor_co.upper())
            await state.set_state(FormTutupPOSReplikasi.status)

            await send_txt_form(bot, session_db, message, state)
            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_status(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.status)
async def input_status(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormTutupPOSReplikasi.nomor_co)
                await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_nomor_co(message)
                return

            if len(raw_text) < 6:
                return

            if text.startswith("/berhasil"):
                status = "✅ Berhasil"
            elif text.startswith("/kendala"):
                status = "Kendala"
            else:
                status = raw_text

            await state.update_data(status=status)
            await state.set_state(FormTutupPOSReplikasi.keterangan)

            await send_txt_form(bot, session_db, message, state)
            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_keterangan(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.keterangan)
async def input_keterangan(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormTutupPOSReplikasi.status)
                await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_status(message)
                return

            data_state = await state.get_data()
            status = (data_state.get("status") or "").lower()

            if text.startswith("/selanjutnya") and "berhasil" in status:
                await state.update_data(keterangan="Tidak ada kendala")
            else:
                if len(raw_text) < 10:
                    return
                await state.update_data(keterangan=raw_text)

            await state.set_state(FormTutupPOSReplikasi.lampiran_1)

            await send_txt_form(bot, session_db, message, state)
            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_1(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.lampiran_1)
async def input_lampiran_1(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/kembali"):
                    await state.set_state(FormTutupPOSReplikasi.keterangan)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_keterangan(message)
                    return

                return

            if message.content_type not in (ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO):
                return          

            file_id = extract_file_id(message)
            if not file_id:
                return

            data_state = await state.get_data()

            tmp_msg = await send_file_preview(bot, message, file_id, data_state.get("form_view_message_id"))
            
            files = data_state.get("files", [])
            files = [f for f in files if f.get("num") != 1]
            files.append({
                "num": 1,
                "file_id": file_id,
                "message_id": tmp_msg.message_id,
                "type": message.content_type,
            })

            await state.update_data(files=files)
            await state.set_state(FormTutupPOSReplikasi.lampiran_2)

            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_2(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.lampiran_2)
async def input_lampiran_2(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            data_state = await state.get_data()

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/selanjutnya"):
                    await state.set_state(FormTutupPOSReplikasi.datetime_end)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_datetime_end(message)
                    return

                if text.startswith("/kembali"):
                    files = data_state.get("files", [])

                    file = next((f for f in files if f.get("num") == 1), None)
                    if file:
                        await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=file["message_id"])

                    files = [f for f in files if f.get("num") != 1]
                    await state.update_data(files=files)

                    await state.set_state(FormTutupPOSReplikasi.lampiran_1)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_1(message)
                    return

                return

            if message.content_type not in (ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO):
                return          

            file_id = extract_file_id(message)
            if not file_id:
                return

            tmp_msg = await send_file_preview(bot, message, file_id, data_state.get("form_view_message_id"))

            files = data_state.get("files", [])
            files = [f for f in files if f.get("num") != 2]
            files.append({
                "num": 2,
                "file_id": file_id,
                "message_id": tmp_msg.message_id,
                "type": message.content_type,
            })

            await state.update_data(files=files)        
            await state.set_state(FormTutupPOSReplikasi.lampiran_3)

            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_3(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.lampiran_3)
async def input_lampiran_3(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            data_state = await state.get_data()

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/selanjutnya"):
                    await state.set_state(FormTutupPOSReplikasi.datetime_end)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_datetime_end(message)
                    return

                if text.startswith("/kembali"):
                    files = data_state.get("files", [])

                    file = next((f for f in files if f.get("num") == 2), None)
                    if file:
                        await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=file["message_id"])
                    
                    files = [f for f in files if f.get("num") != 2]
                    await state.update_data(files=files)

                    await state.set_state(FormTutupPOSReplikasi.lampiran_2)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_2(message)
                    return

                return

            if message.content_type not in (ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO):
                return          

            file_id = extract_file_id(message)
            if not file_id:
                return

            tmp_msg = await send_file_preview(bot, message, file_id, data_state.get("form_view_message_id"))

            files = data_state.get("files", [])
            files = [f for f in files if f.get("num") != 3]
            files.append({
                "num": 3,
                "file_id": file_id,
                "message_id": tmp_msg.message_id,
                "type": message.content_type,
            })

            await state.update_data(files=files)        
            await state.set_state(FormTutupPOSReplikasi.lampiran_4)

            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_4(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.lampiran_4)
async def input_lampiran_4(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            data_state = await state.get_data()

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/selanjutnya"):
                    await state.set_state(FormTutupPOSReplikasi.datetime_end)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_datetime_end(message)
                    return

                if text.startswith("/kembali"):
                    files = data_state.get("files", [])

                    file = next((f for f in files if f.get("num") == 3), None)
                    if file:
                        await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=file["message_id"])
                    
                    files = [f for f in files if f.get("num") != 3]
                    await state.update_data(files=files)

                    await state.set_state(FormTutupPOSReplikasi.lampiran_3)
                    await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_lampiran_3(message)
                    return

                return

            if message.content_type not in (ContentType.PHOTO, ContentType.DOCUMENT, ContentType.VIDEO):
                return          

            file_id = extract_file_id(message)
            if not file_id:
                return

            tmp_msg = await send_file_preview(bot, message, file_id, data_state.get("form_view_message_id"))

            files = data_state.get("files", [])
            files = [f for f in files if f.get("num") != 4]
            files.append({
                "num": 4,
                "file_id": file_id,
                "message_id": tmp_msg.message_id,
                "type": message.content_type,
            })

            await state.update_data(files=files)        
            await state.set_state(FormTutupPOSReplikasi.datetime_end)

            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_datetime_end(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.datetime_end)
async def input_datetime_end(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            text = message.text.strip().lower()

            if text.startswith("/kembali"):
                data_state = await state.get_data()

                files = data_state.get("files", [])

                for num in (4, 3, 2, 1):
                    file = next((f for f in files if f.get("num") == num), None)
                    if not file:
                        continue

                    await safe_delete_message(
                        bot=bot,
                        chat_id=message.chat.id,
                        message_id=file["message_id"]
                    )

                    await state.update_data(
                        files=[f for f in files if f.get("num") != num]
                    )

                    await state.set_state(getattr(FormTutupPOSReplikasi, f"lampiran_{num}"))
                    await getattr(
                        TutupPOSReplikasiFormQuestion(bot, state, session_db),
                        f"q_lampiran_{num}"
                    )(message)

                    return

                return

            if text.startswith("/baru_saja_selesai"):
                dt = datetime.now().replace(microsecond=0)
                await state.update_data(datetime_end=dt)
            else:
                dt = await verify_datetime(message, state)
                if not isinstance(dt, datetime):
                    return
                await state.update_data(datetime_end=dt)

            data_state = await state.get_data()
            id_work = generate_id_work(data_state, "D")

            await state.update_data(id_work=id_work)
            await state.set_state(FormTutupPOSReplikasi.simpan)

            await send_txt_form(bot, session_db, message, state)
            await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_kirim(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormTutupPOSReplikasi.simpan)
async def input_simpan(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            text = message.text.strip().lower()

            if text.startswith("/kembali"):
                await state.set_state(FormTutupPOSReplikasi.datetime_end)
                await TutupPOSReplikasiFormQuestion(bot, state, session_db).q_datetime_end(message)
                return

            if not text.startswith("/kirim"):
                return

            data_state = await state.get_data()
            id_work = data_state.get("id_work")

            FILE_FOLDER = Path("files")
            FILE_FOLDER.mkdir(parents=True, exist_ok=True)

            files: list[dict] = sorted(
                data_state.get("files", []),
                key=lambda f: f.get("num", 0)
            )

            lampiran_files: list[Path] = []

            for file in files:
                file_id = file["file_id"]
                num = file["num"]

                save_path = FILE_FOLDER / f"{id_work}_{num}"
                download_path = await download_and_save_file(
                    bot=bot,
                    file_id=file_id,
                    save_path=save_path
                )
                lampiran_files.append(download_path)

            lampiran_file_str = ", ".join(map(str, lampiran_files))

            session_db.add(
                SiagadanReplikasiDB(
                    id_work=id_work,
                    tipe="POS_REPLIKASI",
                    proses="PENGEMBALIAN",
                    nomor_co=data_state.get("nomor_co"),
                    kdtk=data_state.get("kdtk"),
                    nama_toko=data_state.get("nama_toko"),
                    cabang=data_state.get("cabang"),
                    datetime_end=data_state.get("datetime_end"),
                    status=data_state.get("status"),
                    keterangan=data_state.get("keterangan"),
                    lampiran_file=lampiran_file_str,
                    pelaksana_nik=data_state.get("pelaksana_nik"),
                    pelaksana_nama=data_state.get("pelaksana_nama"),
                    telegram_id=message.from_user.id,
                )
            )

            text_form = await txt_form(state)
            sent_msg = await bot.send_message(
                chat_id=settings.CHANNEL_MDB_ID,
                text=text_form
            )

            for file_path in lampiran_files:
                try:
                    await bot.send_document(
                        chat_id=settings.CHANNEL_MDB_ID,
                        document=FSInputFile(file_path),
                        reply_to_message_id=sent_msg.message_id
                    )
                except Exception as e:
                    logging.error("Send document error: %s", e)

            for file in files:
                await safe_delete_message(
                    bot=bot,
                    chat_id=message.chat.id,
                    message_id=file.get("message_id")
                )

            for key in ("form_view_message_id", "form_write_message_id"):
                if msg_id := data_state.get(key):
                    await safe_delete_message(
                        bot=bot,
                        chat_id=message.chat.id,
                        message_id=msg_id
                    )

            current_state = await state.get_state()
            logging.info("Clearing state %r", current_state)
            await state.clear()

            link = f"https://t.me/c/{str(settings.CHANNEL_MDB_ID)[4:]}/{sent_msg.message_id}"
            await message.answer(
                text=f"✅ Berhasil dikirim\n🔗 {link}",
                reply_markup=menu_main()
            )

    except Exception as e:
        await handle_exception(message, bot, e)
