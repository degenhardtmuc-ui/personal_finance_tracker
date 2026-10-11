"""Provide a standalone transaction interface without owning account data."""

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TransactionsWidget(QWidget):
    """Display transaction inputs and rows, and emit operation requests."""

    add_transaction_requested = Signal()
    save_json_requested = Signal()
    load_json_requested = Signal()
    import_csv_requested = Signal()
    export_csv_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the transaction form, file controls, and table."""
        super().__init__(parent)
        self.setObjectName("transactions_widget")

        layout = QVBoxLayout(self)
        layout.addLayout(self._create_form())
        layout.addLayout(self._create_json_controls())
        layout.addLayout(self._create_csv_controls())

        self.transaction_table = self._create_table()
        layout.addWidget(self.transaction_table)

    def _create_form(self) -> QFormLayout:
        """Create the named transaction input widgets."""
        form = QFormLayout()

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
            ["Income", "Expense"],
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
            self.add_transaction_requested.emit,
        )

        self.transaction_status_label = QLabel()
        self.transaction_status_label.setObjectName(
            "transaction_status_label",
        )

        form.addRow("Description:", self.description_input)
        form.addRow("Amount:", self.amount_input)
        form.addRow(
            "Transaction type:",
            self.transaction_type_input,
        )
        form.addRow("Category:", self.category_input)
        form.addRow("Date:", self.date_input)
        form.addRow("Tags:", self.tags_input)
        form.addRow(self.add_transaction_button)
        form.addRow("Status:", self.transaction_status_label)

        return form

    def _create_json_controls(self) -> QHBoxLayout:
        """Create buttons requesting account saving and loading."""
        controls = QHBoxLayout()

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

        controls.addWidget(self.save_json_button)
        controls.addWidget(self.load_json_button)

        return controls

    def _create_csv_controls(self) -> QHBoxLayout:
        """Create buttons requesting CSV import and export."""
        controls = QHBoxLayout()

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

        controls.addWidget(self.import_csv_button)
        controls.addWidget(self.export_csv_button)

        return controls

    @staticmethod
    def _create_table() -> QTableWidget:
        """Create the read-only, six-column transaction table."""
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

    def append_transaction(self, transaction: dict) -> None:
        """Append one validated transaction to the displayed table."""
        row = self.transaction_table.rowCount()
        self.transaction_table.insertRow(row)

        formatted_tags = ", ".join(
            sorted(transaction["tags"]),
        )

        values = [
            transaction["date"],
            transaction["description"],
            transaction["transaction_type"].value.title(),
            transaction["category"].value.title(),
            f"{transaction['amount']:.2f}",
            formatted_tags,
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
        """Clear text fields after a successful transaction submission."""
        self.description_input.clear()
        self.amount_input.clear()
        self.tags_input.clear()