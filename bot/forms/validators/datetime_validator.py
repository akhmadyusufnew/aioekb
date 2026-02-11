from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

MAX_HISTORY_MONTH = 6


def parse_datetime_input(text: str, now: datetime) -> Optional[datetime]:
    try:
        if len(text)==19:
            # YYYY-MM-DD HH:MM:SS
            return datetime.fromisoformat(text)

        elif len(text)==20:
            # DD-Mmm-YYYY HH:MM:SS
            return datetime.strptime(text, '%d-%b-%Y %H:%M:%S')
        
        if len(text) == 5 and text[2] == ":":
            hour, minute = map(int, text.split(":"))

        elif len(text) == 4 and text.isnumeric():
            hour, minute = int(text[:2]), int(text[2:])
        
        else:
            return None

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        
        return datetime.strptime(
            f"{now:%Y-%m-%d} {hour:02d}:{minute:02d}:00",
            "%Y-%m-%d %H:%M:%S"
        )
    
    except Exception:
        return None


async def verify_datetime(message: Message, state: FSMContext) -> Optional[datetime]:
    text = message.text.strip()

    data_state = await state.get_data()
    datetime_start: Optional[datetime] = data_state.get("datetime_start")

    now = datetime.now()
    earliest_time = now - relativedelta(months=MAX_HISTORY_MONTH)

    waktu = parse_datetime_input(text, now)

    if not waktu:
        return None

    if datetime_start and waktu < datetime_start:
        return None

    if not (earliest_time <= waktu <= now):
        return None

    return waktu
