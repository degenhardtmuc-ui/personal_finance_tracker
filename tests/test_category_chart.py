"""Test the expense category chart and main-window integration."""

import pytest

from PySide6.QtWidgets import QApplication

from finance_tracker.account import add_transaction, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.category_chart import CategoryChartWidget
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.transaction import create_transaction


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for chart tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_empty_chart_displays_no_expenses_message(application):
    """Display an understandable empty state without expense bars."""
    widget = CategoryChartWidget()

    try:
        widget.refresh(create_account("Empty account"))

        assert len(widget.axes.patches) == 0

        messages = [text.get_text() for text in widget.axes.texts]
        assert "No expenses yet." in messages
    finally:
        widget.close()
        widget.deleteLater()


def test_chart_displays_expense_totals_by_category(application):
    """Sum expenses per category and exclude income."""
    account = create_account("Test account")

    transactions = [
        ("Groceries", 25, TransactionType.EXPENSE, Category.FOOD),
        ("Lunch", 15, TransactionType.EXPENSE, Category.FOOD),
        ("Bus", 10, TransactionType.EXPENSE, Category.TRANSPORT),
        ("Salary", 1000, TransactionType.INCOME, Category.SALARY),
    ]

    for description, amount, transaction_type, category in transactions:
        add_transaction(
            account,
            create_transaction(
                description=description,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                date="2026-10-12",
            ),
        )

    widget = CategoryChartWidget()

    try:
        widget.refresh(account)

        labels = [
            tick.get_text()
            for tick in widget.axes.get_yticklabels()
        ]
        amounts = [
            bar.get_width()
            for bar in widget.axes.patches
        ]

        displayed_totals = dict(zip(labels, amounts))

        assert displayed_totals == {
            "Food": 40.0,
            "Transport": 10.0,
        }
        assert widget.axes.get_xlabel() == "Amount"
    finally:
        widget.close()
        widget.deleteLater()


def test_chart_refresh_replaces_previous_expenses(application):
    """Remove outdated bars after switching to an empty account."""
    account = create_account("Account with expenses")

    add_transaction(
        account,
        create_transaction(
            description="Groceries",
            amount=25,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-10-12",
        ),
    )

    widget = CategoryChartWidget()

    try:
        widget.refresh(account)
        assert len(widget.axes.patches) == 1

        widget.refresh(create_account("Empty account"))

        assert len(widget.axes.patches) == 0
        assert "No expenses yet." in [
            text.get_text()
            for text in widget.axes.texts
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_main_window_refreshes_chart_after_transaction(application):
    """Embed the category chart and update it after adding an expense."""
    window = MainWindow()

    try:
        chart = window.category_chart
        assert isinstance(chart, CategoryChartWidget)

        charts_index = window.tab_widget.indexOf(window.chart_tabs)
        assert charts_index >= 0
        assert window.tab_widget.tabText(charts_index) == "Charts"

        category_index = window.chart_tabs.indexOf(chart)
        assert category_index >= 0
        assert window.chart_tabs.tabText(category_index) == "Categories"

        window.description_input.setText("Groceries")
        window.amount_input.setText("25")
        window.transaction_type_input.setCurrentText("Expense")
        window.category_input.setCurrentText("Food")

        window.add_transaction_button.click()

        amounts = [
            bar.get_width()
            for bar in chart.axes.patches
        ]

        assert amounts == [25.0]
    finally:
        window.close()
        window.deleteLater()