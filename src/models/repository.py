from __future__ import annotations

import sqlite3
import time
from typing import Iterable, Optional


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # Profiles
    def create_profile(
        self,
        name: str,
        color: str | None = None,
        target_seconds: int | None = None,
        company: str | None = None,
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        notes: str | None = None,
    ) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO profiles(name, color, archived, target_seconds, company, contact_person, email, phone, notes) VALUES(?, ?, 0, ?, ?, ?, ?, ?, ?)",
                (name, color, target_seconds, company, contact_person, email, phone, notes),
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

    def set_profile_target_seconds(self, profile_id: int, target_seconds: int | None) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profiles SET target_seconds = ? WHERE id = ?",
                (target_seconds, profile_id),
            )

    def update_profile_contacts(
        self,
        profile_id: int,
        company: str | None,
        contact_person: str | None,
        email: str | None,
        phone: str | None,
    ) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profiles SET company = ?, contact_person = ?, email = ?, phone = ? WHERE id = ?",
                (company, contact_person, email, phone, profile_id),
            )

    def set_profile_notes(self, profile_id: int, notes: str | None) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profiles SET notes = ? WHERE id = ?",
                (notes, profile_id),
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

    def delete_profile(self, profile_id: int) -> None:
        """Delete a profile. Time entries under it will cascade-delete per schema."""
        with self.conn:
            self.conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))

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


    def delete_entries(self, entry_ids: Iterable[int]) -> None:
        """Delete multiple time entries efficiently in a single transaction.

        Skips when the iterable is empty. Uses a parameterized IN clause for
        efficiency and safety.
        """
        ids = list(entry_ids)
        if not ids:
            return
        placeholders = ",".join(["?"] * len(ids))
        sql = f"DELETE FROM time_entries WHERE id IN ({placeholders})"
        with self.conn:
            self.conn.execute(sql, ids)


    # Profile todos
    def list_profile_todos(self, profile_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM profile_todos WHERE profile_id = ? ORDER BY created_ts ASC, id ASC",
            (profile_id,)
        ).fetchall()

    def add_profile_todo(self, profile_id: int, text: str) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO profile_todos(profile_id, text, completed) VALUES(?, ?, 0)",
                (profile_id, text),
            )
            return cur.lastrowid

    def delete_profile_todo(self, todo_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM profile_todos WHERE id = ?", (todo_id,))

    def set_profile_todo_completed(self, todo_id: int, completed: bool) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE profile_todos SET completed = ? WHERE id = ?",
                (1 if completed else 0, todo_id),
            )


    # Services
    def list_services(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM services ORDER BY name"
        ).fetchall()

    def create_service(self, name: str, rate_cents: int, estimated_seconds: int | None = None) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO services(name, rate_cents, estimated_seconds) VALUES(?, ?, ?)",
                (name, rate_cents, estimated_seconds),
            )
            return cur.lastrowid

    def update_service(self, service_id: int, name: str, rate_cents: int, estimated_seconds: int | None) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE services SET name = ?, rate_cents = ?, estimated_seconds = ? WHERE id = ?",
                (name, rate_cents, estimated_seconds, service_id),
            )

    def delete_service(self, service_id: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM services WHERE id = ?", (service_id,))

    # Profile Services
    def add_profile_service(self, profile_id: int, service_id: int, notes: str | None = None) -> int:
        """Add a service instance to a profile."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO profile_services(profile_id, service_id, notes) VALUES(?, ?, ?)",
                (profile_id, service_id, notes),
            )
            return cur.lastrowid

    def list_profile_services(self, profile_id: int) -> list[sqlite3.Row]:
        """List all service instances for a profile with service details."""
        return self.conn.execute(
            """
            SELECT ps.*, s.name as service_name, s.rate_cents, s.estimated_seconds
            FROM profile_services ps
            JOIN services s ON s.id = ps.service_id
            WHERE ps.profile_id = ?
            ORDER BY ps.created_ts DESC
            """,
            (profile_id,)
        ).fetchall()

    def get_profile_service(self, profile_service_id: int) -> Optional[sqlite3.Row]:
        """Get a specific profile service instance."""
        return self.conn.execute(
            """
            SELECT ps.*, s.name as service_name, s.rate_cents, s.estimated_seconds
            FROM profile_services ps
            JOIN services s ON s.id = ps.service_id
            WHERE ps.id = ?
            """,
            (profile_service_id,)
        ).fetchone()

    def update_profile_service_notes(self, profile_service_id: int, notes: str | None) -> None:
        """Update notes for a profile service instance."""
        with self.conn:
            self.conn.execute(
                "UPDATE profile_services SET notes = ? WHERE id = ?",
                (notes, profile_service_id),
            )

    def delete_profile_service(self, profile_service_id: int) -> None:
        """Delete a profile service instance."""
        with self.conn:
            self.conn.execute("DELETE FROM profile_services WHERE id = ?", (profile_service_id,))

    # Profile Service Todos
    def list_profile_service_todos(self, profile_service_id: int) -> list[sqlite3.Row]:
        """List all todos for a profile service instance."""
        return self.conn.execute(
            "SELECT * FROM profile_service_todos WHERE profile_service_id = ? ORDER BY created_ts ASC, id ASC",
            (profile_service_id,)
        ).fetchall()

    def add_profile_service_todo(self, profile_service_id: int, text: str) -> int:
        """Add a todo to a profile service instance."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO profile_service_todos(profile_service_id, text, completed) VALUES(?, ?, 0)",
                (profile_service_id, text),
            )
            return cur.lastrowid

    def set_profile_service_todo_completed(self, todo_id: int, completed: bool) -> None:
        """Set completion status of a profile service todo."""
        with self.conn:
            self.conn.execute(
                "UPDATE profile_service_todos SET completed = ? WHERE id = ?",
                (1 if completed else 0, todo_id),
            )

    def delete_profile_service_todo(self, todo_id: int) -> None:
        """Delete a profile service todo."""
        with self.conn:
            self.conn.execute("DELETE FROM profile_service_todos WHERE id = ?", (todo_id,))