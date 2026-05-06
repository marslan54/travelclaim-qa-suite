"""Login / account gateway for TravelClaim portal."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    FORM = 'form[data-testid="login-form"]'

    def open(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        self.page.goto(self.abs_url(f"{loc}/login"))
        expect(self.page).to_have_title(re.compile(r".+"))

    def sign_in(self, email: str, password: str) -> None:
        self.page.locator('[data-testid="login-email"]').fill(email)
        self.page.locator('[data-testid="login-password"]').fill(password)
        self.page.locator('[data-testid="login-submit"]').click()

    def expect_invalid_credentials_banner(self) -> None:
        expect(self.page.locator('[data-testid="login-error-banner"]')).to_be_visible()

    def expect_on_claim_wizard(self, locale: str | None = None) -> None:
        loc = locale or self.locale
        expect(self.page).to_have_url(self.abs_url(f"{loc}/claim/step1"))


class AccountPage(LoginPage):
    """Alias consistent with portal terminology (authentication surface)."""

    pass
