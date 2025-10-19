"""Timer ViewModel - manages timer logic and time entries."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

from src.utils.formatters import format_duration

if TYPE_CHECKING:
    from src.services.state_service import StateService
    from src.services.timer_service import TimerService


class TimerViewModel(QObject):
    """ViewModel for timer view.
    
    Manages:
    - Timer start/stop logic
    - Time entries list
    - Progress calculation
    - Entry editing and deletion
    """
    
    # Signals
    timer_state_changed = Signal(bool)  # is_running
    elapsed_updated = Signal(int)  # seconds
    progress_updated = Signal(int, object)  # elapsed_seconds, target_seconds (Optional[int])
    entries_changed = Signal(list)  # List of entry dicts
    
    def __init__(self, state_service: "StateService", timer_service: "TimerService") -> None:
        """Initialize timer ViewModel.
        
        Args:
            state_service: Central state service
            timer_service: Timer service
        """
        super().__init__()
        self.state = state_service
        self.timer_service = timer_service
        self.repo = state_service.repository
        
        # Internal state
        self._entries: List[dict] = []
        self._elapsed_seconds: int = 0
        self._target_seconds: Optional[int] = None
        
        # Connect to state changes
        self.state.active_entry_changed.connect(self._on_active_entry_changed)
        self.state.profile_changed.connect(self._on_profile_changed)
        self.state.entries_updated.connect(self._refresh_entries)
        
        # Update timer for elapsed time
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(500)
        self._update_timer.timeout.connect(self._update_elapsed)
        self._update_timer.start()
        
        # Initial load
        self._refresh_entries()
        self._update_elapsed()
    
    # Properties
    
    @property
    def elapsed_seconds(self) -> int:
        """Get current elapsed seconds."""
        return self._elapsed_seconds
    
    @property
    def target_seconds(self) -> Optional[int]:
        """Get target seconds for current profile."""
        return self._target_seconds
    
    @property
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self.state.active_entry is not None
    
    @property
    def entries(self) -> List[dict]:
        """Get list of time entries."""
        return self._entries
    
    # Public methods
    
    def toggle_timer(self, note: str = "") -> None:
        """Toggle timer on/off.
        
        Args:
            note: Optional note for new entry
        """
        profile_id = self.state.current_profile_id
        if profile_id is None:
            return  # View should handle this case
        
        active = self.timer_service.get_active_entry()
        if active:
            self.timer_service.stop()
        else:
            self.timer_service.start(profile_id, note=note)
        
        self.timer_state_changed.emit(self.is_running)
    
    def update_entry_note_tags(self, entry_id: int, note: str, tags: str) -> None:
        """Update an entry's note and tags.
        
        Args:
            entry_id: Entry ID
            note: New note text
            tags: New tags (comma-separated)
        """
        self.repo.update_entry_note_tags(entry_id, note, tags)
        self.state.notify_entries_updated()
    
    def delete_entries(self, entry_ids: List[int]) -> None:
        """Delete multiple entries.
        
        Args:
            entry_ids: List of entry IDs to delete
        """
        if len(entry_ids) == 1:
            self.repo.delete_entry(entry_ids[0])
        else:
            self.repo.delete_entries(entry_ids)
        self.state.notify_entries_updated()
    
    def get_entry_by_index(self, index: int) -> Optional[dict]:
        """Get entry by table row index.
        
        Args:
            index: Row index
            
        Returns:
            Entry dict or None
        """
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None
    
    # Private methods
    
    def _on_active_entry_changed(self, entry: Optional[dict]) -> None:
        """Handle active entry change."""
        self.timer_state_changed.emit(self.is_running)
        self._update_elapsed()
    
    def _on_profile_changed(self, profile_id: Optional[int]) -> None:
        """Handle profile selection change."""
        self._refresh_entries()
        self._update_progress()
    
    def _refresh_entries(self) -> None:
        """Refresh entries list from database."""
        profile_id = self.state.current_profile_id
        rows = self.repo.list_entries(profile_id=profile_id)
        self._entries = [dict(row) for row in rows]
        self.entries_changed.emit(self._entries)
        self._update_progress()
    
    def _update_elapsed(self) -> None:
        """Update elapsed time for active entry."""
        active = self.state.active_entry
        if not active:
            self._elapsed_seconds = 0
            self.elapsed_updated.emit(0)
            self._update_progress()
            return
        
        start_s = int(active["start_ts"])
        dur = int(time.time()) - start_s
        self._elapsed_seconds = dur
        self.elapsed_updated.emit(dur)
        self._update_progress()
    
    def _update_progress(self) -> None:
        """Update progress calculation."""
        profile_id = self.state.current_profile_id
        elapsed = self._compute_elapsed_total_seconds(profile_id)
        
        target: Optional[int] = None
        if profile_id is not None:
            prof = self.repo.get_profile(profile_id)
            if prof and prof["target_seconds"] is not None:
                target = int(prof["target_seconds"])
        
        self._target_seconds = target
        self.progress_updated.emit(elapsed, target)
    
    def _compute_elapsed_total_seconds(self, profile_id: Optional[int]) -> int:
        """Compute total elapsed seconds for a profile today.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Total elapsed seconds
        """
        if profile_id is None:
            return 0
        
        now = int(time.time())
        total = 0
        rows = self.repo.list_entries(profile_id=profile_id)
        
        for r in rows:
            start_ts = int(r["start_ts"]) if r["start_ts"] is not None else None
            end_ts = int(r["end_ts"]) if r["end_ts"] is not None else now
            if start_ts is None:
                continue
            if end_ts > start_ts:
                total += end_ts - start_ts
        
        return total

