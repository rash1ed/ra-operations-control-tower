import unittest
from datetime import date

from control_tower.analytics import analyze_rows


AS_OF = date(2026, 1, 15)


class TestPhase2CAnalytics(unittest.TestCase):
    def test_raid_extraction(self):
        rows = [
            {
                "task_id": "R-001",
                "project": "Foxtrot",
                "owner": "Rashed",
                "status": "In Progress",
                "priority": "High",
                "start_date": "2026-01-01",
                "due_date": "2026-01-20",
                "completion_date": "",
                "raid_type": "Risk",
                "raid_description": "Vendor delay may affect milestone.",
            },
            {
                "task_id": "R-002",
                "project": "Foxtrot",
                "owner": "Nora",
                "status": "Blocked",
                "priority": "Critical",
                "start_date": "2026-01-02",
                "due_date": "2026-01-22",
                "completion_date": "",
                "raid_type": "Issue",
                "raid_description": "Access approval is pending.",
            },
            {
                "task_id": "R-003",
                "project": "Golf",
                "owner": "Rashed",
                "status": "Not Started",
                "priority": "Medium",
                "start_date": "",
                "due_date": "2026-01-25",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "Description without type must be excluded.",
            },
            {
                "task_id": "R-004",
                "project": "Golf",
                "owner": "Lina",
                "status": "In Progress",
                "priority": "Low",
                "start_date": "2026-01-03",
                "due_date": "2026-01-28",
                "completion_date": "",
                "raid_type": "Dependency",
                "raid_description": "Awaiting upstream data.",
            },
            {
                "task_id": "R-005",
                "project": "Golf",
                "owner": "Omar",
                "status": "In Progress",
                "priority": "Low",
                "start_date": "2026-01-04",
                "due_date": "2026-01-29",
                "completion_date": "",
                "raid_type": None,
                "raid_description": "None type must be excluded.",
            },
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertEqual(
            result["raid_register"],
            [
                {
                    "project": "Foxtrot",
                    "owner": "Rashed",
                    "raid_type": "Risk",
                    "raid_description": "Vendor delay may affect milestone.",
                },
                {
                    "project": "Foxtrot",
                    "owner": "Nora",
                    "raid_type": "Issue",
                    "raid_description": "Access approval is pending.",
                },
                {
                    "project": "Golf",
                    "owner": "Lina",
                    "raid_type": "Dependency",
                    "raid_description": "Awaiting upstream data.",
                },
            ],
        )

    def test_empty_completed_set_handled(self):
        rows = [
            {
                "task_id": "E-001",
                "project": "Hotel",
                "owner": "Rashed",
                "status": "Not Started",
                "priority": "Low",
                "start_date": "2026-01-10",
                "due_date": "2026-01-30",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            },
            {
                "task_id": "E-002",
                "project": "Hotel",
                "owner": "Rashed",
                "status": "Blocked",
                "priority": "High",
                "start_date": "2026-01-11",
                "due_date": "2026-01-31",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            },
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertIsNone(result["kpis"]["on_time_delivery_pct"])


if __name__ == "__main__":
    unittest.main()

