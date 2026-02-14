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

from src.ui.components import InvoiceGraph, MessageBox, MessageItem, WeekCalendar
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
        self._refresh_calendar()
        self._refresh_invoice_graph()

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
        layout.addSpacing(16)

        # Calendar (left) and invoice graph (right)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        self.week_calendar = WeekCalendar(self)
        self.invoice_graph = InvoiceGraph(self)
        bottom_row.addWidget(self.week_calendar, 1)
        bottom_row.addWidget(self.invoice_graph, 1)
        layout.addLayout(bottom_row)
        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect ViewModel signals."""
        self.viewmodel.messages_updated.connect(self._refresh_messages)
        self.viewmodel.invoice_data_updated.connect(self._refresh_invoice_graph)
        self.viewmodel.calendar_events_updated.connect(self._refresh_calendar)

    def _refresh_messages(self) -> None:
        """Update message box from viewmodel."""
        messages = self.viewmodel.get_messages()
        self.message_box.set_messages(_dicts_to_message_items(messages))

    def _refresh_calendar(self) -> None:
        """Update week calendar from viewmodel."""
        self.week_calendar.refresh(self.viewmodel.get_calendar_events())

    def _refresh_invoice_graph(self) -> None:
        """Update invoice graph from viewmodel."""
        self.invoice_graph.set_data(self.viewmodel.get_invoice_chart_data())

    def _open_message_log(self) -> None:
        """Open dialog with full message log."""
        messages = self.viewmodel.get_messages()
        dialog = MessageLogDialog(_dicts_to_message_items(messages), self)
        dialog.exec()

