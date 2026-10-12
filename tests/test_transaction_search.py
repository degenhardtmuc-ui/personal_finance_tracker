"""Test description search and transaction mapping in filtered views."""

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


def test_search_matches_description_case_insensitively(application):
    """Filter descriptions without changing stored account data."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")
        add_expense(window, "Weekly groceries", "40")

        window.search_input.setText("  GROCERIES  ")

        assert window.transaction_table.rowCount() == 2
        assert [
            window.transaction_table.item(row, 1).text()
            for row in range(2)
        ] == ["Groceries", "Weekly groceries"]

        assert len(window.account["transactions"]) == 3
        assert window.expense_total_label.text() == "75.00"
    finally:
        window.close()
        window.deleteLater()


def test_clearing_search_restores_all_rows(application):
    """Restore the full table after clearing an unmatched query."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")

        window.search_input.setText("No matching description")
        assert window.transaction_table.rowCount() == 0
        assert len(window.account["transactions"]) == 2

        window.search_input.clear()

        assert window.transaction_table.rowCount() == 2
    finally:
        window.close()
        window.deleteLater()


def test_editing_filtered_row_updates_correct_transaction(application):
    """Map a visible row to its original account entry."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")

        window.search_input.setText("Lunch")
        window.transaction_table.selectRow(0)

        assert window.description_input.text() == "Lunch"

        window.amount_input.setText("15")
        window.save_changes_button.click()

        assert window.account["transactions"][0]["description"] == "Groceries"
        assert window.account["transactions"][0]["amount"] == 25.0
        assert window.account["transactions"][1]["description"] == "Lunch"
        assert window.account["transactions"][1]["amount"] == 15.0

        assert window.transaction_table.rowCount() == 1
        assert window.transaction_table.item(0, 4).text() == "15.00"
        assert window.expense_total_label.text() == "40.00"
    finally:
        window.close()
        window.deleteLater()


def test_deleting_filtered_row_removes_correct_transaction(
    application,
    monkeypatch,
):
    """Delete the original account entry behind a filtered row."""
    window = MainWindow()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    try:
        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")

        window.search_input.setText("Lunch")
        window.transaction_table.selectRow(0)
        window.delete_transaction_button.click()

        assert len(window.account["transactions"]) == 1
        assert window.account["transactions"][0]["description"] == "Groceries"
        assert window.account["transactions"][0]["amount"] == 25.0

        assert window.transaction_table.rowCount() == 0
        assert window.expense_total_label.text() == "25.00"

        window.search_input.clear()
        assert window.transaction_table.rowCount() == 1
    finally:
        window.close()
        window.deleteLater()


def test_changing_search_ends_active_edit(application):
    """Reset editing when the visible transaction selection changes."""
    window = MainWindow()

    try:
        add_expense(window, "Groceries", "25")
        add_expense(window, "Lunch", "10")

        window.transaction_table.selectRow(0)
        window.amount_input.setText("99")

        window.search_input.setText("Lunch")

        assert window.account["transactions"][0]["amount"] == 25.0
        assert window.description_input.text() == ""
        assert window.amount_input.text() == ""
        assert not window.save_changes_button.isEnabled()
        assert not window.delete_transaction_button.isEnabled()
        assert window.add_transaction_button.isEnabled()
    finally:
        window.close()
        window.deleteLater()