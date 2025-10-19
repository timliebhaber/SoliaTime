"""Services ViewModel - manages service catalog."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService


class ServicesViewModel(QObject):
    """ViewModel for services management.
    
    Manages:
    - Service CRUD operations
    - Service list
    """
    
    # Signals
    services_changed = Signal(list)  # List of service dicts
    error_occurred = Signal(str, str)  # title, message
    
    def __init__(self, state_service: "StateService") -> None:
        """Initialize services ViewModel.
        
        Args:
            state_service: Central state service
        """
        super().__init__()
        self.state = state_service
        self.repo = state_service.repository
        
        # Internal state
        self._services: List[dict] = []
        
        # Connect to state changes
        self.state.services_updated.connect(self._refresh_services)
        
        # Initial load
        self._refresh_services()
    
    # Properties
    
    @property
    def services(self) -> List[dict]:
        """Get list of all services."""
        return self._services
    
    # Public methods - Service CRUD
    
    def create_service(
        self,
        name: str,
        rate_cents: int,
        estimated_seconds: Optional[int] = None,
    ) -> int:
        """Create a new service.
        
        Args:
            name: Service name
            rate_cents: Hourly rate in cents
            estimated_seconds: Estimated time in seconds
            
        Returns:
            ID of created service
        """
        service_id = self.repo.create_service(name, rate_cents, estimated_seconds)
        self.state.notify_services_updated()
        return service_id
    
    def update_service(
        self,
        service_id: int,
        name: str,
        rate_cents: int,
        estimated_seconds: Optional[int] = None,
    ) -> None:
        """Update service information.
        
        Args:
            service_id: Service ID
            name: New name
            rate_cents: New rate in cents
            estimated_seconds: New estimated time in seconds
        """
        self.repo.update_service(service_id, name, rate_cents, estimated_seconds)
        self.state.notify_services_updated()
    
    def delete_service(self, service_id: int) -> None:
        """Delete a service.
        
        Args:
            service_id: Service ID to delete
        """
        self.repo.delete_service(service_id)
        self.state.notify_services_updated()
    
    def get_service_by_index(self, index: int) -> Optional[dict]:
        """Get service by list index.
        
        Args:
            index: Row index
            
        Returns:
            Service dict or None
        """
        if 0 <= index < len(self._services):
            return self._services[index]
        return None
    
    # Private methods
    
    def _refresh_services(self) -> None:
        """Refresh services list from database."""
        rows = self.repo.list_services()
        self._services = [dict(row) for row in rows]
        self.services_changed.emit(self._services)

