import pytest

from bot.aladhan import AladhanError
from bot.geocode import parse_nominatim, parse_nominatim_all, parse_open_meteo, parse_reverse, pick_city


def test_parse_nominatim():
    place = parse_nominatim(
        [{"display_name": "المدينة المنورة, منطقة المدينة المنورة, السعودية", "lat": "24.47", "lon": "39.61"}]
    )
    assert place.name == "المدينة المنورة, منطقة المدينة المنورة"
    assert (place.lat, place.lon) == (24.47, 39.61)


def test_parse_open_meteo():
    place = parse_open_meteo(
        {"results": [{"name": "Jeddah", "country": "Saudi Arabia", "latitude": 21.49, "longitude": 39.19}]}
    )
    assert place.name == "Jeddah, Saudi Arabia"


@pytest.mark.parametrize("parser, empty", [(parse_nominatim, []), (parse_open_meteo, {})])
def test_empty_results_raise(parser, empty):
    with pytest.raises(AladhanError):
        parser(empty)


def test_malformed_result_raises():
    with pytest.raises(AladhanError):
        parse_nominatim([{"display_name": "x"}])


def test_parse_reverse_prefers_city_then_falls_back():
    assert parse_reverse({"address": {"city": "حائل", "country": "السعودية"}}) == "حائل, السعودية"
    assert parse_reverse({"address": {"county": "Kharj", "state": "Riyadh", "country": "Saudi Arabia"}}) == "Kharj, Saudi Arabia"
    with pytest.raises(AladhanError):
        parse_reverse({})


REGION_THEN_CITY = [
    {"display_name": "منطقة حائل, السعودية", "lat": "26.99", "lon": "41.49", "addresstype": "state"},
    {"display_name": "حائل, محافظة حائل, السعودية", "lat": "27.52", "lon": "41.69", "addresstype": "city"},
]


def test_pick_city_skips_regions():
    assert pick_city(REGION_THEN_CITY).lat == 27.52
    assert parse_nominatim(REGION_THEN_CITY).lat == 26.99  # plain parse keeps the first result


def test_pick_city_returns_none_when_only_regions():
    assert pick_city(REGION_THEN_CITY[:1]) is None
    assert pick_city([]) is None


def test_parse_all_skips_malformed_items():
    items = REGION_THEN_CITY + [{"display_name": "x"}]
    assert [kind for _, kind in parse_nominatim_all(items)] == ["state", "city"]
