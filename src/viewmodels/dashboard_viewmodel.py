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

