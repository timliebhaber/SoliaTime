"""Data export service for CSV and JSON formats."""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Optional

from src.models.repository import Repository


def export_csv(repo: Repository, path: Path, profile_id: Optional[int] = None, project_id: Optional[int] = None) -> None:
    """Export time entries to CSV file.
    
    Args:
        repo: Repository instance
        path: Output file path
        profile_id: Optional profile filter
        project_id: Optional project filter
    """
    rows = repo.list_entries(profile_id=profile_id, project_id=project_id)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # CSV header with formatted fields
        writer.writerow(["profile", "project", "start", "end", "duration", "note", "tags"]) 
        now = int(time.time())
        for r in rows:
            start = int(r["start_ts"]) if r["start_ts"] is not None else None
            end = int(r["end_ts"]) if r["end_ts"] is not None else None
            duration = (end or now) - (start or now) if start else 0
            
            # Format timestamps and duration per requirements
            if start is not None:
                start_date = time.strftime("%d.%m.%y", time.localtime(start))
                start_time = time.strftime("%H:%M", time.localtime(start))
                start_str = f"[{start_date}] - {start_time}"
            else:
                start_str = ""
            
            if end is not None:
                end_date = time.strftime("%d.%m.%y", time.localtime(end))
                end_time = time.strftime("%H:%M", time.localtime(end))
                end_str = f"[{end_date}] - {end_time}"
            else:
                end_str = ""
            
            h = max(0, int(duration)) // 3600
            m = (max(0, int(duration)) % 3600) // 60
            s = max(0, int(duration)) % 60
            duration_str = f"{h:02d}:{m:02d}:{s:02d}"
            
            writer.writerow([
                r["profile_name"],
                r["project_name"] or "—",
                start_str,
                end_str,
                duration_str,
                r["note"] or "",
                r["tags"] or "",
            ])


def export_json(repo: Repository, path: Path, profile_id: Optional[int] = None, project_id: Optional[int] = None) -> None:
    """Export time entries to JSON file.
    
    Args:
        repo: Repository instance
        path: Output file path
        profile_id: Optional profile filter
        project_id: Optional project filter
    """
    rows = repo.list_entries(profile_id=profile_id, project_id=project_id)
    payload = []
    now = int(time.time())
    for r in rows:
        start = int(r["start_ts"]) if r["start_ts"] is not None else None
        end = int(r["end_ts"]) if r["end_ts"] is not None else None
        duration = (end or now) - (start or now) if start else 0
        payload.append({
            "id": int(r["id"]),
            "profile_id": int(r["profile_id"]),
            "profile": r["profile_name"],
            "project_id": int(r["project_id"]) if r.get("project_id") is not None else None,
            "project": r["project_name"] or None,
            "start_ts": start,
            "end_ts": end,
            "duration_sec": duration,
            "note": r["note"] or "",
            "tags": r["tags"] or "",
        })
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

