from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from schemas import EstimateIn, EstimateOut, UserOut

import models  # noqa: F401 - registers models on Base

app = FastAPI()


def seed_mock_data(db: Session) -> None:
    """Insert demo records once for local development."""
    if db.execute(select(models.User)).first() is None:
        db.add_all(
            [
                models.User(name="Ahmed Al Mansoori", email="ahmed@example.com"),
                models.User(name="Sara Khalid", email="sara@example.com"),
                models.User(name="Omar Nasser", email="omar@example.com"),
            ]
        )

    if db.execute(select(models.Property)).first() is None:
        db.add_all(
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

    if db.execute(select(models.Application)).first() is None:
        first_property_id = db.execute(select(models.Property.id).order_by(models.Property.id.asc())).scalar()
        if first_property_id is not None:
            db.add_all(
                [
                    models.Application(
                        borrower_name="Mariam Youssef",
                        borrower_email="mariam@example.com",
                        borrower_emirates_id="784-1992-1234567-1",
                        property_id=first_property_id,
                        requested_amount=950000.0,
                        status="submitted",
                    ),
                    models.Application(
                        borrower_name="Hamad Saeed",
                        borrower_email="hamad@example.com",
                        borrower_emirates_id="784-1989-7654321-2",
                        property_id=first_property_id,
                        requested_amount=1250000.0,
                        status="under_review",
                    ),
                ]
            )

    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_mock_data(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/users", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    stmt = select(models.User)
    users = db.execute(stmt).scalars().all()
    return users


COMMUNITY_PRICE_PER_SQFT_AED: dict[str, float] = {
    # Rough 2025-era averages (AED / sqft). Intentionally hardcoded for estimation only.
    "downtown dubai": 2800.0,
    "palm jumeirah": 4150.0,
    "dubai marina": 2100.0,
    "business bay": 2600.0,
    "jumeirah village circle": 1450.0,
    "jvc": 1450.0,
    "jumeirah lakes towers": 1700.0,
    "jlt": 1700.0,
    "dubai hills estate": 2400.0,
    "arabian ranches": 2375.0,
    "arjan": 1550.0,
    "al barsha": 1300.0,
}


@app.post("/estimate", response_model=EstimateOut)
def estimate(payload: EstimateIn) -> EstimateOut:
    community_key = payload.community.strip().lower()
    if not community_key:
        raise HTTPException(status_code=400, detail="community is required")

    if payload.size_sqft <= 0:
        raise HTTPException(status_code=400, detail="size_sqft must be > 0")

    price = COMMUNITY_PRICE_PER_SQFT_AED.get(community_key)
    if price is None:
        supported = sorted({k for k in COMMUNITY_PRICE_PER_SQFT_AED.keys() if k not in {"jvc", "jlt"}})
        raise HTTPException(
            status_code=400,
            detail={"message": "Unsupported community", "supported_communities": supported},
        )

    estimated_value = price * float(payload.size_sqft)
    return EstimateOut(estimated_value_aed=estimated_value)