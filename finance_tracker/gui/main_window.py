"""Coordinate session data, transaction editing, and financial views."""

from math import isfinite

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QFileDialog, QMainWindow, QTabWidget

from finance_tracker.account import add_transaction, create_account
from finance_tracker.budget import create_budget_tracker, set_budget
from finance_tracker.category import Category, TransactionType
from finance_tracker.csv_storage import (
    export_transactions,
    import_transactions,
)
from finance_tracker.gui.budget_chart import BudgetChartWidget
from finance_tracker.gui.budget_widget import BudgetWidget
from finance_tracker.gui.category_chart import CategoryChartWidget
from finance_tracker.gui.dashboard_widget import DashboardWidget
from finance_tracker.gui.monthly_chart import MonthlyChartWidget
from finance_tracker.gui.status import show_error, show_success
from finance_tracker.gui.styles import build_stylesheet
from finance_tracker.gui.transactions_widget import TransactionsWidget
from finance_tracker.json_storage import (
    load_account,
    load_budgets,
    save_account,
    save_budgets,
)
from finance_tracker.transaction import create_transaction


class MainWindow(QMainWindow):
    """Manage session data and coordinate application operations."""

    def __init__(self) -> None:
        """Initialize session data, editing state, and application tabs."""
        super().__init__()

        self.setStyleSheet(build_stylesheet())

        self.account = create_account("Personal Finance")
        self.budget_tracker = create_budget_tracker()
        self._editing_transaction_index: int | None = None

        self.setWindowTitle("Personal Finance Tracker")
        self.setMinimumSize(900, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self._create_transactions_tab()
        self._create_dashboard_tab()
        self._create_budgets_tab()
        self._create_charts_tab()
        self._refresh_dashboard()

    def _create_transactions_tab(self) -> None:
        """Embed transaction controls and connect operation requests."""
        self.transactions_widget = TransactionsWidget()
        self.tab_widget.addTab(self.transactions_widget, "Transactions")

        # Each alias references the existing widget, not a copy.
        widget_names = [
            "description_input",
            "amount_input",
            "transaction_type_input",
            "category_input",
            "date_input",
            "tags_input",
            "add_transaction_button",
            "save_changes_button",
            "cancel_edit_button",
            "transaction_status_label",
            "save_json_button",
            "load_json_button",
            "import_csv_button",
            "export_csv_button",
            "transaction_table",
        ]

        for name in widget_names:
            setattr(self, name, getattr(self.transactions_widget, name))

        self.transactions_widget.add_transaction_requested.connect(
            self._handle_add_transaction,
        )
        self.transactions_widget.save_changes_requested.connect(
            self._handle_save_changes,
        )
        self.transactions_widget.cancel_edit_requested.connect(
            self._handle_cancel_edit,
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
        self.transaction_table.itemSelectionChanged.connect(
            self._handle_transaction_selection,
        )

    def _create_dashboard_tab(self) -> None:
        """Embed the dashboard and preserve existing widget access."""
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")

        for name in [
            "income_total_label",
            "expense_total_label",
            "balance_label",
            "monthly_summary_table",
            "category_breakdown_table",
        ]:
            setattr(self, name, getattr(self.dashboard_widget, name))

    def _create_budgets_tab(self) -> None:
        """Embed budget controls and connect operation requests."""
        self.budget_widget = BudgetWidget()
        self.tab_widget.addTab(self.budget_widget, "Budgets")

        for name in [
            "budget_category_input",
            "budget_limit_input",
            "budget_month_input",
            "set_budget_button",
            "budget_status_label",
            "save_budgets_button",
            "load_budgets_button",
            "budget_table",
        ]:
            setattr(self, name, getattr(self.budget_widget, name))

        self.budget_widget.set_budget_requested.connect(
            self._handle_set_budget,
        )
        self.budget_widget.save_budgets_requested.connect(
            self._handle_save_budgets,
        )
        self.budget_widget.load_budgets_requested.connect(
            self._handle_load_budgets,
        )

    def _create_charts_tab(self) -> None:
        """Embed the three financial charts in separate subtabs."""
        self.chart_tabs = QTabWidget()
        self.chart_tabs.setObjectName("chart_tabs")

        self.category_chart = CategoryChartWidget()
        self.monthly_chart = MonthlyChartWidget()
        self.budget_chart = BudgetChartWidget()

        self.chart_tabs.addTab(self.category_chart, "Categories")
        self.chart_tabs.addTab(self.monthly_chart, "Monthly")
        self.chart_tabs.addTab(self.budget_chart, "Budgets")

        self.tab_widget.addTab(self.chart_tabs, "Charts")

    def _read_transaction_form(self) -> dict | None:
        """Create a validated transaction or display a validation error."""
        amount_text = self.amount_input.text().strip()

        try:
            amount = float(amount_text)
        except ValueError:
            show_error(
                self.transaction_status_label,
                "Amount must be a valid number.",
            )
            return None

        if not isfinite(amount):
            show_error(
                self.transaction_status_label,
                "Amount must be a valid number.",
            )
            return None

        try:
            return create_transaction(
                description=self.description_input.text().strip(),
                amount=amount,
                transaction_type=TransactionType(
                    self.transaction_type_input.currentText().lower(),
                ),
                category=Category(
                    self.category_input.currentText().lower(),
                ),
                date=self.date_input.date().toString("yyyy-MM-dd"),
                tags=self._parse_tags(self.tags_input.text()),
            )
        except ValueError as error:
            show_error(self.transaction_status_label, str(error))
            return None

    def _handle_add_transaction(self) -> None:
        """Validate and add a transaction when not editing."""
        if self._editing_transaction_index is not None:
            return

        transaction = self._read_transaction_form()
        if transaction is None:
            return

        add_transaction(self.account, transaction)
        self._append_transaction_to_table(transaction)
        self._refresh_dashboard()
        self._clear_transaction_form()

        show_success(
            self.transaction_status_label,
            "Transaction added successfully.",
        )

    def _handle_transaction_selection(self) -> None:
        """Load the selected account transaction into the form."""
        selected_rows = (
            self.transaction_table.selectionModel().selectedRows()
        )

        if not selected_rows:
            if self._editing_transaction_index is not None:
                self._finish_edit()
            return

        index = selected_rows[0].row()
        if not 0 <= index < len(self.account["transactions"]):
            self._finish_edit()
            return

        self._editing_transaction_index = index
        self.transactions_widget.load_transaction(
            self.account["transactions"][index],
        )
        self.transactions_widget.set_edit_mode(True)

    def _handle_save_changes(self) -> None:
        """Replace the selected transaction only after validation."""
        index = self._editing_transaction_index

        if index is None:
            return

        if not 0 <= index < len(self.account["transactions"]):
            self._finish_edit()
            show_error(
                self.transaction_status_label,
                "The selected transaction is no longer available.",
            )
            return

        transaction = self._read_transaction_form()
        if transaction is None:
            return

        self.account["transactions"][index] = transaction
        self._refresh_transaction_table()

        show_success(
            self.transaction_status_label,
            "Transaction updated successfully.",
        )

    def _handle_cancel_edit(self) -> None:
        """Discard unsaved form changes and return to entry mode."""
        if self._editing_transaction_index is None:
            return

        self._finish_edit()
        show_success(
            self.transaction_status_label,
            "Editing cancelled. No changes were saved.",
        )

    def _finish_edit(self) -> None:
        """Clear selection and editing state without changing account data."""
        self._editing_transaction_index = None

        # Programmatic selection changes must not load another transaction.
        with QSignalBlocker(self.transaction_table):
            self.transaction_table.clearSelection()
            self.transaction_table.setCurrentCell(-1, -1)

        self.transactions_widget.set_edit_mode(False)
        self._clear_transaction_form()

    def _handle_save_json(self) -> None:
        """Save the current account, excluding unsaved form edits."""
        selected_path, _ = QFileDialog.getSaveFileName(
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
            show_error(
                self.transaction_status_label,
                f"Account could not be saved: {error}",
            )
            return

        show_success(
            self.transaction_status_label,
            "Account saved successfully.",
        )

    def _handle_load_json(self) -> None:
        """Replace the account and reset editing after successful loading."""
        selected_path, _ = QFileDialog.getOpenFileName(
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
            show_error(
                self.transaction_status_label,
                f"Account could not be loaded: {error}",
            )
            return

        self.account = loaded_account
        self._refresh_transaction_table()

        show_success(
            self.transaction_status_label,
            "Account loaded successfully.",
        )

    def _handle_import_csv(self) -> None:
        """Import transactions and reset editing when rebuilding the table."""
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import transactions from CSV",
            "",
            "CSV files (*.csv)",
        )
        if not selected_path:
            return

        try:
            result = import_transactions(self.account, selected_path)
        except (OSError, TypeError, ValueError) as error:
            show_error(
                self.transaction_status_label,
                f"CSV file could not be imported: {error}",
            )
            return

        self._refresh_transaction_table()

        message = (
            f"Imported {result['imported']} transaction(s); "
            f"skipped {result['skipped']} row(s)."
        )

        if result["skipped"]:
            show_error(self.transaction_status_label, message)
        else:
            show_success(self.transaction_status_label, message)

    def _handle_export_csv(self) -> None:
        """Export stored transactions without applying unsaved form edits."""
        selected_path, _ = QFileDialog.getSaveFileName(
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
            show_error(
                self.transaction_status_label,
                f"CSV file could not be exported: {error}",
            )
            return

        show_success(
            self.transaction_status_label,
            "CSV exported successfully.",
        )

    def _handle_set_budget(self) -> None:
        """Validate budget inputs and update the current tracker."""
        try:
            monthly_limit = float(
                self.budget_limit_input.text().strip(),
            )
        except ValueError:
            show_error(
                self.budget_status_label,
                "Monthly limit must be a valid number.",
            )
            return

        if not isfinite(monthly_limit):
            show_error(
                self.budget_status_label,
                "Monthly limit must be a valid number.",
            )
            return

        try:
            set_budget(
                self.budget_tracker,
                category=Category(
                    self.budget_category_input.currentText().lower(),
                ),
                monthly_limit=monthly_limit,
                month=self.budget_month_input.date().toString("yyyy-MM"),
            )
        except ValueError as error:
            show_error(self.budget_status_label, str(error))
            return

        self._refresh_budget_table()
        show_success(
            self.budget_status_label,
            "Budget saved for this session.",
        )

    def _handle_save_budgets(self) -> None:
        """Select a destination and save the current budget tracker."""
        selected_path, _ = QFileDialog.getSaveFileName(
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
            show_error(
                self.budget_status_label,
                f"Budgets could not be saved: {error}",
            )
            return

        show_success(
            self.budget_status_label,
            "Budgets saved successfully.",
        )

    def _handle_load_budgets(self) -> None:
        """Load validated budgets and refresh their financial views."""
        selected_path, _ = QFileDialog.getOpenFileName(
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
            show_error(
                self.budget_status_label,
                f"Budgets could not be loaded: {error}",
            )
            return

        self.budget_tracker = loaded_tracker
        self._refresh_budget_table()

        show_success(
            self.budget_status_label,
            "Budgets loaded successfully.",
        )

    def _refresh_transaction_table(self) -> None:
        """Reset editing, rebuild rows, and refresh all financial views."""
        self._finish_edit()

        with QSignalBlocker(self.transaction_table):
            self.transactions_widget.refresh(self.account)

        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        """Refresh totals, budgets, and account-based charts."""
        self.dashboard_widget.refresh(self.account)
        self._refresh_budget_table()
        self.category_chart.refresh(self.account)
        self.monthly_chart.refresh(self.account)

    def _refresh_budget_table(self) -> None:
        """Refresh the budget table and comparison chart."""
        self.budget_widget.refresh(self.budget_tracker, self.account)
        self.budget_chart.refresh(self.budget_tracker, self.account)

    def _append_transaction_to_table(self, transaction: dict) -> None:
        """Render one transaction without triggering selection handling."""
        with QSignalBlocker(self.transaction_table):
            self.transactions_widget.append_transaction(transaction)

    def _clear_transaction_form(self) -> None:
        """Delegate clearing of text fields to the transaction widget."""
        self.transactions_widget.clear_form()

    @staticmethod
    def _parse_tags(tags_text: str) -> set[str]:
        """Convert comma-separated text into unique non-empty tags."""
        return {
            tag.strip()
            for tag in tags_text.split(",")
            if tag.strip()
        }