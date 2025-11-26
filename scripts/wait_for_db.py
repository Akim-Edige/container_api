from __future__ import annotations

import asyncio
import os
import sys
import time

from sqlalchemy import text

from app.database import engine


TIMEOUT_SECONDS = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
SLEEP_SECONDS = float(os.getenv("DB_WAIT_INTERVAL", "1"))


async def wait_for_db() -> None:
    deadline = time.monotonic() + TIMEOUT_SECONDS
    attempt = 0

    while True:
        attempt += 1
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except Exception as exc:  # pragma: no cover - best-effort wait
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                print(f"Database not reachable after {TIMEOUT_SECONDS}s: {exc}", file=sys.stderr)
                raise
            print(f"[wait_for_db] Attempt {attempt} failed ({exc}); retrying in {SLEEP_SECONDS}s...")
            await asyncio.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    asyncio.run(wait_for_db())


