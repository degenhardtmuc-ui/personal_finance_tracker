"""Test combined transaction filters and original-entry mapping."""

import pytest

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication

from finance_tracker.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for filter tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def add_expense(window, description, amount, category, date):
    """Add an expense through the existing form."""
    window.description_input.setText(description)
    window.amount_input.setText(amount)
    window.transaction_type_input.setCurrentText("Expense")
    window.category_input.setCurrentText(category)
    window.date_input.setDate(QDate.fromString(date, "yyyy-MM-dd"))
    window.add_transaction_button.click()


def add_sample_expenses(window):
    """Create transactions across two months and categories."""
    add_expense(window, "September groceries", "25", "Food", "2026-09-12")
    add_expense(window, "October groceries", "40", "Food", "2026-10-12")
    add_expense(window, "October bus", "10", "Transport", "2026-10-13")


def visible_descriptions(window):
    """Read the descriptions currently displayed in the table."""
    return [
        window.transaction_table.item(row, 1).text()
        for row in range(window.transaction_table.rowCount())
    ]


def test_filter_controls_start_with_all_values(application):
    """Show the complete account before filters are selected."""
    window = MainWindow()

    try:
        assert window.month_filter.currentText() == "All months"
        assert window.category_filter.currentText() == "All categories"
    finally:
        window.close()
        window.deleteLater()


def test_month_filter_lists_recorded_months_and_filters_rows(application):
    """Populate sorted months and display only the chosen month."""
    window = MainWindow()

    try:
        add_sample_expenses(window)

        assert [
            window.month_filter.itemText(index)
            for index in range(window.month_filter.count())
        ] == ["All months", "2026-09", "2026-10"]

        window.month_filter.setCurrentText("2026-10")

        assert visible_descriptions(window) == [
            "October groceries",
            "October bus",
        ]
        assert len(window.account["transactions"]) == 3
        assert window.expense_total_label.text() == "75.00"
    finally:
        window.close()
        window.deleteLater()


def test_category_month_and_search_combine(application):
    """Require transactions to match every active filter."""
    window = MainWindow()

    try:
        add_sample_expenses(window)

        window.category_filter.setCurrentText("Food")
        assert visible_descriptions(window) == [
            "September groceries",
            "October groceries",
        ]

        window.month_filter.setCurrentText("2026-10")
        window.search_input.setText("GROCERIES")

        assert visible_descriptions(window) == ["October groceries"]

        window.search_input.clear()
        window.month_filter.setCurrentText("All months")
        window.category_filter.setCurrentText("All categories")

        assert window.transaction_table.rowCount() == 3
    finally:
        window.close()
        window.deleteLater()


def test_editing_filtered_row_updates_original_entry(application):
    """Edit the account entry behind combined filters."""
    window = MainWindow()

    try:
        add_sample_expenses(window)

        window.month_filter.setCurrentText("2026-10")
        window.category_filter.setCurrentText("Transport")
        window.transaction_table.selectRow(0)

        assert window.description_input.text() == "October bus"

        window.amount_input.setText("15")
        window.save_changes_button.click()

        assert window.account["transactions"][0]["amount"] == 25.0
        assert window.account["transactions"][1]["amount"] == 40.0
        assert window.account["transactions"][2]["amount"] == 15.0

        assert visible_descriptions(window) == ["October bus"]
        assert window.transaction_table.item(0, 4).text() == "15.00"
    finally:
        window.close()
        window.deleteLater()


def test_filter_change_ends_edit_without_saving(application):
    """Discard unsaved edits when the category filter changes."""
    window = MainWindow()

    try:
        add_sample_expenses(window)

        window.transaction_table.selectRow(0)
        window.amount_input.setText("99")

        window.category_filter.setCurrentText("Transport")

        assert window.account["transactions"][0]["amount"] == 25.0
        assert window.amount_input.text() == ""
        assert not window.save_changes_button.isEnabled()
        assert not window.delete_transaction_button.isEnabled()
        assert window.add_transaction_button.isEnabled()

        assert visible_descriptions(window) == ["October bus"]
    finally:
        window.close()
        window.deleteLater()