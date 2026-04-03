"""SQLAlchemy ORM models for the HELOC API domain.

The models in this module define the relational schema for:
- users who interact with the system
- properties that can secure HELOC applications
- HELOC applications themselves
- DLD community-level price data used for valuation
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """Application user who can own HELOC applications and properties."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Property(Base):
    """Real-estate property that can be valued and used as loan collateral."""

    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    community = Column(String, nullable=False, index=True)
    property_type = Column(String, nullable=False, index=True)
    size_sqft = Column(Float, nullable=False)
    floor_level = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Application(Base):
    """HELOC application submitted by a borrower for a specific property."""

    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    borrower_name = Column(String, nullable=False)
    borrower_email = Column(String, nullable=False, index=True)
    borrower_emirates_id = Column(String, nullable=False, index=True)
    community = Column(String, nullable=False)
    property_type = Column(String, nullable=False)
    size_sqft = Column(Float, nullable=False)
    monthly_income_aed = Column(Float, nullable=True)
    credit_score = Column(Integer, nullable=True)
    credit_utilization_pct = Column(Float, nullable=True)
    existing_mortgage = Column(Boolean, nullable=True)
    monthly_mortgage_payment_aed = Column(Float, nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    requested_amount = Column(Float, nullable=True)
    status = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Contract(Base):
    """Generated contract for an approved HELOC application."""

    __tablename__ = "contracts"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    contract_text = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="draft")
    signature_data = Column(String, nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DLDCommunityPrice(Base):
    """Average DLD price-per-square-foot for a given community and property type."""

    __tablename__ = "dld_community_prices"
    __table_args__ = (
        UniqueConstraint(
            "community_name_normalized",
            "property_type_normalized",
            name="uq_dld_community_property_type",
        ),
    )

    id = Column(Integer, primary_key=True)
    community_name_raw = Column(String, nullable=False)
    community_name_normalized = Column(String, nullable=False, index=True)
    property_type_raw = Column(String, nullable=False)
    property_type_normalized = Column(String, nullable=False, index=True)
    average_price_per_sqft = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
