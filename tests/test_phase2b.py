import unittest

from control_tower.validation import ValidationError, validate_rows


class TestPhase2BValidation(unittest.TestCase):
    def test_missing_required_column_fails_gracefully(self):
        rows = [
            {
                "task_id": "T-301",
                "project": "Delta",
                # owner intentionally missing
                "status": "In Progress",
                "priority": "High",
                "start_date": "2026-01-01",
                "due_date": "2026-01-20",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            }
        ]

        with self.assertRaisesRegex(ValidationError, "owner"):
            validate_rows(rows)

    def test_duplicate_task_id_detected(self):
        rows = [
            {
                "task_id": "T-401",
                "project": "Echo",
                "owner": "Rashed",
                "status": "In Progress",
                "priority": "Medium",
                "start_date": "2026-01-01",
                "due_date": "2026-01-20",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            },
            {
                "task_id": "T-401",
                "project": "Echo",
                "owner": "Rashed",
                "status": "Blocked",
                "priority": "Critical",
                "start_date": "2026-01-02",
                "due_date": "2026-01-21",
                "completion_date": "",
                "raid_type": "Issue",
                "raid_description": "Duplicate ID test fixture",
            },
        ]

        with self.assertRaisesRegex(ValidationError, "T-401"):
            validate_rows(rows)


if __name__ == "__main__":
    unittest.main()

