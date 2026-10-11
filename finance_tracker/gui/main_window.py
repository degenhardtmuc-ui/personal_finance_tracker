"""Provide the main window for the Personal Finance Tracker.

The main window owns the current account and budget tracker.
DashboardWidget and BudgetWidget handle their respective interfaces.
Transaction entry and file operations are coordinated here.
"""

from math import isfinite

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

from finance_tracker.account import (
    add_transaction,
    create_account,
)
from finance_tracker.budget import (
    create_budget_tracker,
    set_budget,
)
from finance_tracker.category import Category, TransactionType
from finance_tracker.csv_storage import (
    export_transactions,
    import_transactions,
)
from finance_tracker.gui.budget_widget import BudgetWidget
from finance_tracker.gui.dashboard_widget import DashboardWidget
from finance_tracker.json_storage import (
    load_account,
    load_budgets,
    save_account,
    save_budgets,
)
from finance_tracker.transaction import create_transaction


class MainWindow(QMainWindow):
    """Coordinate transaction entry, dashboards, budgets, and storage."""

    def __init__(self) -> None:
        """Create session data and initialize the application tabs."""
        super().__init__()

        self.account = create_account("Personal Finance")
        self.budget_tracker = create_budget_tracker()

        self.setWindowTitle("Personal Finance Tracker")
        self.setMinimumSize(900, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._create_transactions_tab()
        self._create_dashboard_tab()
        self._create_budgets_tab()
        self._refresh_dashboard()

    def _create_budgets_tab(self) -> None:
        """Embed the budget widget and connect operation requests."""
        self.budget_widget = BudgetWidget()
        self.tab_widget.addTab(self.budget_widget, "Budgets")

        # Preserve existing access paths to the same widget instances.
        self.budget_category_input = (
            self.budget_widget.budget_category_input
        )
        self.budget_limit_input = self.budget_widget.budget_limit_input
        self.budget_month_input = self.budget_widget.budget_month_input
        self.set_budget_button = self.budget_widget.set_budget_button
        self.budget_status_label = self.budget_widget.budget_status_label
        self.save_budgets_button = self.budget_widget.save_budgets_button
        self.load_budgets_button = self.budget_widget.load_budgets_button
        self.budget_table = self.budget_widget.budget_table

        self.budget_widget.set_budget_requested.connect(
            self._handle_set_budget,
        )
        self.budget_widget.save_budgets_requested.connect(
            self._handle_save_budgets,
        )
        self.budget_widget.load_budgets_requested.connect(
            self._handle_load_budgets,
        )

    def _handle_save_budgets(self) -> None:
        """Ask for a destination and save the current budget tracker."""
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save budgets as JSON",
            "budgets.json",
            "JSON files (*.json)",
        )

        if not selected_path:
            return

        if not selected_path.lower().endswith(".json"):
            selected_path = f"{selected_path}.json"

        try:
            save_budgets(self.budget_tracker, selected_path)
        except (OSError, TypeError, ValueError) as error:
            self.budget_status_label.setText(
                f"Budgets could not be saved: {error}",
            )
            return

        self.budget_status_label.setText(
            "Budgets saved successfully.",
        )

    def _handle_load_budgets(self) -> None:
        """Load a validated tracker and refresh the budget overview."""
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Load budgets from JSON",
            "",
            "JSON files (*.json)",
        )

        if not selected_path:
            return

        try:
            loaded_tracker = load_budgets(selected_path)
        except (OSError, TypeError, ValueError) as error:
            self.budget_status_label.setText(
                f"Budgets could not be loaded: {error}",
            )
            return

        self.budget_tracker = loaded_tracker
        self._refresh_budget_table()
        self.budget_status_label.setText(
            "Budgets loaded successfully.",
        )

    def _handle_set_budget(self) -> None:
        """Validate the budget inputs and update the session tracker."""
        limit_text = self.budget_limit_input.text().strip()

        try:
            monthly_limit = float(limit_text)
        except ValueError:
            self.budget_status_label.setText(
                "Monthly limit must be a valid number.",
            )
            return

        if not isfinite(monthly_limit):
            self.budget_status_label.setText(
                "Monthly limit must be a valid number.",
            )
            return

        category = Category(
            self.budget_category_input.currentText().lower(),
        )
        month = self.budget_month_input.date().toString("yyyy-MM")

        try:
            set_budget(
                self.budget_tracker,
                category=category,
                monthly_limit=monthly_limit,
                month=month,
            )
        except ValueError as error:
            self.budget_status_label.setText(str(error))
            return

        self._refresh_budget_table()
        self.budget_status_label.setText(
            "Budget saved for this session.",
        )

    def _refresh_budget_table(self) -> None:
        """Refresh the budget interface from current session data."""
        self.budget_widget.refresh(
            self.budget_tracker,
            self.account,
        )

    def _create_dashboard_tab(self) -> None:
        """Embed the dashboard and preserve existing widget access."""
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")

        # These aliases reference existing widgets without copying them.
        self.income_total_label = (
            self.dashboard_widget.income_total_label
        )
        self.expense_total_label = (
            self.dashboard_widget.expense_total_label
        )
        self.balance_label = self.dashboard_widget.balance_label
        self.monthly_summary_table = (
            self.dashboard_widget.monthly_summary_table
        )
        self.category_breakdown_table = (
            self.dashboard_widget.category_breakdown_table
        )

    def _refresh_dashboard(self) -> None:
        """Refresh the dashboard and budget usage from the account."""
        self.dashboard_widget.refresh(self.account)
        self._refresh_budget_table()

    def _create_transactions_tab(self) -> None:
        """Create transaction entry, storage controls, and the table."""
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)

        transaction_form = self._create_transaction_form()
        json_controls = self._create_json_controls()
        csv_controls = self._create_csv_controls()
        self.transaction_table = self._create_transaction_table()

        transactions_layout.addLayout(transaction_form)
        transactions_layout.addLayout(json_controls)
        transactions_layout.addLayout(csv_controls)
        transactions_layout.addWidget(self.transaction_table)

        self.tab_widget.addTab(
            transactions_tab,
            "Transactions",
        )

    def _create_transaction_form(self) -> QFormLayout:
        """Create named input widgets for new transactions."""
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
            self._handle_add_transaction,
        )

        self.transaction_status_label = QLabel()
        self.transaction_status_label.setObjectName(
            "transaction_status_label",
        )

        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow(
            "Transaction type:",
            self.transaction_type_input,
        )
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Tags:", self.tags_input)
        form_layout.addRow(self.add_transaction_button)
        form_layout.addRow(
            "Status:",
            self.transaction_status_label,
        )

        return form_layout

    def _create_json_controls(self) -> QHBoxLayout:
        """Create account saving and loading buttons."""
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

    def _create_csv_controls(self) -> QHBoxLayout:
        """Create transaction import and export buttons."""
        csv_controls = QHBoxLayout()

        self.import_csv_button = QPushButton("Import CSV")
        self.import_csv_button.setObjectName("import_csv_button")
        self.import_csv_button.clicked.connect(
            self._handle_import_csv,
        )

        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.setObjectName("export_csv_button")
        self.export_csv_button.clicked.connect(
            self._handle_export_csv,
        )

        csv_controls.addWidget(self.import_csv_button)
        csv_controls.addWidget(self.export_csv_button)

        return csv_controls

    def _create_transaction_table(self) -> QTableWidget:
        """Create a read-only table with six transaction columns."""
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
        """Validate input, store a transaction, and refresh the views."""
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

        add_transaction(self.account, transaction)
        self._append_transaction_to_table(transaction)
        self._refresh_dashboard()
        self._clear_transaction_form()

        self.transaction_status_label.setText(
            "Transaction added successfully.",
        )

    def _handle_save_json(self) -> None:
        """Select a destination and save the current account."""
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
            save_account(self.account, selected_path)
        except (OSError, TypeError, ValueError) as error:
            self.transaction_status_label.setText(
                f"Account could not be saved: {error}",
            )
            return

        self.transaction_status_label.setText(
            "Account saved successfully.",
        )

    def _handle_load_json(self) -> None:
        """Load an account and rebuild all account-dependent views."""
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

    def _handle_import_csv(self) -> None:
        """Import valid CSV rows and display the import result."""
        selected_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Import transactions from CSV",
            "",
            "CSV files (*.csv)",
        )

        if not selected_path:
            return

        try:
            import_result = import_transactions(
                self.account,
                selected_path,
            )
        except (OSError, TypeError, ValueError) as error:
            self.transaction_status_label.setText(
                f"CSV file could not be imported: {error}",
            )
            return

        self._refresh_transaction_table()

        imported = import_result["imported"]
        skipped = import_result["skipped"]

        self.transaction_status_label.setText(
            f"Imported {imported} transaction(s); "
            f"skipped {skipped} row(s).",
        )

    def _handle_export_csv(self) -> None:
        """Select a destination and export account transactions."""
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export transactions as CSV",
            "transactions.csv",
            "CSV files (*.csv)",
        )

        if not selected_path:
            return

        if not selected_path.lower().endswith(".csv"):
            selected_path = f"{selected_path}.csv"

        try:
            export_transactions(self.account, selected_path)
        except (OSError, TypeError, ValueError) as error:
            self.transaction_status_label.setText(
                f"CSV file could not be exported: {error}",
            )
            return

        self.transaction_status_label.setText(
            "CSV exported successfully.",
        )

    def _refresh_transaction_table(self) -> None:
        """Rebuild transaction rows and refresh dashboard and budgets."""
        self.transaction_table.setRowCount(0)

        for transaction in self.account["transactions"]:
            self._append_transaction_to_table(transaction)

        self._refresh_dashboard()

    @staticmethod
    def _parse_tags(tags_text: str) -> set[str]:
        """Convert comma-separated text into unique non-empty tags."""
        return {
            tag.strip()
            for tag in tags_text.split(",")
            if tag.strip()
        }

    def _append_transaction_to_table(
        self,
        transaction: dict,
    ) -> None:
        """Append the display values of one validated transaction."""
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
            self.transaction_table.setItem(
                row,
                column,
                QTableWidgetItem(str(value)),
            )

    def _clear_transaction_form(self) -> None:
        """Clear text inputs after successfully adding a transaction."""
        self.description_input.clear()
        self.amount_input.clear()
        self.tags_input.clear()