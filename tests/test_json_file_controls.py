"""Test the JSON file controls of the PySide6 application.

This module describes the expected graphical behaviour for saving and loading
the dictionary-based account as a JSON file.

The JSON conversion and file operations were implemented in an earlier
project phase. The graphical interface must reuse those domain functions
instead of implementing another JSON storage system.

The tests verify that the graphical interface:

1. provides a button for saving the current account,
2. provides a button for loading an account,
3. calls the existing save function with the selected path,
4. does nothing when the save dialog is cancelled,
5. replaces the current account after loading a file,
6. does nothing when the load dialog is cancelled.

The tests are written before the graphical controls are implemented. This is
the RED step of Test-Driven Development.
"""

from pathlib import Path
from typing import Callable

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QPushButton,
    QTableWidget,
)
from pytestqt.qtbot import QtBot

import finance_tracker.gui.main_window as main_window_module
from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.transaction import create_transaction


@pytest.fixture
def main_window(qtbot: QtBot) -> MainWindow:
    """Create and register a fresh main window for one test.

    Every test receives a new main window with an empty account. This prevents
    saved or loaded data from one test from influencing another test.

    Args:
        qtbot: The pytest-qt helper that manages Qt widgets.

    Returns:
        A newly created Personal Finance Tracker main window.
    """
    window = MainWindow()
    qtbot.addWidget(window)

    return window


@pytest.fixture
def loaded_account() -> dict:
    """Create an example account returned by a mocked JSON loader.

    The fixture represents data that could have been read from a real JSON
    file. It contains one expense transaction with Python enum values and a
    set of tags.

    Returns:
        A dictionary-based account containing one transaction.
    """
    transaction = create_transaction(
        description="Loaded groceries",
        amount=32.75,
        transaction_type=TransactionType.EXPENSE,
        category=Category.FOOD,
        date="2026-09-22",
        tags={"food", "imported"},
    )

    return {
        "name": "Loaded Account",
        "transactions": [transaction],
    }


def test_json_controls_contain_save_button(
    main_window: MainWindow,
) -> None:
    """Verify that the GUI contains a button for saving JSON data."""
    save_button = main_window.findChild(
        QPushButton,
        "save_json_button",
    )

    assert save_button is not None
    assert save_button.text() == "Save JSON"


def test_json_controls_contain_load_button(
    main_window: MainWindow,
) -> None:
    """Verify that the GUI contains a button for loading JSON data."""
    load_button = main_window.findChild(
        QPushButton,
        "load_json_button",
    )

    assert load_button is not None
    assert load_button.text() == "Load JSON"


def test_save_button_saves_account_to_selected_path(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that Save JSON calls the existing storage function.

    The real file-selection dialog is replaced with a predictable test
    response. The storage function is also replaced so that the test can
    record its arguments without writing a real file.

    Args:
        main_window: The main window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
        tmp_path: A temporary directory created by pytest.
    """
    save_button = main_window.findChild(
        QPushButton,
        "save_json_button",
    )

    assert save_button is not None

    selected_path = tmp_path / "account.json"
    recorded_call: dict = {}

    def fake_save_account(account: dict, file_path: str | Path) -> None:
        """Record the arguments passed by the GUI.

        Args:
            account: The account dictionary passed to the storage layer.
            file_path: The selected destination path.
        """
        recorded_call["account"] = account
        recorded_call["file_path"] = Path(file_path)

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (
            str(selected_path),
            "JSON files (*.json)",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "save_account",
        fake_save_account,
        raising=False,
    )

    qtbot.mouseClick(
        save_button,
        Qt.MouseButton.LeftButton,
    )

    assert recorded_call["account"] is main_window.account
    assert recorded_call["file_path"] == selected_path
    assert (
        main_window.transaction_status_label.text()
        == "Account saved successfully."
    )


def test_cancelled_save_dialog_does_not_save_account(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that cancelling the save dialog performs no file operation.

    An empty file path means that the user pressed Cancel. In this situation,
    the existing account must remain unchanged and the storage function must
    not be called.

    Args:
        main_window: The main window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
    """
    save_button = main_window.findChild(
        QPushButton,
        "save_json_button",
    )

    assert save_button is not None

    save_was_called = False

    def fake_save_account(account: dict, file_path: str | Path) -> None:
        """Record an unexpected attempt to save the account.

        Args:
            account: The account that would have been saved.
            file_path: The destination that would have been used.
        """
        nonlocal save_was_called
        save_was_called = True

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (
            "",
            "",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "save_account",
        fake_save_account,
        raising=False,
    )

    qtbot.mouseClick(
        save_button,
        Qt.MouseButton.LeftButton,
    )

    assert save_was_called is False


def test_load_button_replaces_account_and_refreshes_table(
    main_window: MainWindow,
    loaded_account: dict,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that loading JSON replaces the account and refreshes the table.

    The file dialog and JSON loader are replaced by controlled test functions.
    After the button click, the loaded account must become the current account
    and its transaction must appear in the visual table.

    Args:
        main_window: The main window created by the fixture.
        loaded_account: The example account returned by the fake loader.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
        tmp_path: A temporary directory created by pytest.
    """
    load_button = main_window.findChild(
        QPushButton,
        "load_json_button",
    )
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )

    assert load_button is not None
    assert transaction_table is not None

    selected_path = tmp_path / "loaded_account.json"
    recorded_path: dict = {}

    def fake_load_account(file_path: str | Path) -> dict:
        """Return the prepared account instead of reading a real file.

        Args:
            file_path: The path selected by the graphical interface.

        Returns:
            The prepared dictionary-based account.
        """
        recorded_path["file_path"] = Path(file_path)
        return loaded_account

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(selected_path),
            "JSON files (*.json)",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "load_account",
        fake_load_account,
        raising=False,
    )

    qtbot.mouseClick(
        load_button,
        Qt.MouseButton.LeftButton,
    )

    assert recorded_path["file_path"] == selected_path
    assert main_window.account is loaded_account
    assert transaction_table.rowCount() == 1

    assert transaction_table.item(0, 0).text() == "2026-09-22"
    assert transaction_table.item(0, 1).text() == "Loaded groceries"
    assert transaction_table.item(0, 2).text() == "Expense"
    assert transaction_table.item(0, 3).text() == "Food"
    assert transaction_table.item(0, 4).text() == "32.75"
    assert transaction_table.item(0, 5).text() == "food, imported"

    assert (
        main_window.transaction_status_label.text()
        == "Account loaded successfully."
    )


def test_cancelled_load_dialog_keeps_current_account(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that cancelling the load dialog keeps the existing account.

    No load operation may occur when the file dialog returns an empty path.

    Args:
        main_window: The main window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
    """
    load_button = main_window.findChild(
        QPushButton,
        "load_json_button",
    )

    assert load_button is not None

    original_account = main_window.account
    load_was_called = False

    def fake_load_account(file_path: str | Path) -> dict:
        """Record an unexpected attempt to load an account.

        Args:
            file_path: The path that would have been loaded.

        Returns:
            The unchanged current account.
        """
        nonlocal load_was_called
        load_was_called = True
        return original_account

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            "",
            "",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "load_account",
        fake_load_account,
        raising=False,
    )

    qtbot.mouseClick(
        load_button,
        Qt.MouseButton.LeftButton,
    )

    assert load_was_called is False
    assert main_window.account is original_account