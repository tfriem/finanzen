import logging
import time
from pathlib import Path

import typer

from finanzen.bankinterface import get_transactions
from finanzen.config.config import Config
from finanzen.data.storage import (
    ack_file,
    read_transactions,
    write_transactions_to_file,
)
from finanzen.ledger import write_transactions

logging.basicConfig(level=logging.WARN)

app = typer.Typer()


@app.command()
def generate_config_schema():
    schema_path = Path.joinpath(Path().resolve(), "config.schema.json")

    with open(schema_path, "w+") as f:
        f.write(Config.schema_json(indent=2))


@app.command()
def fetch_transactions(config_file="config.json"):
    config = read_config(config_file)

    for bank in config.banks:
        accounts_with_transactions = get_transactions(bank)
        write_transactions_to_file(accounts_with_transactions)


@app.command()
def import_transactions(config_file="config.json", ledger_file="transactions.bean"):
    config = read_config(config_file)

    file_transactions = read_transactions()
    for file in file_transactions:
        typer.echo(f"Importing {file}")
        accounts_with_transactions = file_transactions[file]
        write_transactions(accounts_with_transactions, config.mappings)
        ack_file(file)

    typer.secho("All imports finished", fg=typer.colors.GREEN)


def read_config(config_file):
    config_path = Path.joinpath(Path().resolve(), config_file)
    return Config.parse_file(config_path)


def main():
    app()


if __name__ == "__main__":
    main()
