from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CreditAccount(BaseModel):
    account_type: str
    provider: str
    account_number: str
    opening_date: date
    credit_limit: float
    current_balance: float
    payment_history: List[bool]
    status: str

class CreditBureauInput(BaseModel):
    full_name: str
    date_of_birth: date
    address: str
    ssn_last_four: str
    inquiries_last_6_months: int
    total_debt: float
    credit_score: Optional[int] = None
    credit_accounts: List[CreditAccount]
