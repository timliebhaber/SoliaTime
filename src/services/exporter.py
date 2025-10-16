from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Iterable

from src.models.repository import Repository


def export_csv(repo: Repository, path: Path, profile_id: int | None = None) -> None:
    rows = repo.list_entries(profile_id=profile_id)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["profile", "start", "end", "duration_sec", "note", "tags"]) 
        now = int(time.time())
        for r in rows:
            start = int(r["start_ts"]) if r["start_ts"] is not None else None
            end = int(r["end_ts"]) if r["end_ts"] is not None else None
            duration = (end or now) - (start or now) if start else 0
            writer.writerow([
                r["profile_name"],
                start,
                end if end is not None else "",
                duration,
                r["note"] or "",
                r["tags"] or "",
            ])


def export_json(repo: Repository, path: Path, profile_id: int | None = None) -> None:
    rows = repo.list_entries(profile_id=profile_id)
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
            "start_ts": start,
            "end_ts": end,
            "duration_sec": duration,
            "note": r["note"] or "",
            "tags": r["tags"] or "",
        })
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


