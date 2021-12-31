from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class TemplateData:
    date: date
    payee: str
    posting: str
    purpose: str
    md5sum: str
    credit_account: str
    debit_account: str
    credit: Decimal
    debit: Decimal
    currency: str
