"""Dashboard ViewModel - minimal, only navigation."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class DashboardViewModel(QObject):
    """ViewModel for the dashboard view.
    
    Dashboard is primarily for navigation, so this ViewModel is minimal.
    """
    
    # Navigation signals
    navigate_to_timer = Signal()
    navigate_to_profiles = Signal()
    navigate_to_projects = Signal()
    navigate_to_services = Signal()
    navigate_to_weekly = Signal()
    navigate_to_invoices = Signal()
    navigate_to_vat_calculator = Signal()
    
    def __init__(self) -> None:
        """Initialize dashboard ViewModel."""
        super().__init__()
    
    def request_navigate_to_timer(self) -> None:
        """Request navigation to timer view."""
        self.navigate_to_timer.emit()
    
    def request_navigate_to_profiles(self) -> None:
        """Request navigation to profiles view."""
        self.navigate_to_profiles.emit()
    
    def request_navigate_to_projects(self) -> None:
        """Request navigation to projects view."""
        self.navigate_to_projects.emit()
    
    def request_navigate_to_services(self) -> None:
        """Request navigation to services view."""
        self.navigate_to_services.emit()
    
    def request_navigate_to_weekly(self) -> None:
        """Request navigation to weekly view."""
        self.navigate_to_weekly.emit()
    
    def request_navigate_to_invoices(self) -> None:
        """Request navigation to invoices view."""
        self.navigate_to_invoices.emit()
    
    def request_navigate_to_vat_calculator(self) -> None:
        """Request navigation to VAT calculator view."""
        self.navigate_to_vat_calculator.emit()

