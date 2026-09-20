"""Test filtering, search, and analysis functions."""

import pytest

from finance_tracker.analysis import (
    category_breakdown,
    daily_spending,
    filter_by_date_range,
    filter_by_month,
    filter_by_tags,
    monthly_summary,
    search_transactions,
    top_expenses,
)
from finance_tracker.category import Category


def test_filter_by_date_range_includes_boundaries(
    analysis_account: dict,
) -> None:
    """Check that the start and end dates are included."""
    results = filter_by_date_range(
        analysis_account,
        "2026-09-03",
        "2026-09-05",
    )

    descriptions = [
        transaction["description"]
        for transaction in results
    ]

    assert descriptions == [
        "Apartment Rent",
        "Supermarket Groceries",
        "Italian Restaurant",
    ]


def test_filter_by_date_range_returns_empty_list(
    analysis_account: dict,
) -> None:
    """Check a date range without matching transactions."""
    results = filter_by_date_range(
        analysis_account,
        "2026-07-01",
        "2026-07-31",
    )

    assert results == []


def test_filter_by_month(
    analysis_account: dict,
) -> None:
    """Check that only transactions from one month are returned."""
    results = filter_by_month(analysis_account, "2026-08")

    assert len(results) == 2
    assert all(
        transaction["date"].startswith("2026-08")
        for transaction in results
    )


@pytest.mark.parametrize(
    "month",
    [
        "2026",
        "09-2026",
        "2026/09",
        "invalid",
    ],
)
def test_filter_by_month_rejects_invalid_format(
    analysis_account: dict,
    month: str,
) -> None:
    """Check that the month must use the YYYY-MM format."""
    with pytest.raises(ValueError, match="YYYY-MM"):
        filter_by_month(analysis_account, month)


def test_search_transactions_is_case_insensitive(
    analysis_account: dict,
) -> None:
    """Check that uppercase and lowercase letters are treated equally."""
    results = search_transactions(
        analysis_account,
        "groceries",
    )

    assert len(results) == 2


def test_search_transactions_supports_regex(
    analysis_account: dict,
) -> None:
    """Check that regular expression patterns can be used."""
    results = search_transactions(
        analysis_account,
        r"Salary|Freelance",
    )

    assert len(results) == 2


def test_filter_by_tags_matches_any_requested_tag(
    analysis_account: dict,
) -> None:
    """Check that one matching tag is sufficient."""
    results = filter_by_tags(
        analysis_account,
        {"travel", "leisure"},
    )

    descriptions = {
        transaction["description"]
        for transaction in results
    }

    assert descriptions == {
        "Italian Restaurant",
        "Train Ticket",
    }


def test_filter_by_tags_returns_empty_list_for_empty_set(
    analysis_account: dict,
) -> None:
    """Check that an empty search set returns no transactions."""
    assert filter_by_tags(analysis_account, set()) == []


def test_monthly_summary(
    analysis_account: dict,
) -> None:
    """Check monthly income, expenses, and net values."""
    summary = monthly_summary(analysis_account)

    assert summary["2026-08"] == {
        "income": pytest.approx(500.00),
        "expenses": pytest.approx(80.00),
        "net": pytest.approx(420.00),
    }
    assert summary["2026-09"] == {
        "income": pytest.approx(3000.00),
        "expenses": pytest.approx(1155.00),
        "net": pytest.approx(1845.00),
    }


def test_category_breakdown(
    analysis_account: dict,
) -> None:
    """Check expense totals grouped by category."""
    breakdown = category_breakdown(analysis_account)

    assert breakdown[Category.HOUSING] == pytest.approx(900.00)
    assert breakdown[Category.FOOD] == pytest.approx(275.00)
    assert breakdown[Category.TRANSPORT] == pytest.approx(60.00)
    assert Category.SALARY not in breakdown
    assert Category.FREELANCE not in breakdown


def test_top_expenses_uses_default_limit(
    analysis_account: dict,
) -> None:
    """Check that five expenses are returned by default."""
    results = top_expenses(analysis_account)

    assert len(results) == 5
    assert results[0]["description"] == "Apartment Rent"
    assert results[-1]["description"] == "Italian Restaurant"


def test_top_expenses_accepts_custom_limit(
    analysis_account: dict,
) -> None:
    """Check that a custom result limit can be supplied."""
    results = top_expenses(analysis_account, n=2)

    assert [
        transaction["amount"]
        for transaction in results
    ] == [900.00, 150.00]


def test_top_expenses_rejects_negative_limit(
    analysis_account: dict,
) -> None:
    """Check that a negative limit is rejected."""
    with pytest.raises(ValueError, match="non-negative"):
        top_expenses(analysis_account, n=-1)


def test_daily_spending(
    analysis_account: dict,
) -> None:
    """Check expense totals grouped by day for one month."""
    spending = daily_spending(
        analysis_account,
        "2026-09",
    )

    assert spending == {
        "2026-09-03": pytest.approx(900.00),
        "2026-09-05": pytest.approx(195.00),
        "2026-09-18": pytest.approx(60.00),
    }