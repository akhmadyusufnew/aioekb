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
from core.db.models import BackupRestoreDB
from core.db.repository import log_telegram_event
from core.menus import menu_main

from core.telegram import safe_delete_message, extract_file_id, handle_exception
from bot.forms.validators import verify_kdtk, verify_datetime
from bot.forms.fsm_helper import handle_cancel_form, generate_id_work, send_file_preview, delete_file, download_and_save_file

from bot.forms.states import FormBackupRestore
from bot.forms.questions import BackupRestoreFormQuestion


async def txt_form(state: FSMContext) -> str:
    data_state = await state.get_data()

    cabang = data_state.get('cabang')
    datetime_start = data_state.get('datetime_start')
    datetime_end = data_state.get('datetime_end')

    if not cabang:
        cabang = "G000"

    if datetime_end:
        datetime_end = datetime_end.strftime("%d-%b-%Y ± %H:%M")
    else:
        datetime_end = ''

    string  = f"💫 #BR #{cabang[:4]} #{data_state.get('kdtk', '')}\n"
    string += "<pre><code>"
    string += "Form Laporan Backup Restore\n"
    string += "------------------------------------\n\n"
    string += "No. CO".ljust(15) + f": {data_state.get('nomor_co', '')}\n"
    string += "Toko".ljust(15) + f": {data_state.get('kdtk', '')}{' - ' + data_state.get('nama_toko') if data_state.get('nama_toko') else ''}\n"
    string += "Cabang".ljust(15) + f": {data_state.get('cabang') if data_state.get('cabang') else ''}\n"
    string += "IBData Awal".ljust(15) + f": ± {data_state.get('ibdata_mb_awal', '')} MB\n"
    string += "IBData Akhir".ljust(15) + f": ± {data_state.get('ibdata_mb_akhir', '')} MB\n"
    string += "Alasan".ljust(15) + f": {data_state.get('alasan', '')}\n"
    string += "\n"
    string += "Autov2".ljust(15) + f": {data_state.get('autov2', '')}\n"
    string += "H.U Stok".ljust(15) + f": {data_state.get('hu_stok', '')}\n"
    string += "H.U SPD".ljust(15) + f": {data_state.get('hu_spd', '')}\n"
    string += "H.U PKM".ljust(15) + f": {data_state.get('hu_pkm', '')}\n"
    string += "\n"
    string += "Time Selesai".ljust(15) + f": {datetime_end}\n"
    string += "Keterangan".ljust(15) + f": {data_state.get('keterangan', '')}\n"
    string += "\n"
    string += f"{data_state.get('pelaksana_nama', '')}\n"
    string += f"{datetime.now().replace(microsecond=0)}\n"
    string += f"{data_state.get('id_work', '')}"
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


@router.message(StateFilter(FormBackupRestore), F.text.lower() == "/batal")
async def cancel_form(message: Message, bot: Bot, state: FSMContext):
    await safe_delete_message(message)

    async with get_session() as session_db:
        await log_telegram_event(session_db, message)

    await handle_cancel_form(message, bot, state)


@router.message(FormBackupRestore.kdtk)
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
            await state.set_state(FormBackupRestore.nomor_co)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_nomor_co(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.nomor_co)
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
                await state.set_state(FormBackupRestore.kdtk)
                await BackupRestoreFormQuestion(bot, state, session_db).q_kdtk(message)
                return

            if raw_text.startswith("2") and len(raw_text) == 10:
                await state.update_data(nomor_co=raw_text.upper())
            elif raw_text != "/tidak_ada_nomor_co":
                return

            await state.set_state(FormBackupRestore.ibdata_mb_awal)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_ibdata_mb_awal(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.ibdata_mb_awal)
async def input_ibdata_mb_awal(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormBackupRestore.nomor_co)
                await BackupRestoreFormQuestion(bot, state, session_db).q_nomor_co(message)
                return

            ibdata_mb_awal = raw_text
            if not ibdata_mb_awal.isdigit():
                return

            await state.update_data(ibdata_mb_awal=int(ibdata_mb_awal))
            await state.set_state(FormBackupRestore.ibdata_mb_akhir)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_ibdata_mb_akhir(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.ibdata_mb_akhir)
