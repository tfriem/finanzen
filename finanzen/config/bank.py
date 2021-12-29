from typing import List, Optional

from pydantic import BaseModel

from finanzen.config.account import Account


class Bank(BaseModel):
    name: Optional[str]
    blz: str
    user: str
    fints_url: str
    pin: Optional[str]
    accounts: List[Account]

    class Config:
        allow_mutation = False
