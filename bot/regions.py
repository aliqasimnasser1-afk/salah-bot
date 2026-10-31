"""Saudi Arabia's 13 administrative regions with their main cities.

Coordinates are city centres, accurate to a few kilometres, which changes prayer times by seconds.
Each city is (Arabic name, English name, latitude, longitude).
"""

from __future__ import annotations

from typing import NamedTuple


class City(NamedTuple):
    ar: str
    en: str
    lat: float
    lon: float


class Region(NamedTuple):
    ar: str
    en: str
    cities: tuple[City, ...]

    def name(self, lang: str) -> str:
        return self.ar if lang == "ar" else self.en


REGIONS: tuple[Region, ...] = (
    Region("الرياض", "Riyadh", (
        City("الرياض", "Riyadh", 24.7136, 46.6753),
        City("الخرج", "Al-Kharj", 24.1556, 47.3346),
        City("الدرعية", "Diriyah", 24.7341, 46.5742),
        City("المجمعة", "Al Majma'ah", 25.9039, 45.3459),
        City("الدوادمي", "Dawadmi", 24.5077, 44.3924),
        City("عفيف", "Afif", 23.9065, 42.9172),
        City("الزلفي", "Az Zulfi", 26.2994, 44.8052),
        City("شقراء", "Shaqra", 25.2448, 45.2535),
        City("وادي الدواسر", "Wadi ad-Dawasir", 20.4915, 44.7790),
        City("حوطة بني تميم", "Hotat Bani Tamim", 23.5198, 46.8500),
    )),
    Region("مكة المكرمة", "Makkah", (
        City("مكة المكرمة", "Makkah", 21.3891, 39.8579),
        City("جدة", "Jeddah", 21.4858, 39.1925),
        City("الطائف", "Taif", 21.2703, 40.4158),
        City("رابغ", "Rabigh", 22.7986, 39.0349),
        City("القنفذة", "Al Qunfudhah", 19.1281, 41.0789),
        City("الليث", "Al Lith", 20.1500, 40.2700),
        City("خليص", "Khulais", 22.1500, 39.3167),
    )),
    Region("المدينة المنورة", "Madinah", (
        City("المدينة المنورة", "Madinah", 24.4672, 39.6111),
        City("ينبع", "Yanbu", 24.0895, 38.0618),
        City("العلا", "AlUla", 26.6085, 37.9232),
        City("بدر", "Badr", 23.7833, 38.7833),
        City("خيبر", "Khaybar", 25.6997, 39.2924),
        City("المهد", "Mahd adh Dhahab", 23.5000, 40.8500),
        City("الحناكية", "Al Henakiyah", 24.8681, 40.5233),
    )),
    Region("القصيم", "Al-Qassim", (
        City("بريدة", "Buraydah", 26.3260, 43.9750),
        City("عنيزة", "Unaizah", 26.0840, 43.9930),
        City("الرس", "Ar Rass", 25.8693, 43.4973),
        City("البكيرية", "Al Bukayriyah", 26.1333, 43.6500),
        City("المذنب", "Al Mithnab", 25.8644, 44.2189),
        City("البدائع", "Al Badai", 25.9553, 43.7567),
    )),
    Region("المنطقة الشرقية", "Eastern Province", (
        City("الدمام", "Dammam", 26.4207, 50.0888),
        City("الخبر", "Al Khobar", 26.2172, 50.1971),
        City("الظهران", "Dhahran", 26.2361, 50.0393),
        City("الأحساء", "Al-Ahsa (Hofuf)", 25.3647, 49.5864),
        City("الجبيل", "Jubail", 27.0174, 49.6225),
        City("القطيف", "Qatif", 26.5196, 50.0115),
        City("حفر الباطن", "Hafar Al-Batin", 28.4328, 45.9708),
        City("الخفجي", "Khafji", 28.4390, 48.4913),
        City("رأس تنورة", "Ras Tanura", 26.6439, 50.1597),
        City("النعيرية", "An Nuayriyah", 27.4693, 48.4876),
        City("بقيق", "Abqaiq", 25.9333, 49.6667),
    )),
    Region("عسير", "Asir", (
        City("أبها", "Abha", 18.2164, 42.5053),
        City("خميس مشيط", "Khamis Mushait", 18.3066, 42.7292),
        City("بيشة", "Bisha", 19.9890, 42.5990),
        City("النماص", "An Namas", 19.1167, 42.1167),
        City("محايل عسير", "Muhayil Asir", 18.5167, 42.0500),
    )),
    Region("تبوك", "Tabuk", (
        City("تبوك", "Tabuk", 28.3835, 36.5662),
        City("ضباء", "Duba", 27.3500, 35.6833),
        City("الوجه", "Al Wajh", 26.2333, 36.4667),
        City("تيماء", "Tayma", 27.6333, 38.5500),
        City("أملج", "Umluj", 25.0214, 37.2685),
        City("حقل", "Haql", 29.2872, 34.9425),
    )),
    Region("حائل", "Ha'il", (
        City("حائل", "Ha'il", 27.5219, 41.6907),
        City("بقعاء", "Baqaa", 27.8947, 42.4083),
    )),
    Region("الحدود الشمالية", "Northern Borders", (
        City("عرعر", "Arar", 30.9753, 41.0381),
        City("رفحاء", "Rafha", 29.6269, 43.5011),
        City("طريف", "Turaif", 31.6725, 38.6637),
    )),
    Region("جازان", "Jazan", (
        City("جازان", "Jazan", 16.8892, 42.5611),
        City("صبيا", "Sabya", 17.1496, 42.6255),
        City("أبو عريش", "Abu Arish", 16.9683, 42.8311),
        City("صامطة", "Samtah", 16.5967, 42.9442),
    )),
    Region("نجران", "Najran", (
        City("نجران", "Najran", 17.4917, 44.1322),
        City("شرورة", "Sharurah", 17.4667, 47.1167),
    )),
    Region("الباحة", "Al-Baha", (
        City("الباحة", "Al Baha", 20.0129, 41.4677),
        City("بلجرشي", "Baljurashi", 19.8500, 41.5667),
    )),
    Region("الجوف", "Al-Jawf", (
        City("سكاكا", "Sakaka", 29.9697, 40.2064),
        City("دومة الجندل", "Dumat al-Jandal", 29.8118, 39.8683),
        City("القريات", "Al Qurayyat", 31.3317, 37.3428),
    )),
)
