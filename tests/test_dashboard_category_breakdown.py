"""Test the expense category breakdown of the financial dashboard."""

from PySide6.QtWidgets import QTableWidget

from finance_tracker.gui.main_window import MainWindow


def test_dashboard_contains_category_breakdown_table(qtbot) -> None:
    """Verify that the dashboard contains the category expense table."""
    window = MainWindow()
    qtbot.addWidget(window)

    table = window.findChild(
        QTableWidget,
        "category_breakdown_table",
    )

    assert table is not None
    assert table.columnCount() == 2

    headers = [
        table.horizontalHeaderItem(column).text()
        for column in range(table.columnCount())
    ]

    assert headers == ["Category", "Expenses"]


def test_category_breakdown_table_is_empty_for_new_account(qtbot) -> None:
    """Verify that an empty account has no expense category rows."""
    window = MainWindow()
    qtbot.addWidget(window)

    table = window.findChild(
        QTableWidget,
        "category_breakdown_table",
    )

    assert table is not None
    assert table.rowCount() == 0


def test_category_breakdown_updates_after_account_refresh(
    qtbot,
    analysis_account,
) -> None:
    """Verify expense totals by category in descending amount order."""
    window = MainWindow()
    qtbot.addWidget(window)

    window.account = analysis_account
    window._refresh_transaction_table()

    table = window.findChild(
        QTableWidget,
        "category_breakdown_table",
    )

    assert table is not None
    assert table.rowCount() == 3

    actual_rows = [
        [
            table.item(row, column).text()
            for column in range(table.columnCount())
        ]
        for row in range(table.rowCount())
    ]

    assert actual_rows == [
        ["Housing", "900.00"],
        ["Food", "275.00"],
        ["Transport", "60.00"],
    ]