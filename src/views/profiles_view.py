"""Profiles view with list and settings."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.dialogs import ProfileDialog

if TYPE_CHECKING:
    from src.viewmodels import ProfilesViewModel


class ProfilesView(QWidget):
    """Profiles view with list and settings pages.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "ProfilesViewModel", parent: QWidget | None = None) -> None:
        """Initialize profiles view.
        
        Args:
            viewmodel: Profiles ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI components."""
        # Main horizontal layout - profiles list on left, details on right
        main_layout = QHBoxLayout(self)
        
        # Left side - profiles list
        left_panel = self._build_list_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right side - profile details
        right_panel = self._build_details_panel()
        main_layout.addWidget(right_panel, 2)

    def _build_list_panel(self) -> QWidget:
        """Build the profiles list panel (left side)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("<h2>Profiles</h2>"))
        
        # Profiles list
        self.profiles_list = QListWidget()
        self.profiles_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.profiles_list.customContextMenuRequested.connect(self._show_list_context_menu)
        
        # Delete shortcut
        del_action = QAction("Delete Profile", self, shortcut=QKeySequence(Qt.Key_Delete))
        del_action.setShortcutContext(Qt.WidgetShortcut)
        del_action.triggered.connect(self._on_delete_profile)
        self.profiles_list.addAction(del_action)
        
        # Buttons
        self.add_btn = QPushButton("Add Profile")
        self.delete_btn = QPushButton("Delete Profile")
        self.duplicate_btn = QPushButton("Duplicate Profile")
        
        layout.addWidget(self.profiles_list, 1)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.duplicate_btn)
        
        return widget

    def _build_details_panel(self) -> QWidget:
        """Build the profile details panel (right side)."""
        # Use scroll area for details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        form = QFormLayout(widget)
        
        # Profile fields (removed daily target)
        self.name_edit = QLineEdit()
        self.company_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Write notes about this profile…")
        self.notes_edit.setTabChangesFocus(True)
        self.notes_edit.setMaximumHeight(100)
        
        form.addRow("Name", self.name_edit)
        form.addRow("Company", self.company_edit)
        form.addRow("Contact Person", self.contact_edit)
        form.addRow("Email", self.email_edit)
        form.addRow("Phone", self.phone_edit)
        form.addRow("Notes", self.notes_edit)
        
        # Save button
        self.save_btn = QPushButton("Save")
        form.addRow(self.save_btn)
        
        # Todos section
        form.addRow(QLabel("<h3>To-Dos</h3>"))
        todos_layout = QVBoxLayout()
        
        self.todo_list = QListWidget()
        self.todo_list.itemChanged.connect(self._on_todo_toggled)
        self.todo_list.setMaximumHeight(150)
        
        add_row = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("New to-do…")
        self.todo_add_btn = QPushButton("Add")
        
        add_row.addWidget(self.todo_input, 1)
        add_row.addWidget(self.todo_add_btn)
        
        # Delete button under Add button
        self.todo_del_btn = QPushButton("Delete")
        self.todo_del_btn.setMaximumWidth(self.todo_add_btn.sizeHint().width())
        
        todos_layout.addWidget(self.todo_list)
        todos_layout.addLayout(add_row)
        todos_layout.addWidget(self.todo_del_btn)
        
        form.addRow(todos_layout)
        
        # Services section
        form.addRow(QLabel("<h3>Services</h3>"))
        services_layout = QVBoxLayout()
        
        # Service selector and add button
        add_service_row = QHBoxLayout()
        self.service_combo = QComboBox()
        self.add_service_btn = QPushButton("Add Service")
        add_service_row.addWidget(self.service_combo, 1)
        add_service_row.addWidget(self.add_service_btn)
        services_layout.addLayout(add_service_row)
        
        # Container for service instances
        self.services_container = QVBoxLayout()
        services_layout.addLayout(self.services_container)
        
        form.addRow(services_layout)
        
        scroll.setWidget(widget)
        return scroll

    def _connect_signals(self) -> None:
        """Connect UI and ViewModel signals."""
        # List panel UI → ViewModel
        self.add_btn.clicked.connect(self._on_add_profile)
        self.delete_btn.clicked.connect(self._on_delete_profile)
        self.duplicate_btn.clicked.connect(self._on_duplicate_profile)
        self.profiles_list.itemSelectionChanged.connect(self._on_profile_selection_changed)
        
        # Details panel UI → ViewModel
        self.save_btn.clicked.connect(self._on_save_profile)
        self.todo_add_btn.clicked.connect(self._on_add_todo)
        self.todo_del_btn.clicked.connect(self._on_delete_todos)
        self.add_service_btn.clicked.connect(self._on_add_service)
        
        # ViewModel → UI
        self.viewmodel.profiles_changed.connect(self._update_profiles_list)
        self.viewmodel.todos_changed.connect(self._update_todos_list)
        self.viewmodel.profile_selected.connect(self._load_profile_details)
        self.viewmodel.profile_services_changed.connect(self._update_services_list)
        self.viewmodel.service_todos_changed.connect(self._update_service_todos)
        
        # Initial load - populate with existing profiles from viewmodel
        self._update_profiles_list(self.viewmodel.profiles)
        
        # Load available services
        self._populate_service_combo()
    
    # Private helper methods
    
    def _load_profile_details(self, profile_id: Optional[int]) -> None:
        """Load profile details into the right panel.
        
        Args:
            profile_id: Profile ID to load, or None to clear
        """
        if profile_id is None:
            # Clear all fields
            self.name_edit.clear()
            self.company_edit.clear()
            self.contact_edit.clear()
            self.email_edit.clear()
            self.phone_edit.clear()
            self.notes_edit.clear()
            return
        
        prof = self.viewmodel.repo.get_profile(profile_id)
        if not prof:
            return
        
        # Populate fields
        self.name_edit.setText(prof["name"] if prof else "")
        self.company_edit.setText(prof["company"] or "" if prof else "")
        self.contact_edit.setText(prof["contact_person"] or "" if prof else "")
        self.email_edit.setText(prof["email"] or "" if prof else "")
        self.phone_edit.setText(prof["phone"] or "" if prof else "")
        self.notes_edit.setPlainText((prof["notes"] or "") if prof else "")
        
        # Load todos
        self.viewmodel.load_todos(profile_id)
    
    def _populate_service_combo(self) -> None:
        """Populate the service combo box with available services."""
        self.service_combo.clear()
        services = self.viewmodel.repo.list_services()
        for service in services:
            self.service_combo.addItem(str(service["name"]), int(service["id"]))
    
    def _clear_services_container(self) -> None:
        """Clear all widgets from services container."""
        while self.services_container.count():
            item = self.services_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    # UI event handlers - List panel
    
    def _on_add_profile(self) -> None:
        """Handle add profile button."""
        dlg = ProfileDialog(self, title="Create Profile")
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        name = dlg.get_name()
        if not name:
            return
        
        # No longer using target in profile dialog
        company, contact, email, phone = dlg.get_contact_fields()
        self.viewmodel.create_profile(name, None, company, contact, email, phone)
    
    def _on_delete_profile(self) -> None:
        """Handle delete profile button."""
        profile_id = self._get_selected_profile_id()
        if profile_id is None:
            return
        
        # Try to delete
        if not self.viewmodel.delete_profile(profile_id, force=False):
            # Timer is running, confirm with user
            reply = QMessageBox.question(
                self,
                "Timer running",
                "Timer is running for this profile. Stop and delete?",
            )
            if reply == QMessageBox.Yes:
                self.viewmodel.delete_profile(profile_id, force=True)
            return
        
        # Confirm cascade
        reply = QMessageBox.question(
            self,
            "Delete profile",
            "Delete this profile and all its time entries?",
        )
        if reply == QMessageBox.Yes:
            self.viewmodel.delete_profile(profile_id, force=True)
    
    def _on_duplicate_profile(self) -> None:
        """Handle duplicate profile button."""
        profile_id = self._get_selected_profile_id()
        if profile_id is None:
            return
        
        prof = self.viewmodel.repo.get_profile(profile_id)
        if not prof:
            return
        
        base_name = str(prof["name"])
        new_name = self.viewmodel.generate_unique_profile_name(base_name)
        
        # Ask user for name
        name, ok = QInputDialog.getText(self, "Duplicate Profile", "New profile name:", text=new_name)
        if not ok or not name.strip():
            return
        
        try:
            self.viewmodel.duplicate_profile(profile_id, name.strip())
        except Exception as e:
            QMessageBox.warning(self, "Duplicate failed", f"Could not create profile: {e}")
    
    def _on_profile_selection_changed(self) -> None:
        """Handle profile list selection change."""
        profile_id = self._get_selected_profile_id()
        if profile_id is not None:
            self.viewmodel.select_profile(profile_id)
    
    def _show_list_context_menu(self, pos) -> None:
        """Show context menu for profiles list."""
        item = self.profiles_list.itemAt(pos)
        if item is None:
            return
        
        menu = QMenu(self)
        dup_act = menu.addAction("Duplicate Profile…")
        del_act = menu.addAction("Delete Profile")
        
        act = menu.exec(self.profiles_list.viewport().mapToGlobal(pos))
        if act == dup_act:
            self._on_duplicate_profile()
        elif act == del_act:
            self._on_delete_profile()
    
    # UI event handlers - Details panel
    
    def _on_save_profile(self) -> None:
        """Handle save profile button."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        name = self.name_edit.text().strip()
        company = self.company_edit.text().strip() or None
        contact = self.contact_edit.text().strip() or None
        email = self.email_edit.text().strip() or None
        phone = self.phone_edit.text().strip() or None
        notes = self.notes_edit.toPlainText().strip() or None
        
        self.viewmodel.update_profile(
            profile_id, name, None, company, contact, email, phone, notes
        )
    
    def _on_add_todo(self) -> None:
        """Handle add todo button."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        text = self.todo_input.text().strip()
        if not text:
            return
        
        self.viewmodel.add_todo(profile_id, text)
        self.todo_input.clear()
    
    def _on_delete_todos(self) -> None:
        """Handle delete todos button."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        items = self.todo_list.selectedItems()
        if not items:
            return
        
        for item in items:
            todo_id = int(item.data(Qt.UserRole))
            self.viewmodel.delete_todo(todo_id, profile_id)
    
    def _on_todo_toggled(self, item: QListWidgetItem) -> None:
        """Handle todo checkbox toggle."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        todo_id = item.data(Qt.UserRole)
        if todo_id is None:
            return
        
        completed = item.checkState() == Qt.Checked
        self.viewmodel.toggle_todo_completed(int(todo_id), completed, profile_id)
    
    def _on_add_service(self) -> None:
        """Handle add service button."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        if self.service_combo.count() == 0:
            QMessageBox.information(self, "No Services", "Please create services first in the Services view.")
            return
        
        service_id = self.service_combo.currentData()
        if service_id is None:
            return
        
        self.viewmodel.add_service_to_profile(profile_id, int(service_id))
    
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
        
        # Auto-select first if nothing selected
        if self.profiles_list.currentRow() == -1 and self.profiles_list.count() > 0:
            self.profiles_list.setCurrentRow(0)
    
    def _update_todos_list(self, todos: list) -> None:
        """Update todos list with new data.
        
        Args:
            todos: List of todo dicts
        """
        self.todo_list.blockSignals(True)
        self.todo_list.clear()
        
        for todo in todos:
            item = QListWidgetItem(str(todo["text"]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Checked if int(todo["completed"]) else Qt.Unchecked)
            item.setData(Qt.UserRole, int(todo["id"]))
            
            # Strike-through if completed
            if int(todo["completed"]):
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            
            self.todo_list.addItem(item)
        
        self.todo_list.blockSignals(False)
    
    def _update_services_list(self, services: list) -> None:
        """Update services list with new data.
        
        Args:
            services: List of profile service instance dicts
        """
        self._clear_services_container()
        
        for ps in services:
            service_widget = self._create_service_widget(ps)
            self.services_container.addWidget(service_widget)
    
    def _create_service_widget(self, profile_service: dict) -> QWidget:
        """Create a widget for a profile service instance.
        
        Args:
            profile_service: Profile service instance dict
            
        Returns:
            Widget displaying service instance
        """
        ps_id = int(profile_service["id"])
        service_name = str(profile_service["service_name"])
        notes = profile_service.get("notes") or ""
        
        group = QGroupBox(service_name)
        layout = QVBoxLayout(group)
        
        # Notes section
        notes_label = QLabel("Notes:")
        notes_edit = QTextEdit()
        notes_edit.setPlainText(notes)
        notes_edit.setMaximumHeight(80)
        notes_edit.setObjectName(f"service_notes_{ps_id}")
        
        # Save notes on focus out
        original_focus_out = notes_edit.focusOutEvent
        def focus_out_handler(event):
            self._save_service_notes(ps_id, notes_edit)
            original_focus_out(event)
        notes_edit.focusOutEvent = focus_out_handler
        
        layout.addWidget(notes_label)
        layout.addWidget(notes_edit)
        
        # Todos section
        todos_label = QLabel("To-Dos:")
        layout.addWidget(todos_label)
        
        # Todos list
        todos_list = QListWidget()
        todos_list.setMaximumHeight(100)
        todos_list.setObjectName(f"service_todos_{ps_id}")
        todos_list.itemChanged.connect(
            lambda item, ps_id=ps_id: self._on_service_todo_toggled(ps_id, item)
        )
        layout.addWidget(todos_list)
        
        # Add todo
        add_todo_row = QHBoxLayout()
        todo_input = QLineEdit()
        todo_input.setPlaceholderText("New to-do…")
        todo_add_btn = QPushButton("Add")
        todo_add_btn.clicked.connect(
            lambda ps_id=ps_id, todo_input=todo_input: self._on_add_service_todo(ps_id, todo_input)
        )
        add_todo_row.addWidget(todo_input, 1)
        add_todo_row.addWidget(todo_add_btn)
        layout.addLayout(add_todo_row)
        
        # Delete todo and delete service buttons
        button_row = QHBoxLayout()
        todo_del_btn = QPushButton("Delete Todo")
        todo_del_btn.clicked.connect(
            lambda ps_id=ps_id, todos_list=todos_list: self._on_delete_service_todo(ps_id, todos_list)
        )
        delete_service_btn = QPushButton("Remove Service")
        delete_service_btn.clicked.connect(lambda ps_id=ps_id: self._on_remove_service(ps_id))
        button_row.addWidget(todo_del_btn)
        button_row.addWidget(delete_service_btn)
        layout.addLayout(button_row)
        
        # Load todos for this service
        self.viewmodel.load_service_todos(ps_id)
        
        return group
    
    def _update_service_todos(self, profile_service_id: int, todos: list) -> None:
        """Update todos for a specific service instance.
        
        Args:
            profile_service_id: Profile service instance ID
            todos: List of todo dicts
        """
        # Find the todos list widget for this service
        todos_list = self.findChild(QListWidget, f"service_todos_{profile_service_id}")
        if not todos_list:
            return
        
        todos_list.blockSignals(True)
        todos_list.clear()
        
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
            
            todos_list.addItem(item)
        
        todos_list.blockSignals(False)
    
    def _save_service_notes(self, profile_service_id: int, notes_edit: QTextEdit) -> None:
        """Save service notes to database."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        notes = notes_edit.toPlainText().strip() or None
        self.viewmodel.update_profile_service_notes(profile_service_id, notes, profile_id)
    
    def _on_add_service_todo(self, profile_service_id: int, todo_input: QLineEdit) -> None:
        """Handle add todo for service."""
        text = todo_input.text().strip()
        if not text:
            return
        
        self.viewmodel.add_service_todo(profile_service_id, text)
        todo_input.clear()
    
    def _on_delete_service_todo(self, profile_service_id: int, todos_list: QListWidget) -> None:
        """Handle delete todo for service."""
        items = todos_list.selectedItems()
        if not items:
            return
        
        for item in items:
            todo_id = int(item.data(Qt.UserRole))
            self.viewmodel.delete_service_todo(todo_id, profile_service_id)
    
    def _on_service_todo_toggled(self, profile_service_id: int, item: QListWidgetItem) -> None:
        """Handle service todo checkbox toggle."""
        todo_id = item.data(Qt.UserRole)
        if todo_id is None:
            return
        
        completed = item.checkState() == Qt.Checked
        self.viewmodel.toggle_service_todo_completed(int(todo_id), completed, profile_service_id)
    
    def _on_remove_service(self, profile_service_id: int) -> None:
        """Handle remove service button."""
        profile_id = self.viewmodel.current_profile_id
        if profile_id is None:
            return
        
        reply = QMessageBox.question(
            self, "Remove Service", "Remove this service from the profile?"
        )
        if reply != QMessageBox.Yes:
            return
        
        self.viewmodel.delete_profile_service(profile_service_id, profile_id)
    
    # Helper methods
    
    def _get_selected_profile_id(self) -> Optional[int]:
        """Get currently selected profile ID.
        
        Returns:
            Profile ID or None
        """
        item = self.profiles_list.currentItem()
        if not item:
            return None
        return int(item.data(Qt.UserRole))

