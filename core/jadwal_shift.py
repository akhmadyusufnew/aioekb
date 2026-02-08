from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from core.db.repository import get_jadwal_shift_tgl, get_jadwal_shift_saya

# --------------------------------------
# Konstanta Nama Hari dan Bulan
# --------------------------------------
LIST_NAMA_HARI = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu"]
LIST_NAMA_HARI_TIGA = ["MIN", "SEN", "SEL", "RAB", "KAM", "JUM", "SAB"]
LIST_NAMA_BULAN = [
    "Januari", "Februari", "Maret", "Apri", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# --------------------------------------
# Aturan Shift
# --------------------------------------
SHIFT_RULES = {
    0: {"prev_day": True, "prev_shifts": {3,19,20,21,22,23}, "today_shifts": set()},
    1: {"prev_day": True, "prev_shifts": {3,19,20,21,22,23}, "today_shifts": set()},
    2: {"prev_day": True, "prev_shifts": {3,19,20,21,22,23}, "today_shifts": set()},
    3: {"prev_day": True, "prev_shifts": {3,19,20,21,22,23}, "today_shifts": set()},
    4: {"prev_day": True, "prev_shifts": {3,20,21,22,23}, "today_shifts": set()},
    5: {"prev_day": True, "prev_shifts": {3,21,22,23}, "today_shifts": set()},
    6: {"prev_day": True, "prev_shifts": {3,21,22,23}, "today_shifts": {1,6}},
    7: {"prev_day": True, "prev_shifts": {3,23}, "today_shifts": {1,6,7}},
    8: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    9: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    10: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    11: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    12: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    13: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,6,7,8}},
    14: {"prev_day": False, "prev_shifts": set(), "today_shifts": {1,2,6,7,8}},
    15: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,7,8}},
    16: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,8}},
    17: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15}},
    18: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15}},
    19: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15,19}},
    20: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15,19,20}},
    21: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15,19,20,21}},
    22: {"prev_day": False, "prev_shifts": set(), "today_shifts": {2,15,19,20,21,22}},
    23: {"prev_day": False, "prev_shifts": set(), "today_shifts": {3,15,19,20,21,22}},
}

def _get_shift_rules(hour: int):
    return SHIFT_RULES.get(hour, {"prev_day": False, "prev_shifts": set(), "today_shifts": set()})


# --------------------------------------
# Fungsi Ambil Jadwal per Tanggal
# --------------------------------------
async def get_jadwal_tgl(session_db, tanggal: datetime, title: str):
    tgl_str = tanggal.strftime("%y%m%d")
    idx_day = tgl_str[4:].zfill(2)
    datetime_input = datetime.strptime(tgl_str, "%y%m%d")

    # Header tanggal
    time_title_header = (
        f"{LIST_NAMA_HARI[int(datetime_input.strftime('%w'))]}, "
        f"{datetime_input.strftime('%d')} "
        f"{LIST_NAMA_BULAN[int(datetime_input.strftime('%m')) - 1]} "
        f"{datetime_input.strftime('%Y')}"
    )

    data = await get_jadwal_shift_tgl(session_db, tgl_str)

    # Inisialisasi output
    suop_on = suop_off = simprog = spvmgr = ""
    no_on = no_off = no_sim = no_mgr = 0
    shift_prev_on = shift_prev_off = None

    for row in data:
        nama = row["nama_personil"]
        kd_div = row["kd_div"]
        shift_val = str(row.get(f"s_{idx_day}") or "").upper()

        if "SOST" in kd_div:
            if shift_val in ("L", "0", "C", ""):
                no_off += 1
                if no_off > 1 and shift_val != shift_prev_off:
                    suop_off += "\n"
                suop_off += f"{str(no_off).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"
                shift_prev_off = shift_val
            else:
                no_on += 1
                if no_on > 1 and shift_val != shift_prev_on:
                    suop_on += "\n"
                suop_on += f"{str(no_on).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"
                shift_prev_on = shift_val

        elif "SOSP" in kd_div:
            no_sim += 1
            simprog += f"{str(no_sim).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"

        elif "MGT" in kd_div:
            no_mgr += 1
            spvmgr += f"{str(no_mgr).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"

    # Format pesan
    text_message = (
        f"REGIONAL EDP 1 | {title}\n"
        f"{time_title_header}\n"
        "--------------------------------\n\n"
    )
    if suop_on: text_message += f"[SUOP - Support Operasional]\n{suop_on}\n"
    if suop_off: text_message += f"[SUOP - Off Day]\n{suop_off}\n"
    if simprog: text_message += f"[SUOP - Simulasi Program]\n{simprog}\n"
    if spvmgr: text_message += f"[Supervisor]\n{spvmgr}\n"
    text_message += f"[Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"

    return f"<pre>{text_message}</pre>"


