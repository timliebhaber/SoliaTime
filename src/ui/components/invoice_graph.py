"""Bar chart component for invoice amounts over time."""
from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget


class InvoiceGraph(QFrame):
    """Bar chart with dates on x-axis and money (euros) on y-axis."""

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
        self._data: list[tuple[str, float, int]] = []  # (month_abbr, amount, year)

    def set_data(self, data: Sequence[tuple[str, float, int]]) -> None:
        """Set chart data: list of (month_abbr, amount_euros, year).

        Args:
            data: Ordered list of (month_name, y_value, year) e.g. [("Jan", 150.0, 2026), ...]
        """
        self._data = list(data)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        """Draw the bar chart."""
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

        margin_left = 48
        margin_right = 16
        margin_top = 16
        margin_bottom = 44  # Increased for two lines of labels
        w = self.width()
        h = self.height()
        chart_w = max(1, w - margin_left - margin_right)
        chart_h = max(1, h - margin_top - margin_bottom)

        values = [v for _, v, _ in self._data]
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

        # Draw bars
        bar_spacing = 4
        bar_width = max(4, (chart_w - (n - 1) * bar_spacing) / n)
        
        for i in range(n):
            month_name, amount, year = self._data[i]
            x = margin_left + i * (bar_width + bar_spacing)
            bar_height = (amount / grid_max) * chart_h
            y_top = margin_top + chart_h - bar_height
            
            painter.fillRect(
                int(x),
                int(y_top),
                int(bar_width),
                int(bar_height),
                QBrush(QColor(255, 255, 255, 100))
            )
            painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
            painter.drawRect(int(x), int(y_top), int(bar_width), int(bar_height))

        # X-axis labels: month names
        painter.setPen(QColor(255, 255, 255, 180))
        for i in range(n):
            month_name = self._data[i][0]
            x_center = margin_left + i * (bar_width + bar_spacing) + bar_width / 2
            painter.drawText(
                QRectF(x_center - 20, h - margin_bottom + 2, 40, 14),
                Qt.AlignmentFlag.AlignCenter,
                month_name
            )

        # Year labels: centered under June and July for each year change
        painter.setPen(QColor(255, 255, 255, 140))
        font_year = QFont(self.font())
        font_year.setPointSize(7)
        painter.setFont(font_year)
        
        # Track year transitions and place year labels
        seen_years: dict[int, list[int]] = {}  # year -> list of month indices
        for i, (month_name, _, year) in enumerate(self._data):
            if year not in seen_years:
                seen_years[year] = []
            seen_years[year].append(i)
        
        for year, indices in seen_years.items():
            # Find June or July in this year's months, or use middle month
            june_idx = None
            july_idx = None
            for idx in indices:
                month_name = self._data[idx][0]
                if month_name == "Jun":
                    june_idx = idx
                if month_name == "Jul":
                    july_idx = idx
            
            # Prefer June/July boundary, otherwise use middle of year's months
            if june_idx is not None and july_idx is not None:
                label_idx = (june_idx + july_idx) / 2
            elif june_idx is not None:
                label_idx = june_idx
            elif july_idx is not None:
                label_idx = july_idx
            else:
                label_idx = (indices[0] + indices[-1]) / 2
            
            x_center = margin_left + label_idx * (bar_width + bar_spacing) + bar_width / 2
            painter.drawText(
                QRectF(x_center - 30, h - margin_bottom + 18, 60, 14),
                Qt.AlignmentFlag.AlignCenter,
                str(year)
            )

        painter.end()
