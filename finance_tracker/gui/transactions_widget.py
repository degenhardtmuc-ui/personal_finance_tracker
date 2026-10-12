"""Provide transaction entry, editing controls, and a read-only table."""

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TransactionsWidget(QWidget):
    """Display transactions and emit entry, editing, and file requests."""

    add_transaction_requested = Signal()
    save_changes_requested = Signal()
    cancel_edit_requested = Signal()
    save_json_requested = Signal()
    load_json_requested = Signal()
    import_csv_requested = Signal()
    export_csv_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the compact form, action controls, and table."""
        super().__init__(parent)
        self.setObjectName("transactions_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        layout.addLayout(self._create_form())
        layout.addLayout(self._create_submission_controls())
        layout.addLayout(self._create_file_controls())

        self.transaction_table = self._create_table()
        layout.addWidget(self.transaction_table, 1)

        self.set_edit_mode(False)

    def _create_form(self) -> QGridLayout:
        """Arrange transaction inputs in two groups of three columns."""
        grid = QGridLayout()
        grid.setObjectName("transaction_form_grid")
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

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
        self.transaction_type_input.addItems(["Income", "Expense"])

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
        self.tags_input.setPlaceholderText("food, weekly, essential")

        fields = [
            ("Description:", self.description_input, 0, 0),
            ("Amount:", self.amount_input, 0, 1),
            ("Transaction type:", self.transaction_type_input, 0, 2),
            ("Category:", self.category_input, 2, 0),
            ("Date:", self.date_input, 2, 1),
            ("Tags:", self.tags_input, 2, 2),
        ]

        for label_text, input_widget, label_row, column in fields:
            label = QLabel(label_text)
            label.setBuddy(input_widget)

            input_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            grid.addWidget(label, label_row, column)
            grid.addWidget(input_widget, label_row + 1, column)

        for column in range(3):
            grid.setColumnStretch(column, 1)

        return grid

    def _create_submission_controls(self) -> QHBoxLayout:
        """Create add, save changes, cancel edit, and status controls."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)

        self.add_transaction_button = QPushButton("Add transaction")
        self.add_transaction_button.setObjectName(
            "add_transaction_button",
        )
        self.add_transaction_button.clicked.connect(
            self.add_transaction_requested.emit,
        )

        self.save_changes_button = QPushButton("Save changes")
        self.save_changes_button.setObjectName("save_changes_button")
        self.save_changes_button.clicked.connect(
            self.save_changes_requested.emit,
        )

        self.cancel_edit_button = QPushButton("Cancel edit")
        self.cancel_edit_button.setObjectName("cancel_edit_button")
        self.cancel_edit_button.clicked.connect(
            self.cancel_edit_requested.emit,
        )

        self.transaction_status_label = QLabel()
        self.transaction_status_label.setObjectName(
            "transaction_status_label",
        )
        self.transaction_status_label.setWordWrap(True)

        controls.addWidget(self.add_transaction_button)
        controls.addWidget(self.save_changes_button)
        controls.addWidget(self.cancel_edit_button)
        controls.addWidget(self.transaction_status_label, 1)

        return controls

    def _create_file_controls(self) -> QHBoxLayout:
        """Group JSON and CSV operations in one toolbar."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(24)

        controls.addLayout(self._create_json_controls())
        controls.addLayout(self._create_csv_controls())
        controls.addStretch(1)

        return controls

    def _create_json_controls(self) -> QHBoxLayout:
        """Create account saving and loading controls."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)

        self.save_json_button = QPushButton("Save JSON")
        self.save_json_button.setObjectName("save_json_button")
        self.save_json_button.clicked.connect(
            self.save_json_requested.emit,
        )

        self.load_json_button = QPushButton("Load JSON")
        self.load_json_button.setObjectName("load_json_button")
        self.load_json_button.clicked.connect(
            self.load_json_requested.emit,
        )

        controls.addWidget(QLabel("JSON"))
        controls.addWidget(self.save_json_button)
        controls.addWidget(self.load_json_button)

        return controls

    def _create_csv_controls(self) -> QHBoxLayout:
        """Create transaction import and export controls."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)

        self.import_csv_button = QPushButton("Import CSV")
        self.import_csv_button.setObjectName("import_csv_button")
        self.import_csv_button.clicked.connect(
            self.import_csv_requested.emit,
        )

        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.setObjectName("export_csv_button")
        self.export_csv_button.clicked.connect(
            self.export_csv_requested.emit,
        )

        controls.addWidget(QLabel("CSV"))
        controls.addWidget(self.import_csv_button)
        controls.addWidget(self.export_csv_button)

        return controls

    @staticmethod
    def _create_table() -> QTableWidget:
        """Create the read-only transaction table in account order."""
        table = QTableWidget()
        table.setObjectName("transaction_table")
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            ["Date", "Description", "Type", "Category", "Amount", "Tags"],
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

        # Row numbers currently correspond to account list positions.
        table.setSortingEnabled(False)

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )

        return table

    def set_edit_mode(self, editing: bool) -> None:
        """Enable either transaction entry or edit actions."""
        self.add_transaction_button.setEnabled(not editing)
        self.save_changes_button.setEnabled(editing)
        self.cancel_edit_button.setEnabled(editing)

    def load_transaction(self, transaction: dict) -> None:
        """Copy a transaction's values into the input widgets."""
        self.description_input.setText(transaction["description"])

        # Preserve the stored precision until the user changes the amount.
        self.amount_input.setText(str(transaction["amount"]))

        self.transaction_type_input.setCurrentText(
            transaction["transaction_type"].value.title(),
        )
        self.category_input.setCurrentText(
            transaction["category"].value.title(),
        )
        self.date_input.setDate(
            QDate.fromString(transaction["date"], "yyyy-MM-dd"),
        )
        self.tags_input.setText(
            ", ".join(sorted(transaction["tags"])),
        )

    def append_transaction(self, transaction: dict) -> None:
        """Append one validated transaction to the displayed table."""
        row = self.transaction_table.rowCount()
        self.transaction_table.insertRow(row)

        values = [
            transaction["date"],
            transaction["description"],
            transaction["transaction_type"].value.title(),
            transaction["category"].value.title(),
            f"{transaction['amount']:.2f}",
            ", ".join(sorted(transaction["tags"])),
        ]

        for column, value in enumerate(values):
            self.transaction_table.setItem(
                row,
                column,
                QTableWidgetItem(str(value)),
            )

    def refresh(self, account: dict) -> None:
        """Replace displayed rows with the supplied account transactions."""
        self.transaction_table.setRowCount(0)

        for transaction in account["transactions"]:
            self.append_transaction(transaction)

    def clear_form(self) -> None:
        """Clear text fields while retaining category, type, and date."""
        self.description_input.clear()
        self.amount_input.clear()
        self.tags_input.clear()