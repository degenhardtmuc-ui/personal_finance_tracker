"""Provide JSON serialization and persistence for finance data."""

import json
from pathlib import Path

from finance_tracker.account import add_transaction, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.transaction import create_transaction


def transaction_to_dict(transaction: dict) -> dict:
    """Convert a transaction into a JSON-compatible dictionary."""
    return {
        "description": transaction["description"],
        "amount": transaction["amount"],
        "transaction_type": transaction["transaction_type"].name,
        "category": transaction["category"].name,
        "date": transaction["date"],
        "tags": sorted(transaction["tags"]),
    }


def transaction_from_dict(data: dict) -> dict:
    """Create a transaction dictionary from JSON-compatible data."""
    return create_transaction(
        description=data["description"],
        amount=data["amount"],
        transaction_type=TransactionType[data["transaction_type"]],
        category=Category[data["category"]],
        date=data["date"],
        tags=set(data["tags"]),
    )


def account_to_dict(account: dict) -> dict:
    """Convert an account into a JSON-compatible dictionary."""
    return {
        "name": account["name"],
        "transactions": [
            transaction_to_dict(transaction)
            for transaction in account["transactions"]
        ],
    }


def account_from_dict(data: dict) -> dict:
    """Create an account dictionary from JSON-compatible data."""
    account = create_account(data["name"])

    for transaction_data in data["transactions"]:
        transaction = transaction_from_dict(transaction_data)
        add_transaction(account, transaction)

    return account


def save_account(
    account: dict,
    path: str | Path,
) -> None:
    """Save an account dictionary to a JSON file."""
    file_path = Path(path)
    serialized_account = account_to_dict(account)

    with file_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            serialized_account,
            file,
            indent=4,
            ensure_ascii=False,
        )


def load_account(path: str | Path) -> dict:
    """Load and return an account dictionary from a JSON file."""
    file_path = Path(path)

    with file_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return account_from_dict(data)