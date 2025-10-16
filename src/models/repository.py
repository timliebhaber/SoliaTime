from __future__ import annotations

import sqlite3
import time
from typing import Iterable, Optional


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # Profiles
    def create_profile(self, name: str, color: str | None = None) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO profiles(name, color) VALUES(?, ?)", (name, color)
            )
            return cur.lastrowid

    def list_profiles(self, include_archived: bool = False) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            "SELECT * FROM profiles WHERE (? OR archived = 0) ORDER BY name",
            (1 if include_archived else 0,),
        ).fetchall()
        return rows

    def rename_profile(self, profile_id: int, new_name: str) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profiles SET name = ? WHERE id = ?", (new_name, profile_id)
            )

    def set_profile_archived(self, profile_id: int, archived: bool) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profiles SET archived = ? WHERE id = ?",
                (1 if archived else 0, profile_id),
            )

    def get_profile(self, profile_id: int) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)
        ).fetchone()

    # Time entries
    def get_active_entry(self) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM time_entries WHERE end_ts IS NULL ORDER BY start_ts DESC LIMIT 1"
        ).fetchone()

    def start_entry(
        self, profile_id: int, note: str = "", tags_csv: str = ""
    ) -> int:
        now = int(time.time())
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO time_entries(profile_id, start_ts, note, tags) VALUES(?, ?, ?, ?)",
                (profile_id, now, note, tags_csv),
            )
            return cur.lastrowid

    def stop_active_entry(self) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE time_entries SET end_ts = ? WHERE end_ts IS NULL",
                (int(time.time()),),
            )

    def list_entries(
        self,
        profile_id: Optional[int] = None,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
    ) -> list[sqlite3.Row]:
        clauses: list[str] = []
        params: list[object] = []
        if profile_id is not None:
            clauses.append("profile_id = ?")
            params.append(profile_id)
        if start_ts is not None:
            clauses.append("start_ts >= ?")
            params.append(start_ts)
        if end_ts is not None:
            clauses.append("start_ts <= ?")
            params.append(end_ts)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = (
            "SELECT e.*, p.name as profile_name, p.color as profile_color "
            "FROM time_entries e JOIN profiles p ON p.id = e.profile_id "
            f"{where} ORDER BY e.start_ts DESC"
        )
        return self.conn.execute(sql, params).fetchall()

    def update_entry_note_tags(self, entry_id: int, note: str, tags_csv: str) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE time_entries SET note = ?, tags = ? WHERE id = ?",
                (note, tags_csv, entry_id),
            )

    def delete_entry(self, entry_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))


