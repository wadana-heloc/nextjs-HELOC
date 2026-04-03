"""Centralized configuration and business rules for the HELOC API service.

This module contains:
- filesystem paths used by the application
- business-rule constants for credit / risk logic
- eligibility lists for communities and property types
- any cross-cutting configuration such as allowed CORS origins
"""

from pathlib import Path
from typing import Final, Iterable, Set


BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Web / API configuration
# ---------------------------------------------------------------------------

# Define allowed frontend origins for CORS as configuration instead of
# hard-coding them inside the FastAPI app wiring.
FRONTEND_ALLOWED_ORIGINS: Final[Iterable[str]] = (
    "http://localhost:3000",
)

# ---------------------------------------------------------------------------
# Business-rule configuration
# ---------------------------------------------------------------------------

# These can be tuned without touching any other code.
CREDIT_SCORE_MIN: Final[int] = 657
DBR_MAX: Final[float] = 0.5  # 50% debt-burden ratio cap
LTV_MAX: Final[float] = 0.6  # 60% max lendable value
RENTAL_RATE: Final[float] = 0.05  # 5% annual rental rate
OFFER_EXPIRY_YEARS: Final[int] = 10
REPAYMENT_YEARS: Final[int] = 20

# Application statuses
APPLICATION_STATUS_PENDING: Final[str] = "pending"
APPLICATION_STATUS_APPROVED: Final[str] = "approved"
APPLICATION_STATUS_REJECTED: Final[str] = "rejected"
APPLICATION_STATUS_EXPIRED: Final[str] = "expired"
APPLICATION_INITIAL_STATUS: Final[str] = APPLICATION_STATUS_PENDING

# Contract statuses
CONTRACT_STATUS_DRAFT: Final[str] = "draft"
CONTRACT_STATUS_SIGNED: Final[str] = "signed"
CONTRACT_STATUS_REJECTED: Final[str] = "rejected"


# ---------------------------------------------------------------------------
# Eligibility configuration
# ---------------------------------------------------------------------------

# These should correspond to communities in the DLD price table.
ELIGIBLE_COMMUNITIES: Final[Set[str]] = {
    "AL FURJAN",
    "AL KHAIL HEIGHTS",
    "ARABIAN RANCHES I",
    "ARABIAN RANCHES III",
    "ARJAN",
    "Al Hebiah Fifth",
    "Al Hebiah Fourth",
    "Al Hebiah Sixth",
    "Al Khairan First",
    "Al Kifaf",
    "Al Satwa",
    "Al Warqa First",
    "Al Wasl",
    "Al Yelayiss 1",
    "Al Yelayiss 2",
    "Al Yelayiss 5",
    "BLUEWATERS",
    "BURJ KHALIFA",
    "BUSINESS BAY",
    "BUSINESS PARK",
    "Bukadra",
    "Business Bay",
    "DAMAC HILLS",
    "DISCOVERY GARDENS",
    "DMCC-EZ2",
    "DOWN TOWN JABAL ALI",
    "DUBAI CREEK HARBOUR",
    "DUBAI HEALTHCARE CITY - PHASE 2",
    "DUBAI HILLS",
    "DUBAI INDUSTRIAL CITY",
    "DUBAI INVESTMENT PARK FIRST",
    "DUBAI INVESTMENT PARK SECOND",
    "DUBAI LAND RESIDENCE COMPLEX",
    "DUBAI MARINA",
    "DUBAI MARITIME CITY",
    "DUBAI PRODUCTION CITY",
    "DUBAI SCIENCE PARK",
    "DUBAI SOUTH",
    "DUBAI SPORTS CITY",
    "DUBAI STUDIO CITY",
    "DUBAI WATER CANAL",
    "Dubai Investment Park Second",
    "EMAAR SOUTH",
    "EMIRATE LIVING",
    "HORIZON",
    "Hadaeq Sheikh Mohammed Bin Rashid",
    "INTERNATIONAL CITY PH 1",
    "INTERNATIONAL CITY PH 2 & 3",
    "JADDAF WATERFRONT",
    "JUMEIRAH BEACH RESIDENCE",
    "JUMEIRAH GOLF",
    "JUMEIRAH LAKES TOWERS",
    "JUMEIRAH VILLAGE CIRCLE",
    "JUMEIRAH VILLAGE TRIANGLE",
    "Jabal Ali First",
    "LIVING LEGENDS",
    "LIWAN",
    "MAJAN",
    "MBR DISTRICT 1",
    "MEYDAN ONE",
    "MINA RASHID",
    "MOTOR CITY",
    "MUDON",
    "Madinat Al Mataar",
    "Madinat Dubai Almelaheyah",
    "Madinat Hind 3",
    "Marsa Dubai",
    "Me'Aisem First",
    "Mirdif",
    "Muhaisanah First",
    "NAD AL SHEBA GARDENS",
    "Nad Al Shiba First",
    "PALM JUMEIRAH",
    "Palm Deira",
    "Ras Al Khor Industrial First",
    "SAMA AL JADAF",
    "SILICON OASIS",
    "SOBHA HEARTLAND",
    "TECOM SITE A",
    "TOWN SQUARE",
    "VILLANOVA",
    "Wadi Al Safa 3",
    "Wadi Al Safa 5",
    "Zaabeel First",
    "Zaabeel Second",
}

ELIGIBLE_PROPERTY_TYPES: Final[Set[str]] = {
    "apartment",
    "villa",
}


# ---------------------------------------------------------------------------
# Contract template
# ---------------------------------------------------------------------------

CONTRACT_TEXT: Final[str] = """\
### **CO-OWNERSHIP & RENT (IJARA) AGREEMENT**

**1. THE CONCEPT**
This is a **Rent-Only Co-Ownership** agreement. The Platform does not lend money; instead, it purchases a proportional ownership stake in the Property whenever the Homeowner draws funds.

**2. OWNERSHIP STAKES**
*   **Initial:** The Platform owns 0% until funds are accessed.
*   **Dynamic:** The Platform's ownership share increases with every draw and decreases with every capital repayment.

**3. RENT (IJARA)**
*   The Homeowner shall pay monthly rent to the Platform.
*   **Calculation:** Rent is charged **only** on the Platform's current ownership percentage.
*   No interest (Riba) shall be charged.

**4. ESCALATION & SALE**
*   **Non-Payment:** If rent is not paid, the Platform's ownership share increases according to the agreed schedule in lieu of penalties.
*   **Property Sale:** If the property is sold, proceeds are shared based on the ownership percentages at that time.

**5. NO OBLIGATION**
The Homeowner is not required to buy back the Platform's stake by a fixed date. The relationship remains a flexible co-ownership until the capital is voluntarily returned or the property is sold.\
"""


# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------

DLD_PRICE_JSON_PATH: Final[Path] = BASE_DIR / "data" / "DLD_avg_price_per_sqft_by_community_property_type.json"
DUMMY_APPLICANTS_JSON_PATH: Final[Path] = BASE_DIR / "data" / "dummy_applicants.json"

