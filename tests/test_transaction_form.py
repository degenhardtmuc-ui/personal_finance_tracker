"""Test the transaction input form of the PySide6 application.

This module verifies the user interface elements required to enter a new
financial transaction. The tests describe the expected behaviour before the
complete transaction form is implemented.

The transaction form must allow the user to enter a description, an amount,
a transaction type, a category, a date, and optional tags. A button must add
valid transaction data to the transaction table.

The tests follow Test-Driven Development:

1. The expected behaviour is described with automated tests.
2. The tests initially fail because the form is not implemented yet.
3. The form is implemented in the production code.
4. All tests are executed again until they pass.
"""

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
)
from pytestqt.qtbot import QtBot

from finance_tracker.gui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot: QtBot) -> MainWindow:
    """Create and register a fresh main window for one test.

    The ``qtbot`` fixture is provided by the pytest-qt package. It manages Qt
    widgets during a test and closes them automatically after the test has
    finished.

    A new main window is created for every test. Therefore, changes made by
    one test cannot accidentally influence another test.

    Args:
        qtbot: The pytest-qt helper used to manage Qt widgets.

    Returns:
        A newly created Personal Finance Tracker main window.
    """
    window = MainWindow()
    qtbot.addWidget(window)

    return window


def test_transaction_form_contains_description_input(
    main_window: MainWindow,
) -> None:
    """Verify that the form contains an input for the description.

    The object name allows the application and the automated tests to locate
    this specific widget without depending on its visual position.
    """
    description_input = main_window.findChild(
        QLineEdit,
        "description_input",
    )

    assert description_input is not None
    assert description_input.placeholderText() == "Transaction description"


def test_transaction_form_contains_amount_input(
    main_window: MainWindow,
) -> None:
    """Verify that the form contains an input for the transaction amount."""
    amount_input = main_window.findChild(
        QLineEdit,
        "amount_input",
    )

    assert amount_input is not None
    assert amount_input.placeholderText() == "0.00"


def test_transaction_form_contains_transaction_type_input(
    main_window: MainWindow,
) -> None:
    """Verify that income and expense can be selected.

    A combo box restricts the user to the two transaction types supported by
    the domain model. This prevents arbitrary and invalid values.
    """
    transaction_type_input = main_window.findChild(
        QComboBox,
        "transaction_type_input",
    )

    assert transaction_type_input is not None

    available_types = [
        transaction_type_input.itemText(index)
        for index in range(transaction_type_input.count())
    ]

    assert available_types == ["Income", "Expense"]


def test_transaction_form_contains_category_input(
    main_window: MainWindow,
) -> None:
    """Verify that the category combo box contains all domain categories."""
    category_input = main_window.findChild(
        QComboBox,
        "category_input",
    )

    assert category_input is not None

    available_categories = [
        category_input.itemText(index)
        for index in range(category_input.count())
    ]

    assert available_categories == [
        "Housing",
        "Food",
        "Transport",
        "Entertainment",
        "Health",
        "Education",
        "Clothing",
        "Salary",
        "Freelance",
        "Investment",
        "Other",
    ]


def test_transaction_form_contains_date_input(
    main_window: MainWindow,
) -> None:
    """Verify that the user can select a transaction date.

    The date is entered with a QDateEdit widget instead of a normal text
    field. Qt therefore prevents impossible dates such as 31 February.
    """
    date_input = main_window.findChild(
        QDateEdit,
        "date_input",
    )

    assert date_input is not None
    assert date_input.displayFormat() == "yyyy-MM-dd"
    assert date_input.calendarPopup() is True


def test_transaction_form_contains_tags_input(
    main_window: MainWindow,
) -> None:
    """Verify that optional comma-separated tags can be entered."""
    tags_input = main_window.findChild(
        QLineEdit,
        "tags_input",
    )

    assert tags_input is not None
    assert tags_input.placeholderText() == "food, weekly, essential"


def test_transaction_form_contains_add_button(
    main_window: MainWindow,
) -> None:
    """Verify that the form contains a button for adding a transaction."""
    add_button = main_window.findChild(
        QPushButton,
        "add_transaction_button",
    )

    assert add_button is not None
    assert add_button.text() == "Add transaction"


