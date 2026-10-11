"""Provide a standalone dashboard for the current account."""

from PySide6.QtWidgets import (
    QFormLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from finance_tracker.account import (
    calculate_balance,
    calculate_expense_total,
    calculate_income_total,
)
from finance_tracker.analysis import category_breakdown, monthly_summary


class DashboardWidget(QWidget):
    """Display account totals, monthly summaries, and expense categories."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build an empty dashboard without owning an account."""
        super().__init__(parent)
        self.setObjectName("dashboard_widget")

        layout = QVBoxLayout(self)
        totals_layout = QFormLayout()

        self.income_total_label = QLabel("0.00")
        self.income_total_label.setObjectName("income_total_label")
        self.expense_total_label = QLabel("0.00")
        self.expense_total_label.setObjectName("expense_total_label")
        self.balance_label = QLabel("0.00")
        self.balance_label.setObjectName("balance_label")

        totals_layout.addRow("Income:", self.income_total_label)
        totals_layout.addRow("Expenses:", self.expense_total_label)
        totals_layout.addRow("Balance:", self.balance_label)

        self.monthly_summary_table = self._create_table(
            "monthly_summary_table",
            ["Month", "Income", "Expenses", "Balance"],
        )
        self.category_breakdown_table = self._create_table(
            "category_breakdown_table",
            ["Category", "Expenses"],
        )

        layout.addLayout(totals_layout)
        layout.addWidget(QLabel("Monthly summary"))
        layout.addWidget(self.monthly_summary_table)
        layout.addWidget(QLabel("Expenses by category"))
        layout.addWidget(self.category_breakdown_table)

    @staticmethod
    def _create_table(object_name: str, headers: list[str]) -> QTableWidget:
        """Create a named, read-only summary table with stretching columns."""
        table = QTableWidget()
        table.setObjectName(object_name)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )
        return table

    @staticmethod
    def _set_rows(table: QTableWidget, rows: list[list[str]]) -> None:
        """Replace all displayed rows without changing the account data."""
        table.setRowCount(0)
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))

    def refresh(self, account: dict) -> None:
        """Rebuild every dashboard value from the explicitly supplied account."""
        self.income_total_label.setText(f"{calculate_income_total(account):.2f}")
        self.expense_total_label.setText(f"{calculate_expense_total(account):.2f}")
        self.balance_label.setText(f"{calculate_balance(account):.2f}")

        monthly_rows = [
            [
                month,
                f"{totals['income']:.2f}",
                f"{totals['expenses']:.2f}",
                f"{totals['net']:.2f}",
            ]
            for month, totals in monthly_summary(account).items()
        ]
        self._set_rows(self.monthly_summary_table, monthly_rows)

        category_rows = [
            [category.value.title(), f"{amount:.2f}"]
            for category, amount in category_breakdown(account).items()
        ]
        self._set_rows(self.category_breakdown_table, category_rows)