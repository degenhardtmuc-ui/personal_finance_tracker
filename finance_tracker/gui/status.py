"""Provide shared helpers for success and error status messages."""

from PySide6.QtWidgets import QLabel


def _show_status(
    label: QLabel,
    message: str,
    status: str,
) -> None:
    """Set the message and refresh styling for its status property."""
    label.setText(message)
    label.setProperty("status", status)

    # Reapply stylesheet rules after changing a dynamic property.
    style = label.style()
    style.unpolish(label)
    style.polish(label)

    label.updateGeometry()
    label.update()


def show_success(label: QLabel, message: str) -> None:
    """Display a message with the shared success appearance."""
    _show_status(label, message, "success")


def show_error(label: QLabel, message: str) -> None:
    """Display a message with the shared error appearance."""
    _show_status(label, message, "error")