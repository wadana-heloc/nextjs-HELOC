from sqlalchemy import Column, Float, ForeignKey, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    community = Column(String, nullable=False, index=True)
    property_type = Column(String, nullable=False, index=True)
    size_sqft = Column(Float, nullable=False)
    floor_level = Column(Integer, nullable=True)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    borrower_name = Column(String, nullable=False)
    borrower_email = Column(String, nullable=False, index=True)
    borrower_emirates_id = Column(String, nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    requested_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, index=True)