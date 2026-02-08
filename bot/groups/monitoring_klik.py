import json
import random

from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import Message, ReactionTypeEmoji

from core.telegram import handle_exception
from core.config import settings
from core.db.database import get_session
from core.db.repository import log_telegram_event

REACTIONS = ["🔥", "❤️", "🙏", "🤩", "🤝", "👌", "💯"]

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_TOKO_FILE = BASE_DIR / "data" / "DataMasterToko.json"


# ---------- Utils ----------

def load_data_master_toko():
    try:
        with open(DATA_TOKO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan: {DATA_TOKO_FILE}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON rusak: {e}")

    return []


def get_toko_by_kdtk(kdtk: str, data_json):
    kdtk = kdtk.upper()
    for toko in data_json:
        if toko.get("kdtk") == kdtk:
            return f"{toko['cabang']} / {kdtk} - {toko['namatoko']}".upper()
    return None


async def send_and_log(session_db, message: Message, text: str):
    msg = await message.answer(
        text,
        reply_to_message_id=message.message_id,
        parse_mode="Markdown"
    )
    await log_telegram_event(session_db, msg)


# ---------- Command Config ----------

COMMANDS = {
    "/koneksioff": {
        "slice": slice(11, 15),
        "template": "`{desc}, mohon di bantu koneksinya off karena ada pesanan istore pending di server. Terimakasih`",
    },
    "/underlaying": {
        "slice": slice(12, 16),
        "template": "`{desc}, mohon di bantu koneksi ke posrealtime underlying karena ada pesanan istore pending di server. Terimakasih`",
    },
}


router = Router()


@router.message(F.chat.id == settings.GROUP_MONITORING_KLIK_ID)
async def handle_group_monitoring_klik(message: Message, bot: Bot):

    try:
        async with get_session() as session_db:
            await log_telegram_event(session_db, message)

            if not message.text:
                return

            data = message.text.strip().lower()
            data_json = load_data_master_toko()

            # Handle text commands
            for cmd, cfg in COMMANDS.items():
                if data.startswith(cmd):
                    kdtk = message.text[cfg["slice"]].strip()
                    desc = get_toko_by_kdtk(kdtk, data_json)

                    if not desc:
                        await send_and_log(session_db, message, f"Kode toko {kdtk} tidak ditemukan.")
                        return

                    text = cfg["template"].format(desc=desc)
                    await send_and_log(session_db, message, text)
                    return

            # Handle /clear
            if data.startswith("/clear"):
                emoji = random.choice(REACTIONS)
                await message.react([ReactionTypeEmoji(emoji=emoji)])

    except Exception as e:
        await handle_exception(message, bot, e)