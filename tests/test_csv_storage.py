"""Test CSV import, export, validation, and custom exceptions."""

import csv
from pathlib import Path

import pytest

from finance_tracker.account import calculate_balance, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.csv_storage import (
    export_transactions,
    import_transactions,
    normalize_category,
    parse_csv_row,
)
from finance_tracker.exceptions import (
    CsvImportError,
    InvalidTransactionError,
)


def test_csv_import_error_contains_line_number_and_reason() -> None:
    """Check that CSV errors contain useful diagnostic information."""
    error = CsvImportError(
        line_number=4,
        reason="Amount must not be zero",
    )

    assert error.line_number == 4
    assert error.reason == "Amount must not be zero"
    assert str(error) == (
        "CSV import error on line 4: "
        "Amount must not be zero"
    )


@pytest.mark.parametrize(
    "category_name",
    [
        "food",
        "FOOD",
        "  Food  ",
    ],
)
def test_normalize_category_accepts_flexible_spelling(
    category_name: str,
) -> None:
    """Check category matching without case or surrounding spaces."""
    assert normalize_category(category_name) == Category.FOOD


def test_normalize_category_rejects_unknown_category() -> None:
    """Check that an unknown category raises a project-specific error."""
    with pytest.raises(
        InvalidTransactionError,
        match="Unknown category",
    ):
        normalize_category("vacation")


def test_parse_csv_row_detects_positive_income() -> None:
    """Check that a positive amount creates an income transaction."""
    row = {
        "date": "2026-10-01",
        "description": "October Salary",
        "amount": "3200.00",
        "category": "salary",
    }

    transaction = parse_csv_row(row, line_number=2)

    assert transaction["amount"] == pytest.approx(3200.00)
    assert transaction["transaction_type"] == TransactionType.INCOME
    assert transaction["category"] == Category.SALARY


def test_parse_csv_row_detects_negative_expense() -> None:
    """Check that a negative amount creates an expense transaction."""
    row = {
        "date": "2026-10-02",
        "description": "Supermarket",
        "amount": "-45.50",
        "category": "food",
    }

    transaction = parse_csv_row(row, line_number=2)

    assert transaction["amount"] == pytest.approx(45.50)
    assert transaction["transaction_type"] == TransactionType.EXPENSE
    assert transaction["category"] == Category.FOOD


def test_parse_csv_row_rejects_zero_amount() -> None:
    """Check that zero cannot be imported as a transaction."""
    row = {
        "date": "2026-10-02",
        "description": "Invalid transaction",
        "amount": "0",
        "category": "other",
    }

    with pytest.raises(
        InvalidTransactionError,
        match="zero",
    ):
        parse_csv_row(row, line_number=2)


def test_import_transactions_imports_valid_rows(
    tmp_path: Path,
) -> None:
    """Check that valid CSV rows are added to an account."""
    csv_path = tmp_path / "valid_transactions.csv"
    csv_path.write_text(
        "date,description,amount,category\n"
        "2026-10-01,October Salary,3200.00,salary\n"
        "2026-10-02,Cafe,-12.50,food\n",
        encoding="utf-8",
    )
    account = create_account("Checking")

    result = import_transactions(account, csv_path)

    assert result == {
        "imported": 2,
        "skipped": 0,
        "errors": [],
    }
    assert len(account["transactions"]) == 2
    assert calculate_balance(account) == pytest.approx(3187.50)


def test_import_transactions_collects_errors_and_continues(
    tmp_path: Path,
) -> None:
    """Check that every invalid row is reported without stopping import."""
    csv_path = tmp_path / "mixed_transactions.csv"
    csv_path.write_text(
        "date,description,amount,category\n"
        "2026-10-01,October Salary,3200.00,salary\n"
        "20.10.2026,Bad Date,-10.00,food\n"
        "2026-10-03,Zero Amount,0,other\n"
        "2026-10-04,Holiday,-100.00,vacation\n"
        "2026-10-05,Groceries,-80.00,food\n",
        encoding="utf-8",
    )
    account = create_account("Checking")

    result = import_transactions(account, csv_path)

    assert result["imported"] == 2
    assert result["skipped"] == 3
    assert len(result["errors"]) == 3
    assert len(account["transactions"]) == 2

    assert all(
        isinstance(error, CsvImportError)
        for error in result["errors"]
    )
    assert [
        error.line_number
        for error in result["errors"]
    ] == [3, 4, 5]


def test_import_transactions_rejects_missing_file(
    tmp_path: Path,
) -> None:
    """Check that a missing CSV file raises FileNotFoundError."""
    missing_path = tmp_path / "missing.csv"
    account = create_account("Checking")

    with pytest.raises(FileNotFoundError):
        import_transactions(account, missing_path)


def test_export_transactions_writes_header_and_signed_amounts(
    analysis_account: dict,
    tmp_path: Path,
) -> None:
    """Check the CSV header and signed income and expense amounts."""
    csv_path = tmp_path / "export.csv"

    export_transactions(analysis_account, csv_path)

    with csv_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[0] == [
        "date",
        "description",
        "amount",
        "category",
    ]

    assert rows[1] == [
        "2026-09-01",
        "September Salary",
        "3000.00",
        "SALARY",
    ]

    assert rows[2] == [
        "2026-09-03",
        "Apartment Rent",
        "-900.00",
        "HOUSING",
    ]


def test_export_transactions_adds_summary_row(
    analysis_account: dict,
    tmp_path: Path,
) -> None:
    """Check that the final CSV row contains the account balance."""
    csv_path = tmp_path / "export.csv"

    export_transactions(analysis_account, csv_path)

    with csv_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[-1] == [
        "SUMMARY",
        "Net Balance",
        "2265.00",
        "",
    ]