"""Test shared application styling and main-window integration."""

import pytest

from PySide6.QtWidgets import QApplication

from finance_tracker.gui.main_window import MainWindow
from finance_tracker.gui.styles import build_stylesheet


@pytest.fixture(scope="module")
def application():
    """Provide a QApplication for GUI style tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_stylesheet_defines_shared_widget_styles():
    """Provide styling for the main interface elements."""
    stylesheet = build_stylesheet()

    assert isinstance(stylesheet, str)
    assert stylesheet.strip()

    expected_selectors = [
        "QMainWindow",
        "QTabWidget::pane",
        "QTabBar::tab",
        "QLineEdit",
        "QComboBox",
        "QDateEdit",
        "QPushButton",
        "QTableWidget",
        "QHeaderView::section",
    ]

    for selector in expected_selectors:
        assert selector in stylesheet


def test_stylesheet_identifies_primary_actions():
    """Style submission buttons through their existing object names."""
    stylesheet = build_stylesheet()

    assert "QPushButton#add_transaction_button" in stylesheet
    assert "QPushButton#set_budget_button" in stylesheet


def test_main_window_applies_shared_stylesheet(application):
    """Apply the central stylesheet to the main application window."""
    window = MainWindow()

    try:
        assert window.styleSheet() == build_stylesheet()
    finally:
        window.close()
        window.deleteLater()