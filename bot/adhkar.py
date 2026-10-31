"""Morning and evening adhkar. A short selection; see Hisn al-Muslim for the full collection."""

from __future__ import annotations

from html import escape

AYAT_AL_KURSI = (
    "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ "
    "لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ "
    "يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ "
    "وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
)

IKHLAS = "قُلْ هُوَ اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ ۝ وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ"
FALAQ = (
    "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ ۝ مِن شَرِّ مَا خَلَقَ ۝ وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ ۝ "
    "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ ۝ وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ"
)
NAS = (
    "قُلْ أَعُوذُ بِرَبِّ النَّاسِ ۝ مَلِكِ النَّاسِ ۝ إِلَٰهِ النَّاسِ ۝ مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ ۝ "
    "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ ۝ مِنَ الْجِنَّةِ وَالنَّاسِ"
)

SAYYID_ISTIGHFAR = (
    "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ "
    "وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، "
    "وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي، فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ"
)

COMMON = [
    ("آية الكرسي", AYAT_AL_KURSI, 1),
    ("سورة الإخلاص", IKHLAS, 3),
    ("سورة الفلق", FALAQ, 3),
    ("سورة الناس", NAS, 3),
    ("سيد الاستغفار", SAYYID_ISTIGHFAR, 1),
    (
        "",
        "بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ "
        "وَهُوَ السَّمِيعُ الْعَلِيمُ",
        3,
    ),
    (
        "",
        "رَضِيتُ بِاللَّهِ رَبًّا، وَبِالْإِسْلَامِ دِينًا، وَبِمُحَمَّدٍ صَلَّى اللهُ عَلَيْهِ وَسَلَّمَ نَبِيًّا",
        3,
    ),
    (
        "",
        "اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، "
        "اللَّهُمَّ عَافِنِي فِي بَصَرِي، لَا إِلَهَ إِلَّا أَنْتَ",
        3,
    ),
    ("", "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ", 100),
]

MORNING = [
    (
        "",
        "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ "
        "لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
        1,
    ),
    (
        "",
        "اللَّهُمَّ بِكَ أَصْبَحْنَا، وَبِكَ أَمْسَيْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ النُّشُورُ",
        1,
    ),
]

EVENING = [
    (
        "",
        "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ "
        "لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
        1,
    ),
    (
        "",
        "اللَّهُمَّ بِكَ أَمْسَيْنَا، وَبِكَ أَصْبَحْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ الْمَصِيرُ",
        1,
    ),
    ("", "أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ", 3),
]

HEADERS = {
    "ar": {"morning": "🌅 أذكار الصباح", "evening": "🌇 أذكار المساء"},
    "en": {"morning": "🌅 Morning adhkar", "evening": "🌇 Evening adhkar"},
}
REPEAT = {"ar": "التكرار", "en": "Repeat"}
FOOTER = {
    "ar": "للاستزادة راجع «حصن المسلم».",
    "en": "For the complete collection see Hisn al-Muslim.",
}


def _items(kind: str) -> list[tuple[str, str, int]]:
    """Ayat al-Kursi and the three suras first, then the time-specific adhkar, then the rest."""
    specific = MORNING if kind == "morning" else EVENING
    return COMMON[:4] + specific + COMMON[4:]


def total(kind: str) -> int:
    return len(_items(kind))


def render_item(kind: str, index: int, lang: str = "ar") -> str:
    """One dhikr as an HTML card with its position, for in-place paging."""
    items = _items(kind)
    index %= len(items)
    title, text, count = items[index]
    lines = [f"<b>{HEADERS[lang][kind]}</b>  •  {index + 1}/{len(items)}", ""]
    if title:
        lines.append(f"<b>{escape(title)}</b>")
    lines.append(escape(text))
    if count > 1:
        lines += ["", f"<i>{REPEAT[lang]}: {count}×</i>"]
    return "\n".join(lines)


def render(kind: str, lang: str = "ar") -> list[str]:
    """Adhkar as HTML messages, each under Telegram's 4096-character limit."""
    messages: list[str] = []
    current = f"<b>{HEADERS[lang][kind]}</b>\n"
    for title, text, count in _items(kind):
        block = "\n"
        if title:
            block += f"<b>{escape(title)}</b>\n"
        block += f"{escape(text)}\n"
        if count > 1:
            block += f"<i>{REPEAT[lang]}: {count}×</i>\n"
        if len(current) + len(block) > 3500:
            messages.append(current)
            current = ""
        current += block
    current += f"\n<i>{FOOTER[lang]}</i>"
    messages.append(current)
    return messages
