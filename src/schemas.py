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
    id: int
    status: str


class ApplicationListOut(BaseModel): #this is the output schema for the GET applications endpoint
    id: int
    borrower_name: str
    borrower_email: str
    borrower_emirates_id: str
    property_id: int
    user_id: Optional[Union[int, str]]
    requested_amount: float
    status: str

    model_config = ConfigDict(from_attributes=True)

