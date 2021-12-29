from typing import List, Mapping

from pydantic import BaseModel

from finanzen.config.bank import Bank


class Config(BaseModel):
    banks: List[Bank]
    mappings: List[Mapping]

    class Config:
        allow_mutation = False
