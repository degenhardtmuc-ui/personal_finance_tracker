"""Provide the main PySide6 window for the Personal Finance Tracker.

This module contains the main desktop application window. The window organizes
the graphical user interface into tabs and initially provides a transactions
tab containing a table for displaying transaction dictionaries.
"""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Represent the main window of the Personal Finance Tracker.

    The window acts as the central container for all graphical application
    components. Different features are organized into separate tabs.

    Phase 4A provides the initial transactions tab and its table. Additional
    tabs for budgets and analyses can be added in later development steps.
    """

    WINDOW_TITLE = "Personal Finance Tracker"

    TRANSACTION_HEADERS = [
        "Date",
        "Description",
        "Type",
        "Category",
        "Amount",
        "Tags",
    ]

    def __init__(self) -> None:
        """Initialize the main window and create its user interface."""
        super().__init__()

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(900, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._create_transactions_tab()

    def _create_transactions_tab(self) -> None:
        """Create and add the transactions tab to the main window.

        The transactions tab contains a table with one column for every
        important value stored in a transaction dictionary.
        """
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)

        self.transaction_table = QTableWidget()
        self.transaction_table.setObjectName("transaction_table")
        self.transaction_table.setColumnCount(
            len(self.TRANSACTION_HEADERS),
        )
        self.transaction_table.setHorizontalHeaderLabels(
            self.TRANSACTION_HEADERS,
        )

        self.transaction_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )
        self.transaction_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.transaction_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection,
        )

        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )

        transactions_layout.addWidget(self.transaction_table)

        self.tab_widget.addTab(
            transactions_tab,
            "Transactions",
        )