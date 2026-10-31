from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    token: str
    db_path: str = "data/salah.db"
    default_method: int = 4  # Umm Al-Qura University, Makkah
    port: int = 8080
    admin_ids: frozenset[int] = field(default_factory=frozenset)

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("BOT_TOKEN is missing. Copy .env.example to .env and set it.")
        admins = {
            int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x.isdigit()
        }
        return cls(
            token=token,
            db_path=os.getenv("DB_PATH", "data/salah.db"),
            default_method=int(os.getenv("DEFAULT_METHOD", "4")),
            port=int(os.getenv("PORT", "8080")),
            admin_ids=frozenset(admins),
        )
