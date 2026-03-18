from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date

class Shareholder(BaseModel):
    name: str
    ownership_percentage: float

class KybKycInput(BaseModel):
    company_name: str
    registration_number: str
    registration_date: date
    registered_address: str
    business_type: str
    contact_person_name: str
    contact_person_email: EmailStr
    phone_number: str
    website: Optional[str] = None
    shareholders: List[Shareholder] = []
