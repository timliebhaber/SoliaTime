"""Week calendar component showing current week with optional day annotations."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QWidget


def _monday_of_week(d: date) -> date:
    """Return Monday of the week containing d (ISO week: Mon-Sun)."""
    return d - timedelta(days=d.weekday())


def _week_dates(d: date) -> list[date]:
    """Return [Mon, Tue, ..., Sun] for the week containing d."""
    monday = _monday_of_week(d)
    return [monday + timedelta(days=i) for i in range(7)]


DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class WeekCalendar(QFrame):
    """Displays 7 days (Mon–Sun) of the current week with optional annotations."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize week calendar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("""
            WeekCalendar {
                background-color: rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self._day_frames: list[QFrame] = []
        self._day_labels: list[QLabel] = []
        self._annotation_labels: list[QLabel] = []
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the 7-day grid."""
        layout = QGridLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        for col in range(7):
            day_frame = QFrame()
            day_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.08);
                    border-radius: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                }
            """)
            day_frame.setMinimumWidth(60)
            day_layout = QGridLayout(day_frame)
            day_layout.setContentsMargins(6, 6, 6, 6)
            day_layout.setSpacing(2)

            name_label = QLabel(DAY_NAMES[col])
            name_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
            day_layout.addWidget(name_label, 0, 0)

            date_label = QLabel("")
            date_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            day_layout.addWidget(date_label, 1, 0)

            annotation_label = QLabel("")
            annotation_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 10px;")
            annotation_label.setWordWrap(True)
            annotation_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            day_layout.addWidget(annotation_label, 2, 0)

            layout.addWidget(day_frame, 0, col)
            self._day_frames.append(day_frame)
            self._day_labels.append(date_label)
            self._annotation_labels.append(annotation_label)

    def set_week_and_events(
        self,
        week_dates: list[date],
        events: Mapping[str, str] | None = None,
    ) -> None:
        """Set the week to display and optional day annotations.

        Args:
            week_dates: List of 7 dates [Mon, Tue, ..., Sun]
            events: Optional dict mapping date string (YYYY-MM-DD) to annotation text
        """
        events = events or {}
        today = date.today()
        for i, d in enumerate(week_dates):
            if i < len(self._day_labels):
                self._day_labels[i].setText(str(d.day))
                key = d.isoformat()
                self._annotation_labels[i].setText(events.get(key, ""))
                self._annotation_labels[i].setVisible(bool(events.get(key)))
                # Highlight current day
                if d == today:
                    self._day_frames[i].setStyleSheet("""
                        QFrame {
                            background-color: rgba(255, 255, 255, 0.15);
                            border-radius: 8px;
                            border: 2px solid rgba(255, 255, 255, 0.25);
                        }
                    """)
                else:
                    self._day_frames[i].setStyleSheet("""
                        QFrame {
                            background-color: rgba(255, 255, 255, 0.08);
                            border-radius: 8px;
                            border: 1px solid rgba(255, 255, 255, 0.12);
                        }
                    """)

    def refresh(self, events: Mapping[str, str] | None = None) -> None:
        """Set calendar to current week and optional day annotations.

        Args:
            events: Optional dict mapping date string (YYYY-MM-DD) to annotation text
        """
        self.set_week_and_events(_week_dates(date.today()), events or {})
