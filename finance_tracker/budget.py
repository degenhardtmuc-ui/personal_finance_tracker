"""Provide dictionary-based budget and budget tracker functions."""

from finance_tracker.analysis import validate_month
from finance_tracker.category import Category
from finance_tracker.transaction import is_expense


def create_budget(
    category: Category,
    monthly_limit: float,
    month: str,
) -> dict:
    """Create and return a validated budget dictionary."""
    if monthly_limit <= 0:
        raise ValueError("Monthly limit must be positive")

    validate_month(month)

    return {
        "category": category,
        "monthly_limit": monthly_limit,
        "month": month,
    }


def calculate_spent_amount(
    budget: dict,
    account: dict,
) -> float:
    """Return the expenses matching a budget's category and month."""
    return sum(
        transaction["amount"]
        for transaction in account["transactions"]
        if is_expense(transaction)
        and transaction["category"] == budget["category"]
        and transaction["date"].startswith(budget["month"])
    )


def remaining(
    budget: dict,
    account: dict,
) -> float:
    """Return the unused amount of a budget."""
    spent = calculate_spent_amount(budget, account)

    return budget["monthly_limit"] - spent


def is_exceeded(
    budget: dict,
    account: dict,
) -> bool:
    """Return whether the budget limit has been exceeded."""
    return remaining(budget, account) < 0


def usage_percentage(
    budget: dict,
    account: dict,
) -> float:
    """Return the percentage of the budget that has been used."""
    spent = calculate_spent_amount(budget, account)

    return spent / budget["monthly_limit"] * 100


def create_budget_tracker() -> dict:
    """Create and return an empty budget tracker dictionary."""
    return {
        "budgets": [],
    }


def set_budget(
    tracker: dict,
    category: Category,
    monthly_limit: float,
    month: str,
) -> None:
    """Add a budget or replace an existing budget."""
    new_budget = create_budget(
        category=category,
        monthly_limit=monthly_limit,
        month=month,
    )

    for index, existing_budget in enumerate(tracker["budgets"]):
        same_category = existing_budget["category"] == category
        same_month = existing_budget["month"] == month

        if same_category and same_month:
            tracker["budgets"][index] = new_budget
            return

    tracker["budgets"].append(new_budget)


def check_budgets(
    tracker: dict,
    account: dict,
) -> list[tuple[dict, float]]:
    """Return every budget together with its usage percentage."""
    return [
        (
            budget,
            usage_percentage(budget, account),
        )
        for budget in tracker["budgets"]
    ]


def exceeded_budgets(
    tracker: dict,
    account: dict,
) -> list[dict]:
    """Return all budgets whose limits have been exceeded."""
    return [
        budget
        for budget in tracker["budgets"]
        if is_exceeded(budget, account)
    ]