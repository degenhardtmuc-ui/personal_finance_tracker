"""Provide the shared light theme for the Personal Finance Tracker."""


def build_stylesheet() -> str:
    """Return the application stylesheet with orange primary actions."""
    return """
        QMainWindow {
            background-color: #f7f8fa;
        }

        QWidget {
            color: #243044;
            font-size: 14px;
        }

        QTabWidget::pane {
            background-color: #f7f8fa;
            border: 1px solid #d0d6de;
            border-radius: 6px;
        }

        QTabBar::tab {
            background-color: #edf0f4;
            color: #243044;
            padding: 10px 20px;
            margin-right: 4px;
            border: 1px solid #d0d6de;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #b84a0b;
            font-weight: bold;
        }

        QTabBar::tab:hover:!selected {
            background-color: #e3e8ee;
        }

        QLabel {
            background-color: transparent;
        }

        QLineEdit,
        QComboBox,
        QDateEdit {
            background-color: #ffffff;
            color: #243044;
            border: 1px solid #aab5c3;
            border-radius: 6px;
            padding: 7px 10px;
            min-height: 20px;
            selection-background-color: #b84a0b;
            selection-color: #ffffff;
        }

        QLineEdit:focus,
        QComboBox:focus,
        QDateEdit:focus {
            border: 1px solid #b84a0b;
        }

        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #243044;
            border: 1px solid #aab5c3;
            selection-background-color: #b84a0b;
            selection-color: #ffffff;
            outline: 0;
        }

        QPushButton {
            background-color: #ffffff;
            color: #243044;
            border: 1px solid #aab5c3;
            border-radius: 6px;
            padding: 8px 14px;
            min-height: 20px;
        }

        QPushButton:hover {
            background-color: #edf0f4;
        }

        QPushButton:pressed {
            background-color: #e0e5eb;
        }

        QPushButton:focus {
            border: 1px solid #b84a0b;
        }

        QPushButton#add_transaction_button,
        QPushButton#set_budget_button {
            background-color: #b84a0b;
            color: #ffffff;
            border: 1px solid #b84a0b;
            font-weight: bold;
        }

        QPushButton#add_transaction_button:hover,
        QPushButton#set_budget_button:hover {
            background-color: #9e3f09;
            border-color: #9e3f09;
        }

        QPushButton#add_transaction_button:pressed,
        QPushButton#set_budget_button:pressed {
            background-color: #843507;
            border-color: #843507;
        }

        QPushButton#add_transaction_button:focus,
        QPushButton#set_budget_button:focus {
            border: 2px solid #243044;
        }

        QPushButton:disabled,
        QPushButton#add_transaction_button:disabled,
        QPushButton#set_budget_button:disabled {
            background-color: #edf0f4;
            color: #687486;
            border-color: #d0d6de;
        }

        QTableWidget {
            background-color: #ffffff;
            color: #243044;
            alternate-background-color: #f3f5f8;
            gridline-color: #e0e5eb;
            border: 1px solid #d0d6de;
            border-radius: 6px;
            selection-background-color: #fbe4d4;
            selection-color: #243044;
        }

        QTableWidget::item {
            padding: 5px;
        }

        QHeaderView::section {
            background-color: #e9edf2;
            color: #243044;
            border: none;
            border-bottom: 1px solid #d0d6de;
            padding: 8px;
            font-weight: bold;
        }

        QTableCornerButton::section {
            background-color: #e9edf2;
            border: none;
        }

        QLabel#income_total_label,
        QLabel#expense_total_label,
        QLabel#balance_label {
            font-size: 22px;
            font-weight: bold;
            padding: 4px 0;
        }

        QToolTip {
            background-color: #ffffff;
            color: #243044;
            border: 1px solid #aab5c3;
            padding: 6px;
        }
    """