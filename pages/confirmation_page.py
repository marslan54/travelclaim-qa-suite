"""Post-submission confirmation / receipt screen."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ConfirmationPage(BasePage):
    def expect_success(self) -> None:
        expect(self.page.locator('[data-testid="confirmation-heading"]')).to_be_visible()
        expect(self.page.locator('[data-testid="confirmation-reference"]')).to_have_text(
            re.compile(r"[A-Z0-9]{6,}")
        )

    def reference_value(self) -> str:
        return self.page.locator('[data-testid="confirmation-reference"]').inner_text()
