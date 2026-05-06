"""Multi-step travel expense / compensation claim wizard (POM split per step)."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ClaimFlightDetailsPage(BasePage):
    """Step 1 — itinerary capture."""

    def open(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        self.page.goto(self.abs_url(f"{loc}/claim/step1"))

    def fill_flight_segment(
        self,
        *,
        airline_code: str,
        flight_number: str,
        departure: str,
        arrival: str,
        travel_date: str,
        booking_reference: str = "",
    ) -> None:
        self.page.locator('[data-testid="field-airline-code"]').fill(airline_code)
        self.page.locator('[data-testid="field-flight-number"]').fill(flight_number)
        self.page.locator('[data-testid="field-departure-airport"]').fill(departure)
        self.page.locator('[data-testid="field-arrival-airport"]').fill(arrival)
        self.page.locator('[data-testid="field-travel-date"]').fill(travel_date)
        if booking_reference:
            self.page.locator('[data-testid="field-booking-ref"]').fill(booking_reference)

    def proceed(self) -> None:
        self.page.locator('[data-testid="claim-step1-next"]').click()

    def expect_validation_errors_visible(self, *tokens: str) -> None:
        for token in tokens:
            expect(self.page.locator(f'[data-testid="{token}"]')).to_be_visible()

    def expect_step_heading(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        expect(self.page).to_have_url(self.abs_url(f"{loc}/claim/step1"))
        expect(self.page.locator('[data-testid="claim-heading"]')).to_be_visible()


class ClaimPassengerPage(BasePage):
    """Step 2 — claimant identity & regulatory reason."""

    def fill_passenger(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        reason_code: str,
    ) -> None:
        self.page.locator('[data-testid="field-first-name"]').fill(first_name)
        self.page.locator('[data-testid="field-last-name"]').fill(last_name)
        self.page.locator('[data-testid="field-contact-email"]').fill(email)
        self.page.locator('[data-testid="field-reason-code"]').select_option(value=reason_code)

    def back_to_flight_details(self, locale: str | None = None) -> None:
        self.page.locator('[data-testid="claim-step2-back"]').click()

    def proceed(self) -> None:
        self.page.locator('[data-testid="claim-step2-next"]').click()

    def expect_on_step(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        expect(self.page).to_have_url(self.abs_url(f"{loc}/claim/step2"))


class ClaimReviewPage(BasePage):
    """Step 3 — read-only recap before submission."""

    def expect_review_contains(self, text: str) -> None:
        expect(self.page.get_by_text(text, exact=False)).to_be_visible()

    def submit(self) -> None:
        self.page.locator('[data-testid="claim-submit-button"]').click()

    def back_to_passenger(self) -> None:
        self.page.locator('[data-testid="claim-step3-back"]').click()

    def expect_on_step(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        expect(self.page).to_have_url(self.abs_url(f"{loc}/claim/step3"))


class TravelClaimWizard:
    """Thin façade bundling wizard steps."""

    def __init__(self, page: Page, base_url: str, locale: str = "en") -> None:
        self.flight = ClaimFlightDetailsPage(page, base_url, locale)
        self.passenger = ClaimPassengerPage(page, base_url, locale)
        self.review = ClaimReviewPage(page, base_url, locale)
