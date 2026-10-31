from __future__ import annotations

import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .aladhan import AladhanClient
from .config import Config
from .db import Database
from .handlers import router
from .health import start_health_server
from .reminders import ReminderService

log = logging.getLogger("salah")

COMMANDS = {
    "ar": [
        ("times", "مواقيت اليوم"),
        ("next", "الصلاة القادمة"),
        ("qibla", "اتجاه القبلة"),
        ("morning", "أذكار الصباح"),
        ("evening", "أذكار المساء"),
        ("settings", "الإعدادات"),
        ("help", "المساعدة"),
    ],
    "en": [
        ("times", "Today's prayer times"),
        ("next", "Next prayer"),
        ("qibla", "Qibla direction"),
        ("morning", "Morning adhkar"),
        ("evening", "Evening adhkar"),
        ("settings", "Settings"),
        ("help", "Help"),
    ],
}


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS["en"]])
    await bot.set_my_commands(
        [BotCommand(command=c, description=d) for c, d in COMMANDS["ar"]], language_code="ar"
    )


async def run() -> None:
    cfg = Config.from_env()
    db = Database(cfg.db_path)
    await db.connect()

    bot = Bot(cfg.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    async with aiohttp.ClientSession() as http:
        api = AladhanClient(http)
        dp.workflow_data.update(db=db, cfg=cfg, api=api)

        health = await start_health_server(cfg.port)
        reminders = asyncio.create_task(ReminderService(bot, db, api).run())
        try:
            await set_commands(bot)
            me = await bot.get_me()
            log.info("Started as @%s", me.username)
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            reminders.cancel()
            await asyncio.gather(reminders, return_exceptions=True)
            await health.cleanup()
            await bot.session.close()
            await db.close()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        log.info("Stopped")


if __name__ == "__main__":
    main()
