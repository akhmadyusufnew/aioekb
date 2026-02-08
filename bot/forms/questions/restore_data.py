from aiogram.types import Message

from ._base import BaseFormQuestion

class RestoreDataFormQuestion(BaseFormQuestion):

    async def q_alasan(self, message: Message):
        cmd = self.command_text()
        
        await self.ask(
            message,
            f"Alasan restore data (boleh ketik manual, min:10, max:600):"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"Contoh:\n"
            f"<code>DB Induk corrupt</code>\n"
            f"<code>PC/Disk Induk tidak bisa di aktifkan</code>\n",
        )

    async def q_restore_from_db_replikasi(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Sumber data dari DB POS Replikasi (boleh ketik manual, min:6, max:600):"
            f"\n\n"
            f"{cmd}\n\n/tidak"
            f"\n\n"
            f"Contoh:\n"
            f"<code>Copy Folder 'MySQL Data Files' E DB Replikasi ke D Induk</code>\n"
            f"<code>Dump DB Replikasi kemudian restore ke MySQL Fresh Induk</code>",
        )

    async def q_restore_from_bckmysql(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Sumber data dari BCKMySQL (boleh ketik manual, min:6, max:600):"
            f"\n\n"
            f"{cmd}\n\n/tidak"
            f"\n\n"
            f"Contoh:\n"
            f"<code>BCKMySQL induk (sekitar jam)</code>\n"
            f"<code>BCKMySQL anak (sekitar jam)</code>",
        )

    async def q_restore_restore_from_dthr(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Sumber data dari DTHR (boleh ketik manual, min:6, max:600):"
            f"\n\n"
            f"{cmd}\n\n/tidak"
            f"\n\n"
            f"Contoh:\n"
            f"DTHR tgl berapa s/d tgl berapa",
        )

    async def q_restore_restore_from_posrealtime(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Sumber data dari POS Realtime (boleh ketik manual, min:6, max:600):\n\n{cmd}\n/tidak",
        )
    
    async def q_restore_restore_from_file_jual(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Sumber data dari File Jual (boleh ketik manual, min:6, max:600):\n\n{cmd}\n/tidak",
        )
    
    async def q_ibdata_mb_akhir(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Ibdata setelah (MB):\n\n{cmd}",
        )

    async def q_autov2(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Setelah BR Sudah Jalankan autov2 di komputer induk/server?:"
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
    
    async def q_lampiran_rd_1(self, message: Message):
        cmd = self.command_text()
        await self.ask(
            message,
            f"Kirim file capture pengecekan BR pada STSAssistent:"
            f"\n\n"
            f"{cmd}"
        )

    async def q_lampiran_rd_2(self, message: Message):
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
            f"Keterangan/kendala yang di alami ketika Restore Data (boleh ketik manual, min:10, max:600):\n\n{cmd}\n\n/tidak_ada_kendala",
        )