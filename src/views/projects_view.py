"""Projects view with profiles list and project management."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.ui.dialogs.project_dialog import ProjectDialog

if TYPE_CHECKING:
    from src.viewmodels.projects_viewmodel import ProjectsViewModel


class ProjectsView(QWidget):
    """Projects view with profile filtering and project management.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "ProjectsViewModel", parent: QWidget | None = None) -> None:
        """Initialize projects view.
        
        Args:
            viewmodel: Projects ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._first_show = True
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI components."""
        # Main layout with three columns
        main_layout = QHBoxLayout(self)
        
        # Left: Profile filter
        left_panel = self._build_profile_panel()
        
        # Middle: Projects list
        middle_panel = self._build_projects_panel()
        
        # Right: Project details
        right_panel = self._build_details_panel()
        
        # Use splitter for resizable columns
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(middle_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 3)
        
        main_layout.addWidget(splitter)

    def _build_profile_panel(self) -> QWidget:
        """Build the profiles filter panel (left side)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("<h2>Profiles</h2>"))
        
        # Profiles list
        self.profiles_list = QListWidget()
        layout.addWidget(self.profiles_list, 1)
        
        return widget

    def _build_projects_panel(self) -> QWidget:
        """Build the projects list panel (middle)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("<h2>Projects</h2>"))
        
        # Projects list
        self.projects_list = QListWidget()
        layout.addWidget(self.projects_list, 1)
        
        # Buttons
        self.add_project_btn = QPushButton("Add Project")
        self.delete_project_btn = QPushButton("Delete Project")
        
        layout.addWidget(self.add_project_btn)
        layout.addWidget(self.delete_project_btn)
        
        return widget

    def _build_details_panel(self) -> QWidget:
        """Build the project details panel (right side)."""
        # Use scroll area for details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Project info group
        info_group = QGroupBox("Project Information")
        info_form = QFormLayout(info_group)
        
        self.project_name_label = QLabel("—")
        self.project_name_label.setWordWrap(True)
        self.project_name_label.setMinimumHeight(20)
        self.project_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.profile_name_label = QLabel("—")
        self.profile_name_label.setWordWrap(True)
        self.profile_name_label.setMinimumHeight(20)
        self.profile_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.estimated_time_label = QLabel("—")
        self.estimated_time_label.setWordWrap(True)
        self.estimated_time_label.setMinimumHeight(20)
        self.estimated_time_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.service_label = QLabel("—")
        self.service_label.setWordWrap(True)
        self.service_label.setMinimumHeight(20)
        self.service_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.deadline_label = QLabel("—")
        self.deadline_label.setWordWrap(True)
        self.deadline_label.setMinimumHeight(20)
        self.deadline_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.notes_display = QPlainTextEdit()
        self.notes_display.setMaximumHeight(80)
        self.notes_display.setPlaceholderText("Enter project notes...")
        
        info_form.addRow("Project:", self.project_name_label)
        info_form.addRow("Profile:", self.profile_name_label)
        info_form.addRow("Estimated Time:", self.estimated_time_label)
        info_form.addRow("Service:", self.service_label)
        info_form.addRow("Deadline:", self.deadline_label)
        info_form.addRow("Notes:", self.notes_display)
        
        # Edit and Save buttons
        button_row = QHBoxLayout()
        self.edit_btn = QPushButton("Edit Project")
        self.save_notes_btn = QPushButton("Save Notes")
        button_row.addWidget(self.edit_btn)
        button_row.addWidget(self.save_notes_btn)
        info_form.addRow(button_row)
        
        layout.addWidget(info_group)
        
        # Todos group
        todos_group = QGroupBox("To-Dos")
        todos_layout = QVBoxLayout(todos_group)
        
        self.todo_list = QListWidget()
        self.todo_list.setMaximumHeight(200)
        todos_layout.addWidget(self.todo_list)
        
        # Add todo
        add_row = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("New to-do…")
        self.todo_add_btn = QPushButton("Add")
        
        add_row.addWidget(self.todo_input, 1)
        add_row.addWidget(self.todo_add_btn)
        
        todos_layout.addLayout(add_row)
        
        # Delete button
        self.todo_del_btn = QPushButton("Delete")
        todos_layout.addWidget(self.todo_del_btn)
        
        layout.addWidget(todos_group)
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll

    def _connect_signals(self) -> None:
        """Connect UI and ViewModel signals."""
        # Profile filter
        self.profiles_list.itemSelectionChanged.connect(self._on_profile_filter_changed)
        
        # Projects list
        self.add_project_btn.clicked.connect(self._on_add_project)
        self.delete_project_btn.clicked.connect(self._on_delete_project)
        self.projects_list.itemSelectionChanged.connect(self._on_project_selection_changed)
        
        # Details panel
        self.edit_btn.clicked.connect(self._on_edit_project)
        self.save_notes_btn.clicked.connect(self._on_save_notes)
        self.todo_add_btn.clicked.connect(self._on_add_todo)
        self.todo_del_btn.clicked.connect(self._on_delete_todos)
        self.todo_list.itemChanged.connect(self._on_todo_toggled)
        
        # ViewModel → UI
        self.viewmodel.profiles_changed.connect(self._update_profiles_list)
        self.viewmodel.projects_changed.connect(self._update_projects_list)
        self.viewmodel.project_selected.connect(self._load_project_details)
        self.viewmodel.todos_changed.connect(self._update_todos_list)
        
        # Initial load
        self._update_profiles_list(self.viewmodel.profiles)
        
        # Auto-select first profile if available
        if self.profiles_list.count() > 0:
            self.profiles_list.setCurrentRow(0)
    
    def showEvent(self, event) -> None:  # type: ignore[override]
        """Handle show event to clear selection on first display.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        if self._first_show:
            self._first_show = False
            # Clear any project selection when first showing the view
            self.projects_list.blockSignals(True)
            self.projects_list.clearSelection()
            self.projects_list.blockSignals(False)
            self.viewmodel.select_project(None)
    
    # Profile filter handlers
    
    def _on_profile_filter_changed(self) -> None:
        """Handle profile filter selection change."""
        item = self.profiles_list.currentItem()
        if item:
            profile_id = int(item.data(Qt.UserRole))
            self.viewmodel.select_profile_filter(profile_id)
        else:
            # No profile selected - clear projects
            self.viewmodel.select_profile_filter(None)
    
    # Project list handlers
    
    def _on_add_project(self) -> None:
        """Handle add project button."""
        # Pre-select profile if filtering by one
        selected_profile_id = self.viewmodel.selected_profile_id
        
        dlg = ProjectDialog(
            self,
            title="Create Project",
            profiles=self.viewmodel.profiles,
            services=self.viewmodel.services,
            profile_id=selected_profile_id,
        )
        
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        profile_id = dlg.get_profile_id()
        name = dlg.get_name()
        
        if not profile_id or not name:
            QMessageBox.warning(self, "Invalid Input", "Please select a profile and enter a name.")
            return
        
        estimated_seconds = dlg.get_estimated_seconds()
        service_id = dlg.get_service_id()
        deadline_ts = dlg.get_deadline_timestamp()
        notes = dlg.get_notes()
        
        self.viewmodel.create_project(
            profile_id, name, estimated_seconds, service_id, deadline_ts, notes
        )
    
    def _on_delete_project(self) -> None:
        """Handle delete project button."""
        project_id = self._get_selected_project_id()
        if project_id is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete project",
            "Delete this project and all its to-dos?",
        )
        
        if reply == QMessageBox.Yes:
            self.viewmodel.delete_project(project_id)
    
    def _on_project_selection_changed(self) -> None:
        """Handle project list selection change."""
        project_id = self._get_selected_project_id()
        self.viewmodel.select_project(project_id)
    
    def _on_save_notes(self) -> None:
        """Handle save notes button."""
        project_id = self.viewmodel.current_project_id
        if project_id is None:
            return
        
        project = self.viewmodel.repo.get_project(project_id)
        if not project:
            return
        
        # Get current notes from text field
        notes = self.notes_display.toPlainText().strip() or None
        
        # Update only the notes
        self.viewmodel.update_project(
            project_id,
            str(project["name"]),
            int(project["estimated_seconds"]) if project.get("estimated_seconds") else None,
            int(project["service_id"]) if project.get("service_id") else None,
            int(project["deadline_ts"]) if project.get("deadline_ts") else None,
            notes
        )
        
        # Reload project details to reflect changes
        self._load_project_details(project_id)
        
        QMessageBox.information(self, "Saved", "Notes saved successfully.")
    
    def _on_edit_project(self) -> None:
        """Handle edit project button."""
        project_id = self.viewmodel.current_project_id
        if project_id is None:
            return
        
        project = self.viewmodel.repo.get_project(project_id)
        if not project:
            return
        
        # Convert timestamp to datetime
        deadline = None
        if project.get("deadline_ts"):
            deadline = datetime.fromtimestamp(int(project["deadline_ts"]))
        
        # Convert seconds to hours
        estimated_hours = 0
        if project.get("estimated_seconds"):
            estimated_hours = int(project["estimated_seconds"]) / 3600
        
        dlg = ProjectDialog(
            self,
            title="Edit Project",
            profiles=self.viewmodel.profiles,
            services=self.viewmodel.services,
            name=str(project["name"]),
            profile_id=int(project["profile_id"]),
            estimated_hours=estimated_hours,
            service_id=int(project["service_id"]) if project.get("service_id") else None,
            deadline=deadline,
            notes=str(project["notes"] or ""),
        )
        
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        name = dlg.get_name()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a project name.")
            return
        
        estimated_seconds = dlg.get_estimated_seconds()
        service_id = dlg.get_service_id()
        deadline_ts = dlg.get_deadline_timestamp()
        notes = dlg.get_notes()
        
        self.viewmodel.update_project(
            project_id, name, estimated_seconds, service_id, deadline_ts, notes
        )
        
        # Reload project details to reflect changes
        self._load_project_details(project_id)
    
    # Todo handlers
    
    def _on_add_todo(self) -> None:
        """Handle add todo button."""
        project_id = self.viewmodel.current_project_id
        if project_id is None:
            return
        
        text = self.todo_input.text().strip()
        if not text:
            return
        
        self.viewmodel.add_todo(project_id, text)
        self.todo_input.clear()
    
    def _on_delete_todos(self) -> None:
        """Handle delete todos button."""
        project_id = self.viewmodel.current_project_id
        if project_id is None:
            return
        
        items = self.todo_list.selectedItems()
        if not items:
            return
        
        for item in items:
            todo_id = int(item.data(Qt.UserRole))
            self.viewmodel.delete_todo(todo_id, project_id)
    
    def _on_todo_toggled(self, item: QListWidgetItem) -> None:
        """Handle todo checkbox toggle."""
        project_id = self.viewmodel.current_project_id
        if project_id is None:
            return
        
        todo_id = item.data(Qt.UserRole)
        if todo_id is None:
            return
        
        completed = item.checkState() == Qt.Checked
        self.viewmodel.toggle_todo_completed(int(todo_id), completed, project_id)
    
    # ViewModel update handlers
    
    def _update_profiles_list(self, profiles: list) -> None:
        """Update profiles list with new data.
        
        Args:
            profiles: List of profile dicts
        """
        self.profiles_list.clear()
        for prof in profiles:
            it = QListWidgetItem(str(prof["name"]))
            it.setData(Qt.UserRole, int(prof["id"]))
            self.profiles_list.addItem(it)
    
    def _update_projects_list(self, projects: list) -> None:
        """Update projects list with new data.
        
        Args:
            projects: List of project dicts
        """
        self.projects_list.clear()
        for proj in projects:
            display_text = f"{proj['name']} ({proj['profile_name']})"
            it = QListWidgetItem(display_text)
            it.setData(Qt.UserRole, int(proj["id"]))
            self.projects_list.addItem(it)
    
    def _load_project_details(self, project_id: Optional[int]) -> None:
        """Load project details into the right panel.
        
        Args:
            project_id: Project ID to load, or None to clear
        """
        if project_id is None:
            # Clear all fields
            self.project_name_label.setText("—")
            self.profile_name_label.setText("—")
            self.estimated_time_label.setText("—")
            self.service_label.setText("—")
            self.deadline_label.setText("—")
            self.notes_display.clear()
            return
        
        # Select the project in the list if not already selected
        self._select_project_in_list(project_id)
        
        project = self.viewmodel.repo.get_project(project_id)
        
        if not project:
            return
        
        # Populate fields
        self.project_name_label.setText(str(project["name"]))
        self.profile_name_label.setText(str(project.get("profile_name") or ""))
        
        # Format estimated time as HH:MM
        if project.get("estimated_seconds") is not None:
            total_seconds = int(project["estimated_seconds"])
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            self.estimated_time_label.setText(f"{hours:02d}:{minutes:02d}")
        else:
            self.estimated_time_label.setText("Not set")
        
        # Service
        service_name = project.get("service_name")
        if service_name is not None:
            self.service_label.setText(str(service_name))
        else:
            self.service_label.setText("None")
        
        # Deadline
        deadline_ts = project.get("deadline_ts")
        if deadline_ts is not None:
            dt = datetime.fromtimestamp(int(deadline_ts))
            self.deadline_label.setText(dt.strftime("%Y-%m-%d"))
        else:
            self.deadline_label.setText("No deadline")
        
        # Notes
        notes = project.get("notes")
        self.notes_display.setPlainText(notes if notes is not None else "")
        
        # Load todos
        self.viewmodel.load_todos(project_id)
    
    def _update_todos_list(self, todos: list) -> None:
        """Update todos list with new data.
        
        Args:
            todos: List of todo dicts
        """
        self.todo_list.blockSignals(True)
        self.todo_list.clear()
        
        for todo in todos:
            item = QListWidgetItem(str(todo["text"]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if int(todo["completed"]) else Qt.Unchecked)
            item.setData(Qt.UserRole, int(todo["id"]))
            
            # Strike-through if completed
            if int(todo["completed"]):
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            
            self.todo_list.addItem(item)
        
        self.todo_list.blockSignals(False)
    
    # Helper methods
    
    def _get_selected_project_id(self) -> Optional[int]:
        """Get currently selected project ID.
        
        Returns:
            Project ID or None
        """
        item = self.projects_list.currentItem()
        if not item:
            return None
        return int(item.data(Qt.UserRole))
    
    def _select_project_in_list(self, project_id: int) -> None:
        """Select a project in the list widget.
        
        Args:
            project_id: Project ID to select
        """
        # Find and select the project in the list
        self.projects_list.blockSignals(True)
        for i in range(self.projects_list.count()):
            item = self.projects_list.item(i)
            if item and int(item.data(Qt.UserRole)) == project_id:
                self.projects_list.setCurrentItem(item)
                break
        self.projects_list.blockSignals(False)

