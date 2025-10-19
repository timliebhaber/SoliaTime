"""Services view with table and CRUD buttons."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import (
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.ui.dialogs import ServiceDialog
from src.utils.formatters import format_rate, format_time_hhmm

if TYPE_CHECKING:
    from src.viewmodels import ServicesViewModel


class ServicesView(QWidget):
    """Services view with table and CRUD operations.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "ServicesViewModel", parent: QWidget | None = None) -> None:
        """Initialize services view.
        
        Args:
            viewmodel: Services ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI components."""
        layout = QVBoxLayout(self)
        
        # Services table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Service", "Stundensatz (EUR)", "Estimated (HH:MM)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Buttons
        buttons = QHBoxLayout()
        self.add_btn = QPushButton("Add Service")
        self.edit_btn = QPushButton("Edit Service")
        self.delete_btn = QPushButton("Delete Service")
        
        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.edit_btn)
        buttons.addWidget(self.delete_btn)
        
        layout.addWidget(self.table, 1)
        layout.addLayout(buttons)

    def _connect_signals(self) -> None:
        """Connect UI and ViewModel signals."""
        # UI → ViewModel
        self.add_btn.clicked.connect(self._on_add_service)
        self.edit_btn.clicked.connect(self._on_edit_service)
        self.delete_btn.clicked.connect(self._on_delete_service)
        
        # ViewModel → UI
        self.viewmodel.services_changed.connect(self._update_services_table)
        
        # Initial load - populate with existing services from viewmodel
        self._update_services_table(self.viewmodel.services)
    
    # UI event handlers
    
    def _on_add_service(self) -> None:
        """Handle add service button."""
        dlg = ServiceDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        name, rate_cents, est_seconds = dlg.get_values()
        if not name:
            QMessageBox.information(self, "Invalid", "Bitte Name angeben.")
            return
        
        try:
            self.viewmodel.create_service(name, rate_cents or 0, est_seconds)
        except Exception as e:
            QMessageBox.warning(self, "Create failed", f"Could not create service: {e}")
    
    def _on_edit_service(self) -> None:
        """Handle edit service button."""
        row = self.table.currentRow()
        if row < 0:
            return
        
        service = self.viewmodel.get_service_by_index(row)
        if not service:
            return
        
        dlg = ServiceDialog(
            self,
            name=service["name"],
            rate_cents=int(service["rate_cents"]),
            estimated_seconds=(int(service["estimated_seconds"]) if service["estimated_seconds"] is not None else None),
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        name, rate_cents, est_seconds = dlg.get_values()
        if not name:
            QMessageBox.information(self, "Invalid", "Bitte Name angeben.")
            return
        
        try:
            self.viewmodel.update_service(int(service["id"]), name, rate_cents or 0, est_seconds)
        except Exception as e:
            QMessageBox.warning(self, "Update failed", f"Could not update service: {e}")
    
    def _on_delete_service(self) -> None:
        """Handle delete service button."""
        row = self.table.currentRow()
        if row < 0:
            return
        
        service = self.viewmodel.get_service_by_index(row)
        if not service:
            return
        
        reply = QMessageBox.question(self, "Delete Service", "Diesen Service löschen?")
        if reply != QMessageBox.Yes:
            return
        
        try:
            self.viewmodel.delete_service(int(service["id"]))
        except Exception as e:
            QMessageBox.warning(self, "Delete failed", f"Could not delete service: {e}")
    
    # ViewModel update handlers
    
    def _update_services_table(self, services: list) -> None:
        """Update services table with new data.
        
        Args:
            services: List of service dicts
        """
        self.table.setRowCount(0)
        
        for service in services:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name = str(service["name"])
            rate_cents = int(service["rate_cents"])
            est_seconds = int(service["estimated_seconds"]) if service["estimated_seconds"] is not None else None
            
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(format_rate(rate_cents)))
            
            if est_seconds and est_seconds > 0:
                est_text = format_time_hhmm(est_seconds)
            else:
                est_text = "—"
            self.table.setItem(row, 2, QTableWidgetItem(est_text))

