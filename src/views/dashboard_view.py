"""Dashboard view with navigation tiles and message box."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.components import MessageBox, MessageItem
from src.ui.dialogs import MessageLogDialog

if TYPE_CHECKING:
    from src.viewmodels import DashboardViewModel


def _dicts_to_message_items(messages: list[dict]) -> list[MessageItem]:
    """Convert viewmodel message dicts to MessageItem list."""
    return [
        MessageItem(
            m["text"],
            m["timestamp"],
            m.get("message_type", "info"),
        )
        for m in messages
    ]


class DashboardView(QWidget):
    """Dashboard view with tiles for navigation and message display.

    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "DashboardViewModel", parent: QWidget | None = None) -> None:
        """Initialize dashboard view.

        Args:
            viewmodel: Dashboard ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()
        self._connect_signals()
        self._refresh_messages()

    def _build_ui(self) -> None:
        """Build the UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title_label = QLabel("SoliaTime")
        title_font = title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(24)

        # Message box
        self.message_box = MessageBox(self)
        layout.addWidget(self.message_box)
        layout.addSpacing(8)

        # View log button (right-aligned)
        row = QHBoxLayout()
        row.addStretch()
        self.view_log_btn = QPushButton("View log")
        self.view_log_btn.clicked.connect(self._open_message_log)
        row.addWidget(self.view_log_btn)
        layout.addLayout(row)
        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect ViewModel signals."""
        self.viewmodel.messages_updated.connect(self._refresh_messages)

    def _refresh_messages(self) -> None:
        """Update message box from viewmodel."""
        messages = self.viewmodel.get_messages()
        self.message_box.set_messages(_dicts_to_message_items(messages))

    def _open_message_log(self) -> None:
        """Open dialog with full message log."""
        messages = self.viewmodel.get_messages()
        dialog = MessageLogDialog(_dicts_to_message_items(messages), self)
        dialog.exec()

