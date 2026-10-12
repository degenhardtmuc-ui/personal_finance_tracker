"""Test shared status messages and transaction/budget integration."""

import pytest

from PySide6.QtWidgets import QApplication, QLabel

from finance_tracker.gui.main_window import MainWindow
from finance_tracker.gui.status import show_error, show_success


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for status tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_show_success_sets_text_and_state(application):
    """Mark a message as successful."""
    label = QLabel()

    try:
        show_success(label, "Account saved successfully.")

        assert label.text() == "Account saved successfully."
        assert label.property("status") == "success"
    finally:
        label.deleteLater()


def test_show_error_replaces_previous_success(application):
    """Replace a success message with an error state."""
    label = QLabel()

    try:
        show_success(label, "Saved.")
        show_error(label, "File could not be loaded.")

        assert label.text() == "File could not be loaded."
        assert label.property("status") == "error"
    finally:
        label.deleteLater()


def test_valid_transaction_sets_success_status(application):
    """Show success after storing a valid transaction."""
    window = MainWindow()

    try:
        window.description_input.setText("Test income")
        window.amount_input.setText("100")
        window.transaction_type_input.setCurrentText("Income")
        window.category_input.setCurrentText("Salary")

        window.add_transaction_button.click()

        assert len(window.account["transactions"]) == 1
        assert (
            window.transaction_status_label.text()
            == "Transaction added successfully."
        )
        assert (
            window.transaction_status_label.property("status")
            == "success"
        )
    finally:
        window.close()
        window.deleteLater()


def test_invalid_transaction_sets_error_status(application):
    """Show an error without storing an invalid transaction."""
    window = MainWindow()

    try:
        window.description_input.setText("Invalid transaction")
        window.amount_input.setText("abc")

        window.add_transaction_button.click()

        assert window.account["transactions"] == []
        assert (
            window.transaction_status_label.text()
            == "Amount must be a valid number."
        )
        assert (
            window.transaction_status_label.property("status")
            == "error"
        )
    finally:
        window.close()
        window.deleteLater()


def test_budget_status_changes_from_error_to_success(application):
    """Clear the error state after correcting the budget input."""
    window = MainWindow()

    try:
        window.budget_category_input.setCurrentText("Food")
        window.budget_limit_input.setText("abc")

        window.set_budget_button.click()

        assert window.budget_tracker["budgets"] == []
        assert window.budget_status_label.property("status") == "error"

        window.budget_limit_input.setText("100")
        window.set_budget_button.click()

        assert len(window.budget_tracker["budgets"]) == 1
        assert (
            window.budget_status_label.text()
            == "Budget saved for this session."
        )
        assert window.budget_status_label.property("status") == "success"
    finally:
        window.close()
        window.deleteLater()