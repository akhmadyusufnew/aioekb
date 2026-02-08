from aiogram.fsm.state import State, StatesGroup

class FormStartPOSReplikasi(StatesGroup):
    kdtk = State()
    nomor_co = State()
    datetime_start = State()
    alasan = State()
    status = State()
    keterangan = State()
    lampiran_1 = State()
    lampiran_2 = State()
    lampiran_3 = State()
    lampiran_4 = State()
    datetime_end = State()
    simpan = State()