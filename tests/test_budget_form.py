"""Test creating and updating budgets through the PySide6 form."""

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QLabel,
    QLineEdit,
    QPushButton,
)
from pytestqt.qtbot import QtBot

from finance_tracker.budget import set_budget
from finance_tracker.category import Category
from finance_tracker.gui.main_window import MainWindow


@pytest.fixture
def budget_window(qtbot: QtBot) -> MainWindow:
    """Return a fresh main window managed by pytest-qt."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.tab_widget.setCurrentIndex(2)
    window.show()
    return window


def fill_budget_form(
    window: MainWindow,
    limit: str,
    month: QDate,
) -> QPushButton:
    """Fill the budget inputs and return the submit button."""
    category_input = window.findChild(QComboBox, "budget_category_input")
    limit_input = window.findChild(QLineEdit, "budget_limit_input")
    month_input = window.findChild(QDateEdit, "budget_month_input")
    button = window.findChild(QPushButton, "set_budget_button")

    assert category_input is not None
    assert limit_input is not None
    assert month_input is not None
    assert button is not None

    category_input.setCurrentText("Food")
    assert category_input.currentText() == "Food"
    limit_input.setText(limit)
    month_input.setDate(month)
    return button


def test_budget_form_contains_required_widgets(
    budget_window: MainWindow,
) -> None:
    """Verify the form inputs, submit button, and status label."""
    category_input = budget_window.findChild(
        QComboBox, "budget_category_input",
    )
    limit_input = budget_window.findChild(QLineEdit, "budget_limit_input")
    month_input = budget_window.findChild(QDateEdit, "budget_month_input")
    button = budget_window.findChild(QPushButton, "set_budget_button")
    status = budget_window.findChild(QLabel, "budget_status_label")

    assert category_input is not None
    assert limit_input is not None
    assert month_input is not None
    assert button is not None
    assert status is not None

    categories = [
        category_input.itemText(index)
        for index in range(category_input.count())
    ]
    assert categories == [category.value.title() for category in Category]
    assert limit_input.placeholderText() == "0.00"
    assert month_input.displayFormat() == "yyyy-MM"
    assert button.text() == "Set budget"
    assert status.text() == ""


def test_submit_creates_budget_and_updates_overview(
    budget_window: MainWindow,
    qtbot: QtBot,
    analysis_account: dict,
) -> None:
    """Verify that submitting a budget immediately displays its values."""
    budget_window.account = analysis_account
    button = fill_budget_form(budget_window, "300.00", QDate(2026, 9, 1))

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.budget_tracker["budgets"] == [
        {
            "category": Category.FOOD,
            "monthly_limit": 300.00,
            "month": "2026-09",
        },
    ]
    table = budget_window.budget_table
    assert table.rowCount() == 1
    assert [table.item(0, column).text() for column in range(7)] == [
        "2026-09", "Food", "300.00", "195.00",
        "105.00", "65.00%", "Within budget",
    ]
    status = budget_window.findChild(QLabel, "budget_status_label")
    assert status is not None
    assert status.text() == "Budget saved for this session."


def test_submit_updates_existing_category_and_month(
    budget_window: MainWindow,
    qtbot: QtBot,
    analysis_account: dict,
) -> None:
    """Verify that updating a limit replaces the budget without duplicates."""
    budget_window.account = analysis_account
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    budget_window._refresh_dashboard()
    button = fill_budget_form(budget_window, "150.00", QDate(2026, 9, 1))

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    budgets = budget_window.budget_tracker["budgets"]
    assert len(budgets) == 1
    assert budgets[0]["monthly_limit"] == 150.00
    table = budget_window.budget_table
    assert table.rowCount() == 1
    assert [table.item(0, column).text() for column in range(7)] == [
        "2026-09", "Food", "150.00", "195.00",
        "-45.00", "130.00%", "Exceeded",
    ]


def test_submit_preserves_budget_for_another_month(
    budget_window: MainWindow,
    qtbot: QtBot,
) -> None:
    """Verify that the same category can have separate monthly budgets."""
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    budget_window._refresh_dashboard()
    button = fill_budget_form(budget_window, "200.00", QDate(2026, 10, 1))

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.budget_tracker["budgets"] == [
        {
            "category": Category.FOOD,
            "monthly_limit": 300.00,
            "month": "2026-09",
        },
        {
            "category": Category.FOOD,
            "monthly_limit": 200.00,
            "month": "2026-10",
        },
    ]
    assert budget_window.budget_table.rowCount() == 2


@pytest.mark.parametrize(
    ("limit_text", "expected_message"),
    [
        ("", "Monthly limit must be a valid number."),
        ("abc", "Monthly limit must be a valid number."),
        ("0", "Monthly limit must be positive"),
        ("-50", "Monthly limit must be positive"),
    ],
)
def test_invalid_limit_preserves_existing_budget(
    budget_window: MainWindow,
    qtbot: QtBot,
    limit_text: str,
    expected_message: str,
) -> None:
    """Verify that invalid input leaves the tracker and overview unchanged."""
    set_budget(budget_window.budget_tracker, Category.FOOD, 300.00, "2026-09")
    budget_window._refresh_dashboard()
    button = fill_budget_form(budget_window, limit_text, QDate(2026, 9, 1))

    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert budget_window.budget_tracker["budgets"] == [
        {
            "category": Category.FOOD,
            "monthly_limit": 300.00,
            "month": "2026-09",
        },
    ]
    assert budget_window.budget_table.rowCount() == 1
    assert budget_window.budget_table.item(0, 2).text() == "300.00"
    status = budget_window.findChild(QLabel, "budget_status_label")
    assert status is not None
    assert status.text() == expected_message