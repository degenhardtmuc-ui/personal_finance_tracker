"""Test budget limit/spending charts and main-window integration."""

import pytest

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication

from finance_tracker.account import add_transaction, create_account
from finance_tracker.budget import create_budget_tracker, set_budget
from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.budget_chart import BudgetChartWidget
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.transaction import create_transaction


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for chart tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_empty_budget_chart_displays_message(application):
    """Show an understandable empty state when no budgets exist."""
    widget = BudgetChartWidget()

    try:
        widget.refresh(
            create_budget_tracker(),
            create_account("Empty account"),
        )

        assert len(widget.axes.patches) == 0
        assert "No budgets yet." in [
            text.get_text()
            for text in widget.axes.texts
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_budget_chart_displays_limits_and_matching_expenses(application):
    """Match spending by category and month, excluding income."""
    account = create_account("Test account")
    tracker = create_budget_tracker()

    # Insert October first to verify chronological ordering.
    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=100,
        month="2026-10",
    )
    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=80,
        month="2026-09",
    )

    transactions = [
        ("September food", 30, TransactionType.EXPENSE,
         Category.FOOD, "2026-09-12"),
        ("October food", 120, TransactionType.EXPENSE,
         Category.FOOD, "2026-10-12"),
        ("October bus", 10, TransactionType.EXPENSE,
         Category.TRANSPORT, "2026-10-12"),
        ("Food refund", 5, TransactionType.INCOME,
         Category.FOOD, "2026-10-12"),
    ]

    for description, amount, transaction_type, category, date in transactions:
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

    widget = BudgetChartWidget()

    try:
        widget.refresh(tracker, account)

        assert [
            tick.get_text()
            for tick in widget.axes.get_yticklabels()
        ] == [
            "2026-09 · Food",
            "2026-10 · Food",
        ]

        containers = {
            container.get_label(): container
            for container in widget.axes.containers
        }

        assert [
            bar.get_width()
            for bar in containers["Limit"]
        ] == [80.0, 100.0]

        assert [
            bar.get_width()
            for bar in containers["Spent"]
        ] == [30.0, 120.0]

        assert widget.axes.get_xlabel() == "Amount"
    finally:
        widget.close()
        widget.deleteLater()


def test_budget_chart_refresh_removes_previous_bars(application):
    """Remove outdated bars after switching to an empty tracker."""
    tracker = create_budget_tracker()
    account = create_account("Test account")

    set_budget(
        tracker,
        category=Category.FOOD,
        monthly_limit=100,
        month="2026-10",
    )

    widget = BudgetChartWidget()

    try:
        widget.refresh(tracker, account)
        assert len(widget.axes.patches) == 2

        widget.refresh(create_budget_tracker(), account)

        assert len(widget.axes.patches) == 0
        assert "No budgets yet." in [
            text.get_text()
            for text in widget.axes.texts
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_main_window_refreshes_budget_chart_after_changes(application):
    """Update the chart after setting a budget and adding an expense."""
    window = MainWindow()

    try:
        chart = window.budget_chart
        assert isinstance(chart, BudgetChartWidget)

        index = window.chart_tabs.indexOf(chart)
        assert index >= 0
        assert window.chart_tabs.tabText(index) == "Budgets"

        window.budget_category_input.setCurrentText("Food")
        window.budget_limit_input.setText("100")
        window.budget_month_input.setDate(QDate(2026, 10, 1))

        window.set_budget_button.click()

        containers = {
            container.get_label(): container
            for container in chart.axes.containers
        }
        assert [
            bar.get_width()
            for bar in containers["Limit"]
        ] == [100.0]

        window.description_input.setText("Groceries")
        window.amount_input.setText("25")
        window.transaction_type_input.setCurrentText("Expense")
        window.category_input.setCurrentText("Food")
        window.date_input.setDate(QDate(2026, 10, 12))

        window.add_transaction_button.click()

        containers = {
            container.get_label(): container
            for container in chart.axes.containers
        }
        assert [
            bar.get_width()
            for bar in containers["Spent"]
        ] == [25.0]
    finally:
        window.close()
        window.deleteLater()