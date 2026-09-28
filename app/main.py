"""Enhanced main API with authentication, rate limiting, and audit."""
from __future__ import annotations

import asyncio
import time
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.auth import TokenData, verify_token, create_access_token
from app.audit import audit_log
from app.booking import build_booking_plan, parse_trip_request
from app.cache import ScheduleCache
from app.config import settings
from app.logger import get_logger
from app.ratelimit import rate_limiter

logger = get_logger(__name__)
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    debug=settings.debug,
)

schedule_cache = ScheduleCache(ttl_seconds=3600)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)  # In production, hash and verify securely.


class BookingRequest(BaseModel):
    request: Annotated[str, Field(min_length=5, max_length=500)]


class BookingResponse(BaseModel):
    status: str
    trip: dict
    candidate_trains: list[dict]
    passengers: list[dict]
    preparation_ms: float
    next_step: str
    automation_limits: list[str]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/auth/login")
async def login(payload: LoginRequest) -> dict[str, str]:
    """Demo login endpoint. In production, validate against a secure store."""
    # For demo: accept any username/password. Replace with real auth.
    if not payload.username or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user_id=f"user_{payload.username}", username=payload.username)
    audit_log.log(f"user_{payload.username}", "login", {"username": payload.username})
    logger.info(f"User {payload.username} logged in")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/booking/plan", response_model=BookingResponse)
async def booking_plan(
    payload: BookingRequest,
    token: Annotated[TokenData, Depends(verify_token)],
) -> BookingResponse:
    """Generate a booking plan based on user input."""
    user_id = token.user_id

    # Rate limit check
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )

    started = time.perf_counter()
    try:
        trip = parse_trip_request(payload.request)
    except ValueError as exc:
        audit_log.log(user_id, "booking_plan_failed", {"error": str(exc)})
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Concurrent cache and profile fetch
    schedule, passengers = await asyncio.gather(
        schedule_cache.get(trip.origin, trip.destination, trip.travel_date),
        load_passenger_profile(trip.passenger_count),
    )

    plan_dict = build_booking_plan(trip, schedule, passengers)
    plan_dict["preparation_ms"] = round((time.perf_counter() - started) * 1000, 2)

    audit_log.log(
        user_id,
        "booking_plan_generated",
        {
            "origin": trip.origin,
            "destination": trip.destination,
            "class": trip.class_code,
            "passengers": trip.passenger_count,
            "preparation_ms": plan_dict["preparation_ms"],
        },
    )
    logger.info(
        f"Booking plan generated for {user_id}: {trip.origin} → {trip.destination} in {plan_dict['preparation_ms']}ms"
    )

    return BookingResponse(**plan_dict)


async def load_passenger_profile(count: int) -> list[dict[str, str]]:
    """Load passenger profiles. In production, fetch from encrypted store."""
    await asyncio.sleep(0)
    return [{"passenger_index": str(i + 1), "status": "details_required"} for i in range(count)]
