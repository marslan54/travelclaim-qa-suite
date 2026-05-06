"""Edge scenarios for international names and extreme input lengths."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.claim_form_pages import TravelClaimWizard
from pages.confirmation_page import ConfirmationPage
from utils.test_data import iso_date_days_ago, valid_flight_segment


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("UI / Edge cases")
@allure.title("Unicode and punctuation are preserved in passenger identity fields")
def test_special_characters_in_legal_name(logged_in_claim_step1: Page, base_url: str) -> None:
    wizard = TravelClaimWizard(logged_in_claim_step1, base_url, locale="en")
    segment = valid_flight_segment()
    wizard.flight.fill_flight_segment(
        airline_code=segment["airline_code"],
        flight_number=segment["flight_number"],
        departure=segment["departure"],
        arrival=segment["arrival"],
        travel_date=segment["travel_date"],
    )
    wizard.flight.proceed()

    wizard.passenger.fill_passenger(
        first_name="François",
        last_name="O'Neill-Ødegaard",
        email="francois.oneill+claim@example.com",
        reason_code="DENIED_BOARD_261",
    )
    wizard.passenger.proceed()
    expect(logged_in_claim_step1.locator('[data-testid="review-name"]')).to_contain_text("François")
    expect(logged_in_claim_step1.locator('[data-testid="review-name"]')).to_contain_text("O'Neill")

    wizard.review.submit()
    ConfirmationPage(logged_in_claim_step1, base_url, locale="en").expect_success()


@pytest.mark.regression
@allure.title("Maximum-length strings within HTML constraints are accepted")
def test_boundary_length_names(logged_in_claim_step1: Page, base_url: str) -> None:
    wizard = TravelClaimWizard(logged_in_claim_step1, base_url, locale="en")
    long_first = "A" * 120
    long_last = "Z" * 120
    wizard.flight.fill_flight_segment(
        airline_code="AY",
        flight_number="AY1332",
        departure="HEL",
        arrival="ORD",
        travel_date=iso_date_days_ago(14),
    )
    wizard.flight.proceed()
    wizard.passenger.fill_passenger(
        first_name=long_first,
        last_name=long_last,
        email="boundary-test@travelclaim.example",
        reason_code="CANCELLED_261",
    )
    wizard.passenger.proceed()
    summary = logged_in_claim_step1.locator('[data-testid="review-name"]')
    expect(summary).to_contain_text(long_first[:32])
    expect(summary).to_contain_text(long_last[:32])
