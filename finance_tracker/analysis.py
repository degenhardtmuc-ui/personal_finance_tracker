"""Provide filtering, search, and analysis functions for account data."""

import re

from finance_tracker.category import Category
from finance_tracker.transaction import is_expense, is_income


MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def validate_month(month: str) -> None:
    """Validate that a month uses the YYYY-MM format."""
    if not MONTH_PATTERN.fullmatch(month):
        raise ValueError("Month must use YYYY-MM format")


def filter_by_date_range(
    account: dict,
    start: str,
    end: str,
) -> list[dict]:
    """Return transactions whose dates are inside the inclusive range."""
    return [
        transaction
        for transaction in account["transactions"]
        if start <= transaction["date"] <= end
    ]


def filter_by_month(
    account: dict,
    month: str,
) -> list[dict]:
    """Return all transactions belonging to the given YYYY-MM month."""
    validate_month(month)

    return [
        transaction
        for transaction in account["transactions"]
        if transaction["date"].startswith(month)
    ]


def search_transactions(
    account: dict,
    query: str,
) -> list[dict]:
    """Search transaction descriptions with a case-insensitive regex."""
    pattern = re.compile(query, re.IGNORECASE)

    return [
        transaction
        for transaction in account["transactions"]
        if pattern.search(transaction["description"])
    ]


def filter_by_tags(
    account: dict,
    tags: set[str],
) -> list[dict]:
    """Return transactions matching at least one requested tag."""
    return [
        transaction
        for transaction in account["transactions"]
        if transaction["tags"] & tags
    ]


def monthly_summary(
    account: dict,
) -> dict[str, dict[str, float]]:
    """Return income, expenses, and net balance grouped by month."""
    summary: dict[str, dict[str, float]] = {}

    for transaction in account["transactions"]:
        month = transaction["date"][:7]

        if month not in summary:
            summary[month] = {
                "income": 0.0,
                "expenses": 0.0,
                "net": 0.0,
            }

        if is_income(transaction):
            summary[month]["income"] += transaction["amount"]

        if is_expense(transaction):
            summary[month]["expenses"] += transaction["amount"]

        summary[month]["net"] = (
            summary[month]["income"]
            - summary[month]["expenses"]
        )

    return dict(sorted(summary.items()))


def category_breakdown(
    account: dict,
) -> dict[Category, float]:
    """Return expense totals grouped by category."""
    breakdown: dict[Category, float] = {}

    for transaction in account["transactions"]:
        if not is_expense(transaction):
            continue

        category = transaction["category"]
        amount = transaction["amount"]

        breakdown[category] = (
            breakdown.get(category, 0.0)
            + amount
        )

    return dict(
        sorted(
            breakdown.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


def top_expenses(
    account: dict,
    n: int = 5,
) -> list[dict]:
    """Return the largest expense transactions in descending order."""
    if n < 0:
        raise ValueError("Limit must be non-negative")

    expenses = [
        transaction
        for transaction in account["transactions"]
        if is_expense(transaction)
    ]

    sorted_expenses = sorted(
        expenses,
        key=lambda transaction: transaction["amount"],
        reverse=True,
    )

    return sorted_expenses[:n]


def daily_spending(
    account: dict,
    month: str,
) -> dict[str, float]:
    """Return daily expense totals for the requested month."""
    monthly_transactions = filter_by_month(account, month)
    spending: dict[str, float] = {}

    for transaction in monthly_transactions:
        if not is_expense(transaction):
            continue

        date = transaction["date"]
        amount = transaction["amount"]

        spending[date] = spending.get(date, 0.0) + amount

    return dict(sorted(spending.items()))