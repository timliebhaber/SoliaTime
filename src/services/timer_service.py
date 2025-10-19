"""Timer management service with state integration."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService


class TimerService(QObject):
    """Timer service for starting and stopping time tracking.
    
    Integrates with StateService to manage active entry state.
    """
    
    # Signals
    timer_started = Signal(int)  # entry_id
    timer_stopped = Signal()
    
    def __init__(self, state_service: "StateService") -> None:
        """Initialize timer service.
        
        Args:
            state_service: Central state service
        """
        super().__init__()
        self.state = state_service
        self.repo = state_service.repository
    
    def get_active_entry(self) -> Optional[dict]:
        """Get the currently active entry.
        
        Returns:
            Active entry dict or None
        """
        return self.state.active_entry
    
    def start(self, profile_id: int, note: str = "", tags: list[str] | None = None, project_id: int | None = None) -> int:
        """Start a timer for the given profile.
        
        Args:
            profile_id: Profile to track time for
            note: Optional note for the entry
            tags: Optional tags for the entry
            project_id: Optional project to track time for
            
        Returns:
            ID of the created entry
        """
        # Ensure only one active entry system-wide
        if self.repo.get_active_entry() is not None:
            self.stop()
        
        entry_id = self.repo.start_entry(profile_id, note, ",".join(tags or []), project_id)
        prof = self.repo.get_profile(profile_id)
        
        # Log event
        self._log_event("START", profile_id, prof["name"] if prof else "", note)
        
        # Update state
        self.state.refresh_active_entry()
        self.state.notify_entries_updated()
        
        self.timer_started.emit(entry_id)
        return entry_id
    
    def stop(self) -> None:
        """Stop the currently active timer."""
        active = self.repo.get_active_entry()
        if active is None:
            return
        
        self.repo.stop_active_entry()
        
        # Log event
        prof = self.repo.get_profile(int(active["profile_id"]))
        self._log_event("STOP", int(active["profile_id"]), prof["name"] if prof else "", active["note"] or "")
        
        # Update state
        self.state.refresh_active_entry()
        self.state.notify_entries_updated()
        
        self.timer_stopped.emit()
    
    def _log_event(self, event: str, profile_id: int, profile_name: str, note: str) -> None:
        """Log a timer event to file.
        
        Args:
            event: Event type (START/STOP)
            profile_id: Profile ID
            profile_name: Profile name
            note: Entry note
        """
        from src.services.settings_service import get_data_dir
        import time
        
        log_path = get_data_dir() / "solia.log"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                f.write(
                    f"{event},{int(time.time())},{profile_id},{profile_name.replace(',', ' ')},{note.replace(',', ' ')}\n"
                )
        except Exception:
            pass

