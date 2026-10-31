from datetime import date

import pytest

from bot.aladhan import parse_timings

SAMPLE = {
    "code": 200,
    "status": "OK",
    "data": {
        "timings": {
            "Fajr": "04:41",
            "Sunrise": "06:00 (+03)",
            "Dhuhr": "11:45",
            "Asr": "15:05",
            "Maghrib": "17:30",
            "Isha": "18:50",
        },
        "date": {
            "hijri": {
                "day": "9",
                "month": {"ar": "رَبيع الآخر", "en": "Rabīʿ al-ākhir"},
                "year": "1448",
            }
        },
        "meta": {"latitude": 24.4672, "longitude": 39.6111, "timezone": "Asia/Riyadh"},
    },
}


@pytest.fixture
def timings():
    return parse_timings(SAMPLE, date(2026, 10, 31))
