"""Pure scheduling logic: which notifications are due right now. No I/O, easy to test."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .aladhan import PRAYERS, Timings

WINDOW = timedelta(seconds=120)
ADHKAR_DELAY = timedelta(minutes=15)


@dataclass(frozen=True)
class Event:
    key: str  # unique per user per day, used to avoid sending twice
    kind: str  # "remind" | "adhan" | "morning" | "evening"
    prayer: str | None = None


def due_events(now: datetime, timings: Timings, remind_before: int, adhkar: bool) -> list[Event]:
    """Events whose scheduled moment passed within the last WINDOW seconds."""
    day = timings.day.isoformat()
    out: list[Event] = []

    def due(moment: datetime) -> bool:
        return moment <= now < moment + WINDOW

    for name in PRAYERS:
        at = timings.times[name]
        if remind_before > 0 and due(at - timedelta(minutes=remind_before)):
            out.append(Event(f"{day}:remind:{name}", "remind", name))
        if due(at):
            out.append(Event(f"{day}:adhan:{name}", "adhan", name))

    if adhkar:
        if due(timings.times["Fajr"] + ADHKAR_DELAY):
            out.append(Event(f"{day}:morning", "morning"))
        if due(timings.times["Asr"] + ADHKAR_DELAY):
            out.append(Event(f"{day}:evening", "evening"))
    return out
