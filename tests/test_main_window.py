"""Test the main PySide6 window of the Personal Finance Tracker.

This module verifies the basic structure of the graphical user interface.
It checks the window title, the central tab widget, the transactions tab,
and the columns of the transaction table.

The tests are written before the complete GUI implementation according to
Test-Driven Development.
"""

import pytest
from PySide6.QtWidgets import QTabWidget, QTableWidget
from pytestqt.qtbot import QtBot

from finance_tracker.gui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot: QtBot) -> MainWindow:
    """Create and register a fresh main window for a single test.

    The pytest-qt ``qtbot`` fixture manages the Qt widget during the test.
    Registering the window ensures that it is closed and cleaned up
    automatically after the test has finished.

    Args:
        qtbot: The pytest-qt helper used to manage Qt widgets.

    Returns:
        A newly created Personal Finance Tracker main window.
    """
    window = MainWindow()
    qtbot.addWidget(window)

    return window


def test_main_window_has_expected_title(
    main_window: MainWindow,
) -> None:
    """Verify that the main window displays the application title.

    Args:
        main_window: The main window created by the pytest fixture.
    """
    assert main_window.windowTitle() == "Personal Finance Tracker"


def test_main_window_uses_tab_widget(
    main_window: MainWindow,
) -> None:
    """Verify that the central widget is a tab widget.

    A tab widget allows the application to organize different areas,
    such as transactions, budgets, and analyses, on separate pages.

    Args:
        main_window: The main window created by the pytest fixture.
    """
    central_widget = main_window.centralWidget()

    assert isinstance(central_widget, QTabWidget)


def test_main_window_contains_transactions_tab(
    main_window: MainWindow,
) -> None:
    """Verify that the first application tab is the transactions tab.

    The transactions tab is the first page because transaction management
    is the central feature of the Personal Finance Tracker.

    Args:
        main_window: The main window created by the pytest fixture.
    """
    tab_widget = main_window.centralWidget()

    assert isinstance(tab_widget, QTabWidget)
    assert tab_widget.count() >= 1
    assert tab_widget.tabText(0) == "Transactions"


def test_transactions_tab_contains_table(
    main_window: MainWindow,
) -> None:
    """Verify that the transactions tab contains a transaction table.

    The table is located by its unique Qt object name. Using an object name
    makes it possible to find and test the widget without depending on its
    exact visual position.

    Args:
        main_window: The main window created by the pytest fixture.
    """
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )

    assert transaction_table is not None


def test_transaction_table_has_expected_columns(
    main_window: MainWindow,
) -> None:
    """Verify the number and names of the transaction table columns.

    The table must provide one column for every important value stored in
    a transaction dictionary: date, description, transaction type,
    category, amount, and tags.

    Args:
        main_window: The main window created by the pytest fixture.
    """
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )

    assert transaction_table is not None
    assert transaction_table.columnCount() == 6

    expected_headers = [
        "Date",
        "Description",
        "Type",
        "Category",
        "Amount",
        "Tags",
    ]

    actual_headers = [
        transaction_table.horizontalHeaderItem(column).text()
        for column in range(transaction_table.columnCount())
    ]

    assert actual_headers == expected_headers