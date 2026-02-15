from collections import defaultdict
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from sqlalchemy import text

from core.config import settings
from core.db.database import get_session


QUERY = """
SELECT m.KDTK,
       m.TIPE,
       m.STATION,
       m.datetime_end AS MULAI
FROM siaga_dan_replikasi m
WHERE m.proses='PEMBUATAN'
  AND m.datetime_end>=DATE_SUB(NOW(), INTERVAL 24 HOUR)
  AND m.datetime_end<=DATE_SUB(NOW(), INTERVAL 2 HOUR)
  AND NOT EXISTS (
      SELECT 1
      FROM siaga_dan_replikasi b
      WHERE b.kdtk=m.kdtk
        AND b.tipe=m.tipe
        AND b.station<=>m.station
        AND b.proses!='PEMBUATAN'
        AND b.datetime_end>m.datetime_end
  )
ORDER BY m.TIPE, m.datetime_end DESC
"""


async def kirim_laporan(bot: Bot):
    async with get_session() as session:
        result = await session.execute(text(QUERY))
        rows = result.fetchall()

        if not rows:
            return

        grouped = defaultdict(list)

        for row in rows:
            tipe_clean = (row.TIPE or "").strip().upper()
            grouped[tipe_clean].append(row)

        pesan = "<b>⌛️ SIAGA DAN REPLIKASI</b>\n\n"

        for tipe, items in grouped.items():

            judul = tipe.replace("_", " ")

            pesan += f"<b>{judul}</b>\n"

            for i, r in enumerate(items, start=1):

                station_part = f" / {r.STATION}" if r.STATION else ""

                pesan += (
                    f"{i}. {r.KDTK} / "
                    f"{r.MULAI.strftime('%H:%M')}"
                    f"{station_part}\n"
                )

            pesan += "\n"

        if len(pesan) > 4000:
            pesan = pesan[:4000] + "\n\n... (data terpotong)"

        await bot.send_message(settings.GROUP_SUOP_NOTIFY, pesan)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")

    trigger = CronTrigger(hour="0-23/2", minute=10)

    scheduler.add_job(
        kirim_laporan,
        trigger,
        args=[bot],
        id="laporan_siaga_replikasi",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
