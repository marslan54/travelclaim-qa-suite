"""Base page primitives shared across the TravelClaim portal POM."""

from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page, base_url: str, locale: str = "en") -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.locale = locale

    def abs_url(self, path: str) -> str:
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    def switch_locale_via_header(self, code: str) -> None:
        link = self.page.get_by_test_id(f"lang-link-{code.lower()}")
        expect(link).to_be_visible()
        link.click()

    def expect_brand_visible(self) -> None:
        expect(self.page.get_by_test_id("app-brand")).to_be_visible()
