import pytest

from bot.db import Database


@pytest.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.connect()
    yield database
    await database.close()


async def test_create_and_update_user(db):
    user = await db.create_user(1, "ar", 4)
    assert not user.has_location and user.remind_before == 10 and user.adhkar

    await db.update(1, lat=24.47, lon=39.61, tz="Asia/Riyadh", lang="en", adhkar=0)
    user = await db.get_user(1)
    assert user.has_location and user.lang == "en" and not user.adhkar


async def test_create_user_is_idempotent(db):
    await db.create_user(1, "ar", 4)
    await db.update(1, lang="en")
    again = await db.create_user(1, "ar", 4)
    assert again.lang == "en"


async def test_update_rejects_unknown_fields(db):
    await db.create_user(1, "ar", 4)
    with pytest.raises(ValueError):
        await db.update(1, created_at="x")


async def test_mark_sent_only_once(db):
    assert await db.mark_sent(1, "2026-10-31:adhan:Asr") is True
    assert await db.mark_sent(1, "2026-10-31:adhan:Asr") is False
    assert await db.mark_sent(2, "2026-10-31:adhan:Asr") is True


async def test_located_users_and_counts(db):
    await db.create_user(1, "ar", 4)
    await db.create_user(2, "en", 4)
    await db.update(2, lat=1.0, lon=2.0, tz="UTC")
    assert [u.user_id for u in await db.located_users()] == [2]
    assert await db.count_users() == (2, 1)


async def test_delete_user_clears_sent(db):
    await db.create_user(1, "ar", 4)
    await db.mark_sent(1, "k")
    await db.delete_user(1)
    assert await db.get_user(1) is None
    assert await db.mark_sent(1, "k") is True


async def test_migration_adds_lang_chosen_to_old_database(tmp_path):
    import aiosqlite

    path = str(tmp_path / "old.db")
    async with aiosqlite.connect(path) as old:
        await old.executescript(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY, lang TEXT NOT NULL DEFAULT 'ar', lat REAL, lon REAL,
                tz TEXT, method INTEGER NOT NULL DEFAULT 4, remind_before INTEGER NOT NULL DEFAULT 10,
                adhkar INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL);
            INSERT INTO users (user_id, lat, lon, tz, created_at) VALUES (1, 1.0, 2.0, 'UTC', 'x');
            INSERT INTO users (user_id, created_at) VALUES (2, 'x');
            """
        )
        await old.commit()

    database = Database(path)
    await database.connect()
    try:
        assert (await database.get_user(1)).lang_chosen is True   # already set up
        assert (await database.get_user(2)).lang_chosen is False  # still has to choose
    finally:
        await database.close()
