"""Regression pack — mirrors production smoke depth with alternate market data."""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.claim_form_pages import TravelClaimWizard
from pages.confirmation_page import ConfirmationPage
from utils.test_data import iso_date_days_ago


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("Regression")
@allure.title("Alternate airline profile still reaches confirmation with unique reference")
def test_alternate_airline_profile_submits(logged_in_claim_step1: Page, base_url: str) -> None:
    wizard = TravelClaimWizard(logged_in_claim_step1, base_url, locale="en")
    wizard.flight.fill_flight_segment(
        airline_code="TP",
        flight_number="TP0234",
        departure="LIS",
        arrival="EWR",
        travel_date=iso_date_days_ago(60),
        booking_reference="TP99ZZ",
    )
    wizard.flight.proceed()
    wizard.passenger.fill_passenger(
        first_name="Ines",
        last_name="Carvalho",
        email="ines.carvalho@example.com",
        reason_code="DELAY_GT3_261",
    )
    wizard.passenger.proceed()
    wizard.review.submit()

    confirmation = ConfirmationPage(logged_in_claim_step1, base_url, locale="en")
    confirmation.expect_success()
    ref = confirmation.reference_value()
    assert re.fullmatch(r"[A-F0-9]{12}", ref)
    expect(logged_in_claim_step1.locator('[data-testid="confirmation-summary-line"]')).to_contain_text("TP")
