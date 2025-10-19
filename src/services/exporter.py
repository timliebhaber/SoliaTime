"""Backward compatibility stub - exporter has been renamed to export_service.

DEPRECATED: Import from src.services.export_service instead.
"""
from __future__ import annotations

import warnings

# Re-export from new location
from src.services.export_service import export_csv, export_json

warnings.warn(
    "Importing from src.services.exporter is deprecated. "
    "Import from src.services.export_service instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["export_csv", "export_json"]
