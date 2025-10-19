"""Profiles ViewModel - manages profile CRUD and todos."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService
    from src.services.timer_service import TimerService


class ProfilesViewModel(QObject):
    """ViewModel for profiles management.
    
    Manages:
    - Profile CRUD operations
    - Profile duplication
    - Profile settings
    - Todo list for profiles
    """
    
    # Signals
    profiles_changed = Signal(list)  # List of profile dicts
    profile_selected = Signal(object)  # Optional[int] - profile_id
    todos_changed = Signal(list)  # List of todo dicts
    profile_services_changed = Signal(list)  # List of profile service dicts
    service_todos_changed = Signal(int, list)  # profile_service_id, list of todo dicts
    error_occurred = Signal(str, str)  # title, message
    
    def __init__(self, state_service: "StateService", timer_service: "TimerService") -> None:
        """Initialize profiles ViewModel.
        
        Args:
            state_service: Central state service
            timer_service: Timer service (for checking active timer)
        """
        super().__init__()
        self.state = state_service
        self.timer_service = timer_service
        self.repo = state_service.repository
        
        # Internal state
        self._profiles: List[dict] = []
        self._todos: List[dict] = []
        self._profile_services: List[dict] = []
        self._service_todos_cache: dict[int, List[dict]] = {}  # profile_service_id -> todos
        
        # Connect to state changes
        self.state.profiles_updated.connect(self._refresh_profiles)
        self.state.profile_changed.connect(self._on_profile_changed)
        
        # Initial load
        self._refresh_profiles()
    
    # Properties
    
    @property
    def profiles(self) -> List[dict]:
        """Get list of all profiles."""
        return self._profiles
    
    @property
    def current_profile(self) -> Optional[dict]:
        """Get currently selected profile."""
        return self.state.get_current_profile()
    
    @property
    def current_profile_id(self) -> Optional[int]:
        """Get currently selected profile ID."""
        return self.state.current_profile_id
    
    @property
    def todos(self) -> List[dict]:
        """Get todos for current profile."""
        return self._todos
    
    # Public methods - Profile CRUD
    
    def create_profile(
        self,
        name: str,
        target_seconds: Optional[int] = None,
        company: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> int:
        """Create a new profile.
        
        Args:
            name: Profile name
            target_seconds: Daily target in seconds
            company: Company name
            contact_person: Contact person name
            email: Contact email
            phone: Contact phone
            
        Returns:
            ID of created profile
        """
        profile_id = self.repo.create_profile(
            name, None, target_seconds, company, contact_person, email, phone
        )
        self.state.notify_profiles_updated()
        self.select_profile(profile_id)
        return profile_id
    
    def update_profile(
        self,
        profile_id: int,
        name: Optional[str] = None,
        target_seconds: Optional[int] = None,
        company: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Update profile information.
        
        Args:
            profile_id: Profile ID
            name: New name (if provided)
            target_seconds: New target (if provided)
            company: New company (if provided)
            contact_person: New contact person (if provided)
            email: New email (if provided)
            phone: New phone (if provided)
            notes: New notes (if provided)
        """
        prof = self.repo.get_profile(profile_id)
        if not prof:
            return
        
        # Update name
        if name is not None and name != prof["name"]:
            self.repo.rename_profile(profile_id, name)
        
        # Update target
        if target_seconds is not None or target_seconds != prof.get("target_seconds"):
            self.repo.set_profile_target_seconds(profile_id, target_seconds)
        
        # Update contacts
        if any(x is not None for x in [company, contact_person, email, phone]):
            self.repo.update_profile_contacts(
                profile_id,
                company if company is not None else prof.get("company"),
                contact_person if contact_person is not None else prof.get("contact_person"),
                email if email is not None else prof.get("email"),
                phone if phone is not None else prof.get("phone"),
            )
        
        # Update notes
        if notes is not None:
            self.repo.set_profile_notes(profile_id, notes)
        
        self.state.notify_profiles_updated()
    
    def delete_profile(self, profile_id: int, force: bool = False) -> bool:
        """Delete a profile.
        
        Args:
            profile_id: Profile ID to delete
            force: If True, skip active timer check
            
        Returns:
            True if deleted, False if blocked (timer running)
        """
        # Check if timer is running for this profile
        if not force:
            active = self.timer_service.get_active_entry()
            if active is not None and int(active["profile_id"]) == profile_id:
                return False  # View should confirm with user
        
        # Stop timer if running
        active = self.timer_service.get_active_entry()
        if active is not None and int(active["profile_id"]) == profile_id:
            self.timer_service.stop()
        
        self.repo.delete_profile(profile_id)
        self.state.notify_profiles_updated()
        self.state.notify_entries_updated()
        return True
    
    def duplicate_profile(self, source_id: int, new_name: str) -> int:
        """Duplicate a profile with a new name.
        
        Args:
            source_id: Source profile ID
            new_name: Name for the duplicated profile
            
        Returns:
            ID of new profile
        """
        prof = self.repo.get_profile(source_id)
        if prof is None:
            raise ValueError("Source profile not found")
        
        # Create new profile with copied fields
        target_seconds = int(prof["target_seconds"]) if prof["target_seconds"] is not None else None
        company = prof["company"] or None
        contact = prof["contact_person"] or None
        email = prof["email"] or None
        phone = prof["phone"] or None
        notes = prof["notes"] or None
        
        new_id = self.repo.create_profile(
            new_name, None, target_seconds, company, contact, email, phone, notes
        )
        
        # Copy todos
        for todo in self.repo.list_profile_todos(source_id):
            text = str(todo["text"])
            completed = int(todo["completed"]) if todo["completed"] is not None else 0
            new_todo_id = self.repo.add_profile_todo(new_id, text)
            if completed:
                self.repo.set_profile_todo_completed(new_todo_id, True)
        
        self.state.notify_profiles_updated()
        self.select_profile(new_id)
        return new_id
    
    def generate_unique_profile_name(self, base_name: str) -> str:
        """Generate a unique profile name for duplication.
        
        Args:
            base_name: Base name to derive from
            
        Returns:
            Unique name like "Base (Copy)" or "Base (Copy 2)"
        """
        existing = {str(r["name"]) for r in self.repo.list_profiles(include_archived=True)}
        candidate = f"{base_name} (Copy)"
        if candidate not in existing:
            return candidate
        
        idx = 2
        while True:
            candidate = f"{base_name} (Copy {idx})"
            if candidate not in existing:
                return candidate
            idx += 1
    
    def select_profile(self, profile_id: Optional[int]) -> None:
        """Select a profile as current.
        
        Args:
            profile_id: Profile ID to select, or None
        """
        self.state.set_current_profile(profile_id)
    
    # Public methods - Todos
    
    def add_todo(self, profile_id: int, text: str) -> None:
        """Add a todo to a profile.
        
        Args:
            profile_id: Profile ID
            text: Todo text
        """
        self.repo.add_profile_todo(profile_id, text)
        self._load_todos(profile_id)
    
    def delete_todo(self, todo_id: int, profile_id: int) -> None:
        """Delete a todo.
        
        Args:
            todo_id: Todo ID
            profile_id: Profile ID (for refresh)
        """
        self.repo.delete_profile_todo(todo_id)
        self._load_todos(profile_id)
    
    def toggle_todo_completed(self, todo_id: int, completed: bool, profile_id: int) -> None:
        """Toggle todo completion state.
        
        Args:
            todo_id: Todo ID
            completed: New completion state
            profile_id: Profile ID (for refresh)
        """
        self.repo.set_profile_todo_completed(todo_id, completed)
        self._load_todos(profile_id)
    
    def load_todos(self, profile_id: int) -> None:
        """Load todos for a profile.
        
        Args:
            profile_id: Profile ID
        """
        self._load_todos(profile_id)
    
    # Private methods
    
    def _refresh_profiles(self) -> None:
        """Refresh profiles list from database."""
        rows = self.repo.list_profiles()
        self._profiles = [dict(row) for row in rows]
        self.profiles_changed.emit(self._profiles)
    
    def _on_profile_changed(self, profile_id: Optional[int]) -> None:
        """Handle profile selection change."""
        self.profile_selected.emit(profile_id)
        if profile_id is not None:
            self._load_todos(profile_id)
            self._load_profile_services(profile_id)
    
    def _load_todos(self, profile_id: int) -> None:
        """Load todos for a profile.
        
        Args:
            profile_id: Profile ID
        """
        rows = self.repo.list_profile_todos(profile_id)
        self._todos = [dict(row) for row in rows]
        self.todos_changed.emit(self._todos)
    
    # Public methods - Profile Services
    
    def add_service_to_profile(self, profile_id: int, service_id: int, notes: str | None = None) -> int:
        """Add a service instance to a profile.
        
        Args:
            profile_id: Profile ID
            service_id: Service ID to add
            notes: Optional notes for this service instance
            
        Returns:
            ID of created profile service instance
        """
        profile_service_id = self.repo.add_profile_service(profile_id, service_id, notes)
        self._load_profile_services(profile_id)
        return profile_service_id
    
    def update_profile_service_notes(self, profile_service_id: int, notes: str | None, profile_id: int) -> None:
        """Update notes for a profile service instance.
        
        Args:
            profile_service_id: Profile service instance ID
            notes: New notes text
            profile_id: Profile ID (for refresh)
        """
        self.repo.update_profile_service_notes(profile_service_id, notes)
        self._load_profile_services(profile_id)
    
    def delete_profile_service(self, profile_service_id: int, profile_id: int) -> None:
        """Delete a profile service instance.
        
        Args:
            profile_service_id: Profile service instance ID
            profile_id: Profile ID (for refresh)
        """
        self.repo.delete_profile_service(profile_service_id)
        self._load_profile_services(profile_id)
    
    def load_profile_services(self, profile_id: int) -> None:
        """Load services for a profile.
        
        Args:
            profile_id: Profile ID
        """
        self._load_profile_services(profile_id)
    
    def _load_profile_services(self, profile_id: int) -> None:
        """Load profile services from database.
        
        Args:
            profile_id: Profile ID
        """
        rows = self.repo.list_profile_services(profile_id)
        self._profile_services = [dict(row) for row in rows]
        self.profile_services_changed.emit(self._profile_services)
    
    # Public methods - Profile Service Todos
    
    def add_service_todo(self, profile_service_id: int, text: str) -> None:
        """Add a todo to a profile service instance.
        
        Args:
            profile_service_id: Profile service instance ID
            text: Todo text
        """
        self.repo.add_profile_service_todo(profile_service_id, text)
        self._load_service_todos(profile_service_id)
    
    def toggle_service_todo_completed(self, todo_id: int, completed: bool, profile_service_id: int) -> None:
        """Toggle service todo completion state.
        
        Args:
            todo_id: Todo ID
            completed: New completion state
            profile_service_id: Profile service instance ID (for refresh)
        """
        self.repo.set_profile_service_todo_completed(todo_id, completed)
        self._load_service_todos(profile_service_id)
    
    def delete_service_todo(self, todo_id: int, profile_service_id: int) -> None:
        """Delete a service todo.
        
        Args:
            todo_id: Todo ID
            profile_service_id: Profile service instance ID (for refresh)
        """
        self.repo.delete_profile_service_todo(todo_id)
        self._load_service_todos(profile_service_id)
    
    def load_service_todos(self, profile_service_id: int) -> None:
        """Load todos for a profile service instance.
        
        Args:
            profile_service_id: Profile service instance ID
        """
        self._load_service_todos(profile_service_id)
    
    def _load_service_todos(self, profile_service_id: int) -> None:
        """Load service todos from database.
        
        Args:
            profile_service_id: Profile service instance ID
        """
        rows = self.repo.list_profile_service_todos(profile_service_id)
        todos = [dict(row) for row in rows]
        self._service_todos_cache[profile_service_id] = todos
        self.service_todos_changed.emit(profile_service_id, todos)

