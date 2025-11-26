"""Projects ViewModel - manages project CRUD and project todos."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from src.services.state_service import StateService


class ProjectsViewModel(QObject):
    """ViewModel for projects management.
    
    Manages:
    - Project CRUD operations
    - Project todos
    - Association with profiles and services
    """
    
    # Signals
    projects_changed = Signal(list)  # List of project dicts
    project_selected = Signal(object)  # Optional[int] - project_id
    todos_changed = Signal(list)  # List of todo dicts
    profiles_changed = Signal(list)  # List of profile dicts
    services_changed = Signal(list)  # List of service dicts
    error_occurred = Signal(str, str)  # title, message
    
    def __init__(self, state_service: "StateService") -> None:
        """Initialize projects ViewModel.
        
        Args:
            state_service: Central state service
        """
        super().__init__()
        self.state = state_service
        self.repo = state_service.repository
        
        # Internal state
        self._projects: List[dict] = []
        self._todos: List[dict] = []
        self._profiles: List[dict] = []
        self._services: List[dict] = []
        self._current_project_id: Optional[int] = None
        self._selected_profile_id: Optional[int] = None
        
        # Connect to state changes
        self.state.profiles_updated.connect(self._refresh_profiles)
        
        # Initial load
        self._refresh_profiles()
        self._refresh_services()
        self._refresh_projects()
    
    # Properties
    
    @property
    def projects(self) -> List[dict]:
        """Get list of all projects."""
        return self._projects
    
    @property
    def profiles(self) -> List[dict]:
        """Get list of all profiles."""
        return self._profiles
    
    @property
    def services(self) -> List[dict]:
        """Get list of all services."""
        return self._services
    
    @property
    def current_project_id(self) -> Optional[int]:
        """Get currently selected project ID."""
        return self._current_project_id
    
    @property
    def selected_profile_id(self) -> Optional[int]:
        """Get currently selected profile ID for filtering."""
        return self._selected_profile_id
    
    @property
    def todos(self) -> List[dict]:
        """Get todos for current project."""
        return self._todos
    
    # Public methods - Project CRUD
    
    def create_project(
        self,
        profile_id: int,
        name: str,
        estimated_seconds: Optional[int] = None,
        service_id: Optional[int] = None,
        deadline_ts: Optional[int] = None,
        start_date_ts: Optional[int] = None,
        invoice_sent: bool = False,
        invoice_paid: bool = False,
        notes: Optional[str] = None,
    ) -> int:
        """Create a new project.
        
        Args:
            profile_id: Profile ID this project belongs to
            name: Project name
            estimated_seconds: Estimated time in seconds
            service_id: Service ID (optional)
            deadline_ts: Deadline timestamp (optional)
            start_date_ts: Start date timestamp (optional)
            invoice_sent: Whether invoice has been sent
            invoice_paid: Whether invoice has been paid
            notes: Project notes
            
        Returns:
            ID of created project
        """
        project_id = self.repo.create_project(
            profile_id, name, estimated_seconds, service_id, deadline_ts,
            start_date_ts, invoice_sent, invoice_paid, notes
        )
        self._refresh_projects()
        self.select_project(project_id)
        return project_id
    
    def update_project(
        self,
        project_id: int,
        name: str,
        estimated_seconds: Optional[int],
        service_id: Optional[int],
        deadline_ts: Optional[int],
        start_date_ts: Optional[int],
        invoice_sent: bool,
        invoice_paid: bool,
        notes: Optional[str],
    ) -> None:
        """Update project information.
        
        Args:
            project_id: Project ID
            name: Project name
            estimated_seconds: Estimated time in seconds
            service_id: Service ID (can be None)
            deadline_ts: Deadline timestamp (can be None)
            start_date_ts: Start date timestamp (can be None)
            invoice_sent: Whether invoice has been sent
            invoice_paid: Whether invoice has been paid
            notes: Project notes
        """
        self.repo.update_project(
            project_id, name, estimated_seconds, service_id, deadline_ts,
            start_date_ts, invoice_sent, invoice_paid, notes
        )
        self._refresh_projects()
    
    def delete_project(self, project_id: int) -> None:
        """Delete a project.
        
        Args:
            project_id: Project ID to delete
        """
        self.repo.delete_project(project_id)
        if self._current_project_id == project_id:
            self._current_project_id = None
            self.project_selected.emit(None)
        self._refresh_projects()
    
    def select_project(self, project_id: Optional[int]) -> None:
        """Select a project as current.
        
        Args:
            project_id: Project ID to select, or None
        """
        self._current_project_id = project_id
        self.project_selected.emit(project_id)
        if project_id is not None:
            self._load_todos(project_id)
        else:
            self._todos = []
            self.todos_changed.emit([])
    
    def select_profile_filter(self, profile_id: Optional[int]) -> None:
        """Select a profile to filter projects by.
        
        Args:
            profile_id: Profile ID to filter by, or None for all
        """
        self._selected_profile_id = profile_id
        self._refresh_projects()
    
    # Public methods - Todos
    
    def add_todo(self, project_id: int, text: str) -> None:
        """Add a todo to a project.
        
        Args:
            project_id: Project ID
            text: Todo text
        """
        self.repo.add_project_todo(project_id, text)
        self._load_todos(project_id)
    
    def delete_todo(self, todo_id: int, project_id: int) -> None:
        """Delete a todo.
        
        Args:
            todo_id: Todo ID
            project_id: Project ID (for refresh)
        """
        self.repo.delete_project_todo(todo_id)
        self._load_todos(project_id)
    
    def toggle_todo_completed(self, todo_id: int, completed: bool, project_id: int) -> None:
        """Toggle todo completion state.
        
        Args:
            todo_id: Todo ID
            completed: New completion state
            project_id: Project ID (for refresh)
        """
        self.repo.set_project_todo_completed(todo_id, completed)
        self._load_todos(project_id)
    
    def load_todos(self, project_id: int) -> None:
        """Load todos for a project.
        
        Args:
            project_id: Project ID
        """
        self._load_todos(project_id)
    
    # Private methods
    
    def _refresh_projects(self) -> None:
        """Refresh projects list from database."""
        if self._selected_profile_id is not None:
            rows = self.repo.list_projects(profile_id=self._selected_profile_id)
        else:
            rows = self.repo.list_projects()
        self._projects = [dict(row) for row in rows]
        self.projects_changed.emit(self._projects)
    
    def _refresh_profiles(self) -> None:
        """Refresh profiles list from database."""
        rows = self.repo.list_profiles()
        self._profiles = [dict(row) for row in rows]
        self.profiles_changed.emit(self._profiles)
    
    def _refresh_services(self) -> None:
        """Refresh services list from database."""
        rows = self.repo.list_services()
        self._services = [dict(row) for row in rows]
        self.services_changed.emit(self._services)
    
    def _load_todos(self, project_id: int) -> None:
        """Load todos for a project.
        
        Args:
            project_id: Project ID
        """
        rows = self.repo.list_project_todos(project_id)
        self._todos = [dict(row) for row in rows]
        self.todos_changed.emit(self._todos)

