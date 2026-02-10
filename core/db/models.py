from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, String
from sqlalchemy import BigInteger

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime


class LogChatDB(SQLModel, table=True):
    __tablename__ = "telegram_logchat"

    sys_id: Optional[int] = Field(default=None, primary_key=True)

    telegram_date: datetime | None
    chat_type: str | None
    chat_title: str | None
    chat_id: int = Field(sa_column=Column(BigInteger))
    message_id: int = Field(sa_column=Column(BigInteger))

    from_id: int = Field(sa_column=Column(BigInteger))
    from_first_name: str | None
    from_last_name: str | None
    from_username: str | None

    message_text: str | None = Field(sa_column=Column(String(4096), nullable=True))

    content_type: str | None
    file_id: str | None

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False))


class TelegramIDDB(SQLModel, table=True):
    __tablename__ = 'telegram_id'

    sys_id: int = Field(default=None, primary_key=True)

    telegram_id: int = Field(sa_column=Column(BigInteger, nullable=False, unique=True))
    first_name: str | None = Field(max_length=100)
    last_name: str | None = Field(max_length=100, nullable=True)
    username: str | None = Field(max_length=100)

    nik: str | None = Field(max_length=10)
    nama_lengkap: str | None = Field(max_length=100)

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False))

    verified_at: datetime | None = Field(sa_column=Column(DateTime, nullable=True))


class SiagadanReplikasiDB(SQLModel, table=True):
    __tablename__ = 'siaga_dan_replikasi'

    id_work: str = Field(max_length=30, primary_key=True)
    tipe: str = Field(max_length=13)
    proses: str = Field(max_length=9)
    nomor_co: str = Field(max_length=10, nullable=True)
    kdtk: str = Field(max_length=4)
    nama_toko: str = Field(max_length=60, nullable=True)
    cabang: str = Field(max_length=60, nullable=True)
    station: str = Field(max_length=2, nullable=True)
    datetime_start: datetime = Field(nullable=True)
    datetime_end: datetime = Field(nullable=True)
    alasan: str = Field(max_length=1000, nullable=True)
    alasan2: str = Field(max_length=1000, nullable=True)
    status: str = Field(max_length=50)
    keterangan: str = Field(max_length=1000, nullable=True)
    lampiran_file: str = Field(max_length=1000, nullable=True)
    pelaksana_nik: str = Field(max_length=10)
    pelaksana_nama: str = Field(max_length=60)
    telegram_id: str

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False))


class BackupRestoreDB(SQLModel, table=True):
    __tablename__ = 'backup_restore'

    id_work: str = Field(max_length=30, primary_key=True)
    tipe: str = Field(max_length=20)

    nomor_co: str = Field(max_length=10, nullable=True)
    kdtk: str = Field(max_length=4)
    nama_toko: str = Field(max_length=60, nullable=True)
    cabang: str = Field(max_length=60, nullable=True)

    alasan: str = Field(max_length=600, nullable=True)
    ibdata_mb_awal: int = Field(nullable=True)
    ibdata_mb_akhir: int

    restore_from_db_replikasi: str = Field(max_length=600, nullable=True)
    restore_from_bckmysql: str = Field(max_length=600, nullable=True)
    restore_from_dthr: str = Field(max_length=600, nullable=True)
    restore_from_posrealtime: str = Field(max_length=600, nullable=True)
    restore_from_file_jual: str = Field(max_length=600, nullable=True)

    datetime_end: datetime = Field(nullable=True)
    keterangan: str = Field(max_length=1000, nullable=True)

    cek_trigger: str = Field(max_length=36, nullable=True)
    cek_relasi_tabel: str = Field(max_length=36, nullable=True)
    autov2: str = Field(max_length=36, nullable=True)
    hu_stok: str = Field(max_length=36, nullable=True)
    hu_spd: str = Field(max_length=36, nullable=True)
    hu_pkm: str = Field(max_length=36, nullable=True)

    lampiran_file: str = Field(max_length=300, nullable=True)
    pelaksana_nik: str = Field(max_length=10)
    pelaksana_nama: str = Field(max_length=60)
    telegram_id: str

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False))


class JadwalShiftDB(SQLModel, table=True):
    __tablename__ = 'jadwal_shift'
    
    sys_id: int = Field(default=None, primary_key=True)

    nik: str = Field(max_length=10)
    username: str = Field(max_length=50)
    nama_personil: str = Field(max_length=50)
    departemen: str = Field(max_length=30)
    divisi: str = Field(max_length=30)
    sub_divisi: str = Field(max_length=30)
    kd_div: str = Field(max_length=30)
    jabatan: str = Field(max_length=30)
    periode: str = Field(max_length=4)
    s_01: str = Field(max_length=4)
    s_02: str = Field(max_length=4)
    s_03: str = Field(max_length=4)
    s_04: str = Field(max_length=4)
    s_05: str = Field(max_length=4)
    s_06: str = Field(max_length=4)
    s_07: str = Field(max_length=4)
    s_08: str = Field(max_length=4)
    s_09: str = Field(max_length=4)
    s_10: str = Field(max_length=4)
    s_11: str = Field(max_length=4)
    s_12: str = Field(max_length=4)
    s_13: str = Field(max_length=4)
    s_14: str = Field(max_length=4)
    s_15: str = Field(max_length=4)
    s_16: str = Field(max_length=4)
    s_17: str = Field(max_length=4)
    s_18: str = Field(max_length=4)
    s_19: str = Field(max_length=4)
    s_20: str = Field(max_length=4)
    s_21: str = Field(max_length=4)
    s_22: str = Field(max_length=4)
    s_23: str = Field(max_length=4)
    s_24: str = Field(max_length=4)
    s_25: str = Field(max_length=4)
    s_26: str = Field(max_length=4)
    s_27: str = Field(max_length=4)
    s_28: str = Field(max_length=4)
    s_29: str = Field(max_length=4)
    s_30: str = Field(max_length=4)
    s_31: str = Field(max_length=4)

    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now, nullable=False))
