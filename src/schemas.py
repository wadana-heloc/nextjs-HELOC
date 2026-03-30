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

