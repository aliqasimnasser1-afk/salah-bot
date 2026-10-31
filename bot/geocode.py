from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

import aiohttp

from .aladhan import AladhanError

log = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
OPEN_METEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
USER_AGENT = "SalahBot/1.0 (+https://github.com/aliqasimnasser1-afk)"
MIN_INTERVAL = 1.1  # Nominatim usage policy: at most one request per second

_lock = asyncio.Lock()
_last_call = 0.0


@dataclass(frozen=True)
class Place:
    name: str
    lat: float
    lon: float


CITY_TYPES = {"city", "town", "village", "municipality"}


def parse_nominatim_all(payload: list) -> list[tuple[Place, str]]:
    """Every result as (place, addresstype), so callers can prefer a real city over a region."""
    out = []
    for item in payload or []:
        try:
            parts = [p.strip() for p in str(item["display_name"]).split(",")]
            place = Place(name=", ".join(parts[:2])[:80], lat=float(item["lat"]), lon=float(item["lon"]))
        except (KeyError, TypeError, ValueError):
            continue
        out.append((place, str(item.get("addresstype", ""))))
    return out


def parse_nominatim(payload: list) -> Place:
    """First result, whatever its kind."""
    places = parse_nominatim_all(payload)
    if not places:
        raise AladhanError("Place not found")
    return places[0][0]


def pick_city(payload: list) -> Place | None:
    """First result that is an actual city, town or village (a region's centroid can be far away)."""
    return next((p for p, kind in parse_nominatim_all(payload) if kind in CITY_TYPES), None)


def parse_open_meteo(payload: dict) -> Place:
    results = payload.get("results") or []
    if not results:
        raise AladhanError("Place not found")
    top = results[0]
    try:
        label = ", ".join(x for x in (top["name"], top.get("country")) if x)
        return Place(name=label[:80], lat=float(top["latitude"]), lon=float(top["longitude"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise AladhanError(f"Unexpected geocoder response: {exc}") from exc


def parse_reverse(payload: dict) -> str:
    """City-level label ("Ha'il, Saudi Arabia") from a Nominatim reverse-geocoding response."""
    address = payload.get("address") or {}
    area = next(
        (address[k] for k in ("city", "town", "village", "municipality", "county", "state") if address.get(k)),
        None,
    )
    country = address.get("country")
    label = ", ".join(x for x in (area, country) if x)
    if not label:
        raise AladhanError("No address for these coordinates")
    return label[:80]


async def _get_json(session: aiohttp.ClientSession, url: str, params: dict):
    async with session.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=aiohttp.ClientTimeout(total=15),
    ) as resp:
        if resp.status != 200:
            raise AladhanError(f"Geocoder returned HTTP {resp.status}")
        return await resp.json(content_type=None)


async def _nominatim(session: aiohttp.ClientSession, url: str, params: dict):
    """One Nominatim call, serialised so the one-request-per-second policy is respected."""
    global _last_call
    async with _lock:
        wait = MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            return await _get_json(session, url, params)
        finally:
            _last_call = time.monotonic()


async def find_place(session: aiohttp.ClientSession, query: str, lang: str = "ar") -> Place:
    """Resolve a city name (Arabic or English) to coordinates.

    1. Nominatim (OpenStreetMap) ranks places well, but for some names it returns a region
       whose centre is far from the city. Only a real city/town/village result is accepted.
    2. Open-Meteo lists populated places, which fixes those cases (e.g. Ha'il).
    3. Failing both, fall back to whatever Nominatim found first, so the user still gets an answer.
    """
    first: Place | None = None
    try:
        data = await _nominatim(
            session, NOMINATIM_URL, {"q": query, "format": "jsonv2", "limit": 5, "accept-language": lang}
        )
        city = pick_city(data)
        if city:
            return city
        found = parse_nominatim_all(data)
        first = found[0][0] if found else None
    except (AladhanError, aiohttp.ClientError, TimeoutError) as exc:
        log.info("Nominatim failed for %r (%s)", query, exc)

    try:
        data = await _get_json(
            session, OPEN_METEO_URL, {"name": query, "count": 1, "language": lang, "format": "json"}
        )
        return parse_open_meteo(data)
    except (AladhanError, aiohttp.ClientError, TimeoutError) as exc:
        if first:
            return first
        if isinstance(exc, AladhanError):
            raise
        raise AladhanError(f"Network error: {exc}") from exc


async def reverse_place(session: aiohttp.ClientSession, lat: float, lon: float, lang: str = "ar") -> str:
    """Name of the city around a coordinate pair, so users can see what the bot understood."""
    try:
        data = await _nominatim(
            session,
            NOMINATIM_REVERSE_URL,
            {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 10, "accept-language": lang},
        )
        return parse_reverse(data)
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise AladhanError(f"Network error: {exc}") from exc
