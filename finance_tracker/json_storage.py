"""Provide JSON serialization and persistence for finance data."""

import json
from math import isfinite
from pathlib import Path

from finance_tracker.account import add_transaction, create_account
from finance_tracker.budget import create_budget_tracker, set_budget
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


def budget_tracker_to_dict(tracker: dict) -> dict:
    """Convert a budget tracker into validated JSON-compatible data."""
    data = {
        "budgets": [
            {
                "category": budget["category"].name,
                "monthly_limit": budget["monthly_limit"],
                "month": budget["month"],
            }
            for budget in tracker["budgets"]
        ],
    }
    budget_tracker_from_dict(data)
    return data


def budget_tracker_from_dict(data: dict) -> dict:
    """Restore a budget tracker while validating the complete file data."""
    if not isinstance(data, dict) or not isinstance(data.get("budgets"), list):
        raise ValueError("Budget file must contain a budgets list.")

    tracker = create_budget_tracker()
    for budget_data in data["budgets"]:
        if not isinstance(budget_data, dict):
            raise ValueError("Each budget must be an object.")

        try:
            category_name = budget_data["category"]
            monthly_limit = budget_data["monthly_limit"]
            month = budget_data["month"]
        except KeyError as error:
            raise ValueError("Budget fields are missing.") from error

        if not isinstance(category_name, str):
            raise ValueError("Budget category must be a string.")
        try:
            category = Category[category_name]
        except KeyError as error:
            raise ValueError("Unknown budget category.") from error

        if isinstance(monthly_limit, bool) or not isinstance(
            monthly_limit, (int, float),
        ):
            raise ValueError("Monthly limit must be a number.")
        if not isfinite(monthly_limit):
            raise ValueError("Monthly limit must be finite.")
        if not isinstance(month, str):
            raise ValueError("Budget month must be a string.")

        set_budget(
            tracker,
            category=category,
            monthly_limit=monthly_limit,
            month=month,
        )

    return tracker


def save_budgets(tracker: dict, path: str | Path) -> None:
    """Save a validated budget tracker to a UTF-8 JSON file."""
    data = budget_tracker_to_dict(tracker)
    with Path(path).open(mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False, allow_nan=False)


def load_budgets(path: str | Path) -> dict:
    """Load and validate a budget tracker from a UTF-8 JSON file."""
    with Path(path).open(mode="r", encoding="utf-8") as file:
        data = json.load(file)

    return budget_tracker_from_dict(data)