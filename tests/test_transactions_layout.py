"""Test the compact transaction layout and its space allocation."""

import pytest

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QVBoxLayout,
)

from finance_tracker.gui.transactions_widget import TransactionsWidget


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for layout tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_transaction_inputs_use_compact_grid(application):
    """Arrange six inputs in two groups of three columns."""
    widget = TransactionsWidget()

    try:
        grid = widget.findChild(
            QGridLayout,
            "transaction_form_grid",
        )

        assert grid is not None

        expected_positions = [
            (widget.description_input, 1, 0),
            (widget.amount_input, 1, 1),
            (widget.transaction_type_input, 1, 2),
            (widget.category_input, 3, 0),
            (widget.date_input, 3, 1),
            (widget.tags_input, 3, 2),
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


def test_transaction_layout_has_consistent_spacing(application):
    """Provide outer margins and clear gaps between input fields."""
    widget = TransactionsWidget()

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
            "transaction_form_grid",
        )

        assert grid is not None
        assert grid.horizontalSpacing() == 16
        assert grid.verticalSpacing() == 8
    finally:
        widget.close()
        widget.deleteLater()


def test_transaction_table_receives_extra_vertical_space(application):
    """Give additional window height to the transaction table."""
    widget = TransactionsWidget()

    try:
        layout = widget.layout()

        assert isinstance(layout, QVBoxLayout)

        table_index = layout.indexOf(widget.transaction_table)

        assert table_index >= 0
        assert layout.stretch(table_index) == 1

        for index in range(layout.count()):
            if index != table_index:
                assert layout.stretch(index) == 0
    finally:
        widget.close()
        widget.deleteLater()