from typing import List

from pydantic import BaseModel

from finanzen.config.bank import Bank
from finanzen.config.mapping import TransactionMapping


class Config(BaseModel):
    banks: List[Bank]
    mappings: List[TransactionMapping]

    class Config:
        allow_mutation = False
