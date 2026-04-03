from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class EstimateIn(BaseModel): #this is the input schema for the estimate endpoint
    community: str
    property_type: str
    size_sqft: float


class EstimateOut(BaseModel): #this is the output schema for the estimate endpoint
    estimated_value_aed: float


class ApplicationIn(BaseModel): #this is the input schema for the applications endpoint
    full_name: str
    email: str
    emirates_id: str
    phone: str
    community: str
    property_type: str
    size_sqft: float


class ApplicationOut(BaseModel): #this is the output schema for the applications endpoint
    id: str
    status: str


class ApplicationListOut(BaseModel): #this is the output schema for the GET applications endpoint
    id: str
    borrower_name: str
    borrower_email: str
    borrower_emirates_id: str
    community: str
    property_type: str
    size_sqft: float
    monthly_income_aed: Optional[float] = None
    credit_score: Optional[int] = None
    credit_utilization_pct: Optional[float] = None
    existing_mortgage: Optional[bool] = None
    monthly_mortgage_payment_aed: Optional[float] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ContractSignIn(BaseModel): #this is the input schema for the contract signing endpoint
    contract_id: str
    signature_data: str
    timestamp: str

