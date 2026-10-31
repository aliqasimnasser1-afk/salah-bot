from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import adhkar
from .db import User
from .regions import REGIONS
from .texts import LANGUAGES, METHODS, REMINDER_CHOICES, t


def language_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code, label in LANGUAGES.items():
        b.button(text=label, callback_data=f"l:{code}")
    b.adjust(2)
    return b.as_markup()


def confirm_location_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_ok"), callback_data="loc:ok")
    b.button(text=t(lang, "btn_change_city"), callback_data="loc:change")
    b.adjust(2)
    return b.as_markup()


def location_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_location"), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_times"), callback_data="m:times")
    b.button(text=t(lang, "btn_next"), callback_data="m:next")
    b.button(text=t(lang, "btn_qibla"), callback_data="m:qibla")
    b.button(text=t(lang, "btn_morning"), callback_data="m:morning")
    b.button(text=t(lang, "btn_evening"), callback_data="m:evening")
    b.button(text=t(lang, "btn_settings"), callback_data="m:settings")
    b.adjust(2, 1, 2, 1)
    return b.as_markup()


def back_kb(lang: str, target: str = "m:menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=target)]]
    )


def settings_kb(user: User) -> InlineKeyboardMarkup:
    lang = user.lang
    state = t(lang, "on" if user.adhkar else "off")
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "btn_lang"), callback_data="s:lang")
    b.button(text=t(lang, "btn_method"), callback_data="s:method")
    b.button(text=t(lang, "btn_remind"), callback_data="s:remind")
    b.button(text=t(lang, "btn_adhkar", state=state), callback_data="s:adhkar")
    b.button(text=t(lang, "btn_location"), callback_data="s:loc")
    b.button(text=t(lang, "btn_back"), callback_data="m:menu")
    b.adjust(1)
    return b.as_markup()


def method_kb(user: User) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for method_id, names in METHODS.items():
        mark = "✅ " if method_id == user.method else ""
        b.button(text=f"{mark}{names[user.lang]}", callback_data=f"sm:{method_id}")
    b.button(text=t(user.lang, "btn_back"), callback_data="m:settings")
    b.adjust(1)
    return b.as_markup()


def remind_kb(user: User) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for minutes in REMINDER_CHOICES:
        label = t(user.lang, "off") if minutes == 0 else t(user.lang, "minutes", n=minutes)
        mark = "✅ " if minutes == user.remind_before else ""
        b.button(text=f"{mark}{label}", callback_data=f"sr:{minutes}")
    b.button(text=t(user.lang, "btn_back"), callback_data="m:settings")
    b.adjust(3, 2, 1)
    return b.as_markup()


def adhkar_kb(kind: str, index: int, lang: str) -> InlineKeyboardMarkup:
    """Prev / position / next, a switch to the other set, and a way home. Wraps around at the ends."""
    count = adhkar.total(kind)
    prev_i, next_i = (index - 1) % count, (index + 1) % count
    other = "evening" if kind == "morning" else "morning"
    if lang == "ar":  # Arabic reads right to left, so "next" sits on the left
        prev_btn = InlineKeyboardButton(text=f"➡️ {t(lang, 'btn_prev')}", callback_data=f"a:{kind}:{prev_i}")
        next_btn = InlineKeyboardButton(text=f"{t(lang, 'btn_next')} ⬅️", callback_data=f"a:{kind}:{next_i}")
        row = [next_btn, prev_btn]
    else:
        prev_btn = InlineKeyboardButton(text=f"⬅️ {t(lang, 'btn_prev')}", callback_data=f"a:{kind}:{prev_i}")
        next_btn = InlineKeyboardButton(text=f"{t(lang, 'btn_next')} ➡️", callback_data=f"a:{kind}:{next_i}")
        row = [prev_btn, next_btn]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            row,
            [InlineKeyboardButton(text=t(lang, f"btn_{other}"), callback_data=f"a:{other}:0")],
            [InlineKeyboardButton(text=t(lang, "btn_home"), callback_data="m:menu")],
        ]
    )


def regions_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, region in enumerate(REGIONS):
        b.button(text=region.name(lang), callback_data=f"r:{i}")
    b.adjust(2)
    b.row(
        InlineKeyboardButton(text=t(lang, "btn_gps"), callback_data="r:gps"),
        InlineKeyboardButton(text=t(lang, "btn_other"), callback_data="r:other"),
    )
    return b.as_markup()


def cities_kb(lang: str, region_index: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for j, city in enumerate(REGIONS[region_index].cities):
        b.button(text=city.ar if lang == "ar" else city.en, callback_data=f"c:{region_index}:{j}")
    b.adjust(2)
    b.row(InlineKeyboardButton(text=t(lang, "btn_regions"), callback_data="r:back"))
    return b.as_markup()
