from typing import Optional

from pydantic import BaseModel


class Account(BaseModel):
    name: Optional[str]
    iban: str
    ledger_name: str

    class Config:
        allow_mutation = False
