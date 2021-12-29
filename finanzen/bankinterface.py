import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from re import sub
from typing import List

import typer
from fints.client import FinTS3PinTanClient, NeedTANResponse
from fints.models import SEPAAccount
from mt940.models import Transaction
from tabulate import tabulate

from finanzen.config.bank import Bank


def get_transactions(bank: Bank):
    client = create_client(bank)
    with client:
        accounts = client.get_sepa_accounts()
        print_accounts(bank, accounts)

        for account in accounts:
            response = client.get_transactions(
                account,
                start_date=date.today() - timedelta(days=14),
                end_date=date.today(),
            )

            if isinstance(response, NeedTANResponse):
                tan = typer.prompt(response.challenge or f"Tan for {bank.name}")
                fints_transactions = client.send_tan(response, tan)
            else:
                fints_transactions = response

            transactions = transform_transactions(fints_transactions)
            print_transactions(transactions)


def create_client(bank: Bank) -> FinTS3PinTanClient:
    pin = bank.pin
    if pin is None:
        pin = typer.prompt(f"Pin for {bank.name}", hide_input=True)

    return FinTS3PinTanClient(
        bank_identifier=bank.blz,
        user_id=bank.user,
        pin=pin,
        server=bank.fints_url,
        product_id=None,
    )


def print_accounts(bank: Bank, accounts: List[SEPAAccount]):
    typer.echo(f"Accounts ({bank.name})")
    typer.echo(tabulate(accounts, headers="keys", tablefmt="grid"))


def transform_transactions(transactions: List[Transaction]):
    return [
        {
            "date": t.data["date"],
            "amount": t.data["amount"].amount,
            "posting_text": t.data["posting_text"],
            "purpose": t.data["purpose"],
            "applicant_iban": t.data["applicant_iban"],
            "applicant_name": t.data["applicant_name"],
        }
        for t in transactions
    ]


def print_transactions(transactions):
    typer.echo(tabulate(transactions, headers="keys", tablefmt="grid"))
