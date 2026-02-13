"""Dialog to display full message log."""
from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.ui.components.message_box import MessageItem


class MessageLogDialog(QDialog):
    """Dialog showing all messages with timestamps in a scrollable list."""

    def __init__(
        self,
        messages: Sequence[MessageItem],
        parent: QWidget | None = None,
    ) -> None:
        """Initialize message log dialog.

        Args:
            messages: All messages to display (newest can be first or last)
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Message Log")
        self.setMinimumSize(480, 400)
        self.resize(520, 450)

        layout = QVBoxLayout(self)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(8)

        for msg in messages:
            row = QFrame()
            row.setFrameShape(QFrame.StyledPanel)
            row.setStyleSheet(_row_style(msg.message_type))
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(12, 6, 12, 6)
            row_layout.setSpacing(2)
            text_label = QLabel(msg.text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("background: transparent; border: none;")
            time_label = QLabel(msg.timestamp)
            time_label.setStyleSheet(
                "background: transparent; border: none; color: rgba(255,255,255,0.6); font-size: 11px;"
            )
            row_layout.addWidget(text_label)
            row_layout.addWidget(time_label)
            content_layout.addWidget(row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_box = QDialogButtonBox(Qt.AlignRight)
        button_box.addButton(close_btn, QDialogButtonBox.AcceptRole)
        layout.addWidget(button_box)


def _row_style(message_type: str) -> str:
    """Return stylesheet for a message row by type."""
    base = "border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);"
    if message_type == "warning":
        return base + " background-color: rgba(255, 193, 7, 0.15);"
    if message_type == "error":
        return base + " background-color: rgba(244, 67, 54, 0.15);"
    if message_type == "success":
        return base + " background-color: rgba(76, 175, 80, 0.15);"
    return base + " background-color: rgba(255, 255, 255, 0.08);"
