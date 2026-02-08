from aiogram.fsm.state import State, StatesGroup

class FormRegistrasiAccount(StatesGroup):
    nik = State()
    nama_lengkap = State()