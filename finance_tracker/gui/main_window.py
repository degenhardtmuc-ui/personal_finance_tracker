"""Coordinate the Personal Finance Tracker GUI and session data.

The main window owns the current account and budget tracker.
Separate widgets display transactions, dashboard summaries, and budgets.
The main window validates submissions and performs file operations.
"""

from math import isfinite

from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QTabWidget,
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
from finance_tracker.gui.transactions_widget import TransactionsWidget
from finance_tracker.json_storage import (
    load_account,
    load_budgets,
    save_account,
    save_budgets,
)
from finance_tracker.transaction import create_transaction


class MainWindow(QMainWindow):
    """Manage session data and coordinate the three GUI components."""

    def __init__(self) -> None:
        """Initialize account data, budget data, and application tabs."""
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

    def _create_transactions_tab(self) -> None:
        """Embed transaction widgets and connect operation requests."""
        self.transactions_widget = TransactionsWidget()
        self.tab_widget.addTab(
            self.transactions_widget,
            "Transactions",
        )

        # Preserve existing access paths to the same widget instances.
        self.description_input = (
            self.transactions_widget.description_input
        )
        self.amount_input = self.transactions_widget.amount_input
        self.transaction_type_input = (
            self.transactions_widget.transaction_type_input
        )
        self.category_input = self.transactions_widget.category_input
        self.date_input = self.transactions_widget.date_input
        self.tags_input = self.transactions_widget.tags_input
        self.add_transaction_button = (
            self.transactions_widget.add_transaction_button
        )
        self.transaction_status_label = (
            self.transactions_widget.transaction_status_label
        )
        self.save_json_button = (
            self.transactions_widget.save_json_button
        )
        self.load_json_button = (
            self.transactions_widget.load_json_button
        )
        self.import_csv_button = (
            self.transactions_widget.import_csv_button
        )
        self.export_csv_button = (
            self.transactions_widget.export_csv_button
        )
        self.transaction_table = (
            self.transactions_widget.transaction_table
        )

        self.transactions_widget.add_transaction_requested.connect(
            self._handle_add_transaction,
        )
        self.transactions_widget.save_json_requested.connect(
            self._handle_save_json,
        )
        self.transactions_widget.load_json_requested.connect(
            self._handle_load_json,
        )
        self.transactions_widget.import_csv_requested.connect(
            self._handle_import_csv,
        )
        self.transactions_widget.export_csv_requested.connect(
            self._handle_export_csv,
        )

    def _create_dashboard_tab(self) -> None:
        """Embed the dashboard and preserve existing widget access."""
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(
            self.dashboard_widget,
            "Dashboard",
        )

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

    def _create_budgets_tab(self) -> None:
        """Embed the budget widget and connect operation requests."""
        self.budget_widget = BudgetWidget()
        self.tab_widget.addTab(
            self.budget_widget,
            "Budgets",
        )

        self.budget_category_input = (
            self.budget_widget.budget_category_input
        )
        self.budget_limit_input = (
            self.budget_widget.budget_limit_input
        )
        self.budget_month_input = (
            self.budget_widget.budget_month_input
        )
        self.set_budget_button = (
            self.budget_widget.set_budget_button
        )
        self.budget_status_label = (
            self.budget_widget.budget_status_label
        )
        self.save_budgets_button = (
            self.budget_widget.save_budgets_button
        )
        self.load_budgets_button = (
            self.budget_widget.load_budgets_button
        )
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

    def _handle_add_transaction(self) -> None:
        """Validate input, store a transaction, and update all views."""
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
        """Load an account and refresh all account-dependent views."""
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

    def _handle_set_budget(self) -> None:
        """Validate budget inputs and update the session tracker."""
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

    def _handle_save_budgets(self) -> None:
        """Select a destination and save the budget tracker."""
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
        """Load a validated tracker and update the budget overview."""
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

    def _refresh_transaction_table(self) -> None:
        """Rebuild transaction rows and refresh summaries and budgets."""
        self.transactions_widget.refresh(self.account)
        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """Refresh dashboard totals and current budget usage."""
        self.dashboard_widget.refresh(self.account)
        self._refresh_budget_table()

    def _refresh_budget_table(self) -> None:
        """Refresh budget rows from current session data."""
        self.budget_widget.refresh(
            self.budget_tracker,
            self.account,
        )

    def _append_transaction_to_table(
        self,
        transaction: dict,
    ) -> None:
        """Delegate transaction row rendering to the widget."""
        self.transactions_widget.append_transaction(transaction)

    def _clear_transaction_form(self) -> None:
        """Delegate text input clearing to the transaction widget."""
        self.transactions_widget.clear_form()

    @staticmethod
    def _parse_tags(tags_text: str) -> set[str]:
        """Convert comma-separated text into unique non-empty tags."""
        return {
            tag.strip()
            for tag in tags_text.split(",")
            if tag.strip()
        }