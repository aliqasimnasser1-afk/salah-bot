"""Drive the real handlers with synthetic updates and a fake Telegram session."""

from datetime import date, datetime, timezone

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage
from aiogram.types import Chat, Message, Update, User as TgUser

from bot.aladhan import AladhanError
from bot.config import Config
from bot.db import Database
from bot.handlers import router

from .conftest import SAMPLE
from bot.aladhan import parse_timings


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.calls = []

    async def make_request(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, (SendMessage, EditMessageText)):
            return Message(
                message_id=len(self.calls),
                date=datetime.now(timezone.utc),
                chat=Chat(id=1, type="private"),
                text=getattr(method, "text", ""),
            )
        return True

    async def stream_content(self, *a, **k):  # pragma: no cover
        yield b""

    async def close(self):
        pass

    def texts(self):
        return [c.text for c in self.calls if isinstance(c, SendMessage | EditMessageText)]


class FakeApi:
    """Stands in for AladhanClient so no network is needed."""

    def __init__(self):
        self.session = None
        self.fail = False

    async def by_coordinates(self, lat, lon, method, day):
        if self.fail:
            raise AladhanError("down")
        return parse_timings(SAMPLE, day)

    async def for_user(self, lat, lon, method, tz, now):
        return await self.by_coordinates(lat, lon, method, now.date())

    async def next_prayer(self, lat, lon, method, tz, now):
        timings = await self.by_coordinates(lat, lon, method, now.date())
        return "Fajr", timings.times["Fajr"], timings


@pytest.fixture
async def env(tmp_path, monkeypatch):
    from bot import handlers
    from bot.geocode import Place

    async def fake_reverse(session, lat, lon, lang="ar"):
        return "Ha'il, Saudi Arabia"

    async def fake_find(session, query, lang="ar"):
        if query == "nowhere":
            raise AladhanError("Place not found")
        return Place(name=f"{query}, Saudi Arabia", lat=27.52, lon=41.69)

    monkeypatch.setattr(handlers, "reverse_place", fake_reverse)
    monkeypatch.setattr(handlers, "find_place", fake_find)

    db = Database(str(tmp_path / "h.db"))
    await db.connect()
    session = FakeSession()
    bot = Bot("123456:TEST", session=session)
    dp = Dispatcher(storage=MemoryStorage())
    router._parent_router = None  # the module-level router is reused across test dispatchers
    dp.include_router(router)
    api = FakeApi()
    dp.workflow_data.update(db=db, cfg=Config(token="x", admin_ids=frozenset({1})), api=api)

    counter = iter(range(1, 10_000))

    async def send(text=None, location=None, callback=None):
        user = TgUser(id=1, is_bot=False, first_name="T", language_code="ar")
        chat = Chat(id=1, type="private")
        if callback:
            from aiogram.types import CallbackQuery

            msg = Message(message_id=5, date=datetime.now(timezone.utc), chat=chat, text="x")
            update = Update(
                update_id=next(counter),
                callback_query=CallbackQuery(id="1", from_user=user, chat_instance="c", data=callback, message=msg),
            )
        else:
            entities = None
            if text and text.startswith("/"):
                from aiogram.types import MessageEntity

                entities = [MessageEntity(type="bot_command", offset=0, length=len(text.split()[0]))]
            msg = Message(
                message_id=next(counter), date=datetime.now(timezone.utc), chat=chat, from_user=user,
                text=text, entities=entities, location=location,
            )
            update = Update(update_id=next(counter), message=msg)
        await dp.feed_update(bot, update)

    yield send, session, db, api
    await db.close()


async def test_start_asks_for_language_first(env):
    send, session, db, _ = env
    await send("/start")
    assert "Choose your language" in session.texts()[-1]
    assert not (await db.get_user(1)).lang_chosen


async def test_choosing_language_then_asks_for_location(env):
    send, session, db, _ = env
    await send("/start")
    await send(callback="l:en")
    user = await db.get_user(1)
    assert user.lang == "en" and user.lang_chosen
    assert "Choose your region" in session.texts()[-1]


