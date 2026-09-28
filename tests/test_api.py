"""Tests for authentication, rate limiting, and booking flow."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import create_access_token
from app.booking import parse_trip_request

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login() -> None:
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_booking_plan_authenticated() -> None:
    # Login
    login_resp = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    # Booking plan
    response = client.post(
        "/booking/plan",
        headers={"Authorization": f"Bearer {token}"},
        json={"request": "26 Oct Mumbai to Delhi, 2AC, 2 passengers"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_user_review"
    assert data["trip"]["origin"] == "Mumbai"
    assert data["trip"]["destination"] == "Delhi"
    assert data["trip"]["class_code"] == "2AC"


def test_parse_trip_request() -> None:
    trip = parse_trip_request("26 Oct Mumbai to Delhi, 2AC, 2 passengers")
    assert trip.origin == "Mumbai"
    assert trip.destination == "Delhi"
    assert trip.class_code == "2AC"
    assert trip.passenger_count == 2


def test_parse_trip_request_invalid() -> None:
    with pytest.raises(ValueError):
        parse_trip_request("invalid request")
