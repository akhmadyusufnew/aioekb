from aiogram.fsm.state import State, StatesGroup

class FormTutupPOSReplikasi(StatesGroup):
    kdtk = State()
    nomor_co = State()
    status = State()
    keterangan = State()
    lampiran_1 = State()
    lampiran_2 = State()
    lampiran_3 = State()
    lampiran_4 = State()
    datetime_end = State()
    simpan = State()