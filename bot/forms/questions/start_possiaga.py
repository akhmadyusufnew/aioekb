from aiogram.types import Message

from ._base import BaseFormQuestion

class StartPOSSiagaFormQuestion(BaseFormQuestion):

    async def q_alasan(self, message: Message):
        cmd = self.command_text()
        
        await self.ask(
            message,
            f"Alasan dibuat POS Siaga (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"Contoh:\n"
            f"<code>PC induk Backup Restore EDP Region</code>\n"
            f"<code>PC induk terkendala pada service Database</code>\n"
            f"<code>PC induk tidak bisa dihidupkan</code>\n"
            f"<code>PC induk tidak bisa masuk Windows</code>\n"
            f"<code>PC induk terkendala disk corrupt</code>\n"
            f"<code>PC induk ganti CPU</code>\n"
            f"<code>PC induk install ulang Windows</code>\n"
            f"<code>PC induk maintenance EDP Lapangan</code>\n"
            f"<code>PC induk ganti disk oleh EDP Lapangan</code>\n",
        )

    async def q_alasan_2(self, message: Message):
        cmd = self.command_text()
        
        await self.ask(
            message,
            f"Alasan tidak dibuat POS Replikasi (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"Contoh:\n"
            f"<code>Toleransi row NOK</code>\n"
            f"<code>Induk tidak respon</code>\n",
        )        

    async def q_status(self, message: Message):
        cmd = self.command_text()
        keyboard_buttons = [
            [
                KeyboardButton(text="✅ Berhasil")
            ],
            [
                KeyboardButton(text="Kendala")
            ],
        ]
        await self.ask(
            message,
            f"Status Pembuatan:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/kendala /berhasil",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard_buttons,
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        )