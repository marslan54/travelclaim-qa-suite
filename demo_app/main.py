"""
Minimal TravelClaim Compensation portal — serves multilingual UI + mock REST API.

Run locally: uvicorn demo_app.main:app --host 127.0.0.1 --port 8765 --reload
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import date
from urllib.parse import quote
from typing import Annotated, Any

from fastapi import FastAPI, Form, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from demo_app.i18n_strings import LABELS
from demo_app.models import TravelClaimAccepted, TravelClaimPayload

LANGS = frozenset({"en", "de", "fr"})
DEMO_EMAIL = os.environ.get("TC_DEMO_EMAIL", "claims.analyst@travelclaim.example")
DEMO_PASSWORD = os.environ.get("TC_DEMO_PASSWORD", "Eu261_R3gress!")

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(_APP_DIR, "templates"))
app = FastAPI(title="TravelClaim Demo Portal", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key="travelclaim-session-dev-key-change-in-prod")
app.mount("/static", StaticFiles(directory=os.path.join(_APP_DIR, "static")), name="static")


def _labels(lang: str) -> dict[str, str]:
    return LABELS.get(lang, LABELS["en"])


def _ensure_lang(lang: str) -> str:
    if lang not in LANGS:
        raise HTTPException(status_code=404, detail="Unknown locale")
    return lang


def _require_login(request: Request, lang: str) -> RedirectResponse | None:
    if request.session.get("logged_in"):
        return None
    next_path = quote(f"/{lang}/claim/step1", safe="/")
    return RedirectResponse(url=f"/{lang}/login?next={next_path}", status_code=302)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Align with canonical FastAPI validation semantics expected by QA consumers."""
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


@app.get("/", response_model=None)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/en/login")


@app.api_route("/health", methods=["GET", "HEAD"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "travelclaim-demo"}


@app.get("/api/v1/config/locales", response_class=JSONResponse)
async def locales() -> dict[str, Any]:
    return {"supported_locales": ["en", "de", "fr"], "default_locale": "en"}


@app.get("/{lang}/login", response_class=HTMLResponse, response_model=None)
async def login_get(request: Request, lang: str) -> HTMLResponse | RedirectResponse:
    lang = _ensure_lang(lang)
    if request.session.get("logged_in"):
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=302)
    tpl = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "login",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "error_login": False,
        },
    )
    return tpl


@app.post("/{lang}/login", response_class=HTMLResponse, response_model=None)
async def login_post(
    request: Request,
    lang: str,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> RedirectResponse | HTMLResponse:
    lang = _ensure_lang(lang)
    if email.strip() == DEMO_EMAIL and password == DEMO_PASSWORD:
        request.session["logged_in"] = True
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "login",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "error_login": True,
            "email_value": email,
        },
        status_code=401,
    )


@app.get("/{lang}/claim/step1", response_class=HTMLResponse, response_model=None)
async def claim_step1(request: Request, lang: str) -> HTMLResponse | RedirectResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    claim = request.session.get("claim") or {}
    flight = claim.get("flight", {})
    return templates.TemplateResponse(
        "claim_step1.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "claim/step1",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "step": 1,
            "total_steps": 3,
            "flight": flight,
            "today": date.today().isoformat(),
        },
    )


@app.post("/{lang}/claim/step1", response_class=HTMLResponse, response_model=None)
async def claim_step1_post(
    request: Request,
    lang: str,
    airline_code: Annotated[str, Form()],
    flight_number: Annotated[str, Form()],
    departure_airport: Annotated[str, Form()],
    arrival_airport: Annotated[str, Form()],
    travel_date: Annotated[str, Form()],
    booking_reference: Annotated[str | None, Form()] = None,
) -> RedirectResponse | HTMLResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    errors: dict[str, bool] = {}
    if not airline_code.strip():
        errors["airline_code"] = True
    if not flight_number.strip():
        errors["flight_number"] = True
    if not departure_airport.strip():
        errors["departure_airport"] = True
    if not arrival_airport.strip():
        errors["arrival_airport"] = True
    if not travel_date.strip():
        errors["travel_date"] = True

    flight = {
        "airline_code": airline_code.strip().upper(),
        "flight_number": flight_number.strip().upper(),
        "departure_airport": departure_airport.strip().upper(),
        "arrival_airport": arrival_airport.strip().upper(),
        "travel_date": travel_date.strip(),
        "booking_reference": (booking_reference or "").strip(),
    }
    if errors:
        return templates.TemplateResponse(
            "claim_step1.html",
            {
                "request": request,
                "lang": lang,
                "route_path": "claim/step1",
                "L": _labels(lang),
                "languages": sorted(LANGS),
                "step": 1,
                "total_steps": 3,
                "flight": flight,
                "field_errors": errors,
                "today": date.today().isoformat(),
            },
            status_code=422,
        )

    sess = dict(request.session.get("claim") or {})
    sess["flight"] = flight
    request.session["claim"] = sess
    return RedirectResponse(url=f"/{lang}/claim/step2", status_code=303)


