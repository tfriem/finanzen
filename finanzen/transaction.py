from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Transaction:
    date: date
    amount: Decimal
    posting_text: str
    purpose: str
    applicant_name: str
    applicant_iban: str
