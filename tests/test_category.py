"""Tests for financial category and transaction type enums."""

import pytest

from finance_tracker.category import Category, TransactionType


@pytest.mark.parametrize(
    ("category", "expected_value"),
    [
        (Category.HOUSING, "housing"),
        (Category.FOOD, "food"),
        (Category.TRANSPORT, "transport"),
        (Category.ENTERTAINMENT, "entertainment"),
        (Category.HEALTH, "health"),
        (Category.EDUCATION, "education"),
        (Category.CLOTHING, "clothing"),
        (Category.SALARY, "salary"),
        (Category.FREELANCE, "freelance"),
        (Category.INVESTMENT, "investment"),
        (Category.OTHER, "other"),
    ],
)
def test_category_values(category, expected_value):
    """Check that every category contains the expected string value."""

    assert category.value == expected_value


@pytest.mark.parametrize(
    ("transaction_type", "expected_value"),
    [
        (TransactionType.INCOME, "income"),
        (TransactionType.EXPENSE, "expense"),
    ],
)
def test_transaction_type_values(
    transaction_type,
    expected_value,
):
    """Check that every transaction type has the expected value."""

    assert transaction_type.value == expected_value