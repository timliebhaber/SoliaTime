"""Message box component for displaying stacked messages."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


@dataclass
class MessageItem:
    """Single message with timestamp and optional type."""

    text: str
    timestamp: str
    message_type: str = "info"


class MessageBox(QFrame):
    """A box that displays messages vertically stacked, full width per message."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize message box.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(120)
        self.setMaximumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("""
            MessageBox {
                background-color: rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setContentsMargins(8, 8, 8, 8)
        self._messages_layout.setSpacing(6)
        self._messages_layout.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._messages_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll)

    def set_messages(self, messages: Sequence[MessageItem]) -> None:
        """Replace displayed messages with the given list.

        Args:
            messages: List of message items to display
        """
        self._clear_message_widgets()
        for msg in messages:
            self._add_message_row(msg)

    def _clear_message_widgets(self) -> None:
        """Remove all message row widgets."""
        while self._messages_layout.count():
            item = self._messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_message_row(self, msg: MessageItem) -> None:
        """Add a single message row to the layout.

        Args:
            msg: Message item to display
        """
        row = QFrame()
        row.setFrameShape(QFrame.StyledPanel)
        row.setStyleSheet(_style_for_type(msg.message_type))
        row.setMinimumHeight(36)
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(10, 4, 10, 4)
        row_layout.setSpacing(2)

        text_label = QLabel(msg.text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("background: transparent; border: none;")
        row_layout.addWidget(text_label)

        time_label = QLabel(msg.timestamp)
        time_label.setStyleSheet(
            "background: transparent; border: none; color: rgba(255,255,255,0.6); font-size: 11px;"
        )
        row_layout.addWidget(time_label)

        self._messages_layout.addWidget(row)


def _style_for_type(message_type: str) -> str:
    """Return stylesheet for a message type (info, warning, error, etc.)."""
    base = "border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);"
    if message_type == "warning":
        return base + " background-color: rgba(255, 193, 7, 0.15);"
    if message_type == "error":
        return base + " background-color: rgba(244, 67, 54, 0.15);"
    if message_type == "success":
        return base + " background-color: rgba(76, 175, 80, 0.15);"
    return base + " background-color: rgba(255, 255, 255, 0.08);"
