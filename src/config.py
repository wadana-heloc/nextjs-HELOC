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
CREDIT_SCORE_MIN: Final[int] = 680
DBR_MAX: Final[float] = 0.5  # 50% debt-burden ratio cap
LTV_MAX: Final[float] = 0.8  # 80% loan-to-value cap


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
# Data paths
# ---------------------------------------------------------------------------

DLD_PRICE_JSON_PATH: Final[Path] = BASE_DIR / "data" / "DLD_avg_price_per_sqft_by_community_property_type.json"

