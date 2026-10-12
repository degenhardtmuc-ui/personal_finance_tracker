"""Provide a compact dashboard for the current account."""

from PySide6.QtWidgets import (
    QGridLayout,
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
from finance_tracker.analysis import (
    category_breakdown,
    monthly_summary,
)


class DashboardWidget(QWidget):
    """Display account totals and financial summary tables."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build a compact dashboard without owning an account."""
        super().__init__(parent)
        self.setObjectName("dashboard_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        layout.addLayout(self._create_totals_grid())

        self.monthly_summary_table = self._create_table(
            "monthly_summary_table",
            ["Month", "Income", "Expenses", "Balance"],
        )
        self.category_breakdown_table = self._create_table(
            "category_breakdown_table",
            ["Category", "Expenses"],
        )

        layout.addWidget(QLabel("Monthly summary"))
        layout.addWidget(self.monthly_summary_table, 1)

        layout.addWidget(QLabel("Expenses by category"))
        layout.addWidget(self.category_breakdown_table, 1)

    def _create_totals_grid(self) -> QGridLayout:
        """Arrange income, expenses, and balance in three columns."""
        grid = QGridLayout()
        grid.setObjectName("dashboard_totals_grid")
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        self.income_total_label = QLabel("0.00")
        self.income_total_label.setObjectName(
            "income_total_label",
        )

        self.expense_total_label = QLabel("0.00")
        self.expense_total_label.setObjectName(
            "expense_total_label",
        )

        self.balance_label = QLabel("0.00")
        self.balance_label.setObjectName("balance_label")

        totals = [
            ("Income", self.income_total_label),
            ("Expenses", self.expense_total_label),
            ("Balance", self.balance_label),
        ]

        for column, (label_text, value_label) in enumerate(totals):
            grid.addWidget(QLabel(label_text), 0, column)
            grid.addWidget(value_label, 1, column)
            grid.setColumnStretch(column, 1)

        return grid

    @staticmethod
    def _create_table(
        object_name: str,
        headers: list[str],
    ) -> QTableWidget:
        """Create a named, read-only table with stretching columns."""
        table = QTableWidget()
        table.setObjectName(object_name)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

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

    @staticmethod
    def _set_rows(
        table: QTableWidget,
        rows: list[list[str]],
    ) -> None:
        """Replace displayed rows without changing account data."""
        table.setRowCount(0)
        table.setRowCount(len(rows))

        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
                )

    def refresh(self, account: dict) -> None:
        """Rebuild all dashboard values from the supplied account."""
        self.income_total_label.setText(
            f"{calculate_income_total(account):.2f}",
        )
        self.expense_total_label.setText(
            f"{calculate_expense_total(account):.2f}",
        )
        self.balance_label.setText(
            f"{calculate_balance(account):.2f}",
        )

        monthly_rows = [
            [
                month,
                f"{totals['income']:.2f}",
                f"{totals['expenses']:.2f}",
                f"{totals['net']:.2f}",
            ]
            for month, totals in monthly_summary(account).items()
        ]

        self._set_rows(
            self.monthly_summary_table,
            monthly_rows,
        )

        category_rows = [
            [
                category.value.title(),
                f"{amount:.2f}",
            ]
            for category, amount in category_breakdown(account).items()
        ]

        self._set_rows(
            self.category_breakdown_table,
            category_rows,
        )