"""Project creation and editing dialog."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
)


class ProjectDialog(QDialog):
    """Dialog for creating or editing a project."""

    def __init__(
        self,
        parent=None,
        title: str = "Project",
        profiles: list = None,
        services: list = None,
        name: str = "",
        profile_id: Optional[int] = None,
        estimated_hours: float = 0,
        service_id: Optional[int] = None,
        deadline: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        invoice_sent: bool = False,
        invoice_paid: bool = False,
        notes: str = "",
    ) -> None:
        """Initialize project dialog.
        
        Args:
            parent: Parent widget
            title: Dialog window title
            profiles: List of profile dicts
            services: List of service dicts
            name: Project name
            profile_id: Profile ID
            estimated_hours: Estimated time in hours
            service_id: Service ID
            deadline: Deadline date
            start_date: Start date
            invoice_sent: Whether invoice has been sent
            invoice_paid: Whether invoice has been paid
            notes: Project notes
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.profiles = profiles or []
        self.services = services or []
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Profile selection
        self.profile_combo = QComboBox(self)
        self.profile_combo.addItem("Select Profile...", None)
        for prof in self.profiles:
            self.profile_combo.addItem(str(prof["name"]), int(prof["id"]))
        
        if profile_id is not None:
            idx = self.profile_combo.findData(profile_id)
            if idx >= 0:
                self.profile_combo.setCurrentIndex(idx)
        
        form.addRow("Profile", self.profile_combo)
        
        # Name field
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(name)
        form.addRow("Name", self.name_edit)
        
        # Estimated time (HH:MM format)
        self.estimated_time_edit = QLineEdit(self)
        self.estimated_time_edit.setPlaceholderText("HH:MM (e.g., 02:30)")
        # Convert hours to HH:MM format
        if estimated_hours > 0:
            hours = int(estimated_hours)
            minutes = int((estimated_hours - hours) * 60)
            self.estimated_time_edit.setText(f"{hours:02d}:{minutes:02d}")
        form.addRow("Estimated Time", self.estimated_time_edit)
        
        # Service selection
        self.service_combo = QComboBox(self)
        self.service_combo.addItem("None", None)
        for svc in self.services:
            self.service_combo.addItem(str(svc["name"]), int(svc["id"]))
        
        if service_id is not None:
            idx = self.service_combo.findData(service_id)
            if idx >= 0:
                self.service_combo.setCurrentIndex(idx)
        
        form.addRow("Service", self.service_combo)
        
        # Deadline
        self.deadline_edit = QDateEdit(self)
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setSpecialValueText("No deadline")
        self.deadline_edit.setMinimumDate(QDate(2000, 1, 1))
        
        if deadline is not None:
            qdate = QDate(deadline.year, deadline.month, deadline.day)
            self.deadline_edit.setDate(qdate)
        else:
            # Set to today's date by default for new projects
            today = datetime.now()
            self.deadline_edit.setDate(QDate(today.year, today.month, today.day))
        
        form.addRow("Deadline", self.deadline_edit)
        
        # Start Date
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setSpecialValueText("No start date")
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
        
        if start_date is not None:
            qdate = QDate(start_date.year, start_date.month, start_date.day)
            self.start_date_edit.setDate(qdate)
        else:
            # Set to minimum date to indicate "no start date"
            self.start_date_edit.setDate(QDate(2000, 1, 1))
        
        form.addRow("Start Date", self.start_date_edit)
        
        # Invoice checkboxes
        invoice_row = QHBoxLayout()
        self.invoice_sent_check = QCheckBox("Invoice sent", self)
        self.invoice_sent_check.setChecked(invoice_sent)
        self.invoice_paid_check = QCheckBox("Invoice paid", self)
        self.invoice_paid_check.setChecked(invoice_paid)
        invoice_row.addWidget(self.invoice_sent_check)
        invoice_row.addWidget(self.invoice_paid_check)
        invoice_row.addStretch()
        form.addRow("", invoice_row)
        
        # Notes
        self.notes_edit = QPlainTextEdit(self)
        self.notes_edit.setPlaceholderText("Notes about this project...")
        self.notes_edit.setPlainText(notes)
        self.notes_edit.setMaximumHeight(100)
        form.addRow("Notes", self.notes_edit)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_profile_id(self) -> Optional[int]:
        """Get the selected profile ID."""
        return self.profile_combo.currentData()

    def get_name(self) -> str:
        """Get the project name."""
        return self.name_edit.text().strip()

    def get_estimated_seconds(self) -> Optional[int]:
        """Get the estimated time in seconds from HH:MM format."""
        time_str = self.estimated_time_edit.text().strip()
        if not time_str:
            return None
        
        # Parse HH:MM format
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return None
            
            hours = int(parts[0])
            minutes = int(parts[1])
            
            if hours < 0 or minutes < 0 or minutes >= 60:
                return None
            
            return (hours * 3600) + (minutes * 60)
        except ValueError:
            return None

    def get_service_id(self) -> Optional[int]:
        """Get the selected service ID."""
        return self.service_combo.currentData()

    def get_deadline_timestamp(self) -> Optional[int]:
        """Get the deadline as a unix timestamp."""
        qdate = self.deadline_edit.date()
        if qdate == QDate(2000, 1, 1):
            return None
        dt = datetime(qdate.year(), qdate.month(), qdate.day())
        return int(dt.timestamp())

    def get_start_date_timestamp(self) -> Optional[int]:
        """Get the start date as a unix timestamp."""
        qdate = self.start_date_edit.date()
        if qdate == QDate(2000, 1, 1):
            return None
        dt = datetime(qdate.year(), qdate.month(), qdate.day())
        return int(dt.timestamp())

    def get_invoice_sent(self) -> bool:
        """Get whether invoice has been sent."""
        return self.invoice_sent_check.isChecked()

    def get_invoice_paid(self) -> bool:
        """Get whether invoice has been paid."""
        return self.invoice_paid_check.isChecked()

    def get_notes(self) -> Optional[str]:
        """Get the project notes."""
        notes = self.notes_edit.toPlainText().strip()
        return notes if notes else None

