"""Fast checks that the compensation portal shell is alive."""

from __future__ import annotations

import allure
import pytest
import requests
from playwright.sync_api import Page, expect

from pages.claim_form_pages import ClaimFlightDetailsPage
from pages.login_page import LoginPage


@pytest.mark.smoke
@allure.suite("TravelClaim")
@allure.sub_suite("Smoke")
@allure.title("Health endpoint reports ready state")
def test_health_probe(base_url: str) -> None:
    response = requests.get(f"{base_url.rstrip('/')}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.smoke
@allure.title("Login surface renders expected controls")
def test_login_form_renders(page: Page, base_url: str) -> None:
    login = LoginPage(page, base_url, locale="en")
    login.open()
    expect(page.locator('[data-testid="login-heading"]')).to_be_visible()
    expect(page.locator('[data-testid="login-email"]')).to_be_visible()
    expect(page.locator('[data-testid="login-password"]')).to_be_visible()
    expect(page.locator('[data-testid="login-submit"]')).to_be_enabled()


@pytest.mark.smoke
@allure.title("Authenticated user sees claim wizard step 1")
def test_claim_wizard_step1_renders(logged_in_claim_step1: Page, base_url: str) -> None:
    flight = ClaimFlightDetailsPage(logged_in_claim_step1, base_url, locale="en")
    flight.expect_step_heading()
    expect(logged_in_claim_step1.locator('[data-testid="claim-step1-form"]')).to_be_visible()
