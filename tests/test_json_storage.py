"""Test JSON serialization and persistence functions."""

import json
from pathlib import Path

import pytest

from finance_tracker.category import Category, TransactionType
from finance_tracker.json_storage import (
    account_from_dict,
    account_to_dict,
    load_account,
    save_account,
    transaction_from_dict,
    transaction_to_dict,
)
from finance_tracker.transaction import create_transaction


@pytest.fixture
def sample_transaction() -> dict:
    """Return one transaction containing enums and a set."""
    return create_transaction(
        description="Supermarket Groceries",
        amount=150.00,
        transaction_type=TransactionType.EXPENSE,
        category=Category.FOOD,
        date="2026-09-05",
        tags={"food", "essential"},
    )


def test_transaction_to_dict_returns_json_compatible_data(
    sample_transaction: dict,
) -> None:
    """Check that enums and sets are converted for JSON."""
    result = transaction_to_dict(sample_transaction)

    assert result == {
        "description": "Supermarket Groceries",
        "amount": 150.00,
        "transaction_type": "EXPENSE",
        "category": "FOOD",
        "date": "2026-09-05",
        "tags": ["essential", "food"],
    }

    json.dumps(result)


def test_transaction_from_dict_restores_python_types() -> None:
    """Check that strings and lists are restored to enums and sets."""
    data = {
        "description": "Supermarket Groceries",
        "amount": 150.00,
        "transaction_type": "EXPENSE",
        "category": "FOOD",
        "date": "2026-09-05",
        "tags": ["essential", "food"],
    }

    transaction = transaction_from_dict(data)

    assert transaction["transaction_type"] == TransactionType.EXPENSE
    assert transaction["category"] == Category.FOOD
    assert transaction["tags"] == {"essential", "food"}


def test_transaction_json_round_trip(
    sample_transaction: dict,
) -> None:
    """Check that converting to JSON data and back preserves the transaction."""
    serialized = transaction_to_dict(sample_transaction)
    restored = transaction_from_dict(serialized)

    assert restored == sample_transaction


def test_account_to_dict_returns_json_compatible_data(
    analysis_account: dict,
) -> None:
    """Check that an account and all transactions can be encoded as JSON."""
    result = account_to_dict(analysis_account)

    assert result["name"] == "Checking"
    assert len(result["transactions"]) == 7
    assert result["transactions"][0]["transaction_type"] == "INCOME"
    assert result["transactions"][0]["category"] == "SALARY"

    json.dumps(result)


def test_account_from_dict_restores_account_data(
    analysis_account: dict,
) -> None:
    """Check that serialized account data is restored correctly."""
    serialized = account_to_dict(analysis_account)
    restored = account_from_dict(serialized)

    assert restored == analysis_account


def test_save_account_creates_valid_json_file(
    analysis_account: dict,
    tmp_path: Path,
) -> None:
    """Check that an account is written to a valid JSON file."""
    file_path = tmp_path / "account.json"

    save_account(analysis_account, file_path)

    assert file_path.exists()

    with file_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        saved_data = json.load(file)

    assert saved_data["name"] == "Checking"
    assert len(saved_data["transactions"]) == 7


def test_load_account_restores_saved_account(
    analysis_account: dict,
    tmp_path: Path,
) -> None:
    """Check the complete save and load round trip."""
    file_path = tmp_path / "account.json"

    save_account(analysis_account, file_path)
    loaded_account = load_account(file_path)

    assert loaded_account == analysis_account


def test_load_account_rejects_missing_file(
    tmp_path: Path,
) -> None:
    """Check that loading a missing file raises FileNotFoundError."""
    missing_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_account(missing_path)