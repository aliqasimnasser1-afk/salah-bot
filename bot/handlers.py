from __future__ import annotations

import logging
from datetime import datetime, timezone
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from . import adhkar, keyboards, qibla
from .aladhan import DISPLAY, AladhanClient, AladhanError
from .geocode import find_place, reverse_place
from .regions import REGIONS
from .config import Config
from .db import Database, User
from .texts import (
    ICONS, LANGUAGE_PROMPT, LANGUAGES, METHODS, REMINDER_CHOICES,
    format_clock, format_left, prayer_name, t,
)

log = logging.getLogger(__name__)
router = Router()


class Flow(StatesGroup):
    waiting_location = State()


# ---------------------------------------------------------------- helpers

def guess_lang(code: str | None) -> str:
    return "en" if code and not code.lower().startswith("ar") else "ar"


async def ensure_user(db: Database, cfg: Config, tg_user) -> User:
    user = await db.get_user(tg_user.id)
    if user is None:
        user = await db.create_user(tg_user.id, guess_lang(tg_user.language_code), cfg.default_method)
    return user


async def show(event: Message | CallbackQuery, text: str, kb=None) -> None:
    """Reply to a message, or edit the message that holds the pressed button."""
    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb)
        except TelegramBadRequest as exc:
            if "not modified" not in str(exc):
                raise
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