async def input_ibdata_mb_akhir(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormBackupRestore.ibdata_mb_awal)
                await BackupRestoreFormQuestion(bot, state, session_db).q_ibdata_mb_awal(message)
                return

            ibdata_mb_akhir = raw_text
            if not ibdata_mb_akhir.isdigit():
                return

            await state.update_data(ibdata_mb_akhir=int(ibdata_mb_akhir))
            await state.set_state(FormBackupRestore.alasan)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_alasan(message)

    except Exception as e:
        await handle_exception(message, bot, e)

@router.message(FormBackupRestore.alasan)
async def input_alasan(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.ibdata_mb_akhir)
                await BackupRestoreFormQuestion(bot, state, session_db).q_ibdata_mb_akhir(message)
                return

            alasan = raw_text
            if not (10 <= len(alasan) <= 600):
                return
            
            await safe_delete_message(message)
            await state.update_data(alasan=alasan)
            await state.set_state(FormBackupRestore.autov2)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_autov2(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.autov2)
async def input_autov2(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.alasan)
                await BackupRestoreFormQuestion(bot, state, session_db).q_alasan(message)
                return

            if not text.startswith("/sudah_jalankan_autov2"):
                return

            await state.update_data(autov2="Sudah di jalankan AutoV2 ✅")

            await state.set_state(FormBackupRestore.hu_stok)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_hu_stok(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.hu_stok)
async def input_hu_stok(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.autov2)
                await BackupRestoreFormQuestion(bot, state, session_db).q_autov2(message)
                return

            if text.startswith("/hitung_ulang_stok_dengan_file_t"):
                await state.update_data(hu_stok="Hitung ulang stok dengan File T ✅")

            elif text.startswith("/hitung_ulang_stok_tanpa_file_t"):
                await state.update_data(hu_stok="Hitung ulang stok tanpa File T")

            elif text.startswith("/tidak_hitung_ulang_stok"):
                await state.update_data(hu_stok="Tidak")

            else:
                return

            await state.set_state(FormBackupRestore.hu_spd)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_hu_spd(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.hu_spd)
async def input_hu_spd(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.hu_stok)
                await BackupRestoreFormQuestion(bot, state, session_db).q_hu_stok(message)
                return

            if text.startswith("/sudah_hitung_ulang_spd"):
                await state.update_data(hu_spd="Sudah hitung ulang SPD ✅")

            elif text.startswith("/tanpa_hitung_ulang_spd"):
                await state.update_data(hu_spd="Tidak")

            else:
                return
            
            await state.set_state(FormBackupRestore.hu_pkm)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_hu_pkm(message)

    except Exception as e:
        await handle_exception(message, bot, e)

@router.message(FormBackupRestore.hu_pkm)
async def input_hu_pkm(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.hu_spd)
                await BackupRestoreFormQuestion(bot, state, session_db).q_hu_spd(message)
                return

            if text.startswith("/sudah_hitung_ulang_pkm"):
                await state.update_data(hu_pkm="Sudah hitung ulang PKM ✅")

            elif text.startswith("/tanpa_hitung_ulang_pkm"):
                await state.update_data(hu_pkm="Tidak")

            else:
                return
            
            await state.set_state(FormBackupRestore.lampiran_1)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_lampiran_br_1(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.lampiran_1)
