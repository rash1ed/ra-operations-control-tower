"""Schema validation for Operations Control Tower v0.1."""

from __future__ import annotations

from datetime import date
import re
import warnings


class ValidationError(Exception):
    """Raised when tracker rows violate the SPEC schema."""

    pass


def validate_rows(rows: list[dict]) -> None:
    """Validate tracker rows in fail-fast SPEC order."""
    required_fields = (
        "task_id",
        "project",
        "owner",
        "status",
        "priority",
        "due_date",
    )
    valid_statuses = {"Not Started", "In Progress", "Blocked", "Completed"}
    valid_priorities = {"Low", "Medium", "High", "Critical"}
    valid_raid_types = {"Risk", "Assumption", "Issue", "Dependency"}
    date_fields = ("start_date", "due_date", "completion_date")
    # 1. Required keys present.
    for row_number, row in enumerate(rows, start=1):
        for field in required_fields:
            if field not in row:
                raise ValidationError(
                    f"Missing required field '{field}' in row {row_number}"
                )

    # 2. Required values non-empty after stripping.
    for row_number, row in enumerate(rows, start=1):
        for field in required_fields:
            value = row[field]
            if value is None or str(value).strip() == "":
                raise ValidationError(
                    f"Empty required field '{field}' in row {row_number}"
                )

    # 3. Duplicate task_id detection.
    seen_task_ids: set[str] = set()
    for row in rows:
        task_id = str(row["task_id"]).strip()
        if task_id in seen_task_ids:
            raise ValidationError(f"Duplicate task_id: {task_id}")
        seen_task_ids.add(task_id)
    # 4. Enum validation.
    for row_number, row in enumerate(rows, start=1):
        status = str(row["status"]).strip()
        if status not in valid_statuses:
            raise ValidationError(
                f"Invalid status '{status}' in row {row_number}"
            )

        priority = str(row["priority"]).strip()
        if priority not in valid_priorities:
            raise ValidationError(
                f"Invalid priority '{priority}' in row {row_number}"
            )

        raid_raw = row.get("raid_type", "")
        raid_type = "" if raid_raw is None else str(raid_raw).strip()
        if raid_type and raid_type not in valid_raid_types:
            raise ValidationError(
                f"Invalid raid_type '{raid_type}' in row {row_number}"
            )
    # 5. ISO YYYY-MM-DD date validation.
    iso_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    for row_number, row in enumerate(rows, start=1):
        for field in date_fields:
            if field not in row:
                continue
            raw = row[field]
            value = "" if raw is None else str(raw).strip()
            if not value:
                continue
            if iso_pattern.fullmatch(value) is None:
                raise ValidationError(
                    f"Invalid ISO date in field '{field}' in row {row_number}: {value}"
                )
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError(
                    f"Invalid ISO date in field '{field}' in row {row_number}: {value}"
                ) from exc

    # SPEC warning: description without a RAID type is tolerated.
    for row_number, row in enumerate(rows, start=1):
        description_raw = row.get("raid_description", "")
        raid_raw = row.get("raid_type", "")
        description = "" if description_raw is None else str(description_raw).strip()
        raid_type = "" if raid_raw is None else str(raid_raw).strip()
        if description and not raid_type:
            warnings.warn(
                f"raid_description present without raid_type in row {row_number}",
                UserWarning,
                stacklevel=2,
            )
