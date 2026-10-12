"""Display monthly income and expenses in an embedded Matplotlib chart."""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from finance_tracker.analysis import monthly_summary


class MonthlyChartWidget(QWidget):
    """Compare monthly income and expenses without owning account data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the figure and embedded Qt canvas."""
        super().__init__(parent)
        self.setObjectName("monthly_chart_widget")

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

        self.refresh({"transactions": []})

    def refresh(self, account: dict) -> None:
        """Replace the chart with chronologically sorted monthly totals."""
        self.axes.clear()
        self.axes.set_facecolor("#ffffff")

        self.axes.set_title(
            "Monthly income and expenses",
            color="#243044",
            fontsize=14,
            fontweight="bold",
            pad=16,
        )
        self.axes.set_xlabel("Month", color="#243044")
        self.axes.set_ylabel("Amount", color="#243044")
        self.axes.tick_params(
            axis="both",
            colors="#243044",
            labelsize=10,
        )

        for spine in ("top", "right"):
            self.axes.spines[spine].set_visible(False)

        for spine in ("bottom", "left"):
            self.axes.spines[spine].set_color("#aab5c3")

        summary = monthly_summary(account)

        if not summary:
            self.axes.text(
                0.5,
                0.5,
                "No transactions yet.",
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

        months = sorted(summary)

        income = [
            summary[month]["income"]
            for month in months
        ]
        expenses = [
            summary[month]["expenses"]
            for month in months
        ]

        positions = list(range(len(months)))
        bar_width = 0.36

        income_bars = self.axes.bar(
            [position - bar_width / 2 for position in positions],
            income,
            width=bar_width,
            label="Income",
            color="#28704a",
        )
        expense_bars = self.axes.bar(
            [position + bar_width / 2 for position in positions],
            expenses,
            width=bar_width,
            label="Expenses",
            color="#b84a0b",
        )

        self.axes.set_xticks(positions)
        self.axes.set_xticklabels(
            months,
            rotation=30,
            ha="right",
        )

        self.axes.set_axisbelow(True)
        self.axes.grid(
            axis="y",
            color="#e0e5eb",
            linewidth=0.8,
        )

        maximum = max(income + expenses)
        self.axes.set_ylim(
            0,
            maximum * 1.2 if maximum > 0 else 1,
        )

        self.axes.bar_label(
            income_bars,
            labels=[f"{amount:.2f}" for amount in income],
            padding=3,
            color="#243044",
            fontsize=9,
        )
        self.axes.bar_label(
            expense_bars,
            labels=[f"{amount:.2f}" for amount in expenses],
            padding=3,
            color="#243044",
            fontsize=9,
        )

        self.axes.legend(
            frameon=False,
            labelcolor="#243044",
        )

        self.canvas.draw_idle()