import json
import logging

from pathlib import Path

DATA_MASTER_TOKO_PATH = Path("data/DataMasterToko.json")


def load_master_toko() -> list[dict]:
    if not DATA_MASTER_TOKO_PATH.exists():
        logging.error(f"{DATA_MASTER_TOKO_PATH} not found")
        return []
    
    try:
        with DATA_MASTER_TOKO_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logging.exception(f"Failed to read {DATA_MASTER_TOKO_PATH}")
        return []


