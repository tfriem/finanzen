from typing import Optional

from pydantic import BaseModel


class TransactionMapping(BaseModel):
    posting_text: Optional[str]
    purpose: Optional[str]
    applicant_name: Optional[str]
    applicant_iban: Optional[str]
    credit_account: str

    class Config:
        allow_mutation = False
