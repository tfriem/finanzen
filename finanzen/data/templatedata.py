from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class TemplateData:
    date: date
    payee: Optional[str]
    posting: str
    purpose: Optional[str]
    md5sum: str
    credit_account: str
    debit_account: str
    credit: Decimal
    debit: Decimal
    currency: str
