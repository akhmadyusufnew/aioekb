import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.db.database import init_db

from bot.scheduler import setup_scheduler

from bot.forms.handlers import (
    registrasi_account_router,
    backup_restore_router,
    restore_data_router,
    start_posreplikasi_router,
    tutup_posreplikasi_router,
    start_possiaga_router,
    tutup_possiaga_router,
)

from bot.groups import (
    monitoring_klik_router,
    support_toko_router,
)

from bot.handlers import router as router_general


TOKEN = settings.BOT_TOKEN


async def main() -> None:
    await init_db()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    dp.include_router(registrasi_account_router)

    dp.include_router(backup_restore_router)
    dp.include_router(restore_data_router)
    dp.include_router(start_posreplikasi_router)
    dp.include_router(tutup_posreplikasi_router)
    dp.include_router(start_possiaga_router)
    dp.include_router(tutup_possiaga_router)

    dp.include_router(monitoring_klik_router)
    dp.include_router(support_toko_router)

    dp.include_router(router_general)

    setup_scheduler(bot)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())