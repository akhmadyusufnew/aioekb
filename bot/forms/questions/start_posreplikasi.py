from aiogram.types import Message

from ._base import BaseFormQuestion

class StartPOSReplikasiFormQuestion(BaseFormQuestion):

    async def q_alasan(self, message: Message):
        cmd = self.command_text()
        
        await self.ask(
            message,
            f"Alasan dibuat POS Replikasi (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"Contoh:\n"
            f"<code>PC induk tidak bisa dihidupkan</code>\n"
            f"<code>PC induk tidak bisa masuk Windows</code>\n"
            f"<code>PC induk terkendala disk corrupt</code>\n"
            f"<code>PC induk ganti CPU</code>\n"
            f"<code>PC induk install ulang Windows</code>\n"
            f"<code>PC induk maintenance EDP Lapangan</code>\n"
            f"<code>PC induk ganti disk oleh EDP Lapangan</code>\n",
        )