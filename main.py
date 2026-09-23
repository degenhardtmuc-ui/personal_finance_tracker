"""Start the Personal Finance Tracker graphical application.

This module is the main entry point of the desktop application. It creates the
Qt application object, creates the main window, displays the window, and starts
the Qt event loop.

The graphical widgets and application behaviour are implemented in
``finance_tracker.gui.main_window``. Keeping the startup code in this separate
module makes the responsibilities clear:

- ``main.py`` starts the application.
- ``main_window.py`` defines the graphical user interface.
- The remaining modules contain the financial business logic.
"""

import sys

from PySide6.QtWidgets import QApplication

from finance_tracker.gui.main_window import MainWindow


def main() -> int:
    """Create and run the Personal Finance Tracker application.

    Qt requires exactly one QApplication object. This object manages the
    complete graphical application, including windows, user input, mouse
    clicks, keyboard input, and operating-system events.

    The main window is created and made visible with ``show()``. Calling
    ``app.exec()`` starts the Qt event loop. The event loop continues running
    until the user closes the application.

    Returns:
        The Qt application exit code. A value of zero normally means that the
        application was closed successfully.
    """
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())