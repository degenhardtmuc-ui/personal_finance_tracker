"""Provide JSON serialization and persistence for finance data."""

from pathlib import Path


def transaction_to_dict(transaction: dict) -> dict:
    """Convert a transaction into a JSON-compatible dictionary."""
    raise NotImplementedError


def transaction_from_dict(data: dict) -> dict:
    """Create a transaction dictionary from JSON-compatible data."""
    raise NotImplementedError


def account_to_dict(account: dict) -> dict:
    """Convert an account into a JSON-compatible dictionary."""
    raise NotImplementedError


def account_from_dict(data: dict) -> dict:
    """Create an account dictionary from JSON-compatible data."""
    raise NotImplementedError


def save_account(
    account: dict,
    path: str | Path,
) -> None:
    """Save an account dictionary to a JSON file."""
    raise NotImplementedError


def load_account(path: str | Path) -> dict:
    """Load and return an account dictionary from a JSON file."""
    raise NotImplementedError