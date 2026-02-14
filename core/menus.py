from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

class MenuMainCB(CallbackData, prefix="menu_main"):
    menu: str

class MenuJadwalShiftCB(CallbackData, prefix="menu_jadwal_shift"):
    menu: str

class MenuFormCB(CallbackData, prefix="menu_form"):
    menu: str

class MenuLinkCB(CallbackData, prefix="menu_link"):
    menu: str

def menu_main():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Jadwal Shift",
                    callback_data=MenuMainCB(menu="menu_jadwal_shift").pack() 
                ),
                InlineKeyboardButton(
                    text="📝 Form Laporan",
                    callback_data=MenuMainCB(menu="menu_form").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 MySQL Admin",
                    callback_data=MenuMainCB(menu="pw_mysqladmin").pack() 
                ),
                InlineKeyboardButton(
                    text="👤 Profile",
                    callback_data=MenuMainCB(menu="profile").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌎 Links",
                    callback_data=MenuMainCB(menu="menu_link").pack() 
                )
            ],            
            [
                InlineKeyboardButton(
                    text="🔚 Selesai",
                    callback_data=MenuMainCB(menu="exit").pack() 
                )
            ]
        ]
    )


def menu_jadwal_shift():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="On Shift",
                    callback_data=MenuJadwalShiftCB(menu="on_shift").pack() 
                ),
                InlineKeyboardButton(
                    text="Hari Ini",
                    callback_data=MenuJadwalShiftCB(menu="hari_ini").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="Jadwal Saya",
                    callback_data=MenuJadwalShiftCB(menu="saya").pack() 
                ),
                InlineKeyboardButton(
                    text="Besok",
                    callback_data=MenuJadwalShiftCB(menu="besok").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="Lusa",
                    callback_data=MenuJadwalShiftCB(menu="lusa").pack() 
                ),
                InlineKeyboardButton(
                    text="Lusa + 1",
                    callback_data=MenuJadwalShiftCB(menu="lusa_1").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="Kemarin",
                    callback_data=MenuJadwalShiftCB(menu="kemarin").pack() 
                ),
                InlineKeyboardButton(
                    text="Kemarin - 1",
                    callback_data=MenuJadwalShiftCB(menu="kemarin_1").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Kembali",
                    callback_data=MenuJadwalShiftCB(menu="menu_main").pack() 
                ),
            ],
        ]
    )


def menu_form():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Backup Restore",
                    callback_data=MenuFormCB(menu="backup_restore").pack() 
                ),
                InlineKeyboardButton(
                    text="Restore Data",
                    callback_data=MenuFormCB(menu="restore_data").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Start Replikasi",
                    callback_data=MenuFormCB(menu="start_pos_replikasi").pack() 
                ),
                InlineKeyboardButton(
                    text="Tutup Replikasi",
                    callback_data=MenuFormCB(menu="tutup_pos_replikasi").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="Start Siaga",
                    callback_data=MenuFormCB(menu="start_pos_siaga").pack() 
                ),
                InlineKeyboardButton(
                    text="Tutup Siaga",
                    callback_data=MenuFormCB(menu="tutup_pos_siaga").pack() 
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Kembali",
                    callback_data=MenuFormCB(menu="menu_main").pack() 
                ),
            ],
        ]
    )


def menu_link():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 EDP R I BOGOR",
                    url="https://t.me/c/1193081646/77886"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 EDP R I - Support TOKO-Software",
                    url="https://t.me/c/1185326166/67757"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 EDP R I + EDP CABANG",
                    url="https://t.me/c/1554083806/81498"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🚛 EDP R I + DC",
                    url="https://t.me/c/1665420323/129446"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 EDP R I + VIRTUAL CABANG",
                    url="https://t.me/c/1797515630/3135"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 SU.OP - Monitoring Klik ⚡️⚡️",
                    url="https://t.me/c/2126657541/18170"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🫂 SU.OP - Support Toko 🏪",
                    url="https://t.me/c/2282207080/16277"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🚛 SU.OP - Support DC 📦",
                    url="https://t.me/c/3100042476/767"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔆 SU.OP - Maintenance DB",
                    url="https://t.me/c/1893545909/18170"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🫂 Report Simulasi DTO",
                    url="https://t.me/+KraqrR9EXB5hZTBl"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Bambang",
                    url="tg://resolve?domain=ComplainOnline_MIB_bot"
                ),
            ],                        
            [
                InlineKeyboardButton(
                    text="📜 SU.OP - Informasi & Supervisi",
                    url="https://t.me/+o-6rCcupumo3YmZl"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🫂 SU.OP - Officer",
                    url="https://t.me/c/1678668164/20496"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌎 Rumah Keduaku",
                    url="http://portal.hrindomaret.com/"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Kembali",
                    callback_data=MenuLinkCB(menu="menu_main").pack() 
                ),
            ],
        ]
    )