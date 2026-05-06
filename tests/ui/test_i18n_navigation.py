"""Locale routing and copy switches for international operations teams."""

from __future__ import annotations

import allure
import pytest
import requests
from playwright.sync_api import Page, expect

from fixtures.auth import portal_credentials
from pages.claim_form_pages import TravelClaimWizard
from pages.login_page import LoginPage
from utils.test_data import iso_date_days_ago


@pytest.mark.regression
@allure.suite("TravelClaim")
@allure.sub_suite("UI / i18n")
@allure.title("Public locale catalog matches supported markets")
def test_locale_config_endpoint(base_url: str) -> None:
    response = requests.get(f"{base_url.rstrip('/')}/api/v1/config/locales", timeout=5)
    body = response.json()
    assert response.status_code == 200
    assert set(body["supported_locales"]) >= {"en", "de", "fr"}


@pytest.mark.regression
@allure.title("Switching header locale updates login copy")
@pytest.mark.parametrize(
    ("locale", "snippet"),
    [
        ("de", "Anmelden"),
        ("fr", "Connexion"),
    ],
)
def test_login_heading_follows_locale(page: Page, base_url: str, locale: str, snippet: str) -> None:
    login = LoginPage(page, base_url, locale="en")
    login.open("en")
    login.switch_locale_via_header(locale)
    expect(page.get_by_role("heading", level=1)).to_contain_text(snippet)


@pytest.mark.regression
@allure.title("Deep-linking to localized routes preserves wizard structure")
def test_localized_claim_url_renders_steps(page: Page, base_url: str) -> None:
    creds = portal_credentials()
    login = LoginPage(page, base_url, locale="de")
    login.open("de")
    login.sign_in(creds.email, creds.password)
    page.goto(f"{base_url.rstrip('/')}/de/claim/step1")
    expect(page.locator('[data-testid="step-indicator"]')).to_contain_text("Schritt")

    wizard = TravelClaimWizard(page, base_url, locale="de")
    wizard.flight.fill_flight_segment(
        airline_code="LX",
        flight_number="LX1610",
        departure="ZRH",
        arrival="VIE",
        travel_date=iso_date_days_ago(40),
    )
    wizard.flight.proceed()
    wizard.passenger.expect_on_step()
