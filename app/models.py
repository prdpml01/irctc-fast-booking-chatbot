"""Encrypted passenger and user profile storage."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class PassengerProfile:
    """Passenger details—name, age, gender, ID type."""

    first_name: str
    last_name: str
    age: int
    gender: str  # M / F / O
    id_type: str  # Aadhaar, PAN, DL, Passport, etc.
    id_number: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> PassengerProfile:
        return PassengerProfile(**data)


@dataclass
class UserProfile:
    """Minimal user profile for booking history and preferences."""

    user_id: str
    username: str
    email: str
    phone: str
    passengers: list[PassengerProfile]
    default_class: Optional[str] = "2AC"
    notification_enabled: bool = True

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "passengers": [p.to_dict() for p in self.passengers],
        }

    @staticmethod
    def from_dict(data: dict) -> UserProfile:
        data["passengers"] = [
            PassengerProfile.from_dict(p) for p in data.get("passengers", [])
        ]
        return UserProfile(**data)
