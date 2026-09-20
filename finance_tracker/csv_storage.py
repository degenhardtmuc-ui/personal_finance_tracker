"""Provide CSV import and export functions for finance data."""

import csv
from pathlib import Path

from finance_tracker.account import (
    add_transaction,
    calculate_balance,
)
from finance_tracker.category import Category, TransactionType
from finance_tracker.exceptions import (
    CsvImportError,
    InvalidTransactionError,
)
from finance_tracker.transaction import (
    create_transaction,
    signed_amount,
)


CSV_FIELDNAMES = [
    "date",
    "description",
    "amount",
    "category",
]


def normalize_category(category_name: str) -> Category:
    """Convert a flexible category name into a Category enum."""
    normalized_name = category_name.strip().upper()

    try:
        return Category[normalized_name]
    except KeyError as error:
        raise InvalidTransactionError(
            f"Unknown category: {category_name}"
        ) from error


def parse_csv_row(
    row: dict[str, str],
    line_number: int,
) -> dict:
    """Convert one CSV row into a validated transaction dictionary."""
    try:
        date = row["date"].strip()
        description = row["description"].strip()
        amount_text = row["amount"].strip()
        category_text = row["category"].strip()
    except (KeyError, AttributeError) as error:
        raise InvalidTransactionError(
            f"Missing or invalid CSV field on line {line_number}"
        ) from error

    try:
        signed_value = float(amount_text)
    except ValueError as error:
        raise InvalidTransactionError(
            f"Amount must be a valid number: {amount_text}"
        ) from error

    if signed_value == 0:
        raise InvalidTransactionError(
            "Amount must not be zero"
        )

    if signed_value > 0:
        transaction_type = TransactionType.INCOME
    else:
        transaction_type = TransactionType.EXPENSE

    category = normalize_category(category_text)

    try:
        return create_transaction(
            description=description,
            amount=abs(signed_value),
            transaction_type=transaction_type,
            category=category,
            date=date,
        )
    except ValueError as error:
        raise InvalidTransactionError(str(error)) from error


def import_transactions(
    account: dict,
    path: str | Path,
) -> dict:
    """Import valid CSV transactions and collect all row errors."""
    file_path = Path(path)
    imported = 0
    skipped = 0
    errors: list[CsvImportError] = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            try:
                transaction = parse_csv_row(
                    row,
                    line_number,
                )
                add_transaction(account, transaction)
                imported += 1

            except InvalidTransactionError as error:
                csv_error = CsvImportError(
                    line_number=line_number,
                    reason=str(error),
                )
                errors.append(csv_error)
                skipped += 1

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
    }


def export_transactions(
    account: dict,
    path: str | Path,
) -> None:
    """Export transactions and a summary row to a CSV file."""
    file_path = Path(path)

    with file_path.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(CSV_FIELDNAMES)

        for transaction in account["transactions"]:
            writer.writerow(
                [
                    transaction["date"],
                    transaction["description"],
                    f"{signed_amount(transaction):.2f}",
                    transaction["category"].name,
                ]
            )

        writer.writerow(
            [
                "SUMMARY",
                "Net Balance",
                f"{calculate_balance(account):.2f}",
                "",
            ]
        )