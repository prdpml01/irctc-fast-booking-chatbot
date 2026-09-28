"""In-memory event log for audit trails and rate limiting."""
from __future__ import annotations

import time
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class AuditEvent:
    timestamp: float
    user_id: str
    action: str
    details: dict


class AuditLog:
    """Simple in-memory audit log; use a database or ELK in production."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []
        self.user_action_counts: defaultdict = defaultdict(int)

    def log(self, user_id: str, action: str, details: dict | None = None) -> None:
        """Log an audit event."""
        event = AuditEvent(
            timestamp=time.time(),
            user_id=user_id,
            action=action,
            details=details or {},
        )
        self.events.append(event)
        self.user_action_counts[user_id] += 1

    def get_user_events(self, user_id: str, limit: int = 100) -> list[AuditEvent]:
        """Retrieve recent events for a user."""
        return [
            e for e in sorted(self.events, key=lambda x: x.timestamp, reverse=True)
            if e.user_id == user_id
        ][:limit]

    def get_action_count(self, user_id: str) -> int:
        """Return action count for rate limiting."""
        return self.user_action_counts.get(user_id, 0)


audit_log = AuditLog()
