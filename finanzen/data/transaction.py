from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic.main import BaseModel

from finanzen.config.account import Account


class Transaction(BaseModel):
    date: date
    amount: Decimal
    posting_text: str
    purpose: Optional[str]
    applicant_name: Optional[str]
    applicant_iban: Optional[str]

    class Config:
        allow_mutation = False


class AccountWithTransactions(BaseModel):
    account: Account
    transactions: List[Transaction]

    class Config:
        allow_mutation = False
