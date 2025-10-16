from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from appdirs import user_data_dir


APP_NAME = "SoliaTimeTracking"
APP_AUTHOR = "Solia"


def get_data_dir() -> Path:
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def ensure_app_dirs() -> None:
    data = get_data_dir()
    data.mkdir(parents=True, exist_ok=True)


@dataclass
class AppSettings:
    theme: str = "dark"
    last_profile_id: int | None = None
    geometry: bytes | None = None  # Qt saves as bytes; serialize as hex
    window_state: bytes | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "last_profile_id": self.last_profile_id,
            "geometry": self.geometry.hex() if isinstance(self.geometry, (bytes, bytearray)) else None,
            "window_state": self.window_state.hex() if isinstance(self.window_state, (bytes, bytearray)) else None,
        }

    @staticmethod
    def from_json(obj: dict[str, Any] | None) -> "AppSettings":
        if not obj:
            return AppSettings()
        s = AppSettings()
        s.theme = obj.get("theme", s.theme)
        s.last_profile_id = obj.get("last_profile_id")
        geom = obj.get("geometry")
        state = obj.get("window_state")
        s.geometry = bytes.fromhex(geom) if isinstance(geom, str) else None
        s.window_state = bytes.fromhex(state) if isinstance(state, str) else None
        return s


SETTINGS_FILE = "settings.json"


class SettingsStore:
    def __init__(self) -> None:
        self.path = get_data_dir() / SETTINGS_FILE

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return AppSettings()
        return AppSettings.from_json(data)

    def save(self, settings: AppSettings) -> None:
        payload = settings.to_json()
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


