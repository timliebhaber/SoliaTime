"""Application settings management."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from appdirs import user_data_dir


APP_NAME = "SoliaTimeTracking"
APP_AUTHOR = "Solia"


def get_data_dir() -> Path:
    """Get the application data directory.
    
    Returns:
        Path to data directory
    """
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def ensure_app_dirs() -> None:
    """Ensure application directories exist."""
    data = get_data_dir()
    data.mkdir(parents=True, exist_ok=True)


@dataclass
class AppSettings:
    """Application settings data class."""
    
    last_profile_id: int | None = None
    geometry: bytes | None = None  # Qt saves as bytes; serialize as hex
    window_state: bytes | None = None

    def to_json(self) -> dict[str, Any]:
        """Convert settings to JSON-serializable dict.
        
        Returns:
            Dictionary representation
        """
        return {
            "last_profile_id": self.last_profile_id,
            "geometry": self.geometry.hex() if isinstance(self.geometry, (bytes, bytearray)) else None,
            "window_state": self.window_state.hex() if isinstance(self.window_state, (bytes, bytearray)) else None,
        }

    @staticmethod
    def from_json(obj: dict[str, Any] | None) -> "AppSettings":
        """Create AppSettings from JSON dict.
        
        Args:
            obj: Dictionary with settings data
            
        Returns:
            AppSettings instance
        """
        if not obj:
            return AppSettings()
        s = AppSettings()
        s.last_profile_id = obj.get("last_profile_id")
        geom = obj.get("geometry")
        state = obj.get("window_state")
        s.geometry = bytes.fromhex(geom) if isinstance(geom, str) else None
        s.window_state = bytes.fromhex(state) if isinstance(state, str) else None
        return s


SETTINGS_FILE = "settings.json"


class SettingsStore:
    """Persistent settings storage."""

    def __init__(self) -> None:
        """Initialize settings store."""
        self.path = get_data_dir() / SETTINGS_FILE

    def load(self) -> AppSettings:
        """Load settings from disk.
        
        Returns:
            Loaded settings or default if not found
        """
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return AppSettings()
        return AppSettings.from_json(data)

    def save(self, settings: AppSettings) -> None:
        """Save settings to disk.
        
        Args:
            settings: Settings to save
        """
        payload = settings.to_json()
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

