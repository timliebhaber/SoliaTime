"""Backward compatibility stub - dialogs have been moved to src.ui.dialogs submodule.

DEPRECATED: Import from src.ui.dialogs.* instead.
"""
from __future__ import annotations

import warnings

# Re-export from new location for backward compatibility
from src.ui.dialogs.entry_dialog import EntryDialog
from src.ui.dialogs.profile_dialog import ProfileDialog
from src.ui.dialogs.service_dialog import ServiceDialog

warnings.warn(
    "Importing from src.ui.dialogs is deprecated. Import from src.ui.dialogs.* submodules instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ProfileDialog", "EntryDialog", "ServiceDialog"]
