"""Test the monthly summary table of the financial dashboard."""

from PySide6.QtWidgets import QTableWidget

from finance_tracker.gui.main_window import MainWindow


def test_dashboard_contains_monthly_summary_table(qtbot) -> None:
    """Verify that the dashboard contains the monthly summary table."""
    window = MainWindow()
    qtbot.addWidget(window)

    table = window.findChild(
        QTableWidget,
        "monthly_summary_table",
    )

    assert table is not None
    assert table.columnCount() == 4

    headers = [
        table.horizontalHeaderItem(column).text()
        for column in range(table.columnCount())
    ]

    assert headers == ["Month", "Income", "Expenses", "Balance"]


def test_monthly_summary_table_is_empty_for_new_account(qtbot) -> None:
    """Verify that an empty account has no monthly summary rows."""
    window = MainWindow()
    qtbot.addWidget(window)

    table = window.findChild(
        QTableWidget,
        "monthly_summary_table",
    )

    assert table is not None
    assert table.rowCount() == 0


def test_monthly_summary_updates_after_account_refresh(
    qtbot,
    analysis_account,
) -> None:
    """Verify monthly values and totals after refreshing the account."""
    window = MainWindow()
    qtbot.addWidget(window)

    window.account = analysis_account
    window._refresh_transaction_table()

    table = window.findChild(
        QTableWidget,
        "monthly_summary_table",
    )

    assert table is not None
    assert table.rowCount() == 2

    actual_rows = [
        [
            table.item(row, column).text()
            for column in range(table.columnCount())
        ]
        for row in range(table.rowCount())
    ]

    assert actual_rows == [
        ["2026-08", "500.00", "80.00", "420.00"],
        ["2026-09", "3000.00", "1155.00", "1845.00"],
    ]

    assert window.income_total_label.text() == "3500.00"
    assert window.expense_total_label.text() == "1235.00"
    assert window.balance_label.text() == "2265.00"