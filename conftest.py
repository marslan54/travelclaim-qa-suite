"""
Shared pytest fixtures for TravelClaim QA Suite.

Prerequisite: demo stack running on BASE_URL (default http://127.0.0.1:8765).
Start with: uvicorn demo_app.main:app --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
import requests
from playwright.sync_api import Page

from fixtures.auth import portal_credentials
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """Prefer TRAVELCLAIM_BASE_URL, then pytest-base-url's ini/CLI option."""

    env = os.environ.get("TRAVELCLAIM_BASE_URL")
    if env:
        return env.rstrip("/")
    return str(request.config.getoption("base_url"))


@pytest.fixture(scope="session", autouse=True)
def verify_demo_portal(base_url: str) -> Generator[None, None, None]:
    """Fail fast with a clear message when the mock portal is not running."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/health", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - exercised in misconfigured envs
        pytest.exit(
            f"TravelClaim demo portal not reachable at {base_url} ({exc}). "
            "Start it with: uvicorn demo_app.main:app --host 127.0.0.1 --port 8765",
            returncode=1,
        )
    yield


@pytest.fixture(scope="session")
def base_url_session(base_url: str) -> str:
    return base_url


@pytest.fixture
def logged_in_claim_step1(page: Page, base_url: str) -> Page:
    """Authenticates through the UI and lands on step 1 of the claim wizard."""
    creds = portal_credentials()
    login = LoginPage(page, base_url)
    login.open()
    login.sign_in(creds.email, creds.password)
    login.expect_on_claim_wizard()
    return page
