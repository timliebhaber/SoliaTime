"""Circular progress widget for displaying elapsed vs target time."""
from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget


class CircularProgress(QWidget):
    """Non-interactive circular progress displaying elapsed vs target seconds."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._elapsed_seconds: int = 0
        self._target_seconds: int | None = None
        self._size = 64
        self.setMinimumSize(self._size, self._size)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(self._size, self._size)

    def set_values(self, elapsed_seconds: int, target_seconds: int | None) -> None:
        """Update the progress values and trigger repaint.
        
        Args:
            elapsed_seconds: Current elapsed time in seconds
            target_seconds: Target time in seconds, or None if no target
        """
        self._elapsed_seconds = max(0, int(elapsed_seconds))
        self._target_seconds = int(target_seconds) if target_seconds is not None else None
        self.update()

    def _ratio(self) -> float:
        """Calculate progress ratio (0.0 to 1.0)."""
        if not self._target_seconds or self._target_seconds <= 0:
            return 0.0
        return max(0.0, min(1.0, float(self._elapsed_seconds) / float(self._target_seconds)))

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(4, 4, -4, -4)
        base_pen = QPen(self.palette().mid().color(), 6)
        painter.setPen(base_pen)
        painter.drawEllipse(rect)

        ratio = self._ratio()
        if ratio > 0:
            # Use highlight color for progress arc
            progress_pen = QPen(self.palette().highlight().color(), 6)
            painter.setPen(progress_pen)
            # Start at 90 deg (top) and go clockwise negative angle
            start_angle = 90 * 16
            span_angle = int(-360 * 16 * ratio)
            painter.drawArc(rect, start_angle, span_angle)

        # Draw centered percentage text
        painter.setPen(QPen(self.palette().text().color()))
        percent_text = "—%"
        if self._target_seconds and self._target_seconds > 0:
            pct = int(max(0, min(100, math.ceil(ratio * 100))))
            percent_text = f"{pct}%"
        painter.drawText(self.rect(), Qt.AlignCenter, percent_text)

