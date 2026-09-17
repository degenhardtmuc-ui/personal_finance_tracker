"""Provide functions for managing a financial account."""

from finance_tracker.category import Category, TransactionType
from finance_tracker.transaction import is_expense, is_income, signed_amount


def create_account(name: str) -> dict:
    """Create and return an empty account dictionary.

    Args:
        name: The name of the financial account.

    Returns:
        A dictionary containing the account name and an empty transaction list.

    Raises:
        ValueError: If the account name is empty.
    """
    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Account name must not be empty.")

    return {
        "name": cleaned_name,
        "transactions": [],
    }


def add_transaction(account: dict, transaction: dict) -> None:
    """Add a transaction to an account.

    Args:
        account: The account that receives the transaction.
        transaction: The transaction that will be added.
    """
    account["transactions"].append(transaction)


def calculate_balance(account: dict) -> float:
    """Calculate and return the current account balance.

    Income increases the balance, while expenses reduce it.

    Args:
        account: The account whose balance will be calculated.

    Returns:
        The calculated account balance.
    """
    return sum(
        signed_amount(transaction)
        for transaction in account["transactions"]
    )


def calculate_income_total(account: dict) -> float:
    """Calculate and return the total income of an account.

    Args:
        account: The account whose income will be calculated.

    Returns:
        The sum of all income transactions.
    """
    return sum(
        float(transaction["amount"])
        for transaction in account["transactions"]
        if is_income(transaction)
    )


def calculate_expense_total(account: dict) -> float:
    """Calculate and return the total expenses of an account.

    Args:
        account: The account whose expenses will be calculated.

    Returns:
        The sum of all expense transactions as a positive number.
    """
    return sum(
        float(transaction["amount"])
        for transaction in account["transactions"]
        if is_expense(transaction)
    )


def filter_by_category(account: dict, category: Category) -> list[dict]:
    """Return all transactions belonging to a given category.

    Args:
        account: The account containing the transactions.
        category: The category used for filtering.

    Returns:
        A list containing matching transactions.
    """
    return [
        transaction
        for transaction in account["transactions"]
        if transaction["category"] == category
    ]


def filter_by_type(
    account: dict,
    transaction_type: TransactionType,
) -> list[dict]:
    """Return all transactions belonging to a given transaction type.

    Args:
        account: The account containing the transactions.
        transaction_type: The transaction type used for filtering.

    Returns:
        A list containing matching transactions.
    """
    return [
        transaction
        for transaction in account["transactions"]
        if transaction["transaction_type"] == transaction_type
    ]