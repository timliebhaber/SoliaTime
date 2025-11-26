"""Main application entry point."""
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.models.db import get_connection
from src.models.repository import Repository
from src.services.settings_service import SettingsStore, ensure_app_dirs
from src.services.state_service import StateService
from src.services.timer_service import TimerService
from src.viewmodels import (
    DashboardViewModel,
    InvoicesViewModel,
    ProfilesViewModel,
    ProjectsViewModel,
    ServicesViewModel,
    TimerViewModel,
    VatCalculatorViewModel,
    WeeklyViewModel,
)
from src.views.main_window import MainWindow


def main() -> int:
    """Main application entry point.
    
    Returns:
        Exit code
    """
    ensure_app_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("SoliaTime")
    app.setOrganizationName("Solia")

    # Set application icon
    try:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        candidates = [
            base / "ui" / "resources" / "App.ico",
            base / "ui" / "resources" / "app.ico",
            base / "ui" / "resources" / "App.png",
        ]
        for icon_path in candidates:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                break
    except Exception:
        pass

    # Initialize services layer (bottom of dependency chain)
    conn = get_connection()
    repo = Repository(conn)
    settings_store = SettingsStore()
    
    # Create central state service (Singleton)
    state_service = StateService(repo, settings_store)
    
    # Create timer service
    timer_service = TimerService(state_service)
    
    # Create ViewModels
    dashboard_vm = DashboardViewModel()
    timer_vm = TimerViewModel(state_service, timer_service)
    profiles_vm = ProfilesViewModel(state_service, timer_service)
    projects_vm = ProjectsViewModel(state_service)
    services_vm = ServicesViewModel(state_service)
    weekly_vm = WeeklyViewModel(state_service)
    invoices_vm = InvoicesViewModel()
    vat_calculator_vm = VatCalculatorViewModel()
    
    # Create main window with ViewModels
    window = MainWindow(
        state_service=state_service,
        timer_service=timer_service,
        dashboard_vm=dashboard_vm,
        timer_vm=timer_vm,
        profiles_vm=profiles_vm,
        projects_vm=projects_vm,
        services_vm=services_vm,
        weekly_vm=weekly_vm,
        invoices_vm=invoices_vm,
        vat_calculator_vm=vat_calculator_vm,
    )
    
    window.show()
    
    # Ensure window is foreground and not minimized
    try:
        window.showNormal()
        window.raise_()
        window.activateWindow()
    except Exception:
        pass

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
