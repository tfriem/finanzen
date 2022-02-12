import hashlib
import os
import re
from typing import List

import typer
from jinja2 import Template

from finanzen.config.account import Account
from finanzen.config.mapping import TransactionMapping
from finanzen.data.templatedata import TemplateData
from finanzen.data.transaction import AccountWithTransactions, Transaction

template = """
{{date}} txn "{{payee}} {{posting}} {{purpose}}"
    ; md5sum: {{md5sum}}
    {{debit_account}}   {{debit}} {{currency}}
    {{credit_account}}   {{credit}} {{currency}}
"""

MD5_REGEX = r"md5sum: (.*)"
LEDGER_FILE = "transactions.bean"


def write_transactions(
    accounts_with_transactions: List[AccountWithTransactions],
    mappings: List[TransactionMapping],
):
    if len(accounts_with_transactions) < 1:
        return

    for entry in accounts_with_transactions:
        account = entry.account
        transactions = entry.transactions

        if len(transactions) < 1:
            continue

        ledger_entries = []
        md5s = _get_transactions_md5s()

        for transaction in transactions:
            # Find mapping for transaction in config
            matched_mapping = _find_mapping(transaction, mappings)
            if matched_mapping is None:
                raise Exception(
                    f"No matching mapping found for transaction {transaction}"
                )

            # Translate transaction data to ledger data
            data = _create_template_data(account, transaction, matched_mapping)

            if data.md5sum in md5s:
                typer.secho(
                    f"Transaction {transaction} already in file", fg=typer.colors.YELLOW
                )
                continue

            # Render template with ledger data
            ledger_entries.append(_render_template(data))

        with open(LEDGER_FILE, "a+") as f:
            for entry in ledger_entries:
                f.write(entry)


def _find_mapping(transaction: Transaction, mappings: List[TransactionMapping]):
    for mapping in mappings:
        matches = True

        matches = matches and _check_field(
            mapping.posting_text, transaction.posting_text
        )

        matches = matches and _check_field(mapping.purpose, transaction.purpose)

        matches = matches and _check_field(
            mapping.applicant_name, transaction.applicant_name
        )
        matches = matches and _check_field(
            mapping.applicant_iban, transaction.applicant_iban
        )

        if matches:
            return mapping

    return None


def _check_field(pattern, value) -> bool:
    if pattern and not value:
        return False

    if not pattern:
        return True

    return re.search(pattern, value) is not None


def _create_template_data(
    account: Account, transaction: Transaction, mapping: TransactionMapping
) -> TemplateData:
    md5 = hashlib.md5()

    md5.update(transaction.date.isoformat().encode("UTF-8"))
    md5.update(transaction.amount.__str__().encode("UTF-8"))
    md5.update(transaction.posting_text.encode("UTF-8"))
    if transaction.purpose:
        md5.update(transaction.purpose.encode("UTF-8"))

    if transaction.applicant_name:
        md5.update(transaction.applicant_name.encode("UTF-8"))

    if transaction.applicant_iban:
        md5.update(transaction.applicant_iban.encode("UTF-8"))

    md5sum = md5.hexdigest()
    return TemplateData(
        date=transaction.date,
        payee=transaction.applicant_name,
        posting=transaction.posting_text,
        purpose=transaction.purpose,
        md5sum=md5sum,
        credit_account=mapping.credit_account,
        debit_account=account.ledger_name,
        credit=-transaction.amount,
        debit=transaction.amount,
        currency="EUR",
    )


def _get_transactions_md5s() -> List[str]:
    if not os.path.isfile(LEDGER_FILE):
        return []

    with open(LEDGER_FILE, "r") as f:
        data = f.read()
        return re.findall(MD5_REGEX, data)


def _render_template(data: TemplateData):
    jinja_template = Template(template)
    return jinja_template.render(data.__dict__)
