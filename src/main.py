"""FastAPI application entrypoint for the HELOC API's.

This module wires together:
- the FastAPI app instance and middleware (e.g. CORS)
- database lifecycle hooks on startup
- routes for health checks, user listing, and value estimation
- seeding logic for mock data and DLD price information
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func as sa_func
from sqlalchemy.orm import Session

import config
from database import Base, SessionLocal, engine, get_db, ensure_db_schema
from schemas import EstimateIn, EstimateOut, UserOut, ApplicationIn, ApplicationOut, ApplicationListOut, ContractSignIn
from agents.offer_summary_agent import summarize_offer

import models  # noqa: F401 - registers models on Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.FRONTEND_ALLOWED_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_mock_data(db_session: Session) -> None:
    """Insert demo user, property, and application records for local development.

    **Inputs**
    - `db_session`: SQLAlchemy session used to query and insert seed data.

    **Outputs**
    - Returns `None`. Commits any inserted seed records to the database.
    """
    if db_session.execute(select(models.User)).first() is None:
        db_session.add_all(
            [
                models.User(name="Ahmed Al Mansoori", email="ahmed@example.com"),
                models.User(name="Sara Khalid", email="sara@example.com"),
                models.User(name="Omar Nasser", email="omar@example.com"),
            ]
        )

    if db_session.execute(select(models.Property)).first() is None:
        db_session.add_all(
            [
                models.Property(
                    community="Dubai Marina",
                    property_type="Apartment",
                    size_sqft=980.0,
                    floor_level=14,
                ),
                models.Property(
                    community="Business Bay",
                    property_type="Apartment",
                    size_sqft=1250.0,
                    floor_level=22,
                ),
                models.Property(
                    community="Arabian Ranches",
                    property_type="Villa",
                    size_sqft=3200.0,
                    floor_level=None,
                ),
            ]
        )

    if db_session.execute(select(models.Application)).first() is None:
        dummy = _load_dummy_applicants()
        dummy_by_id = {r["application_id"]: r for r in dummy}
        seed_apps = [
            {
                "id": "app_001",
                "borrower_name": "Mariam Youssef",
                "borrower_email": "mariam@example.com",
                "borrower_emirates_id": "784-1992-1234567-1",
                "community": "Dubai Marina",
                "property_type": "Apartment",
                "size_sqft": 980.0,
                "status": config.APPLICATION_STATUS_PENDING,
            },
            {
                "id": "app_002",
                "borrower_name": "Hamad Saeed",
                "borrower_email": "hamad@example.com",
                "borrower_emirates_id": "784-1989-7654321-2",
                "community": "Business Bay",
                "property_type": "Apartment",
                "size_sqft": 1250.0,
                "status": config.APPLICATION_STATUS_PENDING,
            },
        ]
        for app_data in seed_apps:
            fin = dummy_by_id.get(app_data["id"], {})
            db_session.add(
                models.Application(
                    **app_data,
                    monthly_income_aed=fin.get("monthly_income_aed"),
                    credit_score=fin.get("credit_score"),
                    credit_utilization_pct=fin.get("credit_utilization_pct"),
                    existing_mortgage=fin.get("existing_mortgage"),
                    monthly_mortgage_payment_aed=fin.get("monthly_mortgage_payment_aed"),
                )
            )

    db_session.commit()


def _load_dummy_applicants() -> List[dict]:
    """Load the dummy applicants JSON file and return the list of records."""
    with config.DUMMY_APPLICANTS_JSON_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _next_application_id(db_session: Session) -> str:
    """Generate the next 'app_NNN' ID based on the current max in the DB."""
    max_id = db_session.execute(
        select(sa_func.max(models.Application.id))
    ).scalar()
    if max_id is None:
        return "app_001"
    # Extract numeric part from e.g. "app_012"
    num = int(max_id.replace("app_", "")) + 1
    return f"app_{num:03d}"


def _normalize_community_and_type(community_name: str, property_type: str) -> Tuple[str, str]:
    """Normalize community and property-type text for consistent lookups.

    **Inputs**
    - `community_name`: Community name as provided by the client or dataset.
    - `property_type`: Property type as provided by the client or dataset.

    **Outputs**
    - 2-tuple of `(community_norm, property_type_norm)` where both values are
      lowercased and stripped versions of the inputs.
    """
    return community_name.strip().lower(), property_type.strip().lower()


def seed_dld_price_data(db_session: Session) -> Dict[Tuple[str, str], float]:
    """Load DLD JSON price data into the database and build an in-memory cache.

    **Inputs**
    - `db_session`: SQLAlchemy session used to read and write DLD price rows.

    **Outputs**
    - Returns a dictionary mapping `(community_norm, property_type_norm)` to
      `average_price_per_sqft` floats.
    """
    from models import DLDCommunityPrice

    import json

    with config.DLD_PRICE_JSON_PATH.open("r", encoding="utf-8") as f:
        records = json.load(f)

    # DLD dataset can contain duplicate (community, property type) keys.
    # Aggregate first so we don't try to insert the same unique key twice in one run.
    file_aggregated: Dict[Tuple[str, str], Tuple[str, str, float]] = {}

    for record in records:
        community_raw = str(record.get("community name", "")).strip()
        property_type_raw = str(record.get("property type", "")).strip()
        avg_price = record.get("average price per sqft")

        if not community_raw or not property_type_raw:
            continue
        if avg_price is None:
            continue

        avg_price_f = float(avg_price)
        if avg_price_f <= 0:
            continue

        community_norm, property_type_norm = _normalize_community_and_type(
            community_raw, property_type_raw
        )

        file_aggregated[(community_norm, property_type_norm)] = (
            community_raw,
            property_type_raw,
            avg_price_f,
        )

    lookup: Dict[Tuple[str, str], float] = {}
    for (community_norm, property_type_norm), (community_raw, property_type_raw, avg_price_f) in file_aggregated.items():
        stmt = select(DLDCommunityPrice).where(
            DLDCommunityPrice.community_name_normalized == community_norm,
            DLDCommunityPrice.property_type_normalized == property_type_norm,
        )
        existing = db_session.execute(stmt).scalar_one_or_none()

        if existing is not None:
            existing.average_price_per_sqft = avg_price_f
        else:
            db_session.add(
                DLDCommunityPrice(
                    community_name_raw=community_raw,
                    community_name_normalized=community_norm,
                    property_type_raw=property_type_raw,
                    property_type_normalized=property_type_norm,
                    average_price_per_sqft=avg_price_f,
                )
            )

        lookup[(community_norm, property_type_norm)] = avg_price_f

    db_session.commit()
    return lookup


def build_price_cache_from_db(db_session: Session) -> Dict[Tuple[str, str], float]:
    """Build an in-memory price cache from the `dld_community_prices` table.

    **Inputs**
    - `db_session`: SQLAlchemy session used to query all DLD price rows.

    **Outputs**
    - Returns a dictionary mapping `(community_norm, property_type_norm)` to
      `average_price_per_sqft` floats, suitable for fast in-memory lookups.
    """
    from models import DLDCommunityPrice

    rows = db_session.execute(select(DLDCommunityPrice)).scalars().all()
    return {
        (row.community_name_normalized, row.property_type_normalized): row.average_price_per_sqft
        for row in rows
    }


price_cache: Dict[Tuple[str, str], float] = {}
eligible_community_norms = {community.strip().lower() for community in config.ELIGIBLE_COMMUNITIES}
eligible_property_types = {property_type.strip().lower() for property_type in config.ELIGIBLE_PROPERTY_TYPES}


@app.on_event("startup")
def on_startup() -> None:
    """FastAPI startup hook to create tables, sync schema, and seed data.

    **Inputs**
    - No explicit inputs; uses global database engine and configuration.

    **Outputs**
    - Returns `None`. Ensures tables and columns exist, seeds mock data,
      and initializes the in-memory DLD price cache.
    """
    # Run schema migration FIRST — it may drop old integer-ID tables so that
    # create_all() can recreate them with the new string-ID schema.
    ensure_db_schema()
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        seed_mock_data(db_session)
        # Load DLD average prices into the DB and build cache for fast lookup.
        global price_cache
        seed_dld_price_data(db_session)
        price_cache = build_price_cache_from_db(db_session)
    finally:
        db_session.close()


@app.get("/health")
def health_check():
    """Simple liveness endpoint used by monitoring and deployment probes.

    **Inputs**
    - No request body or query parameters.

    **Outputs**
    - JSON object with a `status` field indicating service health.
    """
    return {"status": "healthy"}


@app.get("/users", response_model=List[UserOut])
def get_users(db_session: Session = Depends(get_db)) -> List[UserOut]:
    """Return all users currently stored in the database.

    **Inputs**
    - `db_session`: SQLAlchemy session dependency injected by FastAPI.

    **Outputs**
    - List of `UserOut` Pydantic models representing persisted users.
    """
    stmt = select(models.User)
    users: List[UserOut] = db_session.execute(stmt).scalars().all()
    return users

@app.post("/estimate", response_model=EstimateOut)
def estimate(payload: EstimateIn) -> EstimateOut:
    """Estimate a property value in AED using DLD price-per-sqft data.

    **Inputs**
    - `payload`: `EstimateIn` Pydantic model containing community, property type,
      and `size_sqft` for the property being valued.

    **Outputs**
    - `EstimateOut` model with a single `estimated_value_aed` numeric field.
    - Raises `HTTPException` with status 400 for invalid or unsupported inputs.
    """
    community_raw = payload.community.strip()
    property_type_raw = payload.property_type.strip()

    if not community_raw:
        raise HTTPException(status_code=400, detail="community is required")

    if not property_type_raw:
        raise HTTPException(status_code=400, detail="property_type is required")

    if payload.size_sqft <= 0:
        raise HTTPException(status_code=400, detail="size_sqft must be > 0")

    community_norm, property_type_norm = _normalize_community_and_type(
        community_raw, property_type_raw
    )

    if community_norm not in eligible_community_norms:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported or ineligible community",
                "supported_communities": sorted(eligible_community_norms),
            },
        )

    if property_type_norm not in eligible_property_types:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported or ineligible property type",
                "supported_property_types": sorted(eligible_property_types),
            },
        )

    price = price_cache.get((community_norm, property_type_norm))
    if price is None:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No DLD price data for community/property_type combination",
                "community": community_raw,
                "property_type": property_type_raw,
            },
        )

    estimated_value = price * float(payload.size_sqft)
    return EstimateOut(estimated_value_aed=estimated_value)


@app.post("/applications", response_model=ApplicationOut)
def create_application(payload: ApplicationIn, db_session: Session = Depends(get_db)) -> ApplicationOut:
    """Create a new HELOC application for a borrower.

    **Inputs**
    - `payload`: `ApplicationIn` Pydantic model containing borrower details,
      community, property type, and size information.
    - `db_session`: SQLAlchemy session dependency injected by FastAPI.

    **Outputs**
    - `ApplicationOut` model with the initial application `status` set to "pending".
    - Raises `HTTPException` with status 400 for invalid or unsupported inputs.
    """
    # Validate required fields
    full_name = payload.full_name.strip()
    email = payload.email.strip()
    emirates_id = payload.emirates_id.strip()
    phone = payload.phone.strip()
    community = payload.community.strip()
    property_type = payload.property_type.strip()

    if not full_name:
        raise HTTPException(status_code=400, detail="full_name is required")
    if not email:
        raise HTTPException(status_code=400, detail="email is required")
    if not emirates_id:
        raise HTTPException(status_code=400, detail="emirates_id is required")
    if not phone:
        raise HTTPException(status_code=400, detail="phone is required")
    if not community:
        raise HTTPException(status_code=400, detail="community is required")
    if not property_type:
        raise HTTPException(status_code=400, detail="property_type is required")
    if payload.size_sqft <= 0:
        raise HTTPException(status_code=400, detail="size_sqft must be > 0")

    # Normalize and validate community and property type
    community_norm, property_type_norm = _normalize_community_and_type(
        community, property_type
    )

    if community_norm not in eligible_community_norms:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported or ineligible community",
                "supported_communities": sorted(eligible_community_norms),
            },
        )

    if property_type_norm not in eligible_property_types:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported or ineligible property type",
                "supported_property_types": sorted(eligible_property_types),
            },
        )

    # Generate next app_NNN id
    app_id = _next_application_id(db_session)

    # Look up dummy applicant financial data by the generated id
    dummy = _load_dummy_applicants()
    dummy_by_id = {r["application_id"]: r for r in dummy}
    fin = dummy_by_id.get(app_id, {})

    # Create Application record with property info and financial data
    application = models.Application(
        id=app_id,
        borrower_name=full_name,
        borrower_email=email,
        borrower_emirates_id=emirates_id,
        community=community,
        property_type=property_type,
        size_sqft=payload.size_sqft,
        monthly_income_aed=fin.get("monthly_income_aed"),
        credit_score=fin.get("credit_score"),
        credit_utilization_pct=fin.get("credit_utilization_pct"),
        existing_mortgage=fin.get("existing_mortgage"),
        monthly_mortgage_payment_aed=fin.get("monthly_mortgage_payment_aed"),
        status=config.APPLICATION_INITIAL_STATUS,
    )
    db_session.add(application)
    db_session.commit()

    return ApplicationOut(id=application.id, status=config.APPLICATION_INITIAL_STATUS)


@app.get("/applications")
def get_applications(db_session: Session = Depends(get_db)):
    """Return all HELOC applications as JSON.

    **Inputs**
    - `db_session`: SQLAlchemy session dependency injected by FastAPI.

    **Outputs**
    - JSON object with an `applications` key containing a list of all applications.
    """
    stmt = select(models.Application)
    applications = db_session.execute(stmt).scalars().all()
    return {
        "applications": [_application_to_dict(app) for app in applications]
    }


@app.get("/applications/{application_id}")
def get_application(application_id: str, db_session: Session = Depends(get_db)):
    """Return a single HELOC application by ID.

    **Inputs**
    - `application_id`: The string ID of the application (e.g. "app_007").
    - `db_session`: SQLAlchemy session dependency injected by FastAPI.

    **Outputs**
    - JSON object with the application details.
    - Raises `HTTPException` with status 404 if not found.
    """
    stmt = select(models.Application).where(models.Application.id == application_id)
    app = db_session.execute(stmt).scalar_one_or_none()
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return _application_to_dict(app)


@app.post("/check-eligibility/{application_id}")
def check_eligibility(application_id: str, db_session: Session = Depends(get_db)):
    """Check whether a HELOC application is eligible (approved) or not (rejected).

    Rules:
    1. AECB credit score must be >= CREDIT_SCORE_MIN (657).
    2. DBR (monthly_mortgage_payment_aed / monthly_income_aed) must be <= DBR_MAX (50%).
    """
    stmt = select(models.Application).where(models.Application.id == application_id)
    application = db_session.execute(stmt).scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Validate that financial data exists
    if application.credit_score is None or application.monthly_income_aed is None:
        raise HTTPException(status_code=400, detail="Missing financial data for eligibility check")

    # Rule 1: Credit score >= 657
    credit_ok = application.credit_score >= config.CREDIT_SCORE_MIN

    # Rule 2: DBR = monthly_mortgage_payment / monthly_income <= 50%
    mortgage_payment = application.monthly_mortgage_payment_aed or 0.0
    income = application.monthly_income_aed
    dbr = (mortgage_payment / income) 
    dbr_ok = dbr <= config.DBR_MAX

    if credit_ok and dbr_ok:
        new_status = config.APPLICATION_STATUS_APPROVED
    else:
        new_status = config.APPLICATION_STATUS_REJECTED

    application.status = new_status
    db_session.commit()

    return {"id": application.id, "status": new_status}


@app.get("/offers/{application_id}")
def get_application_offer(application_id: str, db_session: Session = Depends(get_db)):
    """Return the offer details for an approved application."""
    stmt = select(models.Application).where(models.Application.id == application_id)
    application = db_session.execute(stmt).scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status != config.APPLICATION_STATUS_APPROVED:
        raise HTTPException(status_code=400, detail="Application is not approved")

    # Look up price per sqft from cache (same logic as /estimate)
    community_norm, property_type_norm = _normalize_community_and_type(
        application.community, application.property_type
    )
    price_per_sqft = price_cache.get((community_norm, property_type_norm))
    if price_per_sqft is None:
        raise HTTPException(
            status_code=400,
            detail="No DLD price data for this application's community/property type",
        )

    estimated_value = price_per_sqft * application.size_sqft
    max_lendable_value = estimated_value * config.LTV_MAX
    rental_rate = config.RENTAL_RATE
    now = datetime.now()
    expiry_date = now.replace(year=now.year + config.OFFER_EXPIRY_YEARS)
    repayment_end = expiry_date.replace(year=expiry_date.year + config.REPAYMENT_YEARS)

    offer_summary = summarize_offer(
        full_name=application.borrower_name,
        email=application.borrower_email,
        emirates_id=application.borrower_emirates_id,
        phone="",
        community=application.community,
        property_type=application.property_type,
        size_sqft=application.size_sqft,
        estimated_value_aed=estimated_value,
        approved_amount=max_lendable_value,
        rental_rate=rental_rate,
        expiry_date=expiry_date.strftime("%Y-%m-%d"),
    )

    return {
        "application_id": application.id,
        "status": application.status,
        "estimated_value_aed": f"{estimated_value:,.2f}",
        "max_lendable_value_aed": f"{max_lendable_value:,.2f}",
        "rental_rate": f"{rental_rate * 100:.0f}%",
        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
        "repayment_end_date": repayment_end.strftime("%Y-%m-%d"),
        "offer_summary": offer_summary,
    }


@app.get("/contracts/generate/{application_id}")
def generate_contract(application_id: str, db_session: Session = Depends(get_db)):
    """Generate a contract record for an approved application."""
    stmt = select(models.Application).where(models.Application.id == application_id)
    application = db_session.execute(stmt).scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status != config.APPLICATION_STATUS_APPROVED:
        raise HTTPException(status_code=400, detail="Application is not approved")

    # Check if a contract already exists for this application
    existing = db_session.execute(
    
        select(models.Contract).where(models.Contract.application_id == application_id)
    ).scalar_one_or_none()
    if existing is not None:
        return {"contract_id": existing.id, "application_id": existing.application_id, "status": existing.status, "contract_text": existing.contract_text}

    # Generate contract ID from application ID (e.g. app_007 -> contract_007)
    contract_id = application_id.replace("app_", "contract_")

    contract = models.Contract(
        id=contract_id,
        application_id=application_id,
        contract_text=config.CONTRACT_TEXT,
        status=config.CONTRACT_STATUS_DRAFT,
    )
    db_session.add(contract)
    db_session.commit()

    return {"contract_id": contract.id, "application_id": contract.application_id, "status": contract.status, "contract_text": contract.contract_text}


@app.post("/contracts/sign")
def sign_contract(payload: ContractSignIn, db_session: Session = Depends(get_db)):
    """Digitally sign a contract by matching signature_data to the borrower name."""
    contract = db_session.execute(
        select(models.Contract).where(models.Contract.id == payload.contract_id)
    ).scalar_one_or_none()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.status == config.CONTRACT_STATUS_SIGNED:
        raise HTTPException(status_code=400, detail="Contract is already signed")

    # Get the linked application to verify signature
    application = db_session.execute(
        select(models.Application).where(models.Application.id == contract.application_id)
    ).scalar_one_or_none()

    if payload.signature_data.strip() == application.borrower_name.strip():
        contract.status = config.CONTRACT_STATUS_SIGNED
    else:
        contract.status = config.CONTRACT_STATUS_REJECTED

    contract.signature_data = payload.signature_data
    contract.signed_at = datetime.fromisoformat(payload.timestamp)
    db_session.commit()

    return {"contract_id": contract.id, "status": contract.status}


def _application_to_dict(app: models.Application) -> dict:
    """Convert an Application model instance to a response dictionary."""
    return {
        "id": app.id,
        "borrower_name": app.borrower_name,
        "borrower_email": app.borrower_email,
        "borrower_emirates_id": app.borrower_emirates_id,
        "community": app.community,
        "property_type": app.property_type,
        "size_sqft": app.size_sqft,
        "monthly_income_aed": app.monthly_income_aed,
        "credit_score": app.credit_score,
        "credit_utilization_pct": app.credit_utilization_pct,
        "existing_mortgage": app.existing_mortgage,
        "monthly_mortgage_payment_aed": app.monthly_mortgage_payment_aed,
        "status": app.status,
        "application_date": app.created_at.isoformat() if app.created_at else None,
    }