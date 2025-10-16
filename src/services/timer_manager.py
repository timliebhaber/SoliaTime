from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal
from pathlib import Path

from src.models.repository import Repository
from src.services.settings import get_data_dir


class TimerManager(QObject):
    active_entry_changed = Signal(object)  # emits row or None

    def __init__(self, repository: Repository) -> None:
        super().__init__()
        self.repo = repository

    def get_active_entry(self):
        return self.repo.get_active_entry()

    def start(self, profile_id: int, note: str = "", tags: list[str] | None = None) -> int:
        # ensure only one active entry system-wide
        if self.repo.get_active_entry() is not None:
            self.stop()
        entry_id = self.repo.start_entry(profile_id, note, ",".join(tags or []))
        prof = self.repo.get_profile(profile_id)
        self._log_event("START", profile_id, prof["name"] if prof else "", note)
        self.active_entry_changed.emit(self.repo.get_active_entry())
        return entry_id

    def stop(self) -> None:
        if self.repo.get_active_entry() is None:
            return
        active = self.repo.get_active_entry()
        self.repo.stop_active_entry()
        if active is not None:
            prof = self.repo.get_profile(int(active["profile_id"]))
            self._log_event("STOP", int(active["profile_id"]), prof["name"] if prof else "", active["note"] or "")
        self.active_entry_changed.emit(None)

    def _log_event(self, event: str, profile_id: int, profile_name: str, note: str) -> None:
        log_path = get_data_dir() / "timely.log"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.open("a", encoding="utf-8").write(
                f"{event},{int(__import__('time').time())},{profile_id},{profile_name.replace(',', ' ')},{note.replace(',', ' ')}\n"
            )
        except Exception:
            pass


