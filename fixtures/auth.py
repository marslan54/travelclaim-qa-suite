"""Demo portal credentials (mirrors demo_app.main defaults)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PortalUser:
    email: str
    password: str


def portal_credentials() -> PortalUser:
    return PortalUser(
        email=os.environ.get("TC_DEMO_EMAIL", "claims.analyst@travelclaim.example"),
        password=os.environ.get("TC_DEMO_PASSWORD", "Eu261_R3gress!"),
    )
