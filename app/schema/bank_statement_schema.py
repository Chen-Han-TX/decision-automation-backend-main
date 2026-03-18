from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Transaction(BaseModel):
    date: date
    description: str
    amount: float
    type: str
    balance: Optional[float] = None

class BankStatementInput(BaseModel):
    account_holder_name: str
    account_number: str
    bank_name: str
    start_date: date
    end_date: date
    transactions: List[Transaction] = Field(..., min_items=1)
    currency: str = "USD"
