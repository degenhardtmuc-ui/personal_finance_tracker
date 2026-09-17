"""Tests for account creation, totals, and transaction filtering."""

import pytest

from finance_tracker.account import (
    add_transaction,
    calculate_balance,
    calculate_expense_total,
    calculate_income_total,
    create_account,
    filter_by_category,
    filter_by_type,
)
from finance_tracker.category import Category, TransactionType
from finance_tracker.transaction import create_transaction


@pytest.fixture
def sample_account():
    """Create and return a reusable account with three transactions."""

    account = create_account("Checking")

    salary = create_transaction(
        description="Salary",
        amount=3000.00,
        transaction_type=TransactionType.INCOME,
        category=Category.SALARY,
        date="2026-09-01",
    )

    rent = create_transaction(
        description="Rent",
        amount=900.00,
        transaction_type=TransactionType.EXPENSE,
        category=Category.HOUSING,
        date="2026-09-03",
    )

    groceries = create_transaction(
        description="Groceries",
        amount=150.00,
        transaction_type=TransactionType.EXPENSE,
        category=Category.FOOD,
        date="2026-09-05",
    )

    add_transaction(account, salary)
    add_transaction(account, rent)
    add_transaction(account, groceries)

    return account


def test_create_account_returns_empty_account():
    """Check that a new account has an empty transaction list."""

    account = create_account("Checking")

    assert account == {
        "name": "Checking",
        "transactions": [],
    }


def test_add_transaction_appends_transaction():
    """Check that a transaction is added to the account."""

    account = create_account("Checking")

    transaction = create_transaction(
        description="Salary",
        amount=3000.00,
        transaction_type=TransactionType.INCOME,
        category=Category.SALARY,
        date="2026-09-01",
    )

    add_transaction(account, transaction)

    assert account["transactions"] == [transaction]


def test_calculate_balance(sample_account):
    """Check the balance of mixed income and expense transactions."""

    assert calculate_balance(sample_account) == pytest.approx(
        1950.00
    )


def test_calculate_totals(sample_account):
    """Check the separate income and expense totals."""

    assert calculate_income_total(
        sample_account
    ) == pytest.approx(3000.00)

    assert calculate_expense_total(
        sample_account
    ) == pytest.approx(1050.00)


def test_filter_by_category(sample_account):
    """Check that transactions can be filtered by category."""

    results = filter_by_category(
        sample_account,
        Category.FOOD,
    )

    assert len(results) == 1
    assert results[0]["description"] == "Groceries"


def test_filter_by_type(sample_account):
    """Check that transactions can be filtered by transaction type."""

    results = filter_by_type(
        sample_account,
        TransactionType.EXPENSE,
    )

    assert len(results) == 2

    assert all(
        transaction["transaction_type"]
        == TransactionType.EXPENSE
        for transaction in results
    )