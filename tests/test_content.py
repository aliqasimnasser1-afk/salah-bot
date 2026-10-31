from datetime import timedelta

import pytest

from bot import adhkar
from bot.texts import STRINGS, format_left


@pytest.mark.parametrize("kind", ["morning", "evening"])
@pytest.mark.parametrize("lang", ["ar", "en"])
def test_adhkar_messages_fit_telegram_limit(kind, lang):
    messages = adhkar.render(kind, lang)
    assert messages and all(len(m) <= 4096 for m in messages)


def test_morning_and_evening_differ():
    assert adhkar.render("morning")[0] != adhkar.render("evening")[0]


def test_languages_have_the_same_keys():
    assert set(STRINGS["ar"]) == set(STRINGS["en"])


def test_format_left():
    assert format_left("en", timedelta(hours=2, minutes=15)) == "2h 15m"
    assert format_left("en", timedelta(minutes=5)) == "5m"
    assert format_left("ar", timedelta(seconds=10)) == "1د"
    assert format_left("en", timedelta(seconds=-5)) == "1m"


@pytest.mark.parametrize("kind", ["morning", "evening"])
def test_render_item_cards(kind):
    total = adhkar.total(kind)
    assert total >= 10
    first = adhkar.render_item(kind, 0)
    assert "آية الكرسي" in first and f"1/{total}" in first
    assert adhkar.render_item(kind, total) == first  # index wraps
    assert all(len(adhkar.render_item(kind, i)) < 4096 for i in range(total))


def test_morning_and_evening_cards_differ():
    morning = [adhkar.render_item("morning", i) for i in range(adhkar.total("morning"))]
    assert any("أَصْبَحْنَا" in m for m in morning)
    assert not any("أَصْبَحْنَا وَأَصْبَحَ" in adhkar.render_item("evening", i) for i in range(adhkar.total("evening")))
