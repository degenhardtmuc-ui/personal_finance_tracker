"""Verify combined transaction editing, filtering, and file workflows."""

import pytest

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
)

from finance_tracker.gui.main_window import MainWindow
from finance_tracker.json_storage import load_account, save_account


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for workflow tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def add_expense(window, description, amount, date):
    """Add a Food expense through the existing GUI."""
    window.description_input.setText(description)
    window.amount_input.setText(amount)
    window.transaction_type_input.setCurrentText("Expense")
    window.category_input.setCurrentText("Food")
    window.date_input.setDate(
        QDate.fromString(date, "yyyy-MM-dd"),
    )
    window.add_transaction_button.click()


def test_filtered_edit_saves_complete_account(
    application,
    monkeypatch,
    tmp_path,
):
    """Persist a filtered edit while retaining hidden transactions."""
    window = MainWindow()
    destination = tmp_path / "account.json"

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(destination), ""),
    )

    try:
        add_expense(window, "September groceries", "25", "2026-09-12")
        add_expense(window, "October groceries", "40", "2026-10-12")

        window.month_filter.setCurrentText("2026-10")
        window.transaction_table.selectRow(0)

        window.amount_input.setText("45")
        window.save_changes_button.click()
        window.save_json_button.click()

        restored = load_account(destination)

        assert len(restored["transactions"]) == 2
        assert restored["transactions"][0]["amount"] == 25.0
        assert restored["transactions"][1]["amount"] == 45.0

        assert window.transaction_table.rowCount() == 1
        assert window.expense_total_label.text() == "70.00"
    finally:
        window.close()
        window.deleteLater()


def test_deleting_last_entry_in_selected_month_resets_month_filter(
    application,
    monkeypatch,
):
    """Remove an obsolete month option and rebuild remaining row mapping."""
    window = MainWindow()

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    try:
        add_expense(window, "September groceries", "25", "2026-09-12")
        add_expense(window, "October groceries", "40", "2026-10-12")

        window.month_filter.setCurrentText("2026-10")
        window.transaction_table.selectRow(0)
        window.delete_transaction_button.click()

        assert window.month_filter.currentText() == "All months"
        assert [
            window.month_filter.itemText(index)
            for index in range(window.month_filter.count())
        ] == ["All months", "2026-09"]

        assert window.transaction_table.rowCount() == 1
        assert (
            window.transaction_table.item(0, 1).text()
            == "September groceries"
        )

        window.transaction_table.selectRow(0)
        assert window.description_input.text() == "September groceries"

        window.amount_input.setText("30")
        window.save_changes_button.click()

        assert len(window.account["transactions"]) == 1
        assert window.account["transactions"][0]["amount"] == 30.0
    finally:
        window.close()
        window.deleteLater()


def test_loading_account_resets_edit_and_rebuilds_filtered_mapping(
    application,
    monkeypatch,
    tmp_path,
):
    """Replace an account safely while a transaction is being edited."""
    window = MainWindow()
    destination = tmp_path / "replacement.json"

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(destination), ""),
    )

    try:
        add_expense(window, "Groceries", "25", "2026-09-12")
        add_expense(window, "Lunch", "10", "2026-10-12")

        # Save replacement data containing only the Lunch transaction.
        save_account(
            {
                "name": "Replacement account",
                "transactions": [window.account["transactions"][1]],
            },
            destination,
        )

        window.search_input.setText("Lunch")
        window.transaction_table.selectRow(0)
        window.amount_input.setText("99")

        window.load_json_button.click()

        assert len(window.account["transactions"]) == 1
        assert window.account["transactions"][0]["amount"] == 10.0

        assert window.search_input.text() == "Lunch"
        assert window.amount_input.text() == ""
        assert not window.save_changes_button.isEnabled()
        assert not window.delete_transaction_button.isEnabled()

        window.transaction_table.selectRow(0)
        assert window.description_input.text() == "Lunch"

        window.amount_input.setText("15")
        window.save_changes_button.click()

        assert window.account["transactions"][0]["amount"] == 15.0
        assert window.expense_total_label.text() == "15.00"
    finally:
        window.close()
        window.deleteLater()