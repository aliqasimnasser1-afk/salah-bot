from datetime import timedelta

from bot.events import due_events


def kinds(events):
    return {(e.kind, e.prayer) for e in events}


def test_nothing_due_in_the_middle_of_the_day(timings):
    now = timings.times["Dhuhr"] - timedelta(hours=2)
    assert due_events(now, timings, 10, True) == []


def test_reminder_then_adhan(timings):
    asr = timings.times["Asr"]
    assert kinds(due_events(asr - timedelta(minutes=10), timings, 10, False)) == {("remind", "Asr")}
    assert kinds(due_events(asr, timings, 10, False)) == {("adhan", "Asr")}
    assert kinds(due_events(asr + timedelta(seconds=119), timings, 10, False)) == {("adhan", "Asr")}


def test_event_expires_after_window(timings):
    asr = timings.times["Asr"]
    assert due_events(asr + timedelta(seconds=121), timings, 0, False) == []


def test_reminder_can_be_disabled(timings):
    asr = timings.times["Asr"]
    assert due_events(asr - timedelta(minutes=10), timings, 0, False) == []


def test_adhkar_follow_fajr_and_asr(timings):
    morning = timings.times["Fajr"] + timedelta(minutes=15)
    evening = timings.times["Asr"] + timedelta(minutes=15)
    assert kinds(due_events(morning, timings, 0, True)) == {("morning", None)}
    assert kinds(due_events(evening, timings, 0, True)) == {("evening", None)}
    assert due_events(morning, timings, 0, False) == []


def test_keys_are_stable_and_unique_per_day(timings):
    now = timings.times["Maghrib"]
    first = due_events(now, timings, 10, True)
    second = due_events(now + timedelta(seconds=30), timings, 10, True)
    assert [e.key for e in first] == [e.key for e in second]
    assert all(e.key.startswith("2026-10-31:") for e in first)
