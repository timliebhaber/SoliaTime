"""Weekly view with list of weeks and tracked time."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.utils.formatters import format_duration

if TYPE_CHECKING:
    from src.viewmodels import WeeklyViewModel


class WeeklyView(QWidget):
    """Weekly view with list of weeks.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "WeeklyViewModel", parent: QWidget | None = None) -> None:
        """Initialize weekly view.
        
        Args:
            viewmodel: Weekly ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()
        self._connect_signals()
    
    def showEvent(self, event) -> None:  # type: ignore[override]
        """Handle show event to refresh data.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Refresh weeks when view is shown
        self.viewmodel._refresh_weeks()

    def _build_ui(self) -> None:
        """Build the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>Weekly Time Tracking</h2>")
        layout.addWidget(title)
        
        # Weeks table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Week", "Start Date", "End Date", "Total Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table, 1)

    def _connect_signals(self) -> None:
        """Connect UI and ViewModel signals."""
        # ViewModel → UI
        self.viewmodel.weeks_changed.connect(self._update_weeks_table)
        
        # Initial load
        self._update_weeks_table(self.viewmodel.weeks)
    
    def _update_weeks_table(self, weeks: list) -> None:
        """Update weeks table with new data.
        
        Args:
            weeks: List of week summary dicts
        """
        self.table.setRowCount(0)
        
        for week_data in weeks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            year = str(week_data.get("year", ""))
            week_number = str(week_data.get("week_number", ""))
            week_start_ts = int(week_data.get("week_start_ts", 0))
            week_end_ts = int(week_data.get("week_end_ts", 0))
            total_seconds = int(week_data.get("total_seconds", 0))
            
            # Calculate actual week start (Monday) and end (Sunday) from the week number
            # SQLite's %W uses Monday as the first day of week
            week_start_date = self._get_week_start_date(int(year), int(week_number))
            week_end_date = week_start_date + timedelta(days=6)
            
            # Week column (e.g., "CW 45" for calendar week 45)
            week_item = QTableWidgetItem(f"CW {week_number}")
            week_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, week_item)
            
            # Start date column
            start_item = QTableWidgetItem(week_start_date.strftime("%Y-%m-%d"))
            start_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, start_item)
            
            # End date column
            end_item = QTableWidgetItem(week_end_date.strftime("%Y-%m-%d"))
            end_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, end_item)
            
            # Total time column
            time_item = QTableWidgetItem(format_duration(total_seconds))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, time_item)
    
    def _get_week_start_date(self, year: int, week_number: int) -> datetime:
        """Get the Monday of a given week number.
        
        Args:
            year: Year
            week_number: Week number (0-based, where week 0 is first week with Monday)
            
        Returns:
            datetime object for Monday of that week
        """
        # SQLite's %W format: week number (0-53), Monday as first day of week
        # Week 0 is the first week with a Monday
        jan_1 = datetime(year, 1, 1)
        
        # Find the first Monday of the year (or earlier if Jan 1 is already Monday)
        days_since_monday = jan_1.weekday()  # 0 = Monday, 6 = Sunday
        if days_since_monday == 0:
            # Jan 1 is a Monday, this is week 0
            first_monday = jan_1
        else:
            # Find next Monday
            days_until_monday = 7 - days_since_monday
            first_monday = jan_1 + timedelta(days=days_until_monday)
        
        # Add the specified number of weeks
        target_monday = first_monday + timedelta(weeks=int(week_number))
        return target_monday

