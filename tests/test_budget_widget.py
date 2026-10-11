"""Test the standalone budget widget and its main-window integration."""

import pytest

from PySide6.QtWidgets import QApplication, QTableWidget

from finance_tracker.account import create_account
from finance_tracker.budget import create_budget_tracker
from finance_tracker.gui.budget_widget import BudgetWidget
from finance_tracker.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for the widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_budget_widget_contains_overview_table(application):
    """Expose the existing seven-column budget overview."""
    widget = BudgetWidget()

    try:
        assert widget.objectName() == "budget_widget"
        assert isinstance(widget.budget_table, QTableWidget)
        assert widget.budget_table.columnCount() == 7

        headers = [
            widget.budget_table.horizontalHeaderItem(column).text()
            for column in range(7)
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
    finally:
        widget.close()
        widget.deleteLater()


def test_budget_widget_refresh_clears_old_rows(application):
    """Remove outdated rows when refreshing with an empty tracker."""
    widget = BudgetWidget()

    try:
        widget.budget_table.setRowCount(1)

        widget.refresh(
            create_budget_tracker(),
            create_account("Test account"),
        )

        assert widget.budget_table.rowCount() == 0
    finally:
        widget.close()
        widget.deleteLater()


def test_budget_buttons_emit_requests(application):
    """Notify the owner when the user requests a budget operation."""
    widget = BudgetWidget()
    requests = []

    try:
        widget.set_budget_requested.connect(
            lambda: requests.append("set")
        )
        widget.save_budgets_requested.connect(
            lambda: requests.append("save")
        )
        widget.load_budgets_requested.connect(
            lambda: requests.append("load")
        )

        widget.set_budget_button.click()
        widget.save_budgets_button.click()
        widget.load_budgets_button.click()

        assert requests == ["set", "save", "load"]
    finally:
        widget.close()
        widget.deleteLater()


def test_main_window_uses_standalone_budget_widget(application):
    """Embed the budget widget and preserve existing table access."""
    window = MainWindow()

    try:
        assert isinstance(window.budget_widget, BudgetWidget)
        assert window.budget_table is window.budget_widget.budget_table

        index = window.tab_widget.indexOf(window.budget_widget)
        assert index >= 0
        assert window.tab_widget.tabText(index) == "Budgets"
    finally:
        window.close()
        window.deleteLater()