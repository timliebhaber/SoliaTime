"""Backward compatibility stub - timer_manager has been renamed to timer_service.

DEPRECATED: Import from src.services.timer_service instead.
"""
from __future__ import annotations

import warnings

# Re-export from new location
from src.services.timer_service import TimerService as TimerManager

warnings.warn(
    "Importing from src.services.timer_manager is deprecated. "
    "Import from src.services.timer_service instead. "
    "TimerManager has been renamed to TimerService.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["TimerManager"]
