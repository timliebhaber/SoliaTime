"""View components for the application."""
from .dashboard_view import DashboardView
from .profiles_view import ProfilesView
from .services_view import ServicesView
from .timer_view import TimerView

# MainWindow is not imported here to avoid circular imports
# Import it directly: from src.views.main_window import MainWindow

__all__ = [
    "DashboardView",
    "ProfilesView",
    "ServicesView",
    "TimerView",
]

