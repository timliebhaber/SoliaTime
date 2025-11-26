"""Weekly ViewModel - manages weekly time tracking data."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService


class WeeklyViewModel(QObject):
    """ViewModel for weekly view.
    
    Manages:
    - Weekly aggregated time data
    - Week list display
    """
    
    # Signals
    weeks_changed = Signal(list)  # List of week summary dicts
    
    def __init__(self, state_service: "StateService") -> None:
        """Initialize weekly ViewModel.
        
        Args:
            state_service: Central state service
        """
        super().__init__()
        self.state = state_service
        self.repo = state_service.repository
        
        # Internal state
        self._weeks: List[dict] = []
        
        # Connect to state changes
        self.state.entries_updated.connect(self._refresh_weeks)
        
        # Initial load
        self._refresh_weeks()
    
    # Properties
    
    @property
    def weeks(self) -> List[dict]:
        """Get list of weekly summaries."""
        return self._weeks
    
    # Private methods
    
    def _refresh_weeks(self) -> None:
        """Refresh weeks list from database."""
        rows = self.repo.get_weekly_summary()
        self._weeks = [dict(row) for row in rows]
        self.weeks_changed.emit(self._weeks)

