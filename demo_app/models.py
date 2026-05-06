"""Pydantic models for the mock travel claim API."""

from pydantic import BaseModel, EmailStr, Field


class FlightSegment(BaseModel):
    airline_code: str = Field(..., min_length=2, max_length=3)
    flight_number: str = Field(..., pattern=r"^[A-Za-z0-9]{1,8}$")
    departure_airport_iata: str = Field(..., min_length=3, max_length=3)
    arrival_airport_iata: str = Field(..., min_length=3, max_length=3)
    departure_date_iso: str = Field(..., description="YYYY-MM-DD")
    booking_reference: str | None = Field(default=None, max_length=64)


class Passenger(BaseModel):
    legal_first_name: str = Field(..., min_length=1, max_length=80)
    legal_last_name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr


class TravelClaimPayload(BaseModel):
    segment: FlightSegment
    passenger: Passenger
    claim_reason_code: str = Field(..., min_length=4, max_length=32)


class TravelClaimAccepted(BaseModel):
    claim_id: str
    reference: str
    status: str = "accepted"
