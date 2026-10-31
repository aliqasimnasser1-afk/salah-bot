from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramAPIError

from . import adhkar
from .aladhan import AladhanClient, AladhanError
from .db import Database, User
from .events import Event, due_events
from .texts import ICONS, prayer_name, t

log = logging.getLogger(__name__)

TICK_SECONDS = 30
SEND_GAP = 0.05  # stay far below Telegram's ~30 messages/second limit


class ReminderService:
    """Every 30 seconds, finds due notifications and sends each exactly once."""

    def __init__(self, bot: Bot, db: Database, api: AladhanClient) -> None:
        self.bot, self.db, self.api = bot, db, api
        self._last_prune = datetime.now(timezone.utc).date()

    async def run(self) -> None:
        log.info("Reminder service started")
        while True:
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Reminder tick failed")
            await asyncio.sleep(TICK_SECONDS)

    async def tick(self) -> None:
        now = datetime.now(timezone.utc)
        for user in await self.db.located_users():
            try:
                timings = await self.api.for_user(user.lat, user.lon, user.method, user.tz, now)
            except AladhanError as exc:
                log.warning("Skipping user %s this tick: %s", user.user_id, exc)
                continue
            for event in due_events(now, timings, user.remind_before, user.adhkar):
                if await self.db.mark_sent(user.user_id, event.key):
                    await self._deliver(user, event)
                    await asyncio.sleep(SEND_GAP)
        today = now.date()
        if today != self._last_prune:
            await self.db.prune_sent()
            self._last_prune = today

    async def _deliver(self, user: User, event: Event) -> None:
        try:
            if event.kind in {"morning", "evening"}:
                for chunk in adhkar.render(event.kind, user.lang):
                    await self._send(user.user_id, chunk)
            else:
                name = prayer_name(user.lang, event.prayer)
                icon = ICONS[event.prayer]
                if event.kind == "remind":
                    text = t(user.lang, "remind_msg", n=user.remind_before, name=name, icon=icon)
                else:
                    text = t(user.lang, "adhan_msg", name=name, icon=icon)
                await self._send(user.user_id, text)
        except TelegramForbiddenError:
            log.info("User %s blocked the bot; removing", user.user_id)
            await self.db.delete_user(user.user_id)
        except TelegramAPIError as exc:
            log.warning("Could not notify %s: %s", user.user_id, exc)

    async def _send(self, chat_id: int, text: str) -> None:
        try:
            await self.bot.send_message(chat_id, text)
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            await self.bot.send_message(chat_id, text)
