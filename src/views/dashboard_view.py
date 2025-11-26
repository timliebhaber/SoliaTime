"""Dashboard view with navigation tiles."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.ui.components import TileButton

if TYPE_CHECKING:
    from src.viewmodels import DashboardViewModel


class DashboardView(QWidget):
    """Dashboard view with tiles for navigation.
    
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
        layout.addSpacing(40)
        
        # Tiles container
        tiles_container = QWidget()
        tiles_layout = QGridLayout(tiles_container)
        tiles_layout.setAlignment(Qt.AlignCenter)
        tiles_layout.setSpacing(20)
        
        # Timer tile
        self.timer_tile = TileButton("Timer", "⏱️")
        self.timer_tile.set_click_callback(self.viewmodel.request_navigate_to_timer)
        tiles_layout.addWidget(self.timer_tile, 0, 0)
        
        # Profiles tile
        self.profiles_tile = TileButton("Profiles", "👥")
        self.profiles_tile.set_click_callback(self.viewmodel.request_navigate_to_profiles)
        tiles_layout.addWidget(self.profiles_tile, 0, 1)
        
        # Projects tile
        self.projects_tile = TileButton("Projects", "📋")
        self.projects_tile.set_click_callback(self.viewmodel.request_navigate_to_projects)
        tiles_layout.addWidget(self.projects_tile, 1, 0)
        
        # Services tile
        self.services_tile = TileButton("Services", "💼")
        self.services_tile.set_click_callback(self.viewmodel.request_navigate_to_services)
        tiles_layout.addWidget(self.services_tile, 1, 1)
        
        # Weekly tile
        self.weekly_tile = TileButton("Weekly", "📅")
        self.weekly_tile.set_click_callback(self.viewmodel.request_navigate_to_weekly)
        tiles_layout.addWidget(self.weekly_tile, 2, 0)
        
        # Invoices tile
        self.invoices_tile = TileButton("Invoices", "📄")
        self.invoices_tile.set_click_callback(self.viewmodel.request_navigate_to_invoices)
        tiles_layout.addWidget(self.invoices_tile, 2, 1)
        
        # Mehrwertsteuer Calculator tile
        self.vat_tile = TileButton("MwSt Calculator", "🧮")
        self.vat_tile.set_click_callback(self.viewmodel.request_navigate_to_vat_calculator)
        tiles_layout.addWidget(self.vat_tile, 3, 0)
        
        layout.addWidget(tiles_container)
        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect ViewModel signals."""
        # Dashboard has no state to update from ViewModel
        pass

