"""Deterministic analytics core for Operations Control Tower v0.1.

This initial implementation is intentionally limited to the first GREEN gate:
basic KPI calculations, overdue detection, and per-project RAG.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


def _parse_iso_date(value: str) -> date:
    """Parse a non-empty ISO YYYY-MM-DD date."""
    return date.fromisoformat(value)


def analyze_rows(rows: list[dict[str, Any]], *, as_of_date: date) -> dict[str, Any]:
    """Analyze already-validated tracker rows for the initial GREEN gate."""
    completed_count = 0
    overdue_items: list[dict[str, Any]] = []
    eligible_completed = 0
    on_time_completed = 0
    open_ages: list[int] = []
    projects: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        projects[row["project"]].append(row)
        status = row["status"]
        due_date = _parse_iso_date(row["due_date"])

        if status == "Completed":
            completed_count += 1
            completion_raw = row.get("completion_date", "")
            if completion_raw:
                completion_date = _parse_iso_date(completion_raw)
                eligible_completed += 1
                if completion_date <= due_date:
                    on_time_completed += 1
        else:
            start_raw = row.get("start_date", "")
            if start_raw:
                open_ages.append((as_of_date - _parse_iso_date(start_raw)).days)

        if status != "Completed" and due_date < as_of_date:
            overdue_item = dict(row)
            overdue_item["days_overdue"] = (as_of_date - due_date).days
            overdue_items.append(overdue_item)

    on_time_delivery_pct: float | None
    if eligible_completed == 0:
        on_time_delivery_pct = None
    else:
        on_time_delivery_pct = round(
            (on_time_completed / eligible_completed) * 100,
            2,
        )

    raid_register = [
        {
            "project": row["project"],
            "owner": row["owner"],
            "raid_type": str(row.get("raid_type", "")).strip(),
            "raid_description": "" if row.get("raid_description") is None else str(row.get("raid_description", "")),
        }
        for row in rows
        if row.get("raid_type") is not None and str(row.get("raid_type", "")).strip()
    ]

    rag: dict[str, dict[str, Any]] = {}
    for project, project_rows in projects.items():
        open_rows = [row for row in project_rows if row["status"] != "Completed"]
        total_open = len(open_rows)

        if total_open == 0:
            overdue_ratio = 0.0
            blocked_ratio = 0.0
        else:
            overdue_open = sum(
                1
                for row in open_rows
                if _parse_iso_date(row["due_date"]) < as_of_date
            )
            blocked_open = sum(1 for row in open_rows if row["status"] == "Blocked")
            overdue_ratio = overdue_open / total_open
            blocked_ratio = blocked_open / total_open

        if overdue_ratio == 0 and blocked_ratio == 0:
            rag_value = "Green"
        elif overdue_ratio <= 0.20 and blocked_ratio <= 0.20:
            rag_value = "Amber"
        else:
            rag_value = "Red"

        rag[project] = {
            "rag": rag_value,
            "overdue_ratio": overdue_ratio,
            "blocked_ratio": blocked_ratio,
        }

    avg_open_age_days = (sum(open_ages) / len(open_ages)) if open_ages else None

    total_tasks = len(rows)
    return {
        "kpis": {
            "total_tasks": total_tasks,
            "completed_count": completed_count,
            "open_count": total_tasks - completed_count,
            "overdue_count": len(overdue_items),
            "on_time_delivery_pct": on_time_delivery_pct,
            "avg_open_age_days": avg_open_age_days,
        },
        "overdue": overdue_items,
        "raid_register": raid_register,
        "rag": rag,
    }
