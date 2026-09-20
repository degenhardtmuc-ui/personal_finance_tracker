"""Provide dictionary-based budget and budget tracker functions."""

from finance_tracker.category import Category


def create_budget(
    category: Category,
    monthly_limit: float,
    month: str,
) -> dict:
    """Create and return a validated budget dictionary."""
    raise NotImplementedError


def remaining(
    budget: dict,
    account: dict,
) -> float:
    """Return the unused amount of a budget."""
    raise NotImplementedError


def is_exceeded(
    budget: dict,
    account: dict,
) -> bool:
    """Return whether the budget limit has been exceeded."""
    raise NotImplementedError


def usage_percentage(
    budget: dict,
    account: dict,
) -> float:
    """Return the percentage of the budget that has been used."""
    raise NotImplementedError


def create_budget_tracker() -> dict:
    """Create and return an empty budget tracker dictionary."""
    raise NotImplementedError


def set_budget(
    tracker: dict,
    category: Category,
    monthly_limit: float,
    month: str,
) -> None:
    """Add a budget or replace an existing budget."""
    raise NotImplementedError


def check_budgets(
    tracker: dict,
    account: dict,
) -> list[tuple[dict, float]]:
    """Return every budget together with its usage percentage."""
    raise NotImplementedError


def exceeded_budgets(
    tracker: dict,
    account: dict,
) -> list[dict]:
    """Return all budgets whose limits have been exceeded."""
    raise NotImplementedError