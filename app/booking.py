"""Request parsing and booking-plan construction without booking-side automation."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Trip:
    origin: str
    destination: str
    travel_date: str
    class_code: str
    passenger_count: int


CLASS_CODES = {"1AC", "2AC", "3AC", "SL", "CC", "EC", "2S"}


def parse_trip_request(text: str) -> Trip:
    # Accepts: "26 Oct Mumbai to Delhi, 2AC, 2 passengers".
    match = re.search(
        r"(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]+)\s+"
        r"(?P<origin>[A-Za-z .'-]+?)\s+to\s+(?P<destination>[A-Za-z .'-]+?)\s*,\s*"
        r"(?P<class>1AC|2AC|3AC|SL|CC|EC|2S)\s*,\s*"
        r"(?P<count>\d+)\s+passengers?",
        text.strip(),
        re.IGNORECASE,
    )
    if not match:
        raise ValueError("Use: DD Mon Origin to Destination, CLASS, N passengers")

    try:
        travel_date = date.fromisoformat(
            f"{date.today().year}-{match.group('month')[:3].title()}-{int(match.group('day')):02d}"
        )
    except ValueError as exc:
        raise ValueError("The travel date is invalid") from exc

    count = int(match.group("count"))
    if not 1 <= count <= 6:
        raise ValueError("Passenger count must be between 1 and 6")

    class_code = match.group("class").upper()
    return Trip(
        origin=match.group("origin").strip(),
        destination=match.group("destination").strip(),
        travel_date=travel_date.isoformat(),
        class_code=class_code,
        passenger_count=count,
    )


def build_booking_plan(trip: Trip, schedule: list[dict], passengers: list[dict]) -> dict:
    return {
        "status": "ready_for_user_review",
        "trip": trip.__dict__,
        "candidate_trains": schedule,
        "passengers": passengers,
        "next_step": "Open the official IRCTC page or authorized provider, verify details, then complete OTP/CAPTCHA/payment yourself.",
        "automation_limits": ["no_otp_bypass", "no_captcha_bypass", "no_payment_bypass"],
    }
