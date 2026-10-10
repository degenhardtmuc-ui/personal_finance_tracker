"""Test the financial dashboard of the PySide6 interface."""

from PySide6.QtWidgets import QLabel

from finance_tracker.gui.main_window import MainWindow


def test_main_window_contains_dashboard_tab(qtbot) -> None:
    """Verify that the main window contains a Dashboard tab."""
    window = MainWindow()
    qtbot.addWidget(window)

    tab_names = [
        window.tab_widget.tabText(index)
        for index in range(window.tab_widget.count())
    ]

    assert "Dashboard" in tab_names


def test_dashboard_displays_zero_totals_for_empty_account(qtbot) -> None:
    """Verify that a new account displays zero financial totals."""
    window = MainWindow()
    qtbot.addWidget(window)

    for object_name in (
        "income_total_label",
        "expense_total_label",
        "balance_label",
    ):
        label = window.findChild(QLabel, object_name)

        assert label is not None, f"Missing dashboard label: {object_name}"
        assert label.text() == "0.00"