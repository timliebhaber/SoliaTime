"""Dashboard ViewModel - navigation and message log."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QObject, Signal


class DashboardViewModel(QObject):
    """ViewModel for the dashboard view.

    Handles navigation and dashboard message log for display across the app.
    """

    # Navigation signals (middle tiles removed)
    navigate_to_timer = Signal()
    navigate_to_profiles = Signal()
    navigate_to_vat_calculator = Signal()

    # Notify view when messages change
    messages_updated = Signal()

    def __init__(self) -> None:
        """Initialize dashboard ViewModel."""
        super().__init__()
        self._messages: list[dict[str, Any]] = []
        self.add_message("SoliaTime initialized successfully", "info")

    def get_messages(self) -> list[dict[str, Any]]:
        """Return a copy of the message history for display.

        Returns:
            List of dicts with keys: text, timestamp, message_type
        """
        return list(self._messages)

    def add_message(self, text: str, message_type: str = "info") -> None:
        """Append a message to the log and notify the view.

        Args:
            text: Message content
            message_type: Optional type (info, warning, error, success)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._messages.append({
            "text": text,
            "timestamp": timestamp,
            "message_type": message_type,
        })
        self.messages_updated.emit()

    def request_navigate_to_timer(self) -> None:
        """Request navigation to timer view."""
        self.navigate_to_timer.emit()

    def request_navigate_to_profiles(self) -> None:
        """Request navigation to profiles view."""
        self.navigate_to_profiles.emit()

    def request_navigate_to_vat_calculator(self) -> None:
        """Request navigation to VAT calculator view."""
        self.navigate_to_vat_calculator.emit()

