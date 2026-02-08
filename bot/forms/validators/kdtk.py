from typing import Optional, Dict, Any
from aiogram.types import Message

from ._master_toko import load_master_toko

VALID_KDTK_PREFIX = {"F", "R", "T"}


async def verify_kdtk(message: Message) -> Optional[Dict[str, Any]]:
    data = message.text.upper().strip()

    if len(data) != 4 or data[0] not in VALID_KDTK_PREFIX:
        return None

    master_toko = load_master_toko()

    for row in master_toko:
        if row.get("kdtk") == data:
            return {
                "kdtk": data,
                "nama_toko": row.get("namatoko"),
                "cabang": row.get("cabang"),
            }

    return {
        "kdtk": data,
        "nama_toko": None,
        "cabang": None
    }