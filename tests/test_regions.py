from bot.keyboards import cities_kb, regions_kb
from bot.regions import REGIONS


def test_thirteen_regions():
    assert len(REGIONS) == 13
    assert len({r.en for r in REGIONS}) == 13


def test_every_city_is_inside_saudi_arabia():
    for region in REGIONS:
        assert region.cities, region.en
        for city in region.cities:
            assert city.ar and city.en
            assert 16.0 <= city.lat <= 32.5, (city.en, city.lat)
            assert 34.0 <= city.lon <= 56.0, (city.en, city.lon)


def test_city_names_are_unique_within_a_region():
    for region in REGIONS:
        assert len({c.en for c in region.cities}) == len(region.cities)


def test_callback_data_fits_telegrams_limit():
    for lang in ("ar", "en"):
        rows = regions_kb(lang).inline_keyboard
        for i, region in enumerate(REGIONS):
            rows += cities_kb(lang, i).inline_keyboard
        assert all(len(b.callback_data.encode()) <= 64 for row in rows for b in row)


def test_holy_cities_are_present_and_accurate():
    makkah = next(r for r in REGIONS if r.en == "Makkah").cities[0]
    madinah = next(r for r in REGIONS if r.en == "Madinah").cities[0]
    assert abs(makkah.lat - 21.42) < 0.1 and abs(makkah.lon - 39.83) < 0.1
    assert abs(madinah.lat - 24.47) < 0.1 and abs(madinah.lon - 39.61) < 0.1
