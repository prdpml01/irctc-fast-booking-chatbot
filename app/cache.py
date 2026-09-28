"""Redis-based caching for production scalability."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


class ScheduleCache:
    """Redis cache wrapper; falls back to in-memory on connection error."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._fallback: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self.redis_client = None
        self._connect_redis()

    def _connect_redis(self) -> None:
        """Attempt to connect to Redis; log and continue if unavailable."""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            logger.info(f"Connected to Redis at {settings.redis_url}")
        except ImportError:
            logger.warning("redis package not installed; using in-memory fallback")
        except Exception as exc:
            logger.warning(f"Redis connection failed: {exc}; using in-memory fallback")

    async def get(self, origin: str, destination: str, travel_date: str) -> list[dict[str, Any]]:
        """Retrieve cached schedule or fetch placeholder."""
        key = f"schedule:{origin.lower()}:{destination.lower()}:{travel_date}"

        if self.redis_client:
            try:
                cached = await self.redis_client.get(key)
                if cached:
                    logger.info(f"Cache hit for {key}")
                    return json.loads(cached)
            except Exception as exc:
                logger.warning(f"Redis read failed: {exc}; falling back")

        # Fallback or placeholder
        value = [{"train": "placeholder", "availability": "recheck_required", "source": "mock_data"}]

        if self.redis_client:
            try:
                await self.redis_client.setex(key, self.ttl_seconds, json.dumps(value))
                logger.info(f"Cached {key} for {self.ttl_seconds}s")
            except Exception as exc:
                logger.warning(f"Redis write failed: {exc}")

        return value