async def ask_language(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(LANGUAGE_PROMPT, reply_markup=keyboards.language_kb())


async def ask_region(event: Message | CallbackQuery, user: User, state: FSMContext) -> None:
    """First step of setup: pick a Saudi region (or share a location / type another city)."""
    await state.clear()
    await show(event, t(user.lang, "pick_region"), keyboards.regions_kb(user.lang))


async def ask_location(event: Message | CallbackQuery, user: User, state: FSMContext) -> None:
    await state.set_state(Flow.waiting_location)
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer(t(user.lang, "welcome"), reply_markup=keyboards.location_kb(user.lang))
    if isinstance(event, CallbackQuery):
        await event.answer()


# ---------------------------------------------------------------- screens

async def menu_text(api: AladhanClient, user: User) -> str:
    """Main-menu text: title, saved place and the next prayer with its countdown."""
    lines = [t(user.lang, "menu_title")]
    if user.place:
        lines.append(t(user.lang, "menu_place", place=escape(user.place)))
    if user.has_location:
        try:
            now = datetime.now(timezone.utc)
            name, at, _ = await api.next_prayer(user.lat, user.lon, user.method, user.tz, now)
            lines += [
                "",
                t(user.lang, "next_line", name=prayer_name(user.lang, name), icon=ICONS[name],
                  left=format_left(user.lang, at - now)),
                f"🕐 <code>{format_clock(at)}</code>",
            ]
        except AladhanError:
            log.warning("Could not load the next prayer for the menu")
    return "\n".join(lines)


async def show_menu(event: Message | CallbackQuery, user: User, api: AladhanClient) -> None:
    await show(event, await menu_text(api, user), keyboards.main_menu(user.lang))


async def times_text(api: AladhanClient, user: User) -> str:
    now = datetime.now(timezone.utc)
    timings = await api.for_user(user.lat, user.lon, user.method, user.tz, now)
    next_name, next_at, _ = await api.next_prayer(user.lat, user.lon, user.method, user.tz, now)
    hijri = timings.hijri_ar if user.lang == "ar" else timings.hijri_en

    lines = [t(user.lang, "times_title"), f"📅 {timings.day:%Y-%m-%d} • {hijri}", ""]
    for name in DISPLAY:
        at = timings.times[name]
        marker = "👉" if name == next_name and at == next_at else ("✔️" if at <= now else "▫️")
        lines.append(f"{marker} {ICONS[name]} <b>{prayer_name(user.lang, name)}</b> — <code>{format_clock(at)}</code>")
    lines += ["", t(user.lang, "next_line", name=prayer_name(user.lang, next_name),
                    icon=ICONS[next_name], left=format_left(user.lang, next_at - now))]
    return "\n".join(lines)


async def next_text(api: AladhanClient, user: User) -> str:
    now = datetime.now(timezone.utc)
    name, at, _ = await api.next_prayer(user.lat, user.lon, user.method, user.tz, now)
    return "\n".join([
        t(user.lang, "next_title"),
        "",
        f"{ICONS[name]} <b>{prayer_name(user.lang, name)}</b> — <code>{format_clock(at)}</code>",
        t(user.lang, "next_line", name=prayer_name(user.lang, name), icon=ICONS[name],
          left=format_left(user.lang, at - now)),
    ])


def qibla_text(user: User) -> str:
    deg = qibla.bearing(user.lat, user.lon)
    return t(user.lang, "qibla", deg=deg, dir=qibla.compass(deg, user.lang),
             km=qibla.distance_km(user.lat, user.lon))


def settings_text(user: User) -> str:
    remind = t(user.lang, "off") if user.remind_before == 0 else t(user.lang, "minutes", n=user.remind_before)
    body = t(
        user.lang, "settings_body",
        method=METHODS.get(user.method, METHODS[4])[user.lang],
        remind=remind,
        adhkar=t(user.lang, "on" if user.adhkar else "off"),
        place=escape(user.place or "—"),
        tz=user.tz or "—",
    )
    return f"{t(user.lang, 'settings_title')}\n\n{body}"


async def run_screen(event: Message | CallbackQuery, user: User, api: AladhanClient, name: str) -> None:
    """Render one of the main screens, guarding against a missing location or a failing service."""
    lang = user.lang
    if not user.has_location and name in {"times", "next", "qibla"}:
        await show(event, t(lang, "need_location"))
        return
    try:
        if name == "times":
            await show(event, await times_text(api, user), keyboards.back_kb(lang))
        elif name == "next":
            await show(event, await next_text(api, user), keyboards.back_kb(lang))
        elif name == "qibla":
            await show(event, qibla_text(user), keyboards.back_kb(lang))
    except AladhanError:
        log.exception("Prayer-times service failed")
        await show(event, t(lang, "service_down"), keyboards.back_kb(lang))


async def store_location(
    db: Database, api: AladhanClient, user: User, lat: float, lon: float, label: str
) -> bool:
    """Validate a location with the prayer-times service, then persist it. False if the service failed."""
    today = datetime.now(timezone.utc).date()
    try:
        timings = await api.by_coordinates(lat, lon, user.method, today)
    except AladhanError as exc:
        log.warning("Location check failed: %s", exc)
        return False
    await db.update(user.user_id, lat=lat, lon=lon, tz=timings.tz, place=label)
    user.lat, user.lon, user.tz, user.place = lat, lon, timings.tz, label
    return True


async def save_location(
    event: Message, db: Database, api: AladhanClient, user: User,
    *, lat: float | None = None, lon: float | None = None, address: str | None = None,
) -> bool:
    """Resolve a shared location or typed city, store it, and show what was understood to confirm."""
    label = ""
    try:
        if address:
            place = await find_place(api.session, address, user.lang)
            lat, lon, label = place.lat, place.lon, place.name
        else:
            try:
                label = await reverse_place(api.session, lat, lon, user.lang)
            except AladhanError:
                label = f"{lat:.2f}, {lon:.2f}"  # the city name is a nicety; the coordinates are what matter
    except AladhanError as exc:
        log.warning("Location lookup failed: %s", exc)
        await event.answer(t(user.lang, "location_failed"), reply_markup=keyboards.location_kb(user.lang))
        return False
    if not await store_location(db, api, user, lat, lon, label):
        await event.answer(t(user.lang, "location_failed"), reply_markup=keyboards.location_kb(user.lang))
        return False
    await event.answer(
        t(user.lang, "location_saved", place=escape(label), tz=user.tz),
        reply_markup=keyboards.confirm_location_kb(user.lang),
    )
    return True


# ---------------------------------------------------------------- commands

@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    await state.clear()
    if user.has_location:
        await show_menu(message, user, api)
    elif not user.lang_chosen:
        await ask_language(message, state)
    else:
        await ask_region(message, user, state)


@router.message(Command("help"))
async def cmd_help(message: Message, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    await message.answer(t(user.lang, "help"))


@router.message(Command("times", "next", "qibla"))
async def cmd_screens(message: Message, db: Database, cfg: Config, api: AladhanClient) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    name = message.text.lstrip("/").split("@")[0].split()[0].lower()
    await run_screen(message, user, api, name)


@router.message(Command("morning", "evening"))
async def cmd_adhkar(message: Message, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    kind = message.text.lstrip("/").split("@")[0].split()[0].lower()
    await show(message, adhkar.render_item(kind, 0, user.lang), keyboards.adhkar_kb(kind, 0, user.lang))


@router.message(Command("settings"))
async def cmd_settings(message: Message, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    await message.answer(settings_text(user), reply_markup=keyboards.settings_kb(user))


@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database, cfg: Config) -> None:
    if message.from_user.id not in cfg.admin_ids:
        return
    total, located = await db.count_users()
    user = await ensure_user(db, cfg, message.from_user)
    await message.answer(t(user.lang, "stats", total=total, located=located))


# ---------------------------------------------------------------- location input

@router.message(F.location)
async def on_location(message: Message, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    loc = message.location
    if await save_location(message, db, api, user, lat=loc.latitude, lon=loc.longitude):
        await state.clear()


@router.message(F.text, ~F.text.startswith("/"))
async def on_text(message: Message, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, message.from_user)
    if not user.lang_chosen and not user.has_location:
        await ask_language(message, state)
        return
    waiting = await state.get_state() == Flow.waiting_location.state
    if user.has_location and not waiting:
        await message.answer(t(user.lang, "hint_menu"), reply_markup=keyboards.main_menu(user.lang))
        return
    if await save_location(message, db, api, user, address=message.text.strip()[:100]):
        await state.clear()


# ---------------------------------------------------------------- callbacks

@router.callback_query(F.data.startswith("l:"))
async def cb_language(call: CallbackQuery, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    code = call.data.split(":", 1)[1]
    if code not in LANGUAGES:
        await call.answer()
        return
    user.lang = code
    await db.update(user.user_id, lang=code, lang_chosen=1)
    await show(call, f"✅ {LANGUAGES[code]}")
    if user.has_location:
        await call.message.answer(await menu_text(api, user), reply_markup=keyboards.main_menu(code))
    else:
        await call.message.answer(t(code, "pick_region"), reply_markup=keyboards.regions_kb(code))


@router.callback_query(F.data.startswith("m:"))
async def cb_menu(call: CallbackQuery, db: Database, cfg: Config, api: AladhanClient) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    name = call.data.split(":", 1)[1]
    if name == "menu":
        await show_menu(call, user, api)
    elif name == "settings":
        await show(call, settings_text(user), keyboards.settings_kb(user))
    elif name in {"morning", "evening"}:
        await show(call, adhkar.render_item(name, 0, user.lang), keyboards.adhkar_kb(name, 0, user.lang))
    else:
        await run_screen(call, user, api, name)


@router.callback_query(F.data.startswith("r:"))
async def cb_region(call: CallbackQuery, db: Database, cfg: Config, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    choice = call.data.split(":", 1)[1]
    if choice in {"gps", "other"}:
        await ask_location(call, user, state)
    elif choice == "back":
        await ask_region(call, user, state)
    elif choice.isdigit() and int(choice) < len(REGIONS):
        region = REGIONS[int(choice)]
        await show(
            call,
            t(user.lang, "pick_city", region=region.name(user.lang)),
            keyboards.cities_kb(user.lang, int(choice)),
        )
    else:
        await call.answer()


@router.callback_query(F.data.startswith("c:"))
async def cb_city(call: CallbackQuery, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    try:
        _, r, c = call.data.split(":")
        region, city = REGIONS[int(r)], REGIONS[int(r)].cities[int(c)]
    except (ValueError, IndexError):
        await call.answer()
        return
    label = f"{city.ar if user.lang == 'ar' else city.en}, {region.name(user.lang)}"
    if not await store_location(db, api, user, city.lat, city.lon, label):
        await call.answer(t(user.lang, "service_down"), show_alert=True)
        return
    await state.clear()
    await show_menu(call, user, api)


@router.callback_query(F.data.startswith("a:"))
async def cb_adhkar(call: CallbackQuery, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    try:
        _, kind, raw = call.data.split(":")
        index = int(raw)
    except ValueError:
        await call.answer()
        return
    if kind not in {"morning", "evening"}:
        await call.answer()
        return
    index %= adhkar.total(kind)
    await show(call, adhkar.render_item(kind, index, user.lang), keyboards.adhkar_kb(kind, index, user.lang))


@router.callback_query(F.data.startswith("loc:"))
async def cb_location(call: CallbackQuery, db: Database, cfg: Config, api: AladhanClient, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    if call.data == "loc:change":
        await ask_region(call, user, state)
    else:
        await state.clear()
        await show_menu(call, user, api)


@router.callback_query(F.data.startswith("s:"))
async def cb_settings(call: CallbackQuery, db: Database, cfg: Config, state: FSMContext) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    action = call.data.split(":", 1)[1]
    if action == "lang":
        user.lang = "en" if user.lang == "ar" else "ar"
        await db.update(user.user_id, lang=user.lang, lang_chosen=1)
        await show(call, settings_text(user), keyboards.settings_kb(user))
    elif action == "method":
        await show(call, t(user.lang, "pick_method"), keyboards.method_kb(user))
    elif action == "remind":
        await show(call, t(user.lang, "pick_remind"), keyboards.remind_kb(user))
    elif action == "adhkar":
        user.adhkar = not user.adhkar
        await db.update(user.user_id, adhkar=int(user.adhkar))
        await show(call, settings_text(user), keyboards.settings_kb(user))
    elif action == "loc":
        await ask_region(call, user, state)


@router.callback_query(F.data.startswith("sm:"))
async def cb_method(call: CallbackQuery, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    method = int(call.data.split(":", 1)[1])
    if method in METHODS:
        user.method = method
        await db.update(user.user_id, method=method)
    await show(call, settings_text(user), keyboards.settings_kb(user))


@router.callback_query(F.data.startswith("sr:"))
async def cb_remind(call: CallbackQuery, db: Database, cfg: Config) -> None:
    user = await ensure_user(db, cfg, call.from_user)
    minutes = int(call.data.split(":", 1)[1])
    if minutes in REMINDER_CHOICES:
        user.remind_before = minutes
        await db.update(user.user_id, remind_before=minutes)
    await show(call, settings_text(user), keyboards.settings_kb(user))
