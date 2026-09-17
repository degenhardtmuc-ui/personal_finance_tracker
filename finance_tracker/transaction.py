"""Provide functions for creating and processing transactions."""

import re

from finance_tracker.category import Category, TransactionType


def create_transaction(
    description: str,
    amount: float,
    transaction_type: TransactionType,
    category: Category,
    date: str,
    tags: set[str] | None = None,
) -> dict:
    """Create and return a validated transaction dictionary.

    Args:
        description: A short description of the transaction.
        amount: The positive monetary amount of the transaction.
        transaction_type: The type of transaction, such as income or expense.
        category: The category assigned to the transaction.
        date: The transaction date in YYYY-MM-DD format.
        tags: Optional keywords used to describe the transaction.

    Returns:
        A dictionary containing the validated transaction data.

    Raises:
        ValueError: If the description is empty.
        ValueError: If the amount is not positive.
        ValueError: If the date does not use YYYY-MM-DD format.
    """
    cleaned_description = description.strip()

    if not cleaned_description:
        raise ValueError("Description must not be empty.")

    if amount <= 0:
        raise ValueError("Amount must be positive.")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("Date must use YYYY-MM-DD format.")

    return {
        "description": cleaned_description,
        "amount": float(amount),
        "transaction_type": transaction_type,
        "category": category,
        "date": date,
        "tags": set() if tags is None else set(tags),
    }


def is_expense(transaction: dict) -> bool:
    """Return True when the transaction is an expense."""
    return transaction["transaction_type"] == TransactionType.EXPENSE


def is_income(transaction: dict) -> bool:
    """Return True when the transaction is income."""
    return transaction["transaction_type"] == TransactionType.INCOME


def signed_amount(transaction: dict) -> float:
    """Return a positive income amount or a negative expense amount."""
    amount = float(transaction["amount"])

    if is_expense(transaction):
        return -amount

    return amount


def format_transaction(transaction: dict) -> str:
    """Return a readable one-line representation of a transaction."""
    amount = signed_amount(transaction)

    return (
        f"{transaction['date']}  "
        f"{transaction['description']:<17}"
        f"{amount:.2f}  "
        f"[{transaction['category'].name}]"
    )