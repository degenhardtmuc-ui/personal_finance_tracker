"""Provide CSV import and export functions for finance data."""

from pathlib import Path

from finance_tracker.category import Category


def normalize_category(category_name: str) -> Category:
    """Convert a flexible category name into a Category enum."""
    raise NotImplementedError


def parse_csv_row(
    row: dict[str, str],
    line_number: int,
) -> dict:
    """Convert one CSV row into a validated transaction dictionary."""
    raise NotImplementedError


def import_transactions(
    account: dict,
    path: str | Path,
) -> dict:
    """Import valid CSV transactions and collect all row errors."""
    raise NotImplementedError


def export_transactions(
    account: dict,
    path: str | Path,
) -> None:
    """Export transactions and a summary row to a CSV file."""
    raise NotImplementedError