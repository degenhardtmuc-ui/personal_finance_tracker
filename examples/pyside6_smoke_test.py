"""Verify that a minimal PySide6 application starts successfully."""

import sys

from PySide6.QtWidgets import QApplication, QLabel


def main() -> int:
    """Create and run a minimal PySide6 application."""
    app = QApplication(sys.argv)

    label = QLabel("Personal Finance Tracker")
    label.setWindowTitle("PySide6 Smoke Test")
    label.resize(400, 100)
    label.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())