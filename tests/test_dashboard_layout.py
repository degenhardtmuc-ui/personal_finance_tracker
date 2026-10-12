"""Test dashboard totals, spacing, and table space allocation."""

import pytest

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QVBoxLayout,
)

from finance_tracker.gui.dashboard_widget import DashboardWidget


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for layout tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dashboard_totals_use_three_columns(application):
    """Display income, expenses, and balance beside each other."""
    widget = DashboardWidget()

    try:
        grid = widget.findChild(
            QGridLayout,
            "dashboard_totals_grid",
        )

        assert grid is not None

        expected_positions = [
            (widget.income_total_label, 1, 0),
            (widget.expense_total_label, 1, 1),
            (widget.balance_label, 1, 2),
        ]

        for label, expected_row, expected_column in expected_positions:
            index = grid.indexOf(label)

            assert index >= 0
            assert grid.getItemPosition(index) == (
                expected_row,
                expected_column,
                1,
                1,
            )
    finally:
        widget.close()
        widget.deleteLater()


def test_dashboard_layout_has_consistent_spacing(application):
    """Use the same outer margins and spacing as the other tabs."""
    widget = DashboardWidget()

    try:
        layout = widget.layout()
        margins = layout.contentsMargins()

        assert (
            margins.left(),
            margins.top(),
            margins.right(),
            margins.bottom(),
        ) == (20, 20, 20, 20)

        assert layout.spacing() == 16

        grid = widget.findChild(
            QGridLayout,
            "dashboard_totals_grid",
        )

        assert grid is not None
        assert grid.horizontalSpacing() == 16
        assert grid.verticalSpacing() == 8
    finally:
        widget.close()
        widget.deleteLater()


def test_dashboard_tables_share_extra_vertical_space(application):
    """Give both summary tables equal vertical stretch factors."""
    widget = DashboardWidget()

    try:
        layout = widget.layout()

        assert isinstance(layout, QVBoxLayout)

        monthly_index = layout.indexOf(widget.monthly_summary_table)
        category_index = layout.indexOf(widget.category_breakdown_table)

        assert monthly_index >= 0
        assert category_index >= 0

        assert layout.stretch(monthly_index) == 1
        assert layout.stretch(category_index) == 1

        for index in range(layout.count()):
            if index not in (monthly_index, category_index):
                assert layout.stretch(index) == 0
    finally:
        widget.close()
        widget.deleteLater()