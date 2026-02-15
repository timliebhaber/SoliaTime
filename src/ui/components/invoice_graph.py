"""Area chart component for invoice amounts over time."""
from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import QPointF, Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget


class InvoiceGraph(QFrame):
    """Area chart with dates on x-axis and money (euros) on y-axis."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize invoice graph.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(280, 160)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet("""
            InvoiceGraph {
                background-color: rgba(255, 255, 255, 0.06);
                border-radius: 12px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        self._data: list[tuple[str, float]] = []

    def set_data(self, data: Sequence[tuple[str, float]]) -> None:
        """Set chart data: list of (month_label, amount_euros).

        Args:
            data: Ordered list of (x_label, y_value) e.g. [("Jan 2026", 150.0), ...]
        """
        self._data = list(data)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Draw the area chart."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self._data:
            painter.setPen(QColor(255, 255, 255, 120))
            font = QFont(self.font())
            font.setPointSize(11)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No invoice data")
            painter.end()
            return
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin_left = 48
        margin_right = 16
        margin_top = 16
        margin_bottom = 32
        w = self.width()
        h = self.height()
        chart_w = max(1, w - margin_left - margin_right)
        chart_h = max(1, h - margin_top - margin_bottom)

        values = [v for _, v in self._data]
        max_val = max(values) if values else 1.0
        if max_val <= 0:
            max_val = 1.0
        n = len(self._data)

        # Grid and axes
        pen_axis = QPen(QColor(255, 255, 255, 80))
        pen_axis.setWidth(1)
        painter.setPen(pen_axis)
        font = QFont(self.font())
        font.setPointSize(8)
        painter.setFont(font)

        # Y-axis labels and grid (500€ steps)
        step_amount = 500.0
        max_steps = int(max_val / step_amount) + 1
        grid_max = max_steps * step_amount
        
        for i in range(max_steps + 1):
            amount = i * step_amount
            y_ratio = 1.0 - (amount / grid_max)
            y = margin_top + y_ratio * chart_h
            label = f"€{int(amount)}"
            painter.drawText(QRectF(0, y - 8, margin_left - 4, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, label)
            if i > 0:
                painter.drawLine(int(margin_left), int(y), int(margin_left + chart_w), int(y))

        # X-axis and labels
        for i in range(n):
            x = margin_left + (i + 0.5) / max(n, 1) * chart_w
            label = self._data[i][0]
            painter.drawText(QRectF(x - 24, h - margin_bottom, 48, 20), Qt.AlignmentFlag.AlignCenter, label[:7])

        # Area and line
        points: list[QPointF] = []
        for i in range(n):
            v = self._data[i][1]
            x = margin_left + (i + 0.5) / max(n, 1) * chart_w
            y = margin_top + (1.0 - v / grid_max) * chart_h
            points.append(QPointF(x, y))

        if len(points) >= 2:
            path = QPainterPath()
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
            path.lineTo(points[-1].x(), margin_top + chart_h)
            path.lineTo(points[0].x(), margin_top + chart_h)
            path.closeSubpath()
            painter.fillPath(path, QBrush(QColor(255, 255, 255, 40)))
            painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
            painter.drawPolyline(points)
        elif len(points) == 1:
            painter.fillRect(
                int(points[0].x() - 4),
                int(points[0].y()),
                8,
                int(margin_top + chart_h - points[0].y()),
                QBrush(QColor(255, 255, 255, 40)),
            )
            painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
            painter.drawPoint(int(points[0].x()), int(points[0].y()))

        painter.end()
