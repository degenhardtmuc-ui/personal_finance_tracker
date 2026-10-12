"""Test monthly income/expense charts and main-window integration."""

import pytest

from PySide6.QtWidgets import QApplication

from finance_tracker.account import add_transaction, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.gui.monthly_chart import MonthlyChartWidget


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for chart tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def add_test_transaction(
    account: dict,
    description: str,
    amount: float,
    transaction_type: TransactionType,
    category: Category,
    date: str,
) -> None:
    """Add a transaction using the existing domain functions."""
    from finance_tracker.transaction import create_transaction

    add_transaction(
        account,
        create_transaction(
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            date=date,
        ),
    )


def test_empty_monthly_chart_displays_message(application):
    """Show an understandable empty state without bars."""
    widget = MonthlyChartWidget()

    try:
        widget.refresh(create_account("Empty account"))

        assert len(widget.axes.patches) == 0
        assert "No transactions yet." in [
            text.get_text()
            for text in widget.axes.texts
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_monthly_chart_displays_sorted_income_and_expenses(application):
    """Display separate monthly totals in chronological order."""
    account = create_account("Test account")

    # Insert October before September to verify sorting.
    add_test_transaction(
        account,
        "October salary",
        1000,
        TransactionType.INCOME,
        Category.SALARY,
        "2026-10-01",
    )
    add_test_transaction(
        account,
        "October groceries",
        40,
        TransactionType.EXPENSE,
        Category.FOOD,
        "2026-10-12",
    )
    add_test_transaction(
        account,
        "September salary",
        900,
        TransactionType.INCOME,
        Category.SALARY,
        "2026-09-01",
    )
    add_test_transaction(
        account,
        "September rent",
        300,
        TransactionType.EXPENSE,
        Category.HOUSING,
        "2026-09-02",
    )
    add_test_transaction(
        account,
        "September groceries",
        25,
        TransactionType.EXPENSE,
        Category.FOOD,
        "2026-09-03",
    )

    widget = MonthlyChartWidget()

    try:
        widget.refresh(account)

        assert [
            tick.get_text()
            for tick in widget.axes.get_xticklabels()
        ] == ["2026-09", "2026-10"]

        containers = {
            container.get_label(): container
            for container in widget.axes.containers
        }

        assert [
            bar.get_height()
            for bar in containers["Income"]
        ] == [900.0, 1000.0]

        assert [
            bar.get_height()
            for bar in containers["Expenses"]
        ] == [325.0, 40.0]

        assert widget.axes.get_xlabel() == "Month"
        assert widget.axes.get_ylabel() == "Amount"
    finally:
        widget.close()
        widget.deleteLater()


def test_monthly_chart_refresh_removes_previous_bars(application):
    """Remove old bars when switching to an empty account."""
    account = create_account("Account with income")

    add_test_transaction(
        account,
        "Salary",
        1000,
        TransactionType.INCOME,
        Category.SALARY,
        "2026-10-01",
    )

    widget = MonthlyChartWidget()

    try:
        widget.refresh(account)
        assert len(widget.axes.patches) == 2

        widget.refresh(create_account("Empty account"))

        assert len(widget.axes.patches) == 0
        assert "No transactions yet." in [
            text.get_text()
            for text in widget.axes.texts
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_main_window_refreshes_monthly_chart_after_transaction(application):
    """Update the embedded monthly chart after an expense is added."""
    window = MainWindow()

    try:
        chart = window.monthly_chart
        assert isinstance(chart, MonthlyChartWidget)

        index = window.chart_tabs.indexOf(chart)
        assert index >= 0
        assert window.chart_tabs.tabText(index) == "Monthly"

        window.description_input.setText("Groceries")
        window.amount_input.setText("25")
        window.transaction_type_input.setCurrentText("Expense")
        window.category_input.setCurrentText("Food")

        window.add_transaction_button.click()

        containers = {
            container.get_label(): container
            for container in chart.axes.containers
        }

        assert [
            bar.get_height()
            for bar in containers["Expenses"]
        ] == [25.0]
    finally:
        window.close()
        window.deleteLater()