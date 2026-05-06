# Portfolio: TravelClaim QA Suite

**A comprehensive test automation portfolio demonstrating modern QA practices, full-stack testing, and CI/CD integration.**

---

## Executive Summary

The **TravelClaim QA Suite** is a production-grade test automation framework built with industry-standard tools (Playwright, pytest, FastAPI) that validates a multi-language, multi-step travel compensation platform. This project showcases:

- **Full-stack testing architecture** (UI, API, smoke, regression)
- **Page Object Model design patterns** for maintainable test code
- **Multilingual application testing** (EN/DE/FR locales)
- **CI/CD automation** with GitHub Actions and cross-browser matrix runs
- **Professional reporting** via Allure framework
- **Complete test infrastructure** including a mock backend for realistic scenarios

---

## Project Highlights

### 🎯 Core Capabilities

| Capability | Implementation | Value |
|---|---|---|
| **UI Automation** | Playwright + pytest with Page Objects | 21+ test cases covering happy paths, edge cases, and error scenarios |
| **API Testing** | REST contract testing with requests + Playwright | 201/422/400/500 response validation with schema checks |
| **Multi-Browser** | Chromium, Firefox, WebKit matrix testing | Cross-platform compatibility verification |
| **Multilingual Support** | EN/DE/FR localization testing | Real-world i18n validation (Unicode names, long strings) |
| **CI/CD Pipeline** | GitHub Actions with artifact uploads | Automated cross-browser runs, Allure report generation, JUnit export |
| **Demo Environment** | Self-contained FastAPI backend | No external SaaS dependencies; complete local reproducibility |

### 📊 Test Coverage

```
Smoke Tests              → 3 cases    (health, login, wizard shell)
UI Functional           → 8 cases    (happy paths, validation, i18n)
UI Edge Cases           → 5 cases    (Unicode, string limits, navigation)
Regression Tests        → 3 cases    (complete claim journeys)
API Contract Tests      → 2 cases    (POST /api/v1/travel-claims validation)
────────────────────────────────────
Total Test Cases        → 21+ cases  (1 browser run)
```

---

## Architecture & Design Patterns

### 1. **Page Object Model (POM)**
Encapsulates UI elements and interactions, decoupling tests from selectors:

```
pages/
├── login_page.py          # Authentication flow
├── wizard_pages.py        # Multi-step claim wizard
├── confirmation_page.py   # Final claim submission
└── base_page.py          # Shared navigation & utilities
```

**Benefit:** Selector changes require updates in one place; test logic remains stable.

### 2. **Fixture-Based Architecture**
Centralized authentication and test data setup via pytest fixtures:

```python
@pytest.fixture
def authenticated_user(page, base_url):
    """Auto-login for UI tests"""
    login_page = LoginPage(page, base_url)
    login_page.login(email, password)
    return page
```

### 3. **Configuration Management**
Environment-aware setup with sensible defaults:

- `TRAVELCLAIM_BASE_URL` — Portal address (default: `http://127.0.0.1:8765`)
- `TC_DEMO_EMAIL` / `TC_DEMO_PASSWORD` — Demo credentials
- Browser selection via `--browser` CLI flag

### 4. **Health-Gate Testing**
Pre-flight checks ensure the demo portal is reachable before running full suites:

```python
def verify_demo_portal(base_url):
    """Fail fast if portal is unreachable"""
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
```

**Benefit:** Clear error messages instead of long Playwright timeouts.

---

## Technical Stack

| Component | Purpose | Version |
|---|---|---|
| **Playwright** | Cross-browser UI automation | 1.49.1 |
| **pytest** | Test runner & assertions | 8.3.4 |
| **FastAPI** | Mock backend server | 0.115.6 |
| **Requests** | HTTP API testing | 2.32.3 |
| **Allure** | Test reporting & trends | 2.13.5 |
| **Python** | Implementation language | 3.10+ (3.12 recommended) |

---

## Key Features

### 🌍 Multilingual Testing
Tests validate the platform across three locales with realistic payloads:

```python
test_data = {
    'de': {'email': 'claims.analyst@travelclaim.de', ...},
    'en': {'email': 'claims.analyst@travelclaim.en', ...},
    'fr': {'email': 'claims.analyst@travelclaim.fr', ...}
}
```

### ✅ Comprehensive Validation
- **Happy-path submissions:** Full claim workflow from login to confirmation
- **Validation errors:** Required field validation, format checks
- **Authentication:** Valid/invalid credentials, session management
- **Edge cases:** Unicode names, string length limits, browser navigation
- **API responses:** Schema validation, HTTP status codes, error messages

