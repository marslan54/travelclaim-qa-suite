"""Field-level validation coverage for the travel claim intake UI."""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.claim_form_pages import ClaimFlightDetailsPage, ClaimPassengerPage, TravelClaimWizard
from utils.test_data import valid_flight_segment


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("UI / Validation")
@allure.title("Step 1 blocks progression when mandatory flight fields are empty")
def test_step1_requires_mandatory_flight_fields(logged_in_claim_step1: Page, base_url: str) -> None:
    flight = ClaimFlightDetailsPage(logged_in_claim_step1, base_url, locale="en")
    flight.proceed()
    flight.expect_validation_errors_visible(
        "field-error-airline",
        "field-error-flight",
        "field-error-dep",
        "field-error-arr",
        "field-error-date",
    )


@pytest.mark.regression
@allure.title("Step 2 surfaces errors when passenger profile is incomplete")
def test_step2_requires_passenger_profile(logged_in_claim_step1: Page, base_url: str) -> None:
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

    passenger = ClaimPassengerPage(logged_in_claim_step1, base_url, locale="en")
    passenger.proceed()
    expect(logged_in_claim_step1.locator('[data-testid="field-error-first"]')).to_be_visible()
    expect(logged_in_claim_step1.locator('[data-testid="field-error-last"]')).to_be_visible()
    expect(logged_in_claim_step1.locator('[data-testid="field-error-email"]')).to_be_visible()
    expect(logged_in_claim_step1.locator('[data-testid="field-error-reason"]')).to_be_visible()


@pytest.mark.regression
@allure.title("Invalid credentials do not advance the session")
def test_invalid_login_shows_banner(page: Page, base_url: str) -> None:
    from pages.login_page import LoginPage

    login = LoginPage(page, base_url, locale="en")
    login.open()
    login.sign_in("not-a-user@example.com", "wrong-password")
    login.expect_invalid_credentials_banner()
    expect(page).to_have_url(re.compile(r".+/en/login$"))
