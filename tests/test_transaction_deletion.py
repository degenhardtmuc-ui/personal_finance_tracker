"""Test confirmed transaction deletion and financial view updates."""

import pytest

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QMessageBox

from finance_tracker.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def add_expense(window, description, amount):
    """Add a Food expense through the transaction form."""
    window.description_input.setText(description)
    window.amount_input.setText(amount)
    window.transaction_type_input.setCurrentText("Expense")
    window.category_input.setCurrentText("Food")
    window.date_input.setDate(QDate(2026, 10, 12))
    window.add_transaction_button.click()


def test_delete_button_starts_disabled(application):
    """Require a selected transaction before deletion."""
    window = MainWindow()

    try:
        assert not window.delete_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_confirmed_deletion_updates_all_views(application, monkeypatch):
    """Delete the selected entry and refresh dependent financial views."""
    window = MainWindow()
    confirmations = []

    def confirm(parent, title, text, buttons, default_button):
        """Record the confirmation request and accept deletion."""
        confirmations.append(
            (title, text, buttons, default_button)
        )
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "question", confirm)

    try:
        window.budget_category_input.setCurrentText("Food")
        window.budget_limit_input.setText("100")
        window.budget_month_input.setDate(QDate(2026, 10, 1))
        window.set_budget_button.click()

        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")

        window.transaction_table.selectRow(0)
        assert window.delete_transaction_button.isEnabled()

        window.delete_transaction_button.click()

        assert len(confirmations) == 1
        title, text, buttons, default_button = confirmations[0]

        assert "Groceries" in text
        assert buttons == (
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )
        assert default_button == QMessageBox.StandardButton.No

        assert len(window.account["transactions"]) == 1
        assert window.account["transactions"][0]["description"] == "Lunch"

        assert window.transaction_table.rowCount() == 1
        assert window.transaction_table.item(0, 1).text() == "Lunch"

        assert window.expense_total_label.text() == "10.00"
        assert window.balance_label.text() == "-10.00"
        assert window.budget_table.item(0, 3).text() == "10.00"

        assert [
            bar.get_width()
            for bar in window.category_chart.axes.patches
        ] == [10.0]

        monthly = {
            container.get_label(): container
            for container in window.monthly_chart.axes.containers
        }
        assert [
            bar.get_height()
            for bar in monthly["Expenses"]
        ] == [10.0]

        budgets = {
            container.get_label(): container
            for container in window.budget_chart.axes.containers
        }
        assert [
            bar.get_width()
            for bar in budgets["Spent"]
        ] == [10.0]

        assert window.transaction_status_label.property("status") == "success"
        assert not window.delete_transaction_button.isEnabled()
        assert not window.save_changes_button.isEnabled()
        assert window.add_transaction_button.isEnabled()
        assert window.transaction_table.selectedItems() == []
    finally:
        window.close()
        window.deleteLater()


def test_cancelled_deletion_preserves_data_and_editing(
    application,
    monkeypatch,
):
    """Keep the transaction and unsaved form edits after declining."""
    window = MainWindow()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    try:
        add_expense(window, "Groceries", "25")
        original = window.account["transactions"][0].copy()

        window.transaction_table.selectRow(0)
        window.description_input.setText("Unsaved edit")
        window.amount_input.setText("40")

        window.delete_transaction_button.click()

        assert window.account["transactions"][0] == original
        assert window.transaction_table.rowCount() == 1
        assert window.description_input.text() == "Unsaved edit"
        assert window.amount_input.text() == "40"

        assert window.delete_transaction_button.isEnabled()
        assert window.save_changes_button.isEnabled()
        assert not window.add_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()


def test_deleting_last_transaction_restores_empty_charts(
    application,
    monkeypatch,
):
    """Clear transaction views after deleting the last stored entry."""
    window = MainWindow()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    try:
        add_expense(window, "Groceries", "25")
        window.transaction_table.selectRow(0)
        window.delete_transaction_button.click()

        assert window.account["transactions"] == []
        assert window.transaction_table.rowCount() == 0
        assert window.expense_total_label.text() == "0.00"
        assert window.balance_label.text() == "0.00"

        assert len(window.category_chart.axes.patches) == 0
        assert "No expenses yet." in [
            text.get_text()
            for text in window.category_chart.axes.texts
        ]

        assert len(window.monthly_chart.axes.patches) == 0
        assert "No transactions yet." in [
            text.get_text()
            for text in window.monthly_chart.axes.texts
        ]
    finally:
        window.close()
        window.deleteLater()