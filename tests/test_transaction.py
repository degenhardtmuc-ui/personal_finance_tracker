"""Tests for transaction creation, validation, and calculations."""

import pytest

from finance_tracker.category import Category, TransactionType
from finance_tracker.transaction import (
    create_transaction,
    format_transaction,
    is_expense,
    is_income,
    signed_amount,
)


def test_create_transaction_returns_expected_dictionary():
    """Check that a transaction contains all expected keys and values."""

    transaction = create_transaction(
        description="Groceries",
        amount=45.50,
        transaction_type=TransactionType.EXPENSE,
        category=Category.FOOD,
        date="2026-09-17",
        tags={"weekly"},
    )

    assert transaction == {
        "description": "Groceries",
        "amount": 45.50,
        "transaction_type": TransactionType.EXPENSE,
        "category": Category.FOOD,
        "date": "2026-09-17",
        "tags": {"weekly"},
    }


@pytest.mark.parametrize(
    "amount",
    [0, -1, -25.50],
)
def test_create_transaction_rejects_non_positive_amount(amount):
    """Check that zero and negative amounts are rejected."""

    with pytest.raises(ValueError, match="positive"):
        create_transaction(
            description="Groceries",
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-09-17",
        )


@pytest.mark.parametrize(
    "description",
    ["", "   "],
)
def test_create_transaction_rejects_empty_description(description):
    """Check that empty descriptions and spaces are rejected."""

    with pytest.raises(ValueError, match="empty"):
        create_transaction(
            description=description,
            amount=45.50,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-09-17",
        )


@pytest.mark.parametrize(
    "date",
    [
        "17.09.2026",
        "2026/09/17",
        "2026-9-17",
        "invalid",
    ],
)
def test_create_transaction_rejects_invalid_date_format(date):
    """Check that dates must use the ISO YYYY-MM-DD format."""

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        create_transaction(
            description="Groceries",
            amount=45.50,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date=date,
        )


def test_create_transaction_uses_empty_set_for_missing_tags():
    """Check that omitted tags produce a new empty set."""

    transaction = create_transaction(
        description="Salary",
        amount=3000.00,
        transaction_type=TransactionType.INCOME,
        category=Category.SALARY,
        date="2026-09-01",
    )

    assert transaction["tags"] == set()


def test_expense_helpers():
    """Check expense detection and the negative signed amount."""

    transaction = create_transaction(
        description="Rent",
        amount=900.00,
        transaction_type=TransactionType.EXPENSE,
        category=Category.HOUSING,
        date="2026-09-03",
    )

    assert is_expense(transaction) is True
    assert is_income(transaction) is False
    assert signed_amount(transaction) == pytest.approx(-900.00)


def test_income_helpers():
    """Check income detection and the positive signed amount."""

    transaction = create_transaction(
        description="Salary",
        amount=3000.00,
        transaction_type=TransactionType.INCOME,
        category=Category.SALARY,
        date="2026-09-01",
    )

    assert is_expense(transaction) is False
    assert is_income(transaction) is True
    assert signed_amount(transaction) == pytest.approx(3000.00)


def test_format_transaction():
    """Check the formatted transaction output."""

    transaction = create_transaction(
        description="Groceries",
        amount=45.50,
        transaction_type=TransactionType.EXPENSE,
        category=Category.FOOD,
        date="2026-09-17",
    )

    assert format_transaction(transaction) == (
        "2026-09-17  Groceries        -45.50  [FOOD]"
    )