async def test_arabic_choice_gets_arabic_welcome(env):
    send, session, db, _ = env
    await send("/start")
    await send(callback="l:ar")
    assert "اختر منطقتك" in session.texts()[-1]


async def test_unknown_language_code_is_ignored(env):
    send, session, db, _ = env
    await send("/start")
    await send(callback="l:xx")
    assert not (await db.get_user(1)).lang_chosen


async def test_typing_a_city_before_choosing_language_shows_picker(env):
    send, session, db, _ = env
    await send("Jeddah")
    assert "Choose your language" in session.texts()[-1]


async def test_returning_user_skips_language_picker(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=24.4672, longitude=39.6111))
    await send("/start")
    assert "Choose your language" not in session.texts()[-1]


async def test_shared_location_is_saved(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send("/start")
    await send(location=Location(latitude=24.4672, longitude=39.6111))
    user = await db.get_user(1)
    assert user.has_location and user.tz == "Asia/Riyadh"
    assert any("Asia/Riyadh" in t for t in session.texts())


async def test_times_and_qibla_after_location(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=24.4672, longitude=39.6111))
    await send("/times")
    assert "الفجر" in session.texts()[-1] and "04:41" in session.texts()[-1]
    await send("/qibla")
    assert "°" in session.texts()[-1]
    await send("/morning")
    assert "آية الكرسي" in " ".join(session.texts())


async def test_times_without_location_asks_for_it(env):
    send, session, *_ = env
    await send("/times")
    assert "موقعك" in session.texts()[-1]


async def test_service_failure_is_reported_not_raised(env):
    from aiogram.types import Location

    send, session, db, api = env
    await send(location=Location(latitude=24.4672, longitude=39.6111))
    api.fail = True
    await send("/times")
    assert "لا تستجيب" in session.texts()[-1]


async def test_settings_callbacks_persist(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=24.4672, longitude=39.6111))
    await send(callback="sr:30")
    await send(callback="sm:3")
    await send(callback="s:adhkar")
    await send(callback="s:lang")
    user = await db.get_user(1)
    assert (user.remind_before, user.method, user.adhkar, user.lang) == (30, 3, False, "en")


async def test_invalid_callback_values_are_ignored(env):
    send, session, db, _ = env
    await send("/start")
    await send(callback="sr:9999")
    await send(callback="sm:12345")
    user = await db.get_user(1)
    assert (user.remind_before, user.method) == (10, 4)


async def test_stats_only_for_admins(env):
    send, session, db, _ = env
    await send("/start")
    await send("/stats")
    assert "المستخدمون" in session.texts()[-1]


async def test_shared_location_shows_city_name_and_confirm_buttons(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=27.52, longitude=41.69))
    assert "Ha&#x27;il, Saudi Arabia" in session.texts()[-1]
    assert (await db.get_user(1)).place == "Ha'il, Saudi Arabia"
    last = [c for c in session.calls if isinstance(c, SendMessage)][-1]
    data = [b.callback_data for row in last.reply_markup.inline_keyboard for b in row]
    assert data == ["loc:ok", "loc:change"]


async def test_change_city_flow(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=24.7, longitude=46.7))  # approximate desktop location
    await send(callback="loc:change")
    assert "اختر منطقتك" in session.texts()[-1]
    await send(callback="r:other")
    assert "اسم مدينتك" in session.texts()[-1]
    await send("حائل")
    user = await db.get_user(1)
    assert user.place == "حائل, Saudi Arabia" and (user.lat, user.lon) == (27.52, 41.69)


async def test_unknown_city_keeps_old_location(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=24.7, longitude=46.7))
    await send(callback="loc:change")
    await send(callback="r:other")
    await send("nowhere")
    assert (await db.get_user(1)).lat == 24.7
    assert "لم أستطع" in session.texts()[-1]


async def test_confirming_shows_menu_with_next_prayer(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=27.52, longitude=41.69))
    await send(callback="loc:ok")
    text = session.texts()[-1]
    assert "Ha&#x27;il" in text and "الصلاة القادمة" in text and "04:41" in text


