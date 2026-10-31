import pytest

from bot import qibla


@pytest.mark.parametrize(
    "lat, lon, low, high",
    [
        (24.4672, 39.6111, 150, 210),  # Madinah: Makkah lies roughly south
        (30.0444, 31.2357, 125, 140),  # Cairo: south-east
        (-6.2088, 106.8456, 285, 300),  # Jakarta: north-west
        (40.7128, -74.0060, 50, 60),  # New York: north-east
        (51.5074, -0.1278, 115, 125),  # London: south-east
    ],
)
def test_bearing_ranges(lat, lon, low, high):
    assert low <= qibla.bearing(lat, lon) <= high


def test_bearing_is_normalised():
    for lat, lon in [(0, 0), (-33.9, 151.2), (64.1, -21.9), (35.7, 139.7)]:
        assert 0 <= qibla.bearing(lat, lon) < 360


def test_distance_known_values():
    assert qibla.distance_km(qibla.KAABA_LAT, qibla.KAABA_LON) == pytest.approx(0, abs=0.01)
    assert 330 <= qibla.distance_km(24.4672, 39.6111) <= 350  # Madinah to Makkah
    assert 1150 <= qibla.distance_km(30.0444, 31.2357) <= 1350  # Cairo


def test_compass_names():
    assert qibla.compass(0, "en") == "North"
    assert qibla.compass(359, "en") == "North"
    assert qibla.compass(90, "en") == "East"
    assert qibla.compass(180, "ar") == "جنوب"
    assert qibla.compass(315, "ar") == "شمال غرب"
