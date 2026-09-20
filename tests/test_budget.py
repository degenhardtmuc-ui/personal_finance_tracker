"""Test dictionary-based budget and budget tracker functions."""

import pytest

from finance_tracker.budget import (
    check_budgets,
    create_budget,
    create_budget_tracker,
    exceeded_budgets,
    is_exceeded,
    remaining,
    set_budget,
    usage_percentage,
)
from finance_tracker.category import Category


def test_create_budget_returns_expected_dictionary() -> None:
    """Check that a budget is represented by the expected dictionary."""
    budget = create_budget(
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )

    assert budget == {
        "category": Category.FOOD,
        "monthly_limit": 200.00,
        "month": "2026-09",
    }


@pytest.mark.parametrize(
    "monthly_limit",
    [
        0,
        -50.00,
    ],
)
def test_create_budget_rejects_non_positive_limit(
    monthly_limit: float,
) -> None:
    """Check that zero and negative budget limits are rejected."""
    with pytest.raises(ValueError, match="positive"):
        create_budget(
            category=Category.FOOD,
            monthly_limit=monthly_limit,
            month="2026-09",
        )


def test_create_budget_rejects_invalid_month() -> None:
    """Check that the budget month must use the YYYY-MM format."""
    with pytest.raises(ValueError, match="YYYY-MM"):
        create_budget(
            category=Category.FOOD,
            monthly_limit=200.00,
            month="September 2026",
        )


def test_remaining_returns_unused_budget_amount(
    analysis_account: dict,
) -> None:
    """Check the remaining amount of a budget."""
    budget = create_budget(
        category=Category.FOOD,
        monthly_limit=300.00,
        month="2026-09",
    )

    assert remaining(budget, analysis_account) == pytest.approx(105.00)


def test_is_exceeded_returns_false_below_limit(
    analysis_account: dict,
) -> None:
    """Check that a budget below its limit is not exceeded."""
    budget = create_budget(
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )

    assert is_exceeded(budget, analysis_account) is False


def test_is_exceeded_returns_false_at_exact_limit(
    analysis_account: dict,
) -> None:
    """Check that reaching the exact limit is not exceeding it."""
    budget = create_budget(
        category=Category.HOUSING,
        monthly_limit=900.00,
        month="2026-09",
    )

    assert remaining(budget, analysis_account) == pytest.approx(0.00)
    assert is_exceeded(budget, analysis_account) is False


def test_is_exceeded_returns_true_above_limit(
    analysis_account: dict,
) -> None:
    """Check that spending above the limit exceeds the budget."""
    budget = create_budget(
        category=Category.TRANSPORT,
        monthly_limit=50.00,
        month="2026-09",
    )

    assert remaining(budget, analysis_account) == pytest.approx(-10.00)
    assert is_exceeded(budget, analysis_account) is True


def test_usage_percentage(
    analysis_account: dict,
) -> None:
    """Check the percentage of the budget that has been used."""
    budget = create_budget(
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )

    assert usage_percentage(
        budget,
        analysis_account,
    ) == pytest.approx(97.50)


def test_create_budget_tracker_returns_empty_tracker() -> None:
    """Check that a new tracker contains no budgets."""
    tracker = create_budget_tracker()

    assert tracker == {
        "budgets": [],
    }


def test_set_budget_appends_budget() -> None:
    """Check that a new budget is added to the tracker."""
    tracker = create_budget_tracker()

    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )

    assert len(tracker["budgets"]) == 1
    assert tracker["budgets"][0] == {
        "category": Category.FOOD,
        "monthly_limit": 200.00,
        "month": "2026-09",
    }


def test_set_budget_replaces_matching_budget() -> None:
    """Check that category and month identify an existing budget."""
    tracker = create_budget_tracker()

    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )
    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=250.00,
        month="2026-09",
    )

    assert len(tracker["budgets"]) == 1
    assert tracker["budgets"][0]["monthly_limit"] == pytest.approx(
        250.00
    )


def test_check_budgets_returns_usage_percentages(
    analysis_account: dict,
) -> None:
    """Check that every budget is returned with its usage."""
    tracker = create_budget_tracker()

    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )
    set_budget(
        tracker,
        category=Category.HOUSING,
        monthly_limit=900.00,
        month="2026-09",
    )

    results = check_budgets(tracker, analysis_account)

    assert len(results) == 2
    assert results[0][0]["category"] == Category.FOOD
    assert results[0][1] == pytest.approx(97.50)
    assert results[1][0]["category"] == Category.HOUSING
    assert results[1][1] == pytest.approx(100.00)


def test_exceeded_budgets_returns_only_exceeded_budgets(
    analysis_account: dict,
) -> None:
    """Check that only budgets above their limits are returned."""
    tracker = create_budget_tracker()

    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=200.00,
        month="2026-09",
    )
    set_budget(
        tracker,
        category=Category.HOUSING,
        monthly_limit=900.00,
        month="2026-09",
    )
    set_budget(
        tracker,
        category=Category.TRANSPORT,
        monthly_limit=50.00,
        month="2026-09",
    )

    results = exceeded_budgets(tracker, analysis_account)

    assert len(results) == 1
    assert results[0]["category"] == Category.TRANSPORT