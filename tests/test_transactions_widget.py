"""Test the standalone transactions interface and its integration."""

import pytest

from PySide6.QtWidgets import QApplication

from finance_tracker.account import create_account
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.gui.transactions_widget import TransactionsWidget


@pytest.fixture(scope="module")
def application():
    """Provide an application instance for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_transactions_widget_contains_expected_table(application):
    """Display the existing six transaction columns."""
    widget = TransactionsWidget()

    try:
        assert widget.objectName() == "transactions_widget"

        table = widget.transaction_table
        headers = [
            table.horizontalHeaderItem(column).text()
            for column in range(table.columnCount())
        ]

        assert headers == [
            "Date",
            "Description",
            "Type",
            "Category",
            "Amount",
            "Tags",
        ]
    finally:
        widget.close()
        widget.deleteLater()


def test_transactions_widget_refresh_removes_old_rows(application):
    """Clear outdated rows when displaying an empty account."""
    widget = TransactionsWidget()

    try:
        widget.transaction_table.setRowCount(1)
        widget.refresh(create_account("Test account"))

        assert widget.transaction_table.rowCount() == 0
    finally:
        widget.close()
        widget.deleteLater()


def test_transaction_buttons_emit_operation_requests(application):
    """Notify the owner when transaction or file buttons are clicked."""
    widget = TransactionsWidget()
    requests = []

    try:
        widget.add_transaction_requested.connect(
            lambda: requests.append("add")
        )
        widget.save_json_requested.connect(
            lambda: requests.append("save")
        )
        widget.load_json_requested.connect(
            lambda: requests.append("load")
        )
        widget.import_csv_requested.connect(
            lambda: requests.append("import")
        )
        widget.export_csv_requested.connect(
            lambda: requests.append("export")
        )

        widget.add_transaction_button.click()
        widget.save_json_button.click()
        widget.load_json_button.click()
        widget.import_csv_button.click()
        widget.export_csv_button.click()

        assert requests == ["add", "save", "load", "import", "export"]
    finally:
        widget.close()
        widget.deleteLater()


def test_main_window_uses_transactions_widget(application):
    """Embed the component and preserve existing input access."""
    window = MainWindow()

    try:
        widget = window.transactions_widget
        assert isinstance(widget, TransactionsWidget)
        assert window.transaction_table is widget.transaction_table
        assert window.description_input is widget.description_input
        assert window.amount_input is widget.amount_input

        index = window.tab_widget.indexOf(widget)
        assert index >= 0
        assert window.tab_widget.tabText(index) == "Transactions"
    finally:
        window.close()
        window.deleteLater()