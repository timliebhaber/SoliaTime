from __future__ import annotations

import warnings

# Re-export from new location
from src.views.main_window import MainWindow

warnings.warn(
    "Importing MainWindow from src.ui.main_window is deprecated. "
    "Import from src.views.main_window instead. "
    "The application has been refactored to MVVM architecture.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["MainWindow"]