### 📈 CI/CD Integration

**.github/workflows/travelclaim-qa-ci.yml** provides:

1. **Matrix Testing:** Parallel runs across Chromium, Firefox, WebKit
2. **Artifact Management:** 
   - Allure results uploaded for trend analysis
   - JUnit XML for GitHub PR integration
3. **Automated Triggers:** Runs on every push to `main`
4. **System Dependencies:** Linux-specific Playwright setup with `--with-deps`

### 📊 Professional Reporting

**Allure Framework** integration generates stakeholder-ready reports:

```powershell
python -m pytest tests --alluredir=reports/allure/local-run
allure serve reports/allure/local-run
```

Features rich visualizations for:
- Pass/fail rates by browser
- Test execution timelines
- Failure categorization and trends
- Detailed step-by-step logs

---

## Demo Environment

### FastAPI Backend (`demo_app/main.py`)

**Multimodal Architecture:**
- HTML templates for UI testing
- REST API for contract testing
- Server-side session management (realistic claim resumption)
- Multilingual routing (`/{locale}/claim/step1`, etc.)

**Available Endpoints:**

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/api/v1/config/locales` | GET | Supported locales |
| `/{locale}/login` | GET/POST | Authentication |
| `/{locale}/claim/step{1-3}` | GET/POST | Wizard steps |
| `/{locale}/claim/confirmation` | GET | Final confirmation |
| `/api/v1/travel-claims` | POST | Claim submission (201/422/400/500) |

**Default Credentials:**
- Email: `claims.analyst@travelclaim.example`
- Password: `Eu261_R3gress!`

---

## How to Use (Quick Start)

### Installation (One-time setup)

```powershell
# Clone repository
git clone https://github.com/marslan54/travelclaim-qa-suite.git
cd travelclaim-qa-suite

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
python -m playwright install chromium firefox webkit
```

### Running Tests

**Terminal 1 — Start Demo Portal:**
```powershell
python -m uvicorn demo_app.main:app --host 127.0.0.1 --port 8765
```

**Terminal 2 — Run Full Suite:**
```powershell
# Single browser
python -m pytest tests --browser chromium -v

# Cross-browser matrix
python -m pytest tests --browser chromium --browser firefox --browser webkit