@app.get("/{lang}/claim/step2", response_class=HTMLResponse, response_model=None)
async def claim_step2(request: Request, lang: str) -> HTMLResponse | RedirectResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    claim = request.session.get("claim") or {}
    if "flight" not in claim:
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=302)
    return templates.TemplateResponse(
        "claim_step2.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "claim/step2",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "step": 2,
            "total_steps": 3,
            "passenger": claim.get("passenger", {}),
        },
    )


@app.post("/{lang}/claim/step2", response_class=HTMLResponse, response_model=None)
async def claim_step2_post(
    request: Request,
    lang: str,
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    contact_email: Annotated[str, Form()],
    claim_reason_code: Annotated[str, Form()],
) -> RedirectResponse | HTMLResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    claim_session = dict(request.session.get("claim") or {})
    if "flight" not in claim_session:
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=302)

    errors: dict[str, bool] = {}
    if not first_name.strip():
        errors["first_name"] = True
    if not last_name.strip():
        errors["last_name"] = True
    if not contact_email.strip():
        errors["contact_email"] = True
    if not claim_reason_code.strip():
        errors["claim_reason_code"] = True

    passenger = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "contact_email": contact_email.strip(),
        "claim_reason_code": claim_reason_code.strip().upper(),
    }
    if errors:
        return templates.TemplateResponse(
            "claim_step2.html",
            {
                "request": request,
                "lang": lang,
                "route_path": "claim/step2",
                "L": _labels(lang),
                "languages": sorted(LANGS),
                "step": 2,
                "total_steps": 3,
                "passenger": passenger,
                "field_errors": errors,
            },
            status_code=422,
        )

    claim_session["passenger"] = passenger
    request.session["claim"] = claim_session
    return RedirectResponse(url=f"/{lang}/claim/step3", status_code=303)


@app.get("/{lang}/claim/step3", response_class=HTMLResponse, response_model=None)
async def claim_step3(request: Request, lang: str) -> HTMLResponse | RedirectResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    claim = request.session.get("claim") or {}
    if "flight" not in claim or "passenger" not in claim:
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=302)
    return templates.TemplateResponse(
        "claim_step3.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "claim/step3",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "step": 3,
            "total_steps": 3,
            "flight": claim["flight"],
            "passenger": claim["passenger"],
        },
    )


@app.post("/{lang}/claim/step3/submit", response_model=None)
async def claim_submit(request: Request, lang: str) -> RedirectResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    claim = request.session.get("claim") or {}
    flight = claim.get("flight") or {}
    passenger = claim.get("passenger") or {}
    if not flight or not passenger:
        return RedirectResponse(url=f"/{lang}/claim/step1", status_code=302)

    reference = secrets.token_hex(6).upper()
    request.session.pop("claim", None)
    request.session["last_reference"] = reference
    request.session["last_summary"] = json.dumps({"flight": flight, "passenger": passenger})
    return RedirectResponse(url=f"/{lang}/claim/confirmation?ref={reference}", status_code=303)


@app.get("/{lang}/claim/confirmation", response_class=HTMLResponse, response_model=None)
async def claim_confirmation(request: Request, lang: str, ref: Annotated[str, Query(alias="ref")]) -> HTMLResponse | RedirectResponse:
    lang = _ensure_lang(lang)
    redir = _require_login(request, lang)
    if redir:
        return redir
    if ref != request.session.get("last_reference"):
        raise HTTPException(status_code=403, detail="Invalid confirmation reference")
    summary_raw = request.session.get("last_summary")
    summary = json.loads(summary_raw) if summary_raw else {}

    tpl = templates.TemplateResponse(
        "confirmation.html",
        {
            "request": request,
            "lang": lang,
            "route_path": "claim/step1",
            "L": _labels(lang),
            "languages": sorted(LANGS),
            "reference": ref,
            "flight": summary.get("flight", {}),
            "passenger": summary.get("passenger", {}),
        },
    )
    request.session.pop("last_reference", None)
    request.session.pop("last_summary", None)
    return tpl


def _simulate_500(enabled: bool) -> None:
    if enabled:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="upstream dependency timeout")


@app.post(
    "/api/v1/travel-claims",
    response_model=TravelClaimAccepted,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def submit_travel_claim(
    payload: TravelClaimPayload,
    simulate_http_status: Annotated[int | None, Query(alias="_simulate")] = None,
    force_500: Annotated[bool, Query(alias="_force500")] = False,
) -> TravelClaimAccepted:
    """Programmatic submission used by automation (and integrators).

    `_simulate`: return a specific HTTP status for negative testing (demo only).
    """
    _simulate_500(force_500)
    if simulate_http_status == 500:
        raise HTTPException(status_code=500, detail="simulated server error")
    if simulate_http_status == 400:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_FAILED", "message": "Simulated validation failure"})

    claim_id = f"TC-{secrets.token_hex(4).upper()}"
    reference = payload.segment.booking_reference or secrets.token_hex(5).upper()
    return TravelClaimAccepted(claim_id=claim_id, reference=reference, status="accepted")
