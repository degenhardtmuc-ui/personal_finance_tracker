"""Test the CSV import and export controls of the PySide6 interface.

This module verifies the graphical connection between the main application
window and the CSV storage functions developed during Phase 3.

The tests check that users can select CSV files, import transactions into the
current account, refresh the visible transaction table, export the current
account, and safely cancel file dialogs.

These tests are written before the Phase 4D GUI implementation according to
Test-Driven Development.
"""

from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QTableWidget
from pytestqt.qtbot import QtBot

import finance_tracker.gui.main_window as main_window_module
from finance_tracker.category import Category, TransactionType
from finance_tracker.gui.main_window import MainWindow
from finance_tracker.transaction import create_transaction


@pytest.fixture
def main_window(qtbot: QtBot) -> MainWindow:
    """Create and register a fresh main window for every CSV GUI test.

    The pytest-qt ``qtbot`` fixture manages the lifetime of the window.
    Registering the widget ensures that it is closed and cleaned up after the
    individual test has finished.

    Args:
        qtbot: The pytest-qt helper used to manage Qt widgets.

    Returns:
        A newly created Personal Finance Tracker main window.
    """
    window = MainWindow()
    qtbot.addWidget(window)

    return window


def test_csv_controls_contain_import_button(
    main_window: MainWindow,
) -> None:
    """Verify that the Transactions tab contains a CSV import button.

    The test searches for the button by its Qt object name. This is more stable
    than depending on the button's exact position in the layout.

    Args:
        main_window: The main application window created by the fixture.
    """
    import_button = main_window.findChild(
        QPushButton,
        "import_csv_button",
    )

    assert import_button is not None
    assert import_button.text() == "Import CSV"


def test_csv_controls_contain_export_button(
    main_window: MainWindow,
) -> None:
    """Verify that the Transactions tab contains a CSV export button.

    Args:
        main_window: The main application window created by the fixture.
    """
    export_button = main_window.findChild(
        QPushButton,
        "export_csv_button",
    )

    assert export_button is not None
    assert export_button.text() == "Export CSV"


