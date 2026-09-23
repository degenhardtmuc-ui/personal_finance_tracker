"""Provide the main PySide6 window for the Personal Finance Tracker.

This module contains the graphical main window of the application. The window
provides a tab-based user interface and currently includes the transactions
tab.

The transactions tab contains two principal areas:

1. A form for entering new transaction data.
2. A table for displaying the transactions that were added.

The graphical user interface does not create an alternative transaction data
model. Instead, it uses the existing dictionary-based domain functions from
the earlier project phases.

This separation is important:

- Qt widgets collect and display user input.
- The transaction module validates and creates transaction dictionaries.
- The account module stores the created transaction dictionaries.

The GUI therefore acts as a presentation layer above the existing business
logic.
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from finance_tracker.account import add_transaction, create_account
from finance_tracker.category import Category, TransactionType
from finance_tracker.json_storage import load_account, save_account
from finance_tracker.transaction import create_transaction


class MainWindow(QMainWindow):
    """Represent the main window of the Personal Finance Tracker.

    The window contains a central tab widget. The first tab provides the
    transaction management interface.

    The class owns one dictionary-based account. New transactions created
    through the form are validated by the domain layer, stored in the account,
    and then displayed in the transaction table.

    Attributes:
        account: The dictionary-based account used by the GUI.
        tab_widget: The central widget containing the application tabs.
        transaction_table: The table displaying entered transactions.
        description_input: The text field for the transaction description.
        amount_input: The text field for the positive transaction amount.
        transaction_type_input: The selection field for income or expense.
        category_input: The selection field for the transaction category.
        date_input: The date selector for the transaction date.
        tags_input: The text field for optional comma-separated tags.
        add_transaction_button: The button that submits the form.
        transaction_status_label: The label displaying success or error text.
    """

    def __init__(self) -> None:
        """Initialize the main application window and its widgets.

        A fresh dictionary-based account is created for the current
        application session. The window title and minimum size are configured
        before the central tab widget is constructed.
        """
        super().__init__()

        self.account = create_account("Personal Finance")

        self.setWindowTitle("Personal Finance Tracker")
        self.setMinimumSize(900, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._create_transactions_tab()

    def _create_transactions_tab(self) -> None:
        """Create the transactions tab and add it to the main window.

        The tab contains three principal areas:

        1. A form for entering new transaction data.
        2. JSON controls for saving and loading the current account.
        3. A table for displaying the account transactions.

        The form and file controls are placed above the transaction table so
        that the user can manage the account from one central interface.
        """
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)

        transaction_form = self._create_transaction_form()
        json_controls = self._create_json_controls()
        self.transaction_table = self._create_transaction_table()

        transactions_layout.addLayout(transaction_form)
        transactions_layout.addLayout(json_controls)
        transactions_layout.addWidget(self.transaction_table)

        self.tab_widget.addTab(
            transactions_tab,
            "Transactions",
        )

    def _create_transaction_form(self) -> QFormLayout:
        """Create and return the transaction input form.

        Object names are assigned to all important widgets. These names allow
        automated tests to find individual widgets without relying on their
        visual position.

        Returns:
            A form layout containing all transaction input widgets.
        """
        form_layout = QFormLayout()

        self.description_input = QLineEdit()
        self.description_input.setObjectName("description_input")
        self.description_input.setPlaceholderText(
            "Transaction description",
        )

        self.amount_input = QLineEdit()
        self.amount_input.setObjectName("amount_input")
        self.amount_input.setPlaceholderText("0.00")

        self.transaction_type_input = QComboBox()
        self.transaction_type_input.setObjectName(
            "transaction_type_input",
        )
        self.transaction_type_input.addItems(
            [
                "Income",
                "Expense",
            ],
        )

        self.category_input = QComboBox()
        self.category_input.setObjectName("category_input")
        self.category_input.addItems(
            [
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
            ],
        )

        self.date_input = QDateEdit()
        self.date_input.setObjectName("date_input")
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.tags_input = QLineEdit()
        self.tags_input.setObjectName("tags_input")
        self.tags_input.setPlaceholderText(
            "food, weekly, essential",
        )

        self.add_transaction_button = QPushButton(
            "Add transaction",
        )
        self.add_transaction_button.setObjectName(
            "add_transaction_button",
        )
        self.add_transaction_button.clicked.connect(
            self._handle_add_transaction,
        )

        self.transaction_status_label = QLabel()
        self.transaction_status_label.setObjectName(
            "transaction_status_label",
        )

        form_layout.addRow(
            "Description:",
            self.description_input,
        )
        form_layout.addRow(
            "Amount:",
            self.amount_input,
        )
        form_layout.addRow(
            "Transaction type:",
            self.transaction_type_input,
        )
        form_layout.addRow(
            "Category:",
            self.category_input,
        )
        form_layout.addRow(
            "Date:",
            self.date_input,
        )
        form_layout.addRow(
            "Tags:",
            self.tags_input,
        )
        form_layout.addRow(
            self.add_transaction_button,
        )
        form_layout.addRow(
            "Status:",
            self.transaction_status_label,
        )

        return form_layout
    
    def _create_json_controls(self) -> QHBoxLayout:
        """Create and return the JSON file control layout.

        The layout contains one button for saving the current account and one
        button for loading an account from a JSON file.

        Object names are assigned to both buttons. Automated GUI tests use
        these names to locate the widgets without depending on their visual
        position.

        The buttons are connected to separate handler methods. This keeps the
        widget construction separate from the actual file operations.

        Returns:
            A horizontal layout containing the Save JSON and Load JSON
            buttons.
        """
        json_controls = QHBoxLayout()

        self.save_json_button = QPushButton("Save JSON")
        self.save_json_button.setObjectName("save_json_button")
        self.save_json_button.clicked.connect(
            self._handle_save_json,
        )

        self.load_json_button = QPushButton("Load JSON")
        self.load_json_button.setObjectName("load_json_button")
        self.load_json_button.clicked.connect(
            self._handle_load_json,
        )

        json_controls.addWidget(self.save_json_button)
        json_controls.addWidget(self.load_json_button)

        return json_controls
    
    def _create_transaction_table(self) -> QTableWidget:
        """Create and configure the transaction table.

        The table contains one column for every value displayed by the
        graphical interface. Users can select complete rows, but they cannot
        directly edit table cells. Transactions must be changed through the
        application logic instead of by modifying the visual representation.

        Returns:
            A configured table widget with six transaction columns.
        """
        table = QTableWidget()
        table.setObjectName("transaction_table")
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            [
                "Date",
                "Description",
                "Type",
                "Category",
                "Amount",
                "Tags",
            ],
        )

        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers,
        )
        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows,
        )
        table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection,
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )

        return table

    def _handle_add_transaction(self) -> None:
        """Validate the form and add one transaction to the account.

        The method performs the following operations:

        1. Read the values from the Qt input widgets.
        2. Convert the amount text into a floating-point number.
        3. Convert visible combo-box text into domain enum values.
        4. Convert comma-separated tag text into a Python set.
        5. Ask the domain layer to create a validated dictionary.
        6. Add the dictionary to the account.
        7. Display the transaction in the table.
        8. Clear the text fields after successful submission.

        Invalid data does not crash the application. A readable message is
        displayed in the status label instead.
        """
        description = self.description_input.text().strip()
        amount_text = self.amount_input.text().strip()

        try:
            amount = float(amount_text)
        except ValueError:
            self.transaction_status_label.setText(
                "Amount must be a valid number.",
            )
            return

        transaction_type = TransactionType(
            self.transaction_type_input.currentText().lower(),
        )
        category = Category(
            self.category_input.currentText().lower(),
        )

        date = self.date_input.date().toString("yyyy-MM-dd")
        tags = self._parse_tags(self.tags_input.text())

        try:
            transaction = create_transaction(
                description=description,
                amount=amount,
                transaction_type=transaction_type,
                category=category,
                date=date,
                tags=tags,
            )
        except ValueError as error:
            self.transaction_status_label.setText(str(error))
            return

        add_transaction(
            self.account,
            transaction,
        )

        self._append_transaction_to_table(transaction)
        self._clear_transaction_form()

        self.transaction_status_label.setText(
            "Transaction added successfully.",
        )
    
    def _handle_save_json(self) -> None:
        """Open a file dialog and save the current account as JSON.

        The user selects the destination with a native Qt file dialog. If no
        file extension is entered, ``.json`` is appended automatically.

        Cancelling the dialog produces an empty path. In this situation, the
        method returns immediately and does not call the storage layer.

        File-system and validation errors are caught so that an unsuccessful
        save operation does not terminate the graphical application.
        """
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save account as JSON",
            "account.json",
            "JSON files (*.json)",
        )

        if not selected_path:
            return

        if not selected_path.lower().endswith(".json"):
            selected_path = f"{selected_path}.json"

        try:
            save_account(
                self.account,
                selected_path,
            )
        except (OSError, TypeError, ValueError) as error:
            self.transaction_status_label.setText(
                f"Account could not be saved: {error}",
            )
            return

        self.transaction_status_label.setText(
            "Account saved successfully.",
        )

    def _handle_load_json(self) -> None:
        """Open a file dialog and load an account from a JSON file.

        After successful loading, the current in-memory account is replaced by
        the loaded dictionary. The transaction table is then rebuilt from the
        loaded transaction dictionaries.

        Cancelling the dialog leaves the existing account unchanged. Storage,
        conversion, and validation errors are displayed in the status label
        instead of crashing the application.
        """
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Load account from JSON",
            "",
            "JSON files (*.json)",
        )

        if not selected_path:
            return

        try:
            loaded_account = load_account(selected_path)
        except (OSError, TypeError, ValueError) as error:
            self.transaction_status_label.setText(
                f"Account could not be loaded: {error}",
            )
            return

        self.account = loaded_account
        self._refresh_transaction_table()

        self.transaction_status_label.setText(
            "Account loaded successfully.",
        )

    def _refresh_transaction_table(self) -> None:
        """Rebuild the transaction table from the current account.

        Existing visual table rows are removed before the account
        transactions are inserted again. The account dictionary itself is not
        changed by this method.

        This separation is important because the table is only a visual
        representation of the account data. The dictionary remains the actual
        source of truth.
        """
        self.transaction_table.setRowCount(0)

        for transaction in self.account["transactions"]:
            self._append_transaction_to_table(transaction)

    @staticmethod
    def _parse_tags(tags_text: str) -> set[str]:
        """Convert comma-separated tag text into a cleaned set.

        Leading and trailing spaces are removed from every tag. Empty entries
        are ignored. A set prevents the same tag from being stored more than
        once.

        Example:
            ``"food, weekly, food"`` becomes
            ``{"food", "weekly"}``.

        Args:
            tags_text: The raw comma-separated text entered by the user.

        Returns:
            A set containing the cleaned non-empty tags.
        """
        return {
            tag.strip()
            for tag in tags_text.split(",")
            if tag.strip()
        }

    def _append_transaction_to_table(
        self,
        transaction: dict,
    ) -> None:
        """Append one transaction dictionary to the visual table.

        The function only controls the visual representation. The transaction
        has already been validated and stored in the account before this
        method is called.

        Args:
            transaction: The validated transaction dictionary to display.
        """
        row = self.transaction_table.rowCount()
        self.transaction_table.insertRow(row)

        formatted_tags = ", ".join(
            sorted(transaction["tags"]),
        )

        displayed_values = [
            transaction["date"],
            transaction["description"],
            transaction["transaction_type"].value.title(),
            transaction["category"].value.title(),
            f"{transaction['amount']:.2f}",
            formatted_tags,
        ]

        for column, value in enumerate(displayed_values):
            table_item = QTableWidgetItem(str(value))
            self.transaction_table.setItem(
                row,
                column,
                table_item,
            )

    def _clear_transaction_form(self) -> None:
        """Clear text fields after a transaction was added successfully.

        The combo boxes and date selector remain unchanged. This is convenient
        when users enter several similar transactions in succession.
        """
        self.description_input.clear()
        self.amount_input.clear()
        self.tags_input.clear()