async def input_lampiran_1(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/kembali"):
                    await state.set_state(FormBackupRestore.hu_pkm)
                    await BackupRestoreFormQuestion(bot, state, session_db).q_hu_pkm(message)
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
            await state.set_state(FormBackupRestore.lampiran_2)

            await BackupRestoreFormQuestion(bot, state, session_db).q_lampiran_br_2(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.lampiran_2)
async def input_lampiran_2(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)
        
            data_state = await state.get_data()

            if message.text:
                text = message.text.strip().lower()

                if text.startswith("/tidak_ada"):
                    await state.set_state(FormBackupRestore.datetime_end)
                    await BackupRestoreFormQuestion(bot, state, session_db).q_datetime_end(message)
                    return

                if text.startswith("/kembali"):
                    files = data_state.get("files", [])

                    file = next((f for f in files if f.get("num") == 1), None)
                    if file:
                        await safe_delete_message(bot=bot, chat_id=message.chat.id, message_id=file["message_id"])

                    files = [f for f in files if f.get("num") != 1]
                    await state.update_data(files=files)

                    await state.set_state(FormBackupRestore.lampiran_1)
                    await BackupRestoreFormQuestion(bot, state, session_db).q_lampiran_br_1(message)
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
            await state.set_state(FormBackupRestore.datetime_end)

            await BackupRestoreFormQuestion(bot, state, session_db).q_datetime_end(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.datetime_end)
async def input_datetime_end(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)
        
            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            data_state = await state.get_data()

            if text.startswith("/kembali"):
                files = data_state.get("files", [])

                for num in (2, 1):
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

                    await state.set_state(getattr(FormBackupRestore, f"lampiran_{num}"))
                    await getattr(
                        BackupRestoreFormQuestion(bot, state, session_db),
                        f"q_lampiran_br_{num}"
                    )(message)

                    return

                return

            if text.startswith("/baru_saja_selesai"):
                await state.update_data(
                    datetime_end=datetime.now().replace(microsecond=0)
                )
            else:
                dt = await verify_datetime(message, state)
                if not isinstance(dt, datetime):
                    return
                await state.update_data(datetime_end=dt)

            data_state = await state.get_data()
            id_work = generate_id_work(data_state, "A")
            await state.update_data(id_work=id_work)
            await state.set_state(FormBackupRestore.keterangan)
            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_keterangan(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.keterangan)
async def input_keterangan(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await safe_delete_message(message)
                await state.set_state(FormBackupRestore.datetime_end)
                await BackupRestoreFormQuestion(bot, state, session_db).q_datetime_end(message)
                return

            keterangan = raw_text
            if not (10 <= len(keterangan) <= 600):
                return

            if text.startswith("/tidak_ada_kendala"):
                await state.update_data(keterangan="Tidak ada kendala saat proses BR")
            else:
                await state.update_data(keterangan=keterangan)

            await safe_delete_message(message)            
            await state.set_state(FormBackupRestore.simpan)

            await send_txt_form(bot, session_db, message, state)
            await BackupRestoreFormQuestion(bot, state, session_db).q_kirim(message)

    except Exception as e:
        await handle_exception(message, bot, e)


@router.message(FormBackupRestore.simpan)
async def input_simpan(message: Message, bot: Bot, state: FSMContext) -> None:
    await safe_delete_message(message)

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)
        
            if not message.text:
                return

            raw_text = message.text.strip()
            text = raw_text.lower()

            if text.startswith("/kembali"):
                await state.set_state(FormBackupRestore.keterangan)
                await BackupRestoreFormQuestion(bot, state, session_db).q_keterangan(message)
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
                BackupRestoreDB(
                    id_work=id_work,
                    tipe="BACKUP_RESTORE",

                    nomor_co=data_state.get("nomor_co"),
                    kdtk=data_state.get("kdtk"),
                    nama_toko=data_state.get("nama_toko"),
                    cabang=data_state.get("cabang"),

                    ibdata_mb_awal=data_state.get("ibdata_mb_awal"),
                    ibdata_mb_akhir=data_state.get("ibdata_mb_akhir"),
                    alasan=data_state.get("alasan"),

                    autov2=data_state.get("autov2"),
                    hu_stok=data_state.get("hu_stok"),
                    hu_spd=data_state.get("hu_spd"),
                    hu_pkm=data_state.get("hu_pkm"),

                    lampiran_file=lampiran_file_str,
                    datetime_end=data_state.get("datetime_end"),

                    keterangan=data_state.get("keterangan"),
                    
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

            await state.clear()

            link = f"https://t.me/c/{str(settings.CHANNEL_MDB_ID)[4:]}/{sent_msg.message_id}"

            user_id = await check_account(session_db, callback, state)
            if user_id:          
                await message.answer(
                    text=f"✅ Berhasil dikirim\n🔗 {link}",
                    reply_markup=menu_main(user_id)
                )
            
            else:
                await message.answer(
                    text=f"✅ Berhasil dikirim\n🔗 {link}"
                )

    except Exception as e:
        await handle_exception(message, bot, e)