async def test_start_for_returning_user_shows_next_prayer(env):
    from aiogram.types import Location

    send, session, db, _ = env
    await send(location=Location(latitude=27.52, longitude=41.69))
    await send("/start")
    assert "الصلاة القادمة" in session.texts()[-1]


async def test_adhkar_menu_opens_in_place_without_new_messages(env):
    send, session, db, _ = env
    await send("/start")
    before = len([c for c in session.calls if isinstance(c, SendMessage)])
    await send(callback="m:morning")
    after = len([c for c in session.calls if isinstance(c, SendMessage)])
    assert after == before  # the existing message is edited, nothing new appears below
    edit = [c for c in session.calls if isinstance(c, EditMessageText)][-1]
    assert "آية الكرسي" in edit.text and "1/" in edit.text


async def test_adhkar_paging_and_wraparound(env):
    from bot import adhkar

    send, session, db, _ = env
    await send(callback="a:morning:1")
    assert "الإخلاص" in session.texts()[-1]
    last = adhkar.total("morning") - 1
    await send(callback=f"a:morning:{last}")
    edit = [c for c in session.calls if isinstance(c, EditMessageText)][-1]
    data = [b.callback_data for row in edit.reply_markup.inline_keyboard for b in row]
    assert "a:morning:0" in data  # "next" from the last card wraps to the first
    await send(callback="a:evening:0")
    assert "أذكار المساء" in session.texts()[-1]


async def test_adhkar_callback_rejects_garbage(env):
    send, session, db, _ = env
    calls_before = len(session.calls)
    await send(callback="a:evil:1")
    await send(callback="a:morning:notanumber")
    assert not any(isinstance(c, EditMessageText) for c in session.calls[calls_before:])


async def test_region_then_city_sets_location_and_opens_menu(env):
    from bot.regions import REGIONS

    send, session, db, _ = env
    await send("/start")
    await send(callback="l:ar")
    assert "اختر منطقتك" in session.texts()[-1]

    hail = next(i for i, r in enumerate(REGIONS) if r.en == "Ha'il")
    await send(callback=f"r:{hail}")
    assert "حائل" in session.texts()[-1] and "اختر مدينتك" in session.texts()[-1]

    await send(callback=f"c:{hail}:0")
    user = await db.get_user(1)
    assert user.has_location and (user.lat, user.lon) == (27.5219, 41.6907)
    assert user.place == "حائل, حائل"
    assert "الصلاة القادمة" in session.texts()[-1]  # straight to the menu with the next prayer


async def test_english_user_sees_english_region_and_city_names(env):
    from bot.regions import REGIONS

    send, session, db, _ = env
    await send("/start")
    await send(callback="l:en")
    madinah = next(i for i, r in enumerate(REGIONS) if r.en == "Madinah")
    await send(callback=f"r:{madinah}")
    assert "Choose your city" in session.texts()[-1]
    await send(callback=f"c:{madinah}:1")  # Yanbu
    assert (await db.get_user(1)).place == "Yanbu, Madinah"


async def test_region_picker_offers_gps_other_and_back(env):
    send, session, db, _ = env
    await send("/start")
    await send(callback="l:ar")
    await send(callback="r:gps")
    assert "أرسل" in session.texts()[-1] or "موقعك" in session.texts()[-1]
    await send(callback="r:0")
    await send(callback="r:back")
    assert "اختر منطقتك" in session.texts()[-1]


async def test_bad_region_and_city_callbacks_are_ignored(env):
    send, session, db, _ = env
    await send("/start")
    for data in ("r:999", "r:abc", "c:0:99", "c:99:0", "c:x:y", "c:1"):
        await send(callback=data)
    assert not (await db.get_user(1)).has_location


async def test_city_pick_survives_prayer_service_outage(env):
    send, session, db, api = env
    await send("/start")
    api.fail = True
    await send(callback="c:0:0")
    assert not (await db.get_user(1)).has_location
    api.fail = False
    await send(callback="c:0:0")
    assert (await db.get_user(1)).has_location
