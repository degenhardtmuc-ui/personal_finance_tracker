"""Test the budget overview of the PySide6 interface."""

from PySide6.QtWidgets import QTableWidget

from finance_tracker.budget import set_budget
from finance_tracker.category import Category
from finance_tracker.gui.main_window import MainWindow


def test_main_window_contains_budgets_tab(qtbot) -> None:
    """Verify that the main window contains a Budgets tab."""
    window = MainWindow()
    qtbot.addWidget(window)

    tab_names = [
        window.tab_widget.tabText(index)
        for index in range(window.tab_widget.count())
    ]

    assert "Budgets" in tab_names


def test_budget_table_has_expected_columns_and_no_initial_rows(qtbot) -> None:
    """Verify the columns and empty state of the budget table."""
    window = MainWindow()
    qtbot.addWidget(window)

    table = window.findChild(QTableWidget, "budget_table")

    assert table is not None
    assert table.columnCount() == 7
    assert table.rowCount() == 0

    headers = [
        table.horizontalHeaderItem(column).text()
        for column in range(table.columnCount())
    ]

    assert headers == [
        "Month",
        "Category",
        "Limit",
        "Spent",
        "Remaining",
        "Usage",
        "Status",
    ]


def test_budget_overview_updates_after_account_refresh(
    qtbot,
    analysis_account,
) -> None:
    """Verify that the overview displays month-specific budget values."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.account = analysis_account

    assert hasattr(window, "budget_tracker")

    set_budget(
        window.budget_tracker,
        category=Category.FOOD,
        monthly_limit=300.00,
        month="2026-09",
    )
    window._refresh_transaction_table()

    table = window.findChild(QTableWidget, "budget_table")

    assert table is not None
    assert table.rowCount() == 1

    actual_values = [
        table.item(0, column).text()
        for column in range(table.columnCount())
    ]

    assert actual_values == [
        "2026-09",
        "Food",
        "300.00",
        "195.00",
        "105.00",
        "65.00%",
        "Within budget",
    ]