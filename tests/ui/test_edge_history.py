"""Browser history regressions mid-wizard."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.claim_form_pages import TravelClaimWizard
from utils.test_data import valid_flight_segment


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("UI / Edge cases")
@allure.title("Back navigation restores persisted server state for step 1")
def test_history_back_retains_flight_segment(logged_in_claim_step1: Page, base_url: str) -> None:
    wizard = TravelClaimWizard(logged_in_claim_step1, base_url, locale="en")
    segment = valid_flight_segment()
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

    logged_in_claim_step1.go_back()
    wizard.flight.expect_step_heading()
    expect(logged_in_claim_step1.locator('[data-testid="field-airline-code"]')).to_have_value(segment["airline_code"])
    expect(logged_in_claim_step1.locator('[data-testid="field-flight-number"]')).to_have_value(segment["flight_number"])


@pytest.mark.regression
@allure.title("Forward navigation returns to the latest wizard step after back")
def test_history_forward_returns_to_step2(logged_in_claim_step1: Page, base_url: str) -> None:
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
    wizard.passenger.expect_on_step()
    logged_in_claim_step1.go_back()
    logged_in_claim_step1.go_forward()
    wizard.passenger.expect_on_step()
