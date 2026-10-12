"""Display expense totals by category in an embedded Matplotlib chart."""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from finance_tracker.analysis import category_breakdown


class CategoryChartWidget(QWidget):
    """Display category expenses without owning account data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the figure, axes, and embedded Qt canvas."""
        super().__init__(parent)
        self.setObjectName("category_chart_widget")

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
        """Replace the chart using current expense totals by category."""
        self.axes.clear()

        self.axes.set_facecolor("#ffffff")
        self.axes.set_title(
            "Expenses by category",
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

        totals = category_breakdown(account)

        if not totals:
            self.axes.text(
                0.5,
                0.5,
                "No expenses yet.",
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

        sorted_totals = sorted(
            totals.items(),
            key=lambda item: (-item[1], item[0].value),
        )

        labels = [
            category.value.title()
            for category, amount in sorted_totals
        ]
        amounts = [
            amount
            for category, amount in sorted_totals
        ]

        bars = self.axes.barh(
            labels,
            amounts,
            color="#b84a0b",
            height=0.65,
        )

        # Display the largest expense category at the top.
        self.axes.invert_yaxis()

        self.axes.set_axisbelow(True)
        self.axes.grid(
            axis="x",
            color="#e0e5eb",
            linewidth=0.8,
        )
        self.axes.set_xlim(0, max(amounts) * 1.2)

        self.axes.bar_label(
            bars,
            labels=[f"{amount:.2f}" for amount in amounts],
            padding=5,
            color="#243044",
            fontsize=10,
        )

        self.canvas.draw_idle()