from datetime import datetime

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.repository import log_telegram_event

from core.telegram import safe_delete_message


class BaseFormQuestion:
    def __init__(self, bot: Bot, state: FSMContext, session_db: AsyncSession):
        self.bot = bot
        self.state = state
        self.session_db = session_db

    def command_text(self, *, back=True, cancel=True) -> str:
        cmds = []

        if cancel:
            cmds.append("/batal")

        if back:
            cmds.append("/kembali")

        return "\n".join(cmds)

    async def ask(
        self,
        message: Message,
        text: str,
        **kwargs
    ):
        data_state = await self.state.get_data()
        chat_id = message.chat.id

        # -------------------------
        # HAPUS MESSAGE SEBELUMNYA
        # -------------------------
        old_msg_id = data_state.get("form_write_message_id")
        if old_msg_id:
            await self.state.update_data(form_write_message_id=None)
            await safe_delete_message(
                bot=self.bot,
                chat_id=chat_id,
                message_id=old_msg_id
            )

        # -------------------------
        # KIRIM MESSAGE BARU
        # -------------------------
        form_view_message_id = data_state.get("form_view_message_id")

        if form_view_message_id:
            try:
                q = await message.answer(
                    text,
                    reply_to_message_id=form_view_message_id,
                    **kwargs
                )
                await log_telegram_event(self.session_db, q)
            except Exception:
                # fallback TANPA reply_to
                q = await message.answer(text, **kwargs)
                await log_telegram_event(self.session_db, q)
        else:
            q = await message.answer(text, **kwargs)
            await log_telegram_event(self.session_db, q)

        # -------------------------
        # SIMPAN STATE
        # -------------------------
        await self.state.update_data(form_write_message_id=q.message_id)


    async def q_kdtk(self, message: Message):
        cmd = self.command_text(back=False)
        await self.ask(message,
            f"Masukkan KDTK (4 digit):"
            f"\n\n"
            f"{cmd}"
        )

    async def q_nomor_co(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Masukan Nomor CO (10 digit):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/tidak_ada_nomor_co"
        )

    async def q_station(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Balas station:"
            f"\n\n"
            f"{cmd}"
        )

    async def q_datetime_start(self, message: Message):
        cmd = self.command_text()
        text = (
            f"Balas waktu mulai pekerjaan ini:\n"
            f"\n\n"
            f"<code>"
            f"{str('[Kode Balasan]').ljust(16, ' ')}= (keterangan)\n"
            f"{str('HHMM').ljust(16, ' ')}= 2 digit jam, 2 digit menit\n"
            f"{str(' ').ljust(18, ' ')}contoh : {datetime.now().strftime('%H%M')}\n"
            f"{str('HH:MM').ljust(16, ' ')}= Format 24 jam, contoh : {datetime.now().strftime('%H:%M')}\n"
            f"{str('Y-m-d H:M:S').ljust(16, ' ')}= {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{str('Copy dr WebCO').ljust(16, ' ')}= {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}"
            f"</code>"
            f"\n\n"
            f"{cmd}"
        )
        await self.ask(message, text, reply_markup=ReplyKeyboardRemove())

    async def q_keterangan(self, message: Message):
        cmd = self.command_text()
        
        data_state = await self.state.get_data()
        status = (data_state.get("status") or "").lower()
        if "berhasil" in status:
            cmd += "\n\n/selanjutnya"

        await self.ask(
            message,
            f"Keterangan/catatan (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}",
            reply_markup=ReplyKeyboardRemove()
        )

    async def q_lampiran_1(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file photo/document/video:"
            f"\n\n"
            f"{cmd}"
        )

    async def q_lampiran_2(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file photo/document/video:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/selanjutnya"
        )

    async def q_lampiran_3(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file photo/document/video:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/selanjutnya"
        )

    async def q_lampiran_4(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file photo/document/video:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/selanjutnya"
        )

    async def q_datetime_end(self, message: Message):
        cmd = self.command_text()
        text = (
            f"Balas waktu selesai pekerjaan ini:\n"
            f"\n\n"
            f"<code>"
            f"{str('[Kode Balasan]').ljust(16, ' ')}= (keterangan)\n"
            f"{str('HHMM').ljust(16, ' ')}= 2 digit jam, 2 digit menit\n"
            f"{str(' ').ljust(18, ' ')}contoh : {datetime.now().strftime('%H%M')}\n"
            f"{str('HH:MM').ljust(16, ' ')}= Format 24 jam, contoh : {datetime.now().strftime('%H:%M')}\n"
            f"{str('Y-m-d H:M:S').ljust(16, ' ')}= {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{str('Copy dr WebCO').ljust(16, ' ')}= {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}"
            f"</code>"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/baru_saja_selesai"
        )

        await self.ask(message, text)

    async def q_kirim(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Apakah form dan lampiran sudah siap di kirim:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/kirim"
        )
