from __future__ import annotations

import math

KAABA_LAT = 21.4225
KAABA_LON = 39.8262
EARTH_RADIUS_KM = 6371.0088

_COMPASS_AR = ["شمال", "شمال شرق", "شرق", "جنوب شرق", "جنوب", "جنوب غرب", "غرب", "شمال غرب"]
_COMPASS_EN = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"]


def bearing(lat: float, lon: float) -> float:
    """Initial great-circle bearing from a point to the Kaaba, in degrees clockwise from north."""
    phi1, phi2 = math.radians(lat), math.radians(KAABA_LAT)
    d_lambda = math.radians(KAABA_LON - lon)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def distance_km(lat: float, lon: float) -> float:
    """Great-circle distance to the Kaaba in kilometres (haversine)."""
    phi1, phi2 = math.radians(lat), math.radians(KAABA_LAT)
    d_phi = phi2 - phi1
    d_lambda = math.radians(KAABA_LON - lon)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def compass(degrees: float, lang: str = "en") -> str:
    names = _COMPASS_AR if lang == "ar" else _COMPASS_EN
    return names[int((degrees % 360 + 22.5) // 45) % 8]
