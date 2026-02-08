from aiogram.fsm.state import State, StatesGroup

class FormStartPOSSiaga(StatesGroup):
    kdtk = State()
    nomor_co = State()
    station = State()
    datetime_start = State()
    alasan = State()
    alasan_2 = State()
    status = State()
    keterangan = State()
    lampiran_1 = State()
    lampiran_2 = State()
    lampiran_3 = State()
    lampiran_4 = State()
    datetime_end = State()
    simpan = State()