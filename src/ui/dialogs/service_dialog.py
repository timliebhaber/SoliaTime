"""Service creation and editing dialog."""
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from src.utils.formatters import format_rate, format_time_hhmm, parse_rate_input, parse_time_input


class ServiceDialog(QDialog):
    """Dialog for creating or editing a service."""

    def __init__(
        self,
        parent=None,
        name: str = "",
        rate_cents: int | None = None,
        estimated_seconds: int | None = None,
    ) -> None:
        """Initialize service dialog.
        
        Args:
            parent: Parent widget
            name: Service name
            rate_cents: Hourly rate in cents
            estimated_seconds: Estimated time in seconds
        """
        super().__init__(parent)
        self.setWindowTitle("Service")
        layout = QVBoxLayout(self)
        
        # Name field
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(name)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_edit)
        
        # Hourly rate in EUR
        self.rate_edit = QLineEdit(self)
        self.rate_edit.setPlaceholderText("Stundensatz in EUR, z.B. 85,50")
        if rate_cents is not None:
            euros = rate_cents // 100
            cents = rate_cents % 100
            self.rate_edit.setText(f"{euros},{cents:02d}")
        layout.addWidget(QLabel("Stundensatz (EUR)"))
        layout.addWidget(self.rate_edit)
        
        # Estimated time HH:MM
        self.est_edit = QLineEdit(self)
        self.est_edit.setPlaceholderText("Estimated Time (HH:MM)")
        if estimated_seconds is not None and estimated_seconds > 0:
            self.est_edit.setText(format_time_hhmm(estimated_seconds))
        layout.addWidget(QLabel("Estimated Time (HH:MM)"))
        layout.addWidget(self.est_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> tuple[str, int | None, int | None]:
        """Get the service values.
        
        Returns:
            Tuple of (name, rate_cents, estimated_seconds)
        """
        name = self.name_edit.text().strip()
        rate_val = parse_rate_input(self.rate_edit.text())
        est_seconds = parse_time_input(self.est_edit.text())
        return name, rate_val, est_seconds

