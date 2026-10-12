"""Compare budget limits and matching expenses in a Matplotlib chart."""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from finance_tracker.budget import calculate_spent_amount


class BudgetChartWidget(QWidget):
    """Display budget limits and spending without owning session data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the figure, plotting area, and embedded Qt canvas."""
        super().__init__(parent)
        self.setObjectName("budget_chart_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.figure = Figure(
            figsize=(7, 4),
            layout="constrained",
            facecolor="#f7f8fa",
        )
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

        layout.addWidget(self.canvas, 1)

        self.refresh(
            {"budgets": []},
            {"transactions": []},
        )

    def refresh(self, budget_tracker: dict, account: dict) -> None:
        """Replace the chart using current budgets and matching expenses."""
        self.axes.clear()
        self.axes.set_facecolor("#ffffff")

        self.axes.set_title(
            "Budget limits and spending",
            color="#243044",
            fontsize=14,
            fontweight="bold",
            pad=16,
        )
        self.axes.set_xlabel("Amount", color="#243044")
        self.axes.tick_params(
            axis="both",
            colors="#243044",
            labelsize=10,
        )

        for spine in ("top", "right", "left"):
            self.axes.spines[spine].set_visible(False)

        self.axes.spines["bottom"].set_color("#aab5c3")

        budgets = sorted(
            budget_tracker["budgets"],
            key=lambda budget: (
                budget["month"],
                budget["category"].value,
            ),
        )

        if not budgets:
            self.axes.text(
                0.5,
                0.5,
                "No budgets yet.",
                transform=self.axes.transAxes,
                ha="center",
                va="center",
                color="#687486",
                fontsize=12,
            )
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.canvas.draw_idle()
            return

        labels = [
            f"{budget['month']} · {budget['category'].value.title()}"
            for budget in budgets
        ]
        limits = [
            budget["monthly_limit"]
            for budget in budgets
        ]
        spent = [
            calculate_spent_amount(budget, account)
            for budget in budgets
        ]

        positions = list(range(len(budgets)))
        bar_height = 0.34

        limit_bars = self.axes.barh(
            [position - bar_height / 2 for position in positions],
            limits,
            height=bar_height,
            label="Limit",
            color="#687486",
        )
        spent_bars = self.axes.barh(
            [position + bar_height / 2 for position in positions],
            spent,
            height=bar_height,
            label="Spent",
            color="#b84a0b",
        )

        self.axes.set_yticks(positions)
        self.axes.set_yticklabels(labels)
        self.axes.invert_yaxis()

        self.axes.set_axisbelow(True)
        self.axes.grid(
            axis="x",
            color="#e0e5eb",
            linewidth=0.8,
        )

        maximum = max(limits + spent)
        self.axes.set_xlim(
            0,
            maximum * 1.25 if maximum > 0 else 1,
        )

        self.axes.bar_label(
            limit_bars,
            labels=[f"{amount:.2f}" for amount in limits],
            padding=4,
            color="#243044",
            fontsize=9,
        )
        self.axes.bar_label(
            spent_bars,
            labels=[f"{amount:.2f}" for amount in spent],
            padding=4,
            color="#243044",
            fontsize=9,
        )

        self.axes.legend(
            frameon=False,
            labelcolor="#243044",
        )

        self.canvas.draw_idle()