import logging
from pathlib import Path

import typer

from finanzen.bankinterface import get_transactions
from finanzen.config.config import Config
from finanzen.ledger import write_transactions

logging.basicConfig(level=logging.WARN)

app = typer.Typer()


@app.command()
def generate_config_schema():
    schema_path = Path.joinpath(Path().resolve(), "config.schema.json")

    with open(schema_path, "w+") as f:
        f.write(Config.schema_json(indent=2))


@app.command()
def import_transactions(config_name="config.json", ledger_name="main.bean"):
    config_path = Path.joinpath(Path().resolve(), config_name)
    config = Config.parse_file(config_path)

    for bank in config.banks:
        transactions = get_transactions(bank)
        write_transactions(transactions, config.mappings)


def main():
    app()


if __name__ == "__main__":
    main()
