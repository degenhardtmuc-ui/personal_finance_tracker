"""Provide filtering, search, and analysis functions for account data."""

from finance_tracker.category import Category


def filter_by_date_range(
    account: dict,
    start: str,
    end: str,
) -> list[dict]:
    """Return transactions whose dates are inside the inclusive range."""
    raise NotImplementedError


def filter_by_month(
    account: dict,
    month: str,
) -> list[dict]:
    """Return all transactions belonging to the given YYYY-MM month."""
    raise NotImplementedError


def search_transactions(
    account: dict,
    query: str,
) -> list[dict]:
    """Search transaction descriptions with a case-insensitive regex."""
    raise NotImplementedError


def filter_by_tags(
    account: dict,
    tags: set[str],
) -> list[dict]:
    """Return transactions matching at least one requested tag."""
    raise NotImplementedError


def monthly_summary(
    account: dict,
) -> dict[str, dict[str, float]]:
    """Return income, expenses, and net balance grouped by month."""
    raise NotImplementedError


def category_breakdown(
    account: dict,
) -> dict[Category, float]:
    """Return expense totals grouped by category."""
    raise NotImplementedError


def top_expenses(
    account: dict,
    n: int = 5,
) -> list[dict]:
    """Return the largest expense transactions in descending order."""
    raise NotImplementedError


def daily_spending(
    account: dict,
    month: str,
) -> dict[str, float]:
    """Return daily expense totals for the requested month."""
    raise NotImplementedError