from aiogram.types import Message

from ._base import BaseFormQuestion

class BackupRestoreFormQuestion(BaseFormQuestion):

    async def q_ibdata_mb_awal(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Ibdata sebelum (MB):\n\n{cmd}",
        )
    
    async def q_ibdata_mb_akhir(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Ibdata setelah (MB):\n\n{cmd}",
        )

    async def q_alasan(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Alasan backup restore (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"Contoh:\n"
            f"<code>Size IBData sudah besar</code>\n"
            f"<code>ErrLog (InnoDB: Error: page)</code>\n"
            f"<code>InnoDB: is in the future! Current system log sequence number</code>\n"
            f"<code>Terindikasi DB corupt</code>\n"
            f"<code>Permintaan EDP Cabang</code>\n",
        )

    async def q_autov2(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Setelah BR sudah jalankan autov2 di komputer induk/server:"
            f"\n\n"
            f"{cmd}\n\n/sudah_jalankan_autov2"
            f"\n\n"
            f"<code>start d:\\idm\\rndagent.exe all</code>\n"
            f"<code>start d:\\backoff\\autov2.bat</code>",
        )

    async def q_hu_stok(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Apa menjalankan hitung ulang stok? <b>WAJIB</b>:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/hitung_ulang_stok_dengan_file_T\n"
            f"/hitung_ulang_stok_tanpa_file_T\n"
            f"/tidak_hitung_ulang_stok",
        )

    async def q_hu_spd(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Apa menjalankan hitung ulang SPD? <b>WAJIB</b>:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/sudah_hitung_ulang_spd\n"
            f"/tanpa_hitung_ulang_spd",
        )

    async def q_hu_pkm(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Apa menjalankan hitung ulang PKM? <b>WAJIB</b>:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/sudah_hitung_ulang_pkm\n"
            f"/tanpa_hitung_ulang_pkm",            
        )
    
    async def q_lampiran_br_1(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file capture pengecekan BR pada STSAssistent:"
            f"\n\n"
            f"{cmd}"
        )

    async def q_lampiran_br_2(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Jika masih ada file photo/document/video silakan dikirim:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/tidak_ada"
        )

    async def q_keterangan(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Keterangan/kendala yang di alami ketika Backup Restore (boleh ketik manual, min:10, max:600):\n\n{cmd}\n\n/tidak_ada_kendala",
        )