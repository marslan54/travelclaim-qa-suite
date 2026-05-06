"""Synthetic but realistic payloads for regulator-style travel disruptions."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def iso_date_days_ago(days: int) -> str:
    """ISO date string for HTML date inputs and REST payloads."""
    return (date.today() - timedelta(days=days)).isoformat()


def valid_flight_segment() -> dict[str, str]:
    return {
        "airline_code": "LH",
        "flight_number": "LH440",
        "departure": "FRA",
        "arrival": "JFK",
        "travel_date": iso_date_days_ago(9),
        "booking_reference": "ABC12X",
    }


def valid_passenger() -> dict[str, str]:
    return {
        "first_name": "Mira",
        "last_name": "Kovács-Łępicka",
        "email": "mira.kovacs+eu261@example.com",
        "reason_code": "DELAY_GT3_261",
    }


def api_claim_payload(
    *,
    passenger_email: str | None = None,
    booking_reference: str | None = "X7K9LM",
) -> dict[str, Any]:
    """JSON body aligned with `/api/v1/travel-claims` schema."""
    traveler_email = passenger_email or "integrations@travelclaim.example"
    return {
        "segment": {
            "airline_code": "BA",
            "flight_number": "BA112",
            "departure_airport_iata": "LHR",
            "arrival_airport_iata": "OSL",
            "departure_date_iso": iso_date_days_ago(21),
            "booking_reference": booking_reference,
        },
        "passenger": {
            "legal_first_name": "Noah",
            "legal_last_name": "Strauss",
            "email": traveler_email,
        },
        "claim_reason_code": "CANCELLED_261",
    }
