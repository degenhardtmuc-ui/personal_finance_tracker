"""Test transaction editing and updates of dependent financial views."""

import pytest

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication

from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def add_expense(window: MainWindow, description: str, amount: str) -> None:
    """Add a Food expense through the existing transaction form."""
    window.description_input.setText(description)
    window.amount_input.setText(amount)
    window.transaction_type_input.setCurrentText("Expense")
    window.category_input.setCurrentText("Food")
    window.date_input.setDate(QDate(2026, 10, 12))
    window.tags_input.setText("weekly, food")
    window.add_transaction_button.click()


def test_edit_controls_start_disabled(application):
    """Disable edit actions until a transaction has been selected."""
    window = MainWindow()

    try:
        assert not window.save_changes_button.isEnabled()
        assert not window.cancel_edit_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_selecting_transaction_loads_form(application):
    """Load all transaction fields when a table row is selected."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")

        window.transaction_table.selectRow(0)

        assert window.description_input.text() == "Groceries"
        assert float(window.amount_input.text()) == 25.0
        assert window.transaction_type_input.currentText() == "Expense"
        assert window.category_input.currentText() == "Food"
        assert window.date_input.date() == QDate(2026, 10, 12)

        tags = {
            tag.strip()
            for tag in window.tags_input.text().split(",")
            if tag.strip()
        }
        assert tags == {"weekly", "food"}

        assert window.save_changes_button.isEnabled()
        assert window.cancel_edit_button.isEnabled()
        assert not window.add_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_save_changes_replaces_selected_transaction(application):
    """Replace one transaction and refresh every dependent view."""
    window = MainWindow()

    try:
        window.budget_category_input.setCurrentText("Food")
        window.budget_limit_input.setText("100")
        window.budget_month_input.setDate(QDate(2026, 10, 1))
        window.set_budget_button.click()

        add_expense(window, "Groceries", "25")
        window.transaction_table.selectRow(0)

        window.description_input.setText("Weekly groceries")
        window.amount_input.setText("40")
        window.save_changes_button.click()

        assert len(window.account["transactions"]) == 1

        transaction = window.account["transactions"][0]
        assert transaction["description"] == "Weekly groceries"
        assert transaction["amount"] == 40.0
        assert transaction["category"] == Category.FOOD
        assert transaction["transaction_type"] == TransactionType.EXPENSE

        assert window.transaction_table.item(0, 1).text() == "Weekly groceries"
        assert window.transaction_table.item(0, 4).text() == "40.00"

        assert window.expense_total_label.text() == "40.00"
        assert window.balance_label.text() == "-40.00"
        assert window.budget_table.item(0, 3).text() == "40.00"

        assert [
            bar.get_width()
            for bar in window.category_chart.axes.patches
        ] == [40.0]

        monthly_containers = {
            container.get_label(): container
            for container in window.monthly_chart.axes.containers
        }
        assert [
            bar.get_height()
            for bar in monthly_containers["Expenses"]
        ] == [40.0]

        budget_containers = {
            container.get_label(): container
            for container in window.budget_chart.axes.containers
        }
        assert [
            bar.get_width()
            for bar in budget_containers["Spent"]
        ] == [40.0]

        assert window.transaction_status_label.property("status") == "success"
        assert not window.save_changes_button.isEnabled()
        assert window.add_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_invalid_edit_preserves_original_transaction(application):
    """Keep the original data and remain in edit mode after invalid input."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        original = window.account["transactions"][0].copy()

        window.transaction_table.selectRow(0)
        window.amount_input.setText("abc")
        window.save_changes_button.click()

        assert window.account["transactions"][0] == original
        assert window.transaction_table.item(0, 4).text() == "25.00"
        assert window.transaction_status_label.property("status") == "error"

        assert window.save_changes_button.isEnabled()
        assert not window.add_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_cancel_edit_preserves_data_and_resets_controls(application):
    """Discard form changes without modifying the selected transaction."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        original = window.account["transactions"][0].copy()

        window.transaction_table.selectRow(0)
        window.description_input.setText("Do not save")
        window.amount_input.setText("99")

        window.cancel_edit_button.click()

        assert window.account["transactions"][0] == original
        assert window.description_input.text() == ""
        assert window.amount_input.text() == ""
        assert window.tags_input.text() == ""

        assert not window.save_changes_button.isEnabled()
        assert not window.cancel_edit_button.isEnabled()
        assert window.add_transaction_button.isEnabled()
        assert window.transaction_table.selectedItems() == []
    finally:
        window.close()
        window.deleteLater()