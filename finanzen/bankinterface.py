from datetime import date
from typing import List

import typer
from fints.client import FinTS3PinTanClient, NeedTANResponse
from fints.models import SEPAAccount
from mt940.models import Transaction as FintsTransaction
from tabulate import tabulate

from finanzen.config.account import Account
from finanzen.config.bank import Bank
from finanzen.data.transaction import AccountWithTransactions, Transaction


def get_transactions(bank: Bank, start_date) -> List[AccountWithTransactions]:
    client = create_client(bank)
    with client:
        sepa_accounts: List[SEPAAccount] = client.get_sepa_accounts()
        print_accounts(bank, sepa_accounts)

        accounts_with_transactions: List[AccountWithTransactions] = []
        for sepa_account in sepa_accounts:
            account = next(
                (a for a in bank.accounts if a.iban == sepa_account.iban), None
            )

            if not account:
                typer.secho(
                    f"No account config found for {sepa_account.iban}",
                    fg=typer.colors.RED,
                )
                continue

            response = client.get_transactions(
                sepa_account,
                start_date=date.fromisoformat(start_date),
                end_date=date.today(),
            )

            if isinstance(response, NeedTANResponse):
                tan = typer.prompt(response.challenge or f"Tan for {bank.name}")
                fints_transactions = client.send_tan(response, tan)
            else:
                fints_transactions = response

            transactions = transform_transactions(fints_transactions)
            accounts_with_transactions.append(
                AccountWithTransactions(account=account, transactions=transactions)
            )

        return accounts_with_transactions


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


def transform_transactions(transactions: List[FintsTransaction]) -> List[Transaction]:
    return [
        Transaction(
            date=date(
                t.data["date"].year,
                t.data["date"].month,
                t.data["date"].day,
            ),
            amount=t.data["amount"].amount,
            posting_text=t.data["posting_text"],
            purpose=t.data["purpose"],
            applicant_name=t.data["applicant_name"],
            applicant_iban=t.data["applicant_iban"],
        )
        for t in transactions
    ]
