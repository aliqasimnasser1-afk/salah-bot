from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    lang           TEXT    NOT NULL DEFAULT 'ar',
    lat            REAL,
    lon            REAL,
    tz             TEXT,
    method         INTEGER NOT NULL DEFAULT 4,
    remind_before  INTEGER NOT NULL DEFAULT 10,
    adhkar         INTEGER NOT NULL DEFAULT 1,
    lang_chosen    INTEGER NOT NULL DEFAULT 0,
    place          TEXT,
    created_at     TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS sent (
    user_id  INTEGER NOT NULL,
    key      TEXT    NOT NULL,
    sent_at  TEXT    NOT NULL,
    PRIMARY KEY (user_id, key)
);
"""

EDITABLE = {"lang", "lang_chosen", "place", "lat", "lon", "tz", "method", "remind_before", "adhkar"}


@dataclass
class User:
    user_id: int
    lang: str
    lat: float | None
    lon: float | None
    tz: str | None
    method: int
    remind_before: int
    adhkar: bool
    lang_chosen: bool = False
    place: str | None = None

    @property
    def has_location(self) -> bool:
        return self.lat is not None and self.lon is not None and bool(self.tz)


def _row_to_user(row: aiosqlite.Row) -> User:
    return User(
        user_id=row["user_id"],
        lang=row["lang"],
        lat=row["lat"],
        lon=row["lon"],
        tz=row["tz"],
        method=row["method"],
        remind_before=row["remind_before"],
        adhkar=bool(row["adhkar"]),
        lang_chosen=bool(row["lang_chosen"]),
        place=row["place"],
    )


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        self._db = await aiosqlite.connect(self.path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)
        await self._migrate()
        await self._db.commit()

    async def _migrate(self) -> None:
        """Upgrade databases created by earlier versions."""
        async with self.db.execute("PRAGMA table_info(users)") as cur:
            columns = {row["name"] for row in await cur.fetchall()}
        if "lang_chosen" not in columns:
            await self.db.execute(
                "ALTER TABLE users ADD COLUMN lang_chosen INTEGER NOT NULL DEFAULT 0"
            )
            # Anyone already set up has effectively chosen a language.
            await self.db.execute("UPDATE users SET lang_chosen = 1 WHERE lat IS NOT NULL")
        if "place" not in columns:
            await self.db.execute("ALTER TABLE users ADD COLUMN place TEXT")

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    @property
    def db(self) -> aiosqlite.Connection:
        assert self._db is not None, "Database.connect() was not called"
        return self._db

    async def get_user(self, user_id: int) -> User | None:
        async with self.db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        return _row_to_user(row) if row else None

    async def create_user(self, user_id: int, lang: str, method: int) -> User:
        await self.db.execute(
            "INSERT OR IGNORE INTO users (user_id, lang, method, created_at) VALUES (?, ?, ?, ?)",
            (user_id, lang, method, datetime.now(timezone.utc).isoformat()),
        )
        await self.db.commit()
        user = await self.get_user(user_id)
        assert user is not None
        return user

    async def update(self, user_id: int, **fields: object) -> None:
        bad = set(fields) - EDITABLE
        if bad:
            raise ValueError(f"Unknown user fields: {sorted(bad)}")
        if not fields:
            return
        cols = ", ".join(f"{k} = ?" for k in fields)
        await self.db.execute(
            f"UPDATE users SET {cols} WHERE user_id = ?", (*fields.values(), user_id)
        )
        await self.db.commit()

    async def delete_user(self, user_id: int) -> None:
        await self.db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await self.db.execute("DELETE FROM sent WHERE user_id = ?", (user_id,))
        await self.db.commit()

    async def located_users(self) -> list[User]:
        async with self.db.execute(
            "SELECT * FROM users WHERE lat IS NOT NULL AND lon IS NOT NULL AND tz IS NOT NULL"
        ) as cur:
            rows = await cur.fetchall()
        return [_row_to_user(r) for r in rows]

    async def count_users(self) -> tuple[int, int]:
        async with self.db.execute(
            "SELECT COUNT(*), SUM(lat IS NOT NULL) FROM users"
        ) as cur:
            row = await cur.fetchone()
        return int(row[0] or 0), int(row[1] or 0)

    async def mark_sent(self, user_id: int, key: str) -> bool:
        """Record a notification. Returns True only the first time, so it is never sent twice."""
        cur = await self.db.execute(
            "INSERT OR IGNORE INTO sent (user_id, key, sent_at) VALUES (?, ?, ?)",
            (user_id, key, datetime.now(timezone.utc).isoformat()),
        )
        await self.db.commit()
        return cur.rowcount == 1

    async def prune_sent(self, days: int = 3) -> None:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        await self.db.execute("DELETE FROM sent WHERE sent_at < ?", (cutoff,))
        await self.db.commit()
