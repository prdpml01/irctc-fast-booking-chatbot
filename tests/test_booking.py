"""Basic parser tests."""
from app.booking import parse_trip_request


def test_parse_request() -> None:
    trip = parse_trip_request("26 Oct Mumbai to Delhi, 2AC, 2 passengers")
    assert trip.origin == "Mumbai"
    assert trip.destination == "Delhi"
    assert trip.class_code == "2AC"
    assert trip.passenger_count == 2
