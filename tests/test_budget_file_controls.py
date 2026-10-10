"""Test the GUI controls for saving and loading budget files."""

import json
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QPushButton
from pytestqt.qtbot import QtBot

from finance_tracker.budget import set_budget
from finance_tracker.category import Category
from finance_tracker.gui.main_window import MainWindow


@pytest.fixture
def budget_window(qtbot: QtBot) -> MainWindow:
    """Return a visible main window with the Budgets tab selected."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.tab_widget.setCurrentIndex(2)
    window.show()
    return window


def test_save_button_writes_budget_file(
    budget_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that saving appends .json and writes the current budgets."""
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    destination = tmp_path / "budgets"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(destination), ""),
    )
    button = budget_window.findChild(QPushButton, "save_budgets_button")
    assert button is not None
    assert button.text() == "Save budgets"

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    path = destination.with_suffix(".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["budgets"][0]["monthly_limit"] == 300.00
    assert budget_window.budget_status_label.text() == "Budgets saved successfully."


def test_load_button_replaces_budgets_and_refreshes_overview(
    budget_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    analysis_account: dict,
) -> None:
    """Verify that loading replaces the tracker and preserves the account."""
    budget_window.account = analysis_account
    set_budget(budget_window.budget_tracker, Category.HOUSING, 900.00, "2026-10")
    budget_window._refresh_dashboard()
    path = tmp_path / "budgets.json"
    path.write_text(
        json.dumps({"budgets": [
            {"category": "FOOD", "monthly_limit": 300.00, "month": "2026-09"},
        ]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )
    button = budget_window.findChild(QPushButton, "load_budgets_button")
    assert button is not None
    assert button.text() == "Load budgets"

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.account is analysis_account
    assert budget_window.budget_tracker["budgets"] == [
        {"category": Category.FOOD, "monthly_limit": 300.00, "month": "2026-09"},
    ]
    table = budget_window.budget_table
    assert table.rowCount() == 1
    assert [table.item(0, column).text() for column in range(7)] == [
        "2026-09", "Food", "300.00", "195.00",
        "105.00", "65.00%", "Within budget",
    ]
    assert budget_window.budget_status_label.text() == "Budgets loaded successfully."


@pytest.mark.parametrize(
    ("button_name", "dialog_method"),
    [
        ("save_budgets_button", "getSaveFileName"),
        ("load_budgets_button", "getOpenFileName"),
    ],
)
def test_cancelled_budget_dialog_preserves_state(
    budget_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    button_name: str,
    dialog_method: str,
) -> None:
    """Verify that cancelling either dialog leaves budgets unchanged."""
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    budget_window._refresh_dashboard()
    tracker = budget_window.budget_tracker
    budget_window.budget_status_label.setText("Previous status")
    monkeypatch.setattr(
        QFileDialog,
        dialog_method,
        lambda *args, **kwargs: ("", ""),
    )
    button = budget_window.findChild(QPushButton, button_name)
    assert button is not None

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.budget_tracker is tracker
    assert tracker["budgets"][0]["monthly_limit"] == 300.00
    assert budget_window.budget_table.rowCount() == 1
    assert budget_window.budget_status_label.text() == "Previous status"


def test_failed_budget_load_preserves_existing_data(
    budget_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that an invalid file does not replace the current tracker."""
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    budget_window._refresh_dashboard()
    tracker = budget_window.budget_tracker
    path = tmp_path / "broken.json"
    path.write_text("invalid JSON", encoding="utf-8")
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )
    button = budget_window.findChild(QPushButton, "load_budgets_button")
    assert button is not None

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.budget_tracker is tracker
    assert tracker["budgets"][0]["monthly_limit"] == 300.00
    assert budget_window.budget_table.item(0, 2).text() == "300.00"
    assert budget_window.budget_status_label.text().startswith(
        "Budgets could not be loaded:",
    )