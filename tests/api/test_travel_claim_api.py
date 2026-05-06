"""Contract tests for the mock travel-claim submission service."""

from __future__ import annotations

import json

import allure
import pytest
import requests

from utils.test_data import api_claim_payload


def _assert_accepted_schema(body: dict) -> None:
    assert set(body.keys()) >= {"claim_id", "reference", "status"}
    assert body["status"] == "accepted"
    assert isinstance(body["claim_id"], str)
    assert body["claim_id"].startswith("TC-")
    assert isinstance(body["reference"], str)
    assert 6 <= len(body["reference"]) <= 64


@pytest.mark.api
@allure.suite("TravelClaim")
@allure.sub_suite("API")
@allure.title("Valid payload returns 201 with stable schema")
def test_travel_claim_accepted(base_url_session: str) -> None:
    response = requests.post(
        f"{base_url_session.rstrip('/')}/api/v1/travel-claims",
        data=json.dumps(api_claim_payload()),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert response.status_code == 201
    _assert_accepted_schema(response.json())


@pytest.mark.api
@allure.title("Malformed JSON body yields 422 validation errors")
def test_travel_claim_validation_error(base_url_session: str) -> None:
    payload = api_claim_payload()
    payload["passenger"].pop("email", None)
    response = requests.post(
        f"{base_url_session.rstrip('/')}/api/v1/travel-claims",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


@pytest.mark.api
@allure.title("Simulated 400 mapping for downstream validation faults")
def test_simulated_bad_request(base_url_session: str) -> None:
    response = requests.post(
        f"{base_url_session.rstrip('/')}/api/v1/travel-claims?_simulate=400",
        data=json.dumps(api_claim_payload()),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "VALIDATION_FAILED"


@pytest.mark.api
@allure.title("Simulated 500 aligns with outage monitoring expectations")
def test_simulated_upstream_failure(base_url_session: str) -> None:
    response = requests.post(
        f"{base_url_session.rstrip('/')}/api/v1/travel-claims?_force500=true",
        data=json.dumps(api_claim_payload()),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert response.status_code == 500


@pytest.mark.api
@allure.title("Playwright API context can drive the same contract")
def test_playwright_request_context(page, base_url: str) -> None:
    """Validates integrator-style calls using Playwright transport (cookies/corp proxies)."""

    payload = api_claim_payload()
    response = page.request.post(
        f"{base_url.rstrip('/')}/api/v1/travel-claims",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    assert response.status == 201
    _assert_accepted_schema(response.json())
