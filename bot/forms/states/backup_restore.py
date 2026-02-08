from aiogram.fsm.state import State, StatesGroup

class FormBackupRestore(StatesGroup):
    kdtk = State()
    nomor_co = State()
    ibdata_mb_awal = State()
    ibdata_mb_akhir = State()
    alasan = State()
    keterangan = State()
    autov2 = State()
    hu_stok = State()
    hu_spd = State()
    hu_pkm = State()
    lampiran_1 = State()
    lampiran_2 = State()
    datetime_end = State()
    simpan = State()