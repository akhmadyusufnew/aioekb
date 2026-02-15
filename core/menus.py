import calendar

from datetime import datetime
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from sqlalchemy import func
from sqlmodel import select

from core.db.database import get_session
from core.db.models import JadwalShiftDB, UserRole

BULAN_MAP = {
    "01": "JAN",
    "02": "FEB",
    "03": "MAR",
    "04": "APR",
    "05": "MEI",
    "06": "JUN",
    "07": "JUL",
    "08": "AGU",
    "09": "SEP",
    "10": "OKT",
    "11": "NOV",
    "12": "DES"
}

HARI_LIST = ["MG", "SN", "SL", "RB", "KM", "JB", "SB"]

class MenuMainCB(CallbackData, prefix="menu_main"):
    menu: str

class MenuJadwalShiftCB(CallbackData, prefix="menu_jadwal_shift"):
    menu: str

class MenuJadwalShiftTahunCB(CallbackData, prefix="menu_jadwal_shift_tahun"):
    menu: str

class MenuJadwalShiftBulanCB(CallbackData, prefix="menu_jadwal_shift_bulan"):
    menu: str

class MenuJadwalShiftTanggalCB(CallbackData, prefix="menu_jadwal_shift_tanggal"):
    menu: str        

class MenuFormCB(CallbackData, prefix="menu_form"):
    menu: str

class MenuLinkCB(CallbackData, prefix="menu_link"):
    menu: str


def menu_main(user_data: dict):
    inline_keyboard = [
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
        ]
    ]

    if user_data.get("role") == UserRole.ADMIN:

        row1 = [
            InlineKeyboardButton(
                text="⬇️ Unduh Siaga/Replikasi",
                callback_data=MenuMainCB(menu="unduh_pos_siaga_replikasi").pack()
            ),
            InlineKeyboardButton(
                text="⬇️ Unduh BR/RD",
                callback_data=MenuMainCB(menu="unduh_br_rd").pack()
            )
        ]

        row2 = [
            InlineKeyboardButton(
                text="⬆️ Upload MSTR TK",
                callback_data=MenuMainCB(menu="upload_mstr_toko").pack()
            ),
            InlineKeyboardButton(
                text="⬆️ Upload Jadwal",
                callback_data=MenuMainCB(menu="upload_jadwal").pack()
            )
        ]

        inline_keyboard += [row1, row2]


    inline_keyboard.append([
        InlineKeyboardButton(
            text="🔚 Selesai",
            callback_data=MenuMainCB(menu="exit").pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


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
                    text="📅 Kalender",
                    callback_data=MenuJadwalShiftCB(menu="kalender_tahun").pack() 
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Kembali",
                    callback_data=MenuJadwalShiftCB(menu="menu_main").pack() 
                ),
            ],
        ]
    )


async def menu_jadwal_shift_kalender_tahun(session_db):
    stmt = (
        select(func.concat("20", func.left(JadwalShiftDB.periode, 2)).label("tahun"))
        .group_by(func.left(JadwalShiftDB.periode, 2))
        .order_by(func.left(JadwalShiftDB.periode, 2))
    )

    result = await session_db.execute(stmt)
    tahun_list = [r.tahun for r in result.fetchall()]

    if not tahun_list:
        return None

    tombol_tahun = [
        InlineKeyboardButton(
            text=tahun,
            callback_data=MenuJadwalShiftTahunCB(menu=tahun[-2:]).pack()
        )
        for tahun in tahun_list
    ]

    inline_keyboard = [
        tombol_tahun[i:i+3]
        for i in range(0, len(tombol_tahun), 3)
    ]

    inline_keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Kembali",
            callback_data=MenuJadwalShiftTahunCB(menu="menu_jadwal_shift").pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def menu_jadwal_shift_kalender_bulan(session_db, tahun_prefix: str):

    stmt = (
        select(func.right(JadwalShiftDB.periode, 2).label("bulan"))
        .where(func.left(JadwalShiftDB.periode, 2) == tahun_prefix)
        .group_by(JadwalShiftDB.periode)
        .order_by(func.right(JadwalShiftDB.periode, 2))
    )
    result = await session_db.execute(stmt)
    bulan_list = [r.bulan for r in result.fetchall()]

    if not bulan_list:
        return None

    tombol_bulan = [
        InlineKeyboardButton(
            text=BULAN_MAP.get(bulan, bulan),
            callback_data=MenuJadwalShiftBulanCB(menu=f"{tahun_prefix}{bulan}").pack()
        )
        for bulan in bulan_list
    ]

    inline_keyboard = [tombol_bulan[i:i+3] for i in range(0, len(tombol_bulan), 3)]

    inline_keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Pilih Tahun",
            callback_data=MenuJadwalShiftBulanCB(menu=f"menu_jadwal_shift_tahun").pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def menu_jadwal_shift_kalender_tanggal(yymm: str):

    year = 2000 + int(yymm[:2])
    month = int(yymm[2:])

    cal = calendar.Calendar(firstweekday=6)
    month_days = list(cal.itermonthdays(year, month))

    header_row = [
        InlineKeyboardButton(text=hari, callback_data="ignore") for hari in HARI_LIST
    ]
    inline_keyboard = [header_row]

    row = []
    for day in month_days:
        if day == 0:
            row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        else:
            row.append(
                InlineKeyboardButton(
                    text=str(day),
                    callback_data=MenuJadwalShiftTanggalCB(menu=f"{yymm}{day:02}").pack()
                )
            )
        if len(row) == 7:
            inline_keyboard.append(row)
            row = []

    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        inline_keyboard.append(row)

    inline_keyboard.append([
        InlineKeyboardButton(
            text=f"⬅️ Pilih Bulan ({year})",
            callback_data=MenuJadwalShiftTanggalCB(menu=f"menu_jadwal_shift_bulan|{yymm}").pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


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