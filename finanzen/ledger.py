import re
from os import write
from typing import Dict, List, Mapping

import typer
from jinja2 import Template

from finanzen.config.account import Account
from finanzen.config.mapping import TransactionMapping
from finanzen.templatedata import TemplateData
from finanzen.transaction import Transaction

template = """
{{date}} txn "{{payee}} {{posting}} {{purpose}}"
    ; md5sum: {{md5sum}}
    {{debit_account}}   {{debit}} {{currency}}
    {{credit_account}}   {{credit}} {{currency}}
"""


def write_transactions(
    transactions_per_account: Dict[Account, List[Transaction]],
    mappings: List[TransactionMapping],
):
    if len(transactions_per_account) < 1:
        return

    for account in transactions_per_account:
        transactions = transactions_per_account[account]

        if len(transactions) < 1:
            continue

        ledger_entries = []

        for transaction in transactions:
            # Find mapping for transaction in config
            matched_mapping = _find_mapping(transaction, mappings)
            if matched_mapping is None:
                typer.secho(
                    f"No matching mapping found for transaction {transaction}",
                    fg=typer.colors.RED,
                )
                continue

            # Translate transaction data to ledger data
            data = _create_template_data(account, transaction, matched_mapping)

            # TODO: Check if transaction is already in ledger file
            _check_if_ledger_has_transaction()

            # Render template with ledger data
            ledger_entries.append(_render_template(data))

        # TODO: Append rendered template to ledger file
        with open("transactions.bean", "w+") as f:
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
            typer.secho(
                f"Found matching mapping {mapping} for transaction {transaction}",
                fg=typer.colors.GREEN,
            )
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
    return TemplateData(
        date=transaction.date,
        payee=transaction.applicant_name,
        posting=transaction.posting_text,
        purpose=transaction.purpose,
        md5sum="",
        credit_account=mapping.credit_account,
        debit_account=account.ledger_name,
        credit=-transaction.amount,
        debit=transaction.amount,
        currency="EUR",
    )


def _check_if_ledger_has_transaction():
    # TODO: Implement
    pass


def _render_template(data: TemplateData):
    jinja_template = Template(template)
    return jinja_template.render(data.__dict__)