# --------------------------------------
# Fungsi Ambil Jadwal Aktif Berdasarkan Shift Saat Ini
# --------------------------------------
async def get_jadwal_tgl_aktif(session_db):
    now = datetime.now()
    rules = _get_shift_rules(now.hour)

    today_str = now.strftime("%y%m%d")
    today_day = today_str[4:].zfill(2)
    prev_str = (now - timedelta(days=1)).strftime("%y%m%d")
    prev_day_idx = prev_str[4:].zfill(2)

    suop_on = simprog = spvmgr = ""
    no_on = no_sim = no_mgr = 0
    shift_prev_on = None

    # Helper untuk proses data
    async def process_data(data, shifts_set):
        nonlocal suop_on, simprog, spvmgr, no_on, no_sim, no_mgr, shift_prev_on
        for row in data:
            nama = row["nama_personil"]
            kd_div = row["kd_div"]
            shift_val = row.get(f"s_{row_day}")
            if not shift_val:
                continue
            shift_val = str(shift_val).upper()
            if shift_val in ("L", "0", "C"):
                continue
            try:
                shift_int = int(shift_val)
            except ValueError:
                continue
            if shift_int not in shifts_set:
                continue

            if "SOST" in kd_div:
                no_on += 1
                if no_on > 1 and shift_val != shift_prev_on:
                    suop_on += "\n"
                suop_on += f"{str(no_on).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"
                shift_prev_on = shift_val
            elif "SOSP" in kd_div:
                no_sim += 1
                simprog += f"{str(no_sim).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"
            elif "MGT" in kd_div:
                no_mgr += 1
                spvmgr += f"{str(no_mgr).ljust(2)}. SF {shift_val.rjust(2)} {nama}\n"

    # Proses jadwal hari ini
    if rules["today_shifts"]:
        row_day = today_day
        data_today = await get_jadwal_shift_tgl(session_db, today_str)
        await process_data(data_today, rules["today_shifts"])

    # Proses jadwal kemarin jika diperlukan
    if rules["prev_day"]:
        row_day = prev_day_idx
        data_prev = await get_jadwal_shift_tgl(session_db, prev_str)
        await process_data(data_prev, rules["prev_shifts"])

    # Format pesan
    header = (
        "REGIONAL EDP 1 | On Shift\n"
        f"{now.strftime('%d %B %Y %H:%M')}\n"
        "--------------------------------\n\n"
    )

    text_message = header
    if suop_on: text_message += f"[SUOP - Support Operasional]\n{suop_on}\n"
    if simprog: text_message += f"[SUOP - Simulasi Program]\n{simprog}\n"
    if spvmgr: text_message += f"[Supervisor]\n{spvmgr}\n"
    text_message += f"[Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}]"

    return f"<pre>{text_message}</pre>"


# --------------------------------------
# Fungsi Jadwal Saya (User)
# --------------------------------------
async def get_jadwal_saya(session_db, nik: str):
    now = datetime.now()
    bulan, tahun, hari_ini = now.month, now.year, now.day

    data = await get_jadwal_shift_saya(session_db, nik)
    if not data:
        return "Data tidak ditemukan"

    shifts = {tgl: data.get(f"s_{str(tgl).zfill(2)}","") for tgl in range(1,32)}

    def get_nama_hari(tgl: int) -> str:
        idx = int(datetime(tahun, bulan, tgl).strftime("%w"))
        return LIST_NAMA_HARI_TIGA[idx]

    def get_nama_shift(shift) -> str:
        if shift in ("", None): return ""
        if shift in ("L", 0): return "LIBUR"
        if shift == "C": return "CUTI"
        try:
            shift = int(shift)
        except ValueError:
            return str(shift)
        if shift == 2: return "SIANG"
        if shift == 3: return "MALAM"
        if shift <= 11: return "PAGI"
        if shift <= 15: return "SIANG"
        if shift <= 17: return "SORE"
        return "MALAM"

    def format_cell(tgl: int) -> str:
        shift = shifts.get(tgl,"")
        nama_shift = get_nama_shift(shift)
        prefix = ">" if tgl == hari_ini else " "
        shift_col = str(shift).rjust(2)
        shift_full = f"{shift_col} {nama_shift}"
        return f"{prefix}{str(tgl).rjust(2)}|{get_nama_hari(tgl).center(5)}|{shift_full.ljust(10)}"

    body = ""

    for start in range(1, 29, 14):  # 1 dan 15
        for i in range(7):
            kiri = start + i
            kanan = kiri + 7

            if kiri > 28:
                continue

            line = format_cell(kiri)
            if kanan <= 28:
                line += format_cell(kanan)

            body += line + "\n"

        body += "\n"


    for tgl in (29,30,31):
        if shifts.get(tgl):
            body += format_cell(tgl) + "|\n"

    header_waktu = f"{LIST_NAMA_BULAN[bulan-1]} {tahun}".ljust(17) + "| " + data.get("nama_personil","").ljust(20)
    text_message = (
        f"<pre>\n"
        f"{'REGIONAL EDP 1'.ljust(17)}| Jadwal Saya\n"
        f"{header_waktu}\n"
        "--------------------------------\n\n"
        "TGL| DAY |SHIFT     TGL| DAY |SHIFT\n"
        "--------------------------------------\n"
        f"{body}"
        f"[Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}]\n"
        f"</pre>"
    )

    return text_message