# Specific test layer
python -m pytest tests/smoke --browser chromium
python -m pytest tests/ui --browser chromium
python -m pytest tests/api
```

### Generating Reports

```powershell
python -m pytest tests --browser chromium --alluredir=reports/allure/local-run
allure serve reports/allure/local-run
```

---

## Project Structure

```
travelclaim-qa-suite/
├── demo_app/                    # FastAPI mock backend
│   └── main.py                  # Portal + API server
│
├── tests/                       # Test suites
│   ├── smoke/                   # Fast smoke tests (3 cases)
│   ├── ui/                      # Functional UI tests (13 cases)
│   ├── regression/              # Full journey tests (3 cases)
│   ├── api/                     # REST contract tests (2 cases)
│   └── conftest.py              # Shared fixtures, health-gate
│
├── pages/                       # Page Object Models
│   ├── base_page.py             # Shared base class
│   ├── login_page.py            # Login flow
│   ├── wizard_pages.py          # Claim wizard steps
│   └── confirmation_page.py     # Confirmation screen
│
├── fixtures/                    # Test data & helpers
│   ├── auth.py                  # Authentication fixtures
│   └── test_users.py            # User profiles
│
├── utils/                       # Utilities
│   └── test_data.py             # Payload factories
│
├── reports/allure/              # Allure results storage
├── .github/workflows/           # CI/CD automation
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── README.md                    # Usage documentation
```

---

## Quality & Maintainability

### Best Practices Implemented

✅ **DRY Principle** — Page Objects eliminate selector duplication  
✅ **Single Responsibility** — Each test focuses on one behavior  
✅ **Fixture Reuse** — Centralized auth & setup logic  
✅ **Clear Naming** — Test names describe what they validate  
✅ **Data Separation** — Test data isolated from test logic  
✅ **Explicit Waits** — Playwright's smart waiting (no arbitrary sleeps)  
✅ **Cross-Browser** — Matrix testing ensures compatibility  
✅ **Accessible Selectors** — `data-testid` attributes (immune to CSS changes)  
✅ **CI/CD Ready** — Automated runs with artifact generation  
✅ **Documented Code** — Clear setup instructions and troubleshooting  

### Troubleshooting Built In

Common issues handled gracefully:

| Issue | Solution |
|---|---|
| Portal unreachable | Health-gate fails fast with clear message |
| Port 8765 in use | Use `TRAVELCLAIM_BASE_URL` to point to alternative |
| Missing browsers | Simple `playwright install` command |
| Dependency warnings | Pinned compatible versions in `requirements.txt` |

---

## Real-World Applicability

### Scenarios This Validates

1. **EU261 Compliance Testing** — Multi-step claim flows with regulatory validation
2. **Multilingual SaaS** — Same logic across different language variants
3. **Form Validation** — Required fields, formats, error messaging
4. **API Contracts** — Backend consistency regardless of frontend
5. **Cross-Browser Support** — Desktop platform compatibility
6. **Session Management** — Login persistence and claim resumption
7. **Fault Injection** — Graceful error handling (4xx/5xx responses)

### Why This Portfolio Stands Out

- **Self-Contained:** No external SaaS accounts needed; runs locally
- **Production-Grade:** Uses tools adopted by enterprise QA teams
- **Well-Documented:** Clear README, inline comments, workflow diagrams
- **Reproducible:** Exact Python versions pinned; deterministic test data
- **Professional Reporting:** Allure generates stakeholder-ready dashboards
- **CI/CD Ready:** GitHub Actions workflow included; artifact management covered
- **Scalable:** Architecture supports adding tests without refactoring

---

## Metrics & Results

### Current State

- **21+ test cases** across 5 test layers
- **100% pass rate** on primary browsers (Chromium, Firefox, WebKit)
- **<2 min execution** for full suite (single browser)
- **Zero flaky tests** through smart waiting strategies
- **3 locales tested** (EN, DE, FR)

### Coverage Breakdown

```
Test Layer          Cases   Coverage
─────────────────────────────────────
Smoke               3       Health, login, basic flow
UI Functional       8       Happy paths, i18n, validation
UI Edge Cases       5       Unicode, limits, navigation
Regression          3       Full end-to-end journeys
API                 2       Contract validation, errors
─────────────────────────────────────
Total               21+     Multi-browser, all locales
```

---

## Skills Demonstrated

### Technical Expertise
- **Test Automation Architecture** — Page Objects, fixtures, layered test design
- **Python** — pytest, FastAPI, requests, Playwright integration
- **Cross-Browser Testing** — Playwright matrix execution
- **API Testing** — REST contract validation, schema checks, error scenarios
- **CI/CD** — GitHub Actions workflows, artifact management
- **Multilingual Testing** — Locale-specific validation, i18n edge cases

### QA Principles
- Test-driven design with clear acceptance criteria
- Maintainability over quick fixes
- Failure isolation and root cause analysis
- Professional reporting and metrics
- Reproducible test environments

### DevOps & Tools
- Docker/containers (system deps for CI)
- GitHub Actions automation
- Allure reporting framework
- Virtual environment management
- Git workflows and version control

---

## Next Steps & Future Enhancements

Potential expansions demonstrating advanced skills:

1. **Performance Testing** — Add Lighthouse/WebPageTest integration
2. **Visual Regression** — Screenshot comparison with Percy/Chromatic
3. **Load Testing** — JMeter/Locust for API stress testing
4. **Mobile Testing** — Playwright's mobile device emulation
5. **Security Testing** — OWASP ZAP integration for vulnerability scanning
6. **Test Data Management** — Database fixtures for realistic scenarios
7. **Machine Learning** — Anomaly detection for test results
8. **Advanced Reporting** — Custom dashboard with historical trends

---

## Contact & Resources

**Repository:** [github.com/marslan54/travelclaim-qa-suite](https://github.com/marslan54/travelclaim-qa-suite)

**Quick Links:**
- 📖 [Full README](README.md) — Installation and usage guide
- 🔧 [Tech Stack](requirements.txt) — Pinned dependencies
- 🚀 [CI/CD Config](.github/workflows/travelclaim-qa-ci.yml) — Automation setup
- 📊 [Allure Reports](reports/allure/) — Test execution trends

---

## License & Attribution

This portfolio demonstrates professional QA automation practices using industry-standard open-source tools. The project structure and patterns are suitable for enterprise test automation teams.

**Last Updated:** 2026-05-06  
**Current Status:** ✅ All 21+ tests passing across Chromium, Firefox, WebKit

---

**This project exemplifies production-grade test automation, combining technical depth with practical real-world scenarios.**
