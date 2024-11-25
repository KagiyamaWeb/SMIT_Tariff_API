from pydantic import BaseModel
from datetime import datetime


class RateBase(BaseModel):
    cargo_type: str
    rate: float
    effective_date: datetime

class RateCreate(RateBase):
    pass

class RateResponse(RateBase):
    id: int
    
    class Config:
        orm_mode = True

class InsuranceCalculationRequest(BaseModel):
    cargo_type: str
    declared_value: float
    date: datetime