def test_import_button_imports_transactions_and_refreshes_table(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that a selected CSV file is imported and displayed.

    The real file dialog and CSV importer are replaced temporarily. The fake
    importer records its arguments and adds one valid transaction to the
    current account.

    The table must be rebuilt after the import so that the new transaction
    becomes visible immediately.

    Args:
        main_window: The main application window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
        tmp_path: A temporary directory supplied by pytest.
    """
    selected_path = tmp_path / "transactions.csv"
    received_arguments: dict[str, object] = {}

    def fake_import_transactions(
        account: dict,
        path: str | Path,
    ) -> dict:
        """Simulate importing one valid transaction."""
        received_arguments["account"] = account
        received_arguments["path"] = path

        transaction = create_transaction(
            description="Groceries",
            amount=45.50,
            transaction_type=TransactionType.EXPENSE,
            category=Category.FOOD,
            date="2026-09-25",
            tags={"food", "weekly"},
        )
        account["transactions"].append(transaction)

        return {
            "imported": 1,
            "skipped": 0,
            "errors": [],
        }

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(selected_path),
            "CSV files (*.csv)",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "import_transactions",
        fake_import_transactions,
        raising=False,
    )

    import_button = main_window.findChild(
        QPushButton,
        "import_csv_button",
    )
    transaction_table = main_window.findChild(
        QTableWidget,
        "transaction_table",
    )

    assert import_button is not None
    assert transaction_table is not None
    assert transaction_table.rowCount() == 0

    qtbot.mouseClick(
        import_button,
        Qt.MouseButton.LeftButton,
    )

    assert received_arguments["account"] is main_window.account
    assert Path(received_arguments["path"]) == selected_path
    assert len(main_window.account["transactions"]) == 1
    assert transaction_table.rowCount() == 1
    assert transaction_table.item(0, 1).text() == "Groceries"


def test_import_button_displays_import_summary(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that imported and skipped row counts appear in the GUI.

    The fake importer reports two imported transactions and one skipped row.
    Both values must appear in the status label.

    Args:
        main_window: The main application window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
        tmp_path: A temporary directory supplied by pytest.
    """
    selected_path = tmp_path / "mixed_transactions.csv"

    def fake_import_transactions(
        account: dict,
        path: str | Path,
    ) -> dict:
        """Return a simulated CSV import summary."""
        return {
            "imported": 2,
            "skipped": 1,
            "errors": ["Invalid amount on line 4"],
        }

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (
            str(selected_path),
            "CSV files (*.csv)",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "import_transactions",
        fake_import_transactions,
        raising=False,
    )

    import_button = main_window.findChild(
        QPushButton,
        "import_csv_button",
    )

    assert import_button is not None

    qtbot.mouseClick(
        import_button,
        Qt.MouseButton.LeftButton,
    )

    status_text = main_window.transaction_status_label.text()

    assert "2" in status_text
    assert "imported" in status_text.lower()
    assert "1" in status_text
    assert "skipped" in status_text.lower()


def test_cancelled_import_dialog_keeps_current_account(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that cancelling the import dialog changes nothing.

    An empty path represents a cancelled Qt file dialog. In that situation,
    the CSV import function must not be called and the current transactions
    must remain unchanged.

    Args:
        main_window: The main application window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
    """
    import_was_called = False

    def fake_import_transactions(
        account: dict,
        path: str | Path,
    ) -> dict:
        """Record an unexpected attempt to import a file."""
        nonlocal import_was_called
        import_was_called = True

        return {
            "imported": 0,
            "skipped": 0,
            "errors": [],
        }

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: ("", ""),
    )
    monkeypatch.setattr(
        main_window_module,
        "import_transactions",
        fake_import_transactions,
        raising=False,
    )

    original_name = main_window.account["name"]
    original_transactions = list(
        main_window.account["transactions"],
    )

    import_button = main_window.findChild(
        QPushButton,
        "import_csv_button",
    )

    assert import_button is not None

    qtbot.mouseClick(
        import_button,
        Qt.MouseButton.LeftButton,
    )

    assert import_was_called is False
    assert main_window.account["name"] == original_name
    assert main_window.account["transactions"] == original_transactions


def test_export_button_exports_account_to_selected_path(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify that the export button uses the selected CSV path.

    The selected filename deliberately has no extension. The GUI must append
    ``.csv`` before passing the path to the CSV export function.

    Args:
        main_window: The main application window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
        tmp_path: A temporary directory supplied by pytest.
    """
    selected_path = tmp_path / "account_transactions"
    expected_path = tmp_path / "account_transactions.csv"
    received_arguments: dict[str, object] = {}

    def fake_export_transactions(
        account: dict,
        path: str | Path,
    ) -> None:
        """Record the values received from the graphical interface."""
        received_arguments["account"] = account
        received_arguments["path"] = path

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (
            str(selected_path),
            "CSV files (*.csv)",
        ),
    )
    monkeypatch.setattr(
        main_window_module,
        "export_transactions",
        fake_export_transactions,
        raising=False,
    )

    export_button = main_window.findChild(
        QPushButton,
        "export_csv_button",
    )

    assert export_button is not None

    qtbot.mouseClick(
        export_button,
        Qt.MouseButton.LeftButton,
    )

    assert received_arguments["account"] is main_window.account
    assert Path(received_arguments["path"]) == expected_path
    assert "exported successfully" in (
        main_window.transaction_status_label.text().lower()
    )


def test_cancelled_export_dialog_does_not_export(
    main_window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that cancelling the export dialog performs no operation.

    Args:
        main_window: The main application window created by the fixture.
        qtbot: The pytest-qt helper used to simulate a mouse click.
        monkeypatch: The pytest helper used to replace functions temporarily.
    """
    export_was_called = False

    def fake_export_transactions(
        account: dict,
        path: str | Path,
    ) -> None:
        """Record an unexpected attempt to export a file."""
        nonlocal export_was_called
        export_was_called = True

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("", ""),
    )
    monkeypatch.setattr(
        main_window_module,
        "export_transactions",
        fake_export_transactions,
        raising=False,
    )

    export_button = main_window.findChild(
        QPushButton,
        "export_csv_button",
    )

    assert export_button is not None

    qtbot.mouseClick(
        export_button,
        Qt.MouseButton.LeftButton,
    )

    assert export_was_called is False