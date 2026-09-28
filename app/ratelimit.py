"""Rate limiting by user."""
from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter; use Redis in production."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: defaultdict = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if user has not exceeded rate limit."""
        now = time.time()
        cutoff = now - self.window_seconds
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if ts > cutoff
        ]
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(now)
            return True
        return False


rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
