import shutil
import time
from os import listdir
from os.path import isfile, join
from typing import Dict, List

from pydantic.main import BaseModel

from finanzen.config.account import Account
from finanzen.data.transaction import AccountWithTransactions

processing_directory = "processing"
finished_directory = "finished"


class TransactionStorage(BaseModel):
    accounts_with_transactions: List[AccountWithTransactions]

    class Config:
        allow_mutation = False


def write_transactions_to_file(
    accounts_with_transactions: List[AccountWithTransactions],
):
    timestr = time.strftime("%Y%m%d%H%M%S")
    filename = f"{processing_directory}/{timestr}_transactions.json"

    data = TransactionStorage(accounts_with_transactions=accounts_with_transactions)

    with open(filename, "w+") as f:
        f.write(data.json())


def read_transactions() -> Dict[str, List[AccountWithTransactions]]:
    files = [
        f
        for f in listdir(processing_directory)
        if isfile(join(processing_directory, f))
    ]

    result: Dict[str, List[AccountWithTransactions]] = {}

    for file in files:
        if file == ".keep":
            continue
        data = TransactionStorage.parse_file(f"{processing_directory}/{file}")
        result[file] = data.accounts_with_transactions

    return result


def ack_file(filename):
    shutil.move(
        f"{processing_directory}/{filename}", f"{finished_directory}/{filename}"
    )
