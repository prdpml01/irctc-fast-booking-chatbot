"""FastAPI entry point for a compliant booking-plan assistant."""
from __future__ import annotations

import asyncio
import time
from datetime import date
from typing import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .booking import build_booking_plan, parse_trip_request
from .cache import ScheduleCache

app = FastAPI(title="IRCTC Fast Booking Assistant", version="0.1.0")
schedule_cache = ScheduleCache(ttl_seconds=3600)


class BookingRequest(BaseModel):
    request: Annotated[str, Field(min_length=5, max_length=500)]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/booking/plan")
async def booking_plan(payload: BookingRequest) -> dict:
    started = time.perf_counter()
    try:
        trip = parse_trip_request(payload.request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # These independent reads are intentionally concurrent. Availability remains
    # advisory and must be revalidated by an authorized provider at checkout.
    schedule, passengers = await asyncio.gather(
        schedule_cache.get(trip.origin, trip.destination, trip.travel_date),
        load_passenger_profile(trip.passenger_count),
    )
    plan = build_booking_plan(trip, schedule, passengers)
    plan["preparation_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return plan


async def load_passenger_profile(count: int) -> list[dict[str, str]]:
    """Demo-only profile loader; production storage must be encrypted and consented."""
    await asyncio.sleep(0)
    return [{"passenger_index": str(i + 1), "status": "details_required"} for i in range(count)]
