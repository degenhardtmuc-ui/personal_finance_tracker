"""Test the compact budget layout and its space allocation."""

import pytest

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QVBoxLayout,
)

from finance_tracker.gui.budget_widget import BudgetWidget


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for layout tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_budget_inputs_use_compact_grid(application):
    """Arrange category, monthly limit, and month in three columns."""
    widget = BudgetWidget()

    try:
        grid = widget.findChild(
            QGridLayout,
            "budget_form_grid",
        )

        assert grid is not None

        expected_positions = [
            (widget.budget_category_input, 1, 0),
            (widget.budget_limit_input, 1, 1),
            (widget.budget_month_input, 1, 2),
        ]

        for input_widget, expected_row, expected_column in expected_positions:
            index = grid.indexOf(input_widget)

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


def test_budget_layout_has_consistent_spacing(application):
    """Use the same main margins and grid spacing as Transactions."""
    widget = BudgetWidget()

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
            "budget_form_grid",
        )

        assert grid is not None
        assert grid.horizontalSpacing() == 16
        assert grid.verticalSpacing() == 8
    finally:
        widget.close()
        widget.deleteLater()


def test_budget_table_receives_extra_vertical_space(application):
    """Allocate additional window height to the budget overview."""
    widget = BudgetWidget()

    try:
        layout = widget.layout()

        assert isinstance(layout, QVBoxLayout)

        table_index = layout.indexOf(widget.budget_table)

        assert table_index >= 0
        assert layout.stretch(table_index) == 1

        for index in range(layout.count()):
            if index != table_index:
                assert layout.stretch(index) == 0
    finally:
        widget.close()
        widget.deleteLater()