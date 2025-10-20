"""Main window - container for all views."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from src.services.export_service import export_csv, export_json
from src.services.settings_service import AppSettings
from src.views import DashboardView, ProfilesView, ProjectsView, ServicesView, TimerView

if TYPE_CHECKING:
    from src.services.state_service import StateService
    from src.services.timer_service import TimerService
    from src.viewmodels import (
        DashboardViewModel,
        ProfilesViewModel,
        ProjectsViewModel,
        ServicesViewModel,
        TimerViewModel,
    )


class MainWindow(QMainWindow):
    """Main application window - lean container for views.
    
    Responsibilities:
    - Window management (geometry, state, icon)
    - View navigation and stacking
    - Menu bar and system tray
    - Profile sidebar
    """

    def __init__(
        self,
        state_service: "StateService",
        timer_service: "TimerService",
        dashboard_vm: "DashboardViewModel",
        timer_vm: "TimerViewModel",
        profiles_vm: "ProfilesViewModel",
        projects_vm: "ProjectsViewModel",
        services_vm: "ServicesViewModel",
    ) -> None:
        """Initialize main window.
        
        Args:
            state_service: Central state service
            timer_service: Timer service
            dashboard_vm: Dashboard ViewModel
            timer_vm: Timer ViewModel
            profiles_vm: Profiles ViewModel
            projects_vm: Projects ViewModel
            services_vm: Services ViewModel
        """
        super().__init__()
        self.state = state_service
        self.timer_service = timer_service
        
        # ViewModels
        self.dashboard_vm = dashboard_vm
        self.timer_vm = timer_vm
        self.profiles_vm = profiles_vm
        self.projects_vm = projects_vm
        self.services_vm = services_vm
        
        # Setup window
        self.setWindowTitle("SoliaTime")
        self._set_window_icon()
        
        # Build UI
        self._build_ui()
        self._connect_signals()
        self._setup_menu_bar()
        self._setup_tray()
        
        # Restore window state
        settings = self.state.settings
        if settings.geometry:
            self.restoreGeometry(QByteArray(settings.geometry))
        if settings.window_state:
            self.restoreState(QByteArray(settings.window_state))
        
        # Default size if no saved geometry
        if not settings.geometry:
            self.resize(1200, 750)
        
        self._ensure_visible_on_screen()
        self.raise_()
        self.activateWindow()

    def _set_window_icon(self) -> None:
        """Set window icon from resources."""
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
            candidates = [
                base / "ui" / "resources" / "App.ico",
                base / "ui" / "resources" / "app.ico",
                base / "ui" / "resources" / "App.png",
            ]
            for p in candidates:
                if p.exists():
                    self.setWindowIcon(QIcon(str(p)))
                    break
        except Exception:
            pass

    def _build_ui(self) -> None:
        """Build the UI structure."""
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Navigation buttons at top
        nav_btn_container = QHBoxLayout()
        self.dashboard_btn = QPushButton("🏠 Dashboard")
        self.dashboard_btn.setMaximumWidth(150)
        self.dashboard_btn.clicked.connect(self._go_to_dashboard)
        nav_btn_container.addWidget(self.dashboard_btn)
        
        self.timer_btn = QPushButton("⏱️ Timer")
        self.timer_btn.setMaximumWidth(150)
        self.timer_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        nav_btn_container.addWidget(self.timer_btn)
        
        self.profiles_btn = QPushButton("👥 Profiles")
        self.profiles_btn.setMaximumWidth(150)
        self.profiles_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        nav_btn_container.addWidget(self.profiles_btn)
        
        self.services_btn = QPushButton("💼 Services")
        self.services_btn.setMaximumWidth(150)
        self.services_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        nav_btn_container.addWidget(self.services_btn)
        
        self.projects_btn = QPushButton("📋 Projects")
        self.projects_btn.setMaximumWidth(150)
        self.projects_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        nav_btn_container.addWidget(self.projects_btn)
        
        nav_btn_container.addStretch()
        main_layout.addLayout(nav_btn_container)
        
        # Content area with sidebar and stack
        content_layout = QHBoxLayout()
        
        # Profiles sidebar (conditionally visible)
        self.profiles_sidebar = self._build_profiles_sidebar()
        
        # Stacked widget for views
        self.stack = QStackedWidget()
        self.stack.currentChanged.connect(self._on_page_changed)
        
        # Create views
        self.dashboard_view = DashboardView(self.dashboard_vm)
        self.timer_view = TimerView(self.timer_vm)
        self.profiles_view = ProfilesView(self.profiles_vm)
        self.projects_view = ProjectsView(self.projects_vm)
        self.services_view = ServicesView(self.services_vm)
        
        # Add to stack (indices: 0=dashboard, 1=timer, 2=profiles, 3=projects, 4=services)
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.timer_view)
        self.stack.addWidget(self.profiles_view)
        self.stack.addWidget(self.projects_view)
        self.stack.addWidget(self.services_view)
        
        content_layout.addWidget(self.profiles_sidebar, 1)
        content_layout.addWidget(self.stack, 3)
        main_layout.addLayout(content_layout)
        
        # Start on dashboard
        self.stack.setCurrentIndex(0)

    def _build_profiles_sidebar(self) -> QWidget:
        """Build the profiles sidebar.
        
        Returns:
            Sidebar widget
        """
        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)
        
        layout.addWidget(QLabel("Profiles"))
        
        self.profiles_list = QListWidget()
        self.add_profile_btn = QPushButton("Add Profile")
        self.edit_profile_btn = QPushButton("Edit Profile")
        
        layout.addWidget(self.profiles_list)
        layout.addWidget(self.add_profile_btn)
        layout.addWidget(self.edit_profile_btn)
        
        return sidebar

    def _connect_signals(self) -> None:
        """Connect signals between ViewModels and UI."""
        # Dashboard navigation
        self.dashboard_vm.navigate_to_timer.connect(lambda: self.stack.setCurrentIndex(1))
        self.dashboard_vm.navigate_to_profiles.connect(lambda: self.stack.setCurrentIndex(2))
        self.dashboard_vm.navigate_to_projects.connect(lambda: self.stack.setCurrentIndex(3))
        self.dashboard_vm.navigate_to_services.connect(lambda: self.stack.setCurrentIndex(4))
        
        # Profiles to Projects navigation
        self.profiles_vm.navigate_to_project_requested.connect(self._navigate_to_project)
        
        # Sidebar profiles
        self.add_profile_btn.clicked.connect(self._on_sidebar_add_profile)
        self.edit_profile_btn.clicked.connect(self._on_sidebar_edit_profile)
        self.profiles_list.itemSelectionChanged.connect(self._on_sidebar_profile_selected)
        
        # State changes
        self.state.profiles_updated.connect(self._populate_sidebar_profiles)
        self.state.active_entry_changed.connect(self._update_tray_tooltip)
        
        # Keyboard shortcuts
        toggle_action = QAction("Toggle Timer", self, shortcut=QKeySequence(Qt.Key_Space))
        toggle_action.triggered.connect(self._on_shortcut_toggle_timer)
        self.addAction(toggle_action)
        
        new_profile_action = QAction("New Profile", self, shortcut=QKeySequence("Ctrl+N"))
        new_profile_action.triggered.connect(self._on_sidebar_add_profile)
        self.addAction(new_profile_action)
        
        # Initial populate
        self._populate_sidebar_profiles()

    def _setup_menu_bar(self) -> None:
        """Setup the menu bar."""
        # Export actions
        export_csv_act = QAction("Export CSV", self)
        export_csv_act.triggered.connect(self._export_csv)
        
        export_json_act = QAction("Export JSON", self)
        export_json_act.triggered.connect(self._export_json)
        
        self.menuBar().addAction(export_csv_act)
        self.menuBar().addAction(export_json_act)

    def _setup_tray(self) -> None:
        """Setup system tray icon."""
        self.tray = QSystemTrayIcon(self)
        
        # Set icon
        try:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
            candidates = [
                base / "ui" / "resources" / "App.ico",
                base / "ui" / "resources" / "app.ico",
                base / "ui" / "resources" / "App.png",
            ]
            icon_found = False
            for p in candidates:
                if p.exists():
                    self.tray.setIcon(QIcon(str(p)))
                    icon_found = True
                    break
            if not icon_found:
                self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        except Exception:
            self.tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        self.tray.setToolTip("Stopped")
        
        # Context menu
        menu = QMenu()
        toggle = menu.addAction("Start/Stop")
        show = menu.addAction("Show")
        quit_act = menu.addAction("Quit")
        
        toggle.triggered.connect(self._on_shortcut_toggle_timer)
        show.triggered.connect(self.showNormal)
        quit_act.triggered.connect(self._on_quit_requested)
        
        self.tray.setContextMenu(menu)
        self.tray.setVisible(True)

    # Navigation
    
    def _go_to_dashboard(self) -> None:
        """Navigate to dashboard."""
        self.stack.setCurrentIndex(0)
    
    def _navigate_to_project(self, project_id: int) -> None:
        """Navigate to projects view and select specific project.
        
        Args:
            project_id: Project ID to select
        """
        # First navigate to projects view
        self.stack.setCurrentIndex(3)
        # Then select the project in the view
        self.projects_vm.select_project(project_id)

    def _on_page_changed(self, index: int) -> None:
        """Handle page change to show/hide sidebar.
        
        Args:
            index: New page index
        """
        # Hide sidebar - profile selection is now done in the Profiles view
        self.profiles_sidebar.setVisible(False)

    # Sidebar methods
    
    def _populate_sidebar_profiles(self) -> None:
        """Populate sidebar profiles list."""
        self.profiles_list.clear()
        for prof in self.profiles_vm.profiles:
            it = QListWidgetItem(str(prof["name"]))
            it.setData(Qt.UserRole, int(prof["id"]))
            self.profiles_list.addItem(it)
        
        # Auto-select based on state
        current_id = self.state.current_profile_id
        if current_id is not None:
            for i in range(self.profiles_list.count()):
                item = self.profiles_list.item(i)
                if item and int(item.data(Qt.UserRole)) == current_id:
                    self.profiles_list.setCurrentItem(item)
                    break
        elif self.profiles_list.count() > 0:
            self.profiles_list.setCurrentRow(0)

    def _on_sidebar_add_profile(self) -> None:
        """Handle add profile from sidebar."""
        from src.ui.dialogs import ProfileDialog
        from PySide6.QtWidgets import QDialog
        
        dlg = ProfileDialog(self, title="Create Profile")
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        name = dlg.get_name()
        if not name:
            return
        
        contact, email, phone = dlg.get_contact_fields()
        self.profiles_vm.create_profile(name, None, contact, email, phone)

    def _on_sidebar_edit_profile(self) -> None:
        """Handle edit profile from sidebar."""
        item = self.profiles_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select profile", "Please select a profile first.")
            return
        
        profile_id = int(item.data(Qt.UserRole))
        # Navigate to profiles view (profile will be selected automatically)
        self.profiles_vm.select_profile(profile_id)
        self.stack.setCurrentIndex(2)

    def _on_sidebar_profile_selected(self) -> None:
        """Handle sidebar profile selection."""
        item = self.profiles_list.currentItem()
        if item:
            profile_id = int(item.data(Qt.UserRole))
            self.profiles_vm.select_profile(profile_id)

    # Export methods
    
    def _export_csv(self) -> None:
        """Export data to CSV."""
        # Generate filename based on selected profile and project
        profile_id = self.timer_vm.selected_profile_id
        project_id = self.timer_vm.selected_project_id
        
        filename_parts = ["SoliaTime Export"]
        
        # Add profile name
        if profile_id is not None:
            profile = self.state.repository.get_profile(profile_id)
            if profile:
                filename_parts.append(profile["name"])
        else:
            filename_parts.append("All Profiles")
        
        # Add project name
        if project_id is not None:
            project = self.state.repository.get_project(project_id)
            if project:
                filename_parts.append(project["name"])
        else:
            filename_parts.append("All Projects")
        
        default_filename = " - ".join(filename_parts) + ".csv"
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_filename, "CSV Files (*.csv)"
        )
        if path:
            export_csv(self.state.repository, Path(path), profile_id=profile_id, project_id=project_id)

    def _export_json(self) -> None:
        """Export data to JSON."""
        # Generate filename based on selected profile and project
        profile_id = self.timer_vm.selected_profile_id
        project_id = self.timer_vm.selected_project_id
        
        filename_parts = ["SoliaTime Export"]
        
        # Add profile name
        if profile_id is not None:
            profile = self.state.repository.get_profile(profile_id)
            if profile:
                filename_parts.append(profile["name"])
        else:
            filename_parts.append("All Profiles")
        
        # Add project name
        if project_id is not None:
            project = self.state.repository.get_project(project_id)
            if project:
                filename_parts.append(project["name"])
        else:
            filename_parts.append("All Projects")
        
        default_filename = " - ".join(filename_parts) + ".json"
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", default_filename, "JSON Files (*.json)"
        )
        if path:
            export_json(self.state.repository, Path(path), profile_id=profile_id, project_id=project_id)

    # Shortcuts
    
    def _on_shortcut_toggle_timer(self) -> None:
        """Handle toggle timer shortcut."""
        if self.state.current_profile_id is None:
            QMessageBox.information(
                self, "Select profile", "Please select or create a profile first."
            )
            return
        self.timer_vm.toggle_timer()

    # System tray
    
    def _update_tray_tooltip(self, entry) -> None:
        """Update tray tooltip based on timer state.
        
        Args:
            entry: Active entry or None
        """
        if hasattr(self, "tray") and self.tray:
            self.tray.setToolTip("Running" if entry else "Stopped")

    def _on_quit_requested(self) -> None:
        """Handle quit request from tray."""
        if self.timer_service.get_active_entry() is not None:
            reply = QMessageBox.question(
                self, "Timer running", "A timer is running. Quit anyway?"
            )
            if reply != QMessageBox.Yes:
                return
        
        # Clean shutdown
        if hasattr(self, "tray") and self.tray:
            self.tray.setVisible(False)
            self.tray.deleteLater()
        
        app = QApplication.instance()
        if app:
            app.quit()
        else:
            self.close()

    # Window management
    
    def _ensure_visible_on_screen(self) -> None:
        """Ensure window is visible on screen."""
        app = QApplication.instance()
        if app is None:
            return
        
        frame = self.frameGeometry()
        if frame.isEmpty():
            return
        
        # Check if on any screen
        center = frame.center()
        screens = app.screens() or []
        for scr in screens:
            if scr.geometry().contains(center):
                return
        
        # Not on any screen - move to primary
        primary = app.primaryScreen()
        if primary is None:
            return
        
        g = primary.availableGeometry()
        self.move(
            max(g.left(), g.center().x() - self.width() // 2),
            max(g.top(), g.center().y() - self.height() // 2),
        )

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Handle window close event.
        
        Args:
            event: Close event
        """
        # Save window state
        settings = self.state.settings
        settings.geometry = bytes(self.saveGeometry())
        settings.window_state = bytes(self.saveState())
        self.state.update_settings(settings)
        
        # Prompt if timer running
        if self.timer_service.get_active_entry() is not None:
            reply = QMessageBox.question(
                self,
                "Timer running",
                "A timer is running. Exit? This will not stop the timer.",
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
        
        # Clean up
        if hasattr(self, "tray") and self.tray:
            self.tray.setVisible(False)
            self.tray.deleteLater()
        
        super().closeEvent(event)

