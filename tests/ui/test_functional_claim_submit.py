"""End-to-end happy path through the multi-step claim workflow."""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.claim_form_pages import TravelClaimWizard
from pages.confirmation_page import ConfirmationPage
from utils.test_data import valid_flight_segment, valid_passenger


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("UI / Functional")
@allure.title("Submit a valid EU261-style claim through the wizard")
def test_full_claim_happy_path(logged_in_claim_step1: Page, base_url: str) -> None:
    wizard = TravelClaimWizard(logged_in_claim_step1, base_url, locale="en")
    segment = valid_flight_segment()
    traveler = valid_passenger()

    wizard.flight.fill_flight_segment(
        airline_code=segment["airline_code"],
        flight_number=segment["flight_number"],
        departure=segment["departure"],
        arrival=segment["arrival"],
        travel_date=segment["travel_date"],
        booking_reference=segment["booking_reference"],
    )
    wizard.flight.proceed()
    wizard.passenger.expect_on_step()

    wizard.passenger.fill_passenger(
        first_name=traveler["first_name"],
        last_name=traveler["last_name"],
        email=traveler["email"],
        reason_code=traveler["reason_code"],
    )
    wizard.passenger.proceed()
    wizard.review.expect_on_step()
    expect(logged_in_claim_step1.locator('[data-testid="review-flight"]')).to_contain_text(segment["airline_code"])

    wizard.review.submit()
    confirmation = ConfirmationPage(logged_in_claim_step1, base_url, locale="en")
    confirmation.expect_success()
    expect(logged_in_claim_step1).to_have_url(re.compile(r".+/en/claim/confirmation\?ref=.+"))
