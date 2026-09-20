"""Provide shared pytest fixtures for the finance tracker tests."""

import pytest

from finance_tracker.account import add_transaction, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.transaction import create_transaction


@pytest.fixture
def analysis_account() -> dict:
    """Return an account containing known transactions for analysis tests."""
    account = create_account("Checking")

    transactions = [
        create_transaction(
            description="September Salary",
            amount=3000.00,
            transaction_type=TransactionType.INCOME,
            category=Category.SALARY,
            date="2026-09-01",
            tags={"work", "monthly"},
        ),
        create_transaction(
            description="Apartment Rent",
            amount=900.00,
            transaction_type=TransactionType.EXPENSE,
            category=Category.HOUSING,
            date="2026-09-03",
            tags={"home", "monthly"},
        ),
        create_transaction(
            description="Supermarket Groceries",
            amount=150.00,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-09-05",
            tags={"food", "essential"},
        ),
        create_transaction(
            description="Italian Restaurant",
            amount=45.00,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-09-05",
            tags={"food", "leisure"},
        ),
        create_transaction(
            description="Train Ticket",
            amount=60.00,
            transaction_type=TransactionType.EXPENSE,
            category=Category.TRANSPORT,
            date="2026-09-18",
            tags={"travel"},
        ),
        create_transaction(
            description="August Freelance Project",
            amount=500.00,
            transaction_type=TransactionType.INCOME,
            category=Category.FREELANCE,
            date="2026-08-20",
            tags={"work"},
        ),
        create_transaction(
            description="August Groceries",
            amount=80.00,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-08-22",
            tags={"food", "essential"},
        ),
    ]

    for transaction in transactions:
        add_transaction(account, transaction)

    return account