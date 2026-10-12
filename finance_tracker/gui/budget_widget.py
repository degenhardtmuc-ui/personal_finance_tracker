"""Provide a compact budget interface without owning account data."""

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

from finance_tracker.budget import (
    calculate_spent_amount,
    is_exceeded,
    remaining,
    usage_percentage,
)
from finance_tracker.category import Category


class BudgetWidget(QWidget):
    """Display compact budget inputs and emit operation requests."""

    set_budget_requested = Signal()
    save_budgets_requested = Signal()
    load_budgets_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the compact form, file controls, and budget overview."""
        super().__init__(parent)
        self.setObjectName("budget_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        layout.addLayout(self._create_form())
        layout.addLayout(self._create_submission_controls())
        layout.addLayout(self._create_file_controls())

        self.budget_table = self._create_table()

        # Allocate additional vertical space to the overview table.
        layout.addWidget(self.budget_table, 1)

    def _create_form(self) -> QGridLayout:
        """Arrange category, monthly limit, and month in three columns."""
        grid = QGridLayout()
        grid.setObjectName("budget_form_grid")
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        self.budget_category_input = QComboBox()
        self.budget_category_input.setObjectName(
            "budget_category_input",
        )
        self.budget_category_input.addItems(
            [category.value.title() for category in Category],
        )

        self.budget_limit_input = QLineEdit()
        self.budget_limit_input.setObjectName("budget_limit_input")
        self.budget_limit_input.setPlaceholderText("0.00")

        self.budget_month_input = QDateEdit()
        self.budget_month_input.setObjectName("budget_month_input")
        self.budget_month_input.setDisplayFormat("yyyy-MM")

        today = QDate.currentDate()
        self.budget_month_input.setDate(
            QDate(today.year(), today.month(), 1),
        )

        fields = [
            ("Category:", self.budget_category_input, 0),
            ("Monthly limit:", self.budget_limit_input, 1),
            ("Month:", self.budget_month_input, 2),
        ]

        for label_text, input_widget, column in fields:
            label = QLabel(label_text)
            label.setBuddy(input_widget)

            input_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )

            grid.addWidget(label, 0, column)
            grid.addWidget(input_widget, 1, column)
            grid.setColumnStretch(column, 1)

        return grid

    def _create_submission_controls(self) -> QHBoxLayout:
        """Place the Set budget button beside the status message."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)

        self.set_budget_button = QPushButton("Set budget")
        self.set_budget_button.setObjectName("set_budget_button")
        self.set_budget_button.clicked.connect(
            self.set_budget_requested.emit,
        )

        self.budget_status_label = QLabel()
        self.budget_status_label.setObjectName("budget_status_label")
        self.budget_status_label.setWordWrap(True)

        controls.addWidget(self.set_budget_button)
        controls.addWidget(self.budget_status_label, 1)

        return controls

    def _create_file_controls(self) -> QHBoxLayout:
        """Group the budget saving and loading buttons."""
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)

        self.save_budgets_button = QPushButton("Save budgets")
        self.save_budgets_button.setObjectName("save_budgets_button")
        self.save_budgets_button.clicked.connect(
            self.save_budgets_requested.emit,
        )

        self.load_budgets_button = QPushButton("Load budgets")
        self.load_budgets_button.setObjectName("load_budgets_button")
        self.load_budgets_button.clicked.connect(
            self.load_budgets_requested.emit,
        )

        controls.addWidget(QLabel("JSON"))
        controls.addWidget(self.save_budgets_button)
        controls.addWidget(self.load_budgets_button)
        controls.addStretch(1)

        return controls

    @staticmethod
    def _create_table() -> QTableWidget:
        """Create the read-only, seven-column budget overview."""
        table = QTableWidget()
        table.setObjectName("budget_table")
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            [
                "Month",
                "Category",
                "Limit",
                "Spent",
                "Remaining",
                "Usage",
                "Status",
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

    def refresh(self, budget_tracker: dict, account: dict) -> None:
        """Rebuild the overview from the explicitly supplied data."""
        self.budget_table.setRowCount(0)

        for budget in budget_tracker["budgets"]:
            spent = calculate_spent_amount(budget, account)
            remaining_amount = remaining(budget, account)
            usage = usage_percentage(budget, account)
            exceeded = is_exceeded(budget, account)

            values = [
                budget["month"],
                budget["category"].value.title(),
                f"{budget['monthly_limit']:.2f}",
                f"{spent:.2f}",
                f"{remaining_amount:.2f}",
                f"{usage:.2f}%",
                "Exceeded" if exceeded else "Within budget",
            ]

            row = self.budget_table.rowCount()
            self.budget_table.insertRow(row)

            for column, value in enumerate(values):
                self.budget_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
                )