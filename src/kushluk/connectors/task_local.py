"""Provider-neutral, owner-exported local task connector (no remote account scope).

Only dated, incomplete tasks enter the day's practical column. Input is
untrusted local data and never conveys instructions to Kushluk.
"""
from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path

from kushluk.models import PracticalItem, SourceRef


class TaskSourceError(ValueError):
    """Fixed, non-private error messages for rejected task snapshots."""


class LocalTaskConnector:
    def __init__(self, path: Path, target_date: date, *, max_tasks: int = 6):
        self.path, self.target_date = path, target_date
        self.max_tasks = max_tasks

    def fetch(self) -> list[PracticalItem]:
        if self.max_tasks < 1 or self.max_tasks > 30:
            raise TaskSourceError("invalid_task_limit")
        try:
            if (self.path.is_symlink() or not self.path.is_file()
                    or self.path.stat().st_size > 65536):
                raise TaskSourceError("invalid_task_snapshot")
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError) as exc:
            raise TaskSourceError("invalid_task_snapshot") from exc
        if (not isinstance(data, dict) or set(data) != {"schema_version", "tasks"}
                or data["schema_version"] != 1 or not isinstance(data["tasks"], list)
                or len(data["tasks"]) > 150):
            raise TaskSourceError("invalid_task_snapshot")
        seen: set[str] = set()
        selected: list[tuple[str, str, str]] = []
        for row in data["tasks"]:
            if not isinstance(row, dict) or set(row) != {
                "id", "title", "due_date", "status"
            }:
                raise TaskSourceError("invalid_task_record")
            identity, title, due, status = (row[x] for x in (
                "id", "title", "due_date", "status"
            ))
            if (not isinstance(identity, str) or not 1 <= len(identity) <= 100
                    or not isinstance(title, str) or not 1 <= len(title.strip()) <= 140
                    or any(ord(ch) < 32 for ch in title)
                    or status not in ("open", "done")
                    or not isinstance(due, str)):
                raise TaskSourceError("invalid_task_record")
            try:
                day = date.fromisoformat(due)
                if day.isoformat() != due:
                    raise ValueError
            except ValueError as exc:
                raise TaskSourceError("invalid_task_date") from exc
            if identity in seen:
                raise TaskSourceError("duplicate_task_id")
            seen.add(identity)
            if status == "open" and day <= self.target_date:
                selected.append((due, identity, " ".join(title.split())))
        selected.sort(key=lambda x: (x[0], x[1]))
        return [
            PracticalItem(
                label="Task" if due == self.target_date.isoformat() else "Overdue task",
                value=title,
                source=SourceRef(kind="task", name="Owner's local task export"),
            )
            for due, _identity, title in selected[: self.max_tasks]
        ]
