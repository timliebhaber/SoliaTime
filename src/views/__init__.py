"""View components for the application."""
from .dashboard_view import DashboardView
from .invoices_view import InvoicesView
from .profiles_view import ProfilesView
from .projects_view import ProjectsView
from .services_view import ServicesView
from .timer_view import TimerView
from .vat_calculator_view import VatCalculatorView
from .weekly_view import WeeklyView

# MainWindow is not imported here to avoid circular imports
# Import it directly: from src.views.main_window import MainWindow

__all__ = [
    "DashboardView",
    "InvoicesView",
    "ProfilesView",
    "ProjectsView",
    "ServicesView",
    "TimerView",
    "VatCalculatorView",
    "WeeklyView",
]

