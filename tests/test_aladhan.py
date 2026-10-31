from copy import deepcopy
from datetime import date

import pytest

from bot.aladhan import AladhanError, parse_timings

from .conftest import SAMPLE


def test_parse_times_and_timezone(timings):
    assert timings.tz == "Asia/Riyadh"
    assert timings.times["Fajr"].hour == 4 and timings.times["Fajr"].minute == 41
    assert timings.times["Sunrise"].hour == 6  # suffix like " (+03)" is ignored
    assert timings.times["Isha"].utcoffset().total_seconds() == 3 * 3600


def test_parse_hijri(timings):
    assert "1448" in timings.hijri_ar and "هـ" in timings.hijri_ar
    assert timings.hijri_en.endswith("AH")


def test_parse_rejects_bad_payload():
    broken = deepcopy(SAMPLE)
    del broken["data"]["timings"]["Asr"]
    with pytest.raises(AladhanError):
        parse_timings(broken, date(2026, 10, 31))
    with pytest.raises(AladhanError):
        parse_timings({"data": {}}, date(2026, 10, 31))
