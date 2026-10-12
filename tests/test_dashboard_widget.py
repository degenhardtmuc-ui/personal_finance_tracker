"""Test the standalone dashboard component and its window integration."""

from PySide6.QtWidgets import QTableWidget, QWidget

from finance_tracker.account import create_account
from finance_tracker.gui.dashboard_widget import DashboardWidget
from finance_tracker.gui.main_window import MainWindow


def table_rows(table: QTableWidget) -> list[list[str]]:
    """Return the displayed table values as rows of strings."""
    return [
        [table.item(row, column).text() for column in range(table.columnCount())]
        for row in range(table.rowCount())
    ]


def test_dashboard_widget_starts_with_empty_values(qtbot) -> None:
    """Verify that the dashboard works without a main window."""
    dashboard = DashboardWidget()
    qtbot.addWidget(dashboard)

    assert isinstance(dashboard, QWidget)
    assert dashboard.income_total_label.text() == "0.00"
    assert dashboard.expense_total_label.text() == "0.00"
    assert dashboard.balance_label.text() == "0.00"
    assert dashboard.monthly_summary_table.rowCount() == 0
    assert dashboard.category_breakdown_table.rowCount() == 0


def test_dashboard_widget_refreshes_from_account(qtbot, analysis_account) -> None:
    """Verify totals and both summaries using existing domain data."""
    dashboard = DashboardWidget()
    qtbot.addWidget(dashboard)

    dashboard.refresh(analysis_account)

    assert dashboard.income_total_label.text() == "3500.00"
    assert dashboard.expense_total_label.text() == "1235.00"
    assert dashboard.balance_label.text() == "2265.00"
    assert table_rows(dashboard.monthly_summary_table) == [
        ["2026-08", "500.00", "80.00", "420.00"],
        ["2026-09", "3000.00", "1155.00", "1845.00"],
    ]
    assert table_rows(dashboard.category_breakdown_table) == [
        ["Housing", "900.00"],
        ["Food", "275.00"],
        ["Transport", "60.00"],
    ]


def test_dashboard_widget_replaces_previous_display(qtbot, analysis_account) -> None:
    """Verify that loading an empty account removes stale display values."""
    dashboard = DashboardWidget()
    qtbot.addWidget(dashboard)
    dashboard.refresh(analysis_account)

    dashboard.refresh(create_account("Empty account"))

    assert dashboard.income_total_label.text() == "0.00"
    assert dashboard.expense_total_label.text() == "0.00"
    assert dashboard.balance_label.text() == "0.00"
    assert dashboard.monthly_summary_table.rowCount() == 0
    assert dashboard.category_breakdown_table.rowCount() == 0


def test_dashboard_widget_refresh_does_not_duplicate_rows(qtbot, analysis_account) -> None:
    """Verify that repeated refreshes preserve the same summary rows."""
    dashboard = DashboardWidget()
    qtbot.addWidget(dashboard)
    dashboard.refresh(analysis_account)
    expected_months = table_rows(dashboard.monthly_summary_table)
    expected_categories = table_rows(dashboard.category_breakdown_table)

    dashboard.refresh(analysis_account)

    assert table_rows(dashboard.monthly_summary_table) == expected_months
    assert table_rows(dashboard.category_breakdown_table) == expected_categories


def test_main_window_uses_dashboard_widget(qtbot, analysis_account) -> None:
    """Verify that the window delegates account updates to its dashboard."""
    window = MainWindow()
    qtbot.addWidget(window)
    dashboard = window.dashboard_widget

    assert isinstance(dashboard, DashboardWidget)
    dashboard_index = window.tab_widget.indexOf(dashboard)
    assert dashboard_index >= 0
    assert window.tab_widget.tabText(dashboard_index) == "Dashboard"

    window.account = analysis_account
    window._refresh_transaction_table()

    assert dashboard.balance_label.text() == "2265.00"
    assert table_rows(dashboard.category_breakdown_table)[0] == ["Housing", "900.00"]