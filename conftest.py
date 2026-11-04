"""Project fixtures for this repository's tests.

Shared fixtures (base_url, the portal health check and the saved login) come from the installed
travelclaim_qa.plugin. Prerequisite: the demo portal running on the base URL
(uvicorn demo_app.main:app --host 127.0.0.1 --port 8765).
"""

from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import Page

from travelclaim_qa.pages.claim_form_pages import ClaimFlightDetailsPage
from travelclaim_qa.pages.login_page import LoginPage

AUTHENTICATED_FIXTURES = {"logged_in_claim_step1"}


@pytest.fixture
def browser_context_args(browser_context_args: dict[str, Any], request: pytest.FixtureRequest) -> dict[str, Any]:
    """Start authenticated tests from the saved login instead of logging in through the UI each time."""
    if AUTHENTICATED_FIXTURES & set(request.fixturenames):
        return {**browser_context_args, "storage_state": request.getfixturevalue("auth_storage_state")}
    return browser_context_args


@pytest.fixture
def logged_in_claim_step1(page: Page, base_url: str) -> Page:
    """An authenticated page on step 1 of the claim wizard."""
    ClaimFlightDetailsPage(page, base_url).open()
    LoginPage(page, base_url).expect_on_claim_wizard()
    return page
