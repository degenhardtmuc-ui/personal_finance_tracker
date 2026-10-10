"""Test JSON persistence for dictionary-based budget trackers."""

import json
from pathlib import Path

import pytest

from finance_tracker import json_storage
from finance_tracker.budget import create_budget_tracker, set_budget
from finance_tracker.category import Category


def test_save_budgets_writes_json(tmp_path: Path) -> None:
    """Verify that budget categories are serialized as enum names."""
    tracker = create_budget_tracker()
    set_budget(tracker, Category.FOOD, 300.00, "2026-09")
    path = tmp_path / "budgets.json"

    json_storage.save_budgets(tracker, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {
        "budgets": [
            {
                "category": "FOOD",
                "monthly_limit": 300.00,
                "month": "2026-09",
            },
        ],
    }
    assert tracker["budgets"][0]["category"] == Category.FOOD


def test_budget_file_round_trip(tmp_path: Path) -> None:
    """Verify that loading restores all budgets and category enums."""
    tracker = create_budget_tracker()
    set_budget(tracker, Category.FOOD, 300.00, "2026-09")
    set_budget(tracker, Category.HOUSING, 900.00, "2026-10")
    path = tmp_path / "budgets.json"

    json_storage.save_budgets(tracker, path)
    restored = json_storage.load_budgets(path)

    assert restored == tracker
    assert restored is not tracker


def test_empty_budget_tracker_round_trip(tmp_path: Path) -> None:
    """Verify that an empty tracker can be saved and loaded."""
    path = tmp_path / "empty.json"
    json_storage.save_budgets(create_budget_tracker(), path)

    assert json_storage.load_budgets(path) == {"budgets": []}


def test_load_budgets_rejects_missing_file(tmp_path: Path) -> None:
    """Verify that a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        json_storage.load_budgets(tmp_path / "missing.json")


def test_load_budgets_rejects_invalid_json(tmp_path: Path) -> None:
    """Verify that invalid JSON raises a decoding error."""
    path = tmp_path / "broken.json"
    path.write_text("not valid JSON", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        json_storage.load_budgets(path)


@pytest.mark.parametrize(
    ("limit", "month"),
    [(0.00, "2026-09"), (300.00, "2026-13")],
)
def test_load_budgets_validates_domain_data(
    tmp_path: Path,
    limit: float,
    month: str,
) -> None:
    """Verify that loading applies the existing budget validation."""
    path = tmp_path / "invalid_budget.json"
    data = {
        "budgets": [
            {"category": "FOOD", "monthly_limit": limit, "month": month},
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        json_storage.load_budgets(path)