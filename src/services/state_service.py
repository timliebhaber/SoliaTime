"""Central state management service for the application."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal

from src.models.repository import Repository
from src.services.settings_service import AppSettings, SettingsStore


class StateService(QObject):
    """Central state manager using Singleton pattern.
    
    Manages:
    - Currently selected profile
    - Active timer entry
    - Application settings
    
    Emits signals when state changes to notify ViewModels and Views.
    """
    
    # Signals for state changes
    profile_changed = Signal(object)  # Optional[int] - profile_id
    active_entry_changed = Signal(object)  # Optional[dict] - entry
    entries_updated = Signal()
    profiles_updated = Signal()
    services_updated = Signal()
    settings_changed = Signal(object)  # AppSettings
    
    _instance: Optional["StateService"] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern: only one instance allowed."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, repository: Repository, settings_store: SettingsStore) -> None:
        """Initialize state service.
        
        Args:
            repository: Database repository
            settings_store: Settings persistence store
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        super().__init__()
        self._repository = repository
        self._settings_store = settings_store
        
        # State
        self._current_profile_id: Optional[int] = None
        self._active_entry: Optional[dict] = None
        self._settings: AppSettings = settings_store.load()
        
        # Load last profile if available
        if self._settings.last_profile_id:
            self._current_profile_id = self._settings.last_profile_id
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> Optional["StateService"]:
        """Get the singleton instance.
        
        Returns:
            The StateService instance, or None if not initialized
        """
        return cls._instance
    
    # Profile state
    
    @property
    def current_profile_id(self) -> Optional[int]:
        """Get currently selected profile ID."""
        return self._current_profile_id
    
    def set_current_profile(self, profile_id: Optional[int]) -> None:
        """Set the currently selected profile.
        
        Args:
            profile_id: Profile ID to select, or None
        """
        if self._current_profile_id != profile_id:
            self._current_profile_id = profile_id
            # Persist to settings
            self._settings.last_profile_id = profile_id
            self._settings_store.save(self._settings)
            self.profile_changed.emit(profile_id)
    
    def get_current_profile(self) -> Optional[dict]:
        """Get the currently selected profile data.
        
        Returns:
            Profile dict or None
        """
        if self._current_profile_id is None:
            return None
        row = self._repository.get_profile(self._current_profile_id)
        return dict(row) if row else None
    
    # Active entry state
    
    @property
    def active_entry(self) -> Optional[dict]:
        """Get the active timer entry."""
        return self._active_entry
    
    def set_active_entry(self, entry: Optional[dict]) -> None:
        """Set the active timer entry.
        
        Args:
            entry: Entry dict or None
        """
        self._active_entry = entry
        self.active_entry_changed.emit(entry)
    
    def refresh_active_entry(self) -> None:
        """Refresh active entry from database."""
        row = self._repository.get_active_entry()
        self._active_entry = dict(row) if row else None
        self.active_entry_changed.emit(self._active_entry)
    
    # Settings state
    
    @property
    def settings(self) -> AppSettings:
        """Get application settings."""
        return self._settings
    
    def update_settings(self, settings: AppSettings) -> None:
        """Update application settings.
        
        Args:
            settings: New settings to save
        """
        self._settings = settings
        self._settings_store.save(settings)
        self.settings_changed.emit(settings)
    
    # Notify methods for data changes
    
    def notify_entries_updated(self) -> None:
        """Notify that time entries have been updated."""
        self.entries_updated.emit()
    
    def notify_profiles_updated(self) -> None:
        """Notify that profiles have been updated."""
        self.profiles_updated.emit()
    
    def notify_services_updated(self) -> None:
        """Notify that services have been updated."""
        self.services_updated.emit()
    
    # Repository access (convenience methods)
    
    @property
    def repository(self) -> Repository:
        """Get the repository instance."""
        return self._repository

