"""Small in-memory cache abstraction; replace with Redis in production."""
from __future__ import annotations

import asyncio
import time
from typing import Any


class ScheduleCache:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def get(self, origin: str, destination: str, travel_date: str) -> list[dict[str, Any]]:
        key = f"{origin.lower()}:{destination.lower()}:{travel_date}"
        now = time.monotonic()
        async with self._lock:
            cached = self._values.get(key)
            if cached and now - cached[0] < self.ttl_seconds:
                return cached[1]
            # Placeholder only. Populate this through an authorized provider.
            value = [{"train": "availability-provider-required", "availability": "recheck_required"}]
            self._values[key] = (now, value)
            return value
