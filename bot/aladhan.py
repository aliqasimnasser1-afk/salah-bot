from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import aiohttp

log = logging.getLogger(__name__)

BASE_URL = "https://api.aladhan.com/v1"
PRAYERS = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")
DISPLAY = ("Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha")
CACHE_TTL = 6 * 3600


class AladhanError(Exception):
    """The prayer-times service failed or could not resolve the location."""


@dataclass(frozen=True)
class Timings:
    day: date
    times: dict[str, datetime]
    tz: str
    lat: float
    lon: float
    hijri_ar: str
    hijri_en: str


def parse_timings(payload: dict, day: date) -> Timings:
    """Turn an Aladhan API response into timezone-aware datetimes."""
    try:
        data = payload["data"]
        raw = data["timings"]
        meta = data["meta"]
        tz = ZoneInfo(meta["timezone"])
        times = {}
        for name in DISPLAY:
            hh, mm = raw[name][:5].split(":")
            times[name] = datetime(day.year, day.month, day.day, int(hh), int(mm), tzinfo=tz)
        hijri = data["date"]["hijri"]
        hijri_ar = f'{hijri["day"]} {hijri["month"]["ar"]} {hijri["year"]}هـ'
        hijri_en = f'{hijri["day"]} {hijri["month"]["en"]} {hijri["year"]} AH'
        return Timings(
            day=day,
            times=times,
            tz=meta["timezone"],
            lat=float(meta["latitude"]),
            lon=float(meta["longitude"]),
            hijri_ar=hijri_ar,
            hijri_en=hijri_en,
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise AladhanError(f"Unexpected response from prayer-times service: {exc}") from exc


class AladhanClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session
        self._cache: dict[tuple, tuple[float, Timings]] = {}

    async def _get(self, url: str, params: dict) -> dict:
        try:
            async with self.session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                payload = await resp.json(content_type=None)
                if resp.status != 200 or payload.get("code") != 200:
                    raise AladhanError(str(payload.get("data") or payload.get("status") or resp.status))
                return payload
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise AladhanError(f"Network error: {exc}") from exc

    async def by_coordinates(self, lat: float, lon: float, method: int, day: date) -> Timings:
        key = (round(lat, 2), round(lon, 2), method, day)
        hit = self._cache.get(key)
        if hit and time.monotonic() - hit[0] < CACHE_TTL:
            return hit[1]
        payload = await self._get(
            f"{BASE_URL}/timings/{day:%d-%m-%Y}",
            {"latitude": lat, "longitude": lon, "method": method},
        )
        result = parse_timings(payload, day)
        self._cache[key] = (time.monotonic(), result)
        if len(self._cache) > 5000:
            self._cache.clear()
        return result

    async def for_user(self, lat: float, lon: float, method: int, tz: str, now: datetime) -> Timings:
        """Today's timings in the user's own timezone."""
        local_day = now.astimezone(ZoneInfo(tz)).date()
        return await self.by_coordinates(lat, lon, method, local_day)

    async def next_prayer(
        self, lat: float, lon: float, method: int, tz: str, now: datetime
    ) -> tuple[str, datetime, Timings]:
        """Next of the five daily prayers, rolling over to tomorrow's Fajr after Isha."""
        today = await self.for_user(lat, lon, method, tz, now)
        for name in PRAYERS:
            if today.times[name] > now:
                return name, today.times[name], today
        tomorrow = await self.by_coordinates(lat, lon, method, today.day + timedelta(days=1))
        return "Fajr", tomorrow.times["Fajr"], tomorrow
