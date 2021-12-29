from typing import Optional

from pydantic import BaseModel


class Mapping(BaseModel):
    posting_text: Optional[str]
    purpose: Optional[str]
    applicant_iban: Optional[str]
    applicant_name: Optional[str]
    target: str

    class Config:
        allow_mutation = False