def test_add_transaction_button_adds_valid_transaction_to_table(
    main_window: MainWindow,
    qtbot: QtBot,
) -> None:
    """Verify that valid form data creates a new table row.

    The test fills in all relevant form fields, simulates a mouse click, and
    checks the resulting values in the transaction table.

    Args:
        main_window: The main window created by the pytest fixture.
        qtbot: The pytest-qt helper used to simulate the button click.
    """
    description_input = main_window.findChild(
        QLineEdit,
        "description_input",
    )
    amount_input = main_window.findChild(
        QLineEdit,
        "amount_input",
    )
    transaction_type_input = main_window.findChild(
        QComboBox,
        "transaction_type_input",
    )
    category_input = main_window.findChild(
        QComboBox,
        "category_input",
    )
    date_input = main_window.findChild(
        QDateEdit,
        "date_input",
    )
    tags_input = main_window.findChild(
        QLineEdit,
        "tags_input",
    )
    add_button = main_window.findChild(
        QPushButton,
        "add_transaction_button",
    )
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )

    assert description_input is not None
    assert amount_input is not None
    assert transaction_type_input is not None
    assert category_input is not None
    assert date_input is not None
    assert tags_input is not None
    assert add_button is not None
    assert transaction_table is not None

    description_input.setText("Groceries")
    amount_input.setText("45.50")
    transaction_type_input.setCurrentText("Expense")
    category_input.setCurrentText("Food")
    date_input.setDate(QDate(2026, 9, 23))
    tags_input.setText("food, weekly")

    qtbot.mouseClick(
        add_button,
        Qt.MouseButton.LeftButton,
    )

    assert transaction_table.rowCount() == 1
    assert transaction_table.item(0, 0).text() == "2026-09-23"
    assert transaction_table.item(0, 1).text() == "Groceries"
    assert transaction_table.item(0, 2).text() == "Expense"
    assert transaction_table.item(0, 3).text() == "Food"
    assert transaction_table.item(0, 4).text() == "45.50"
    assert transaction_table.item(0, 5).text() == "food, weekly"


def test_successful_transaction_clears_text_inputs(
    main_window: MainWindow,
    qtbot: QtBot,
) -> None:
    """Verify that successful submission prepares an empty form.

    Clearing the text fields makes it possible to enter the next transaction
    without manually deleting the previous values.

    Args:
        main_window: The main window created by the pytest fixture.
        qtbot: The pytest-qt helper used to simulate the button click.
    """
    description_input = main_window.findChild(
        QLineEdit,
        "description_input",
    )
    amount_input = main_window.findChild(
        QLineEdit,
        "amount_input",
    )
    transaction_type_input = main_window.findChild(
        QComboBox,
        "transaction_type_input",
    )
    category_input = main_window.findChild(
        QComboBox,
        "category_input",
    )
    tags_input = main_window.findChild(
        QLineEdit,
        "tags_input",
    )
    add_button = main_window.findChild(
        QPushButton,
        "add_transaction_button",
    )

    assert description_input is not None
    assert amount_input is not None
    assert transaction_type_input is not None
    assert category_input is not None
    assert tags_input is not None
    assert add_button is not None

    description_input.setText("Monthly salary")
    amount_input.setText("3000")
    transaction_type_input.setCurrentText("Income")
    category_input.setCurrentText("Salary")
    tags_input.setText("salary, monthly")

    qtbot.mouseClick(
        add_button,
        Qt.MouseButton.LeftButton,
    )

    assert description_input.text() == ""
    assert amount_input.text() == ""
    assert tags_input.text() == ""


def test_invalid_amount_is_rejected(
    main_window: MainWindow,
    qtbot: QtBot,
) -> None:
    """Verify that a non-numeric amount is not added to the table.

    Invalid input must not crash the application. Instead, the transaction
    table remains unchanged and a readable validation message is displayed.

    Args:
        main_window: The main window created by the pytest fixture.
        qtbot: The pytest-qt helper used to simulate the button click.
    """
    description_input = main_window.findChild(
        QLineEdit,
        "description_input",
    )
    amount_input = main_window.findChild(
        QLineEdit,
        "amount_input",
    )
    add_button = main_window.findChild(
        QPushButton,
        "add_transaction_button",
    )
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )
    status_label = main_window.findChild(
        QLabel,
        "transaction_status_label",
    )

    assert description_input is not None
    assert amount_input is not None
    assert add_button is not None
    assert transaction_table is not None
    assert status_label is not None

    description_input.setText("Invalid example")
    amount_input.setText("not-a-number")

    qtbot.mouseClick(
        add_button,
        Qt.MouseButton.LeftButton,
    )

    assert transaction_table.rowCount() == 0
    assert status_label.text() == "Amount must be a valid number."