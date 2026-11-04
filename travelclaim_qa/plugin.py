"""Pytest plugin shipped with the package: base URL override, portal health check and a saved login.

Registered through the ``pytest11`` entry point in pyproject.toml, so every project that installs
travelclaim-qa gets these fixtures without copying a conftest.py.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Browser

from travelclaim_qa.auth import portal_credentials
from travelclaim_qa.pages.login_page import LoginPage


def pytest_configure(config: pytest.Config) -> None:
    """Resolve base_url once: TRAVELCLAIM_BASE_URL, then --base-url, then the ini value.

    pytest-base-url skips its own configure step on pytest-xdist workers, so the value is set here,
    where it runs on the controller and on every worker.
    """
    url = os.environ.get("TRAVELCLAIM_BASE_URL") or config.option.base_url or config.getini("base_url")
    if url:
        config.option.base_url = url.rstrip("/")


@pytest.fixture(scope="session", autouse=True)
def verify_portal(base_url: str) -> None:
    """Fail fast with a clear message when the portal is not running."""
    try:
        requests.get(f"{base_url.rstrip('/')}/health", timeout=5).raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - exercised in misconfigured envs
        pytest.exit(
            f"TravelClaim portal not reachable at {base_url} ({exc}). "
            "Start it with: uvicorn demo_app.main:app --host 127.0.0.1 --port 8765",
            returncode=1,
        )


@pytest.fixture(scope="session")
def auth_storage_state(browser: Browser, base_url: str, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Log in once per session (once per worker under xdist) and save the session cookie for reuse."""
    path = tmp_path_factory.mktemp("auth") / "storage_state.json"
    context = browser.new_context()
    try:
        page = context.new_page()
        creds = portal_credentials()
        login = LoginPage(page, base_url)
        login.open()
        login.sign_in(creds.email, creds.password)
        login.expect_on_claim_wizard()
        context.storage_state(path=str(path))
    finally:
        context.close()
    return path
