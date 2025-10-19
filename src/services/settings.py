"""Backward compatibility stub - settings has been renamed to settings_service.

DEPRECATED: Import from src.services.settings_service instead.
"""
from __future__ import annotations

import warnings

# Re-export from new location
from src.services.settings_service import (
    APP_AUTHOR,
    APP_NAME,
    SETTINGS_FILE,
    AppSettings,
    SettingsStore,
    ensure_app_dirs,
    get_data_dir,
)

warnings.warn(
    "Importing from src.services.settings is deprecated. "
    "Import from src.services.settings_service instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "APP_NAME",
    "APP_AUTHOR",
    "SETTINGS_FILE",
    "AppSettings",
    "SettingsStore",
    "get_data_dir",
    "ensure_app_dirs",
]
