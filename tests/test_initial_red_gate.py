import unittest
from datetime import date

from control_tower.analytics import analyze_rows


AS_OF = date(2026, 1, 15)


class TestInitialRedGate(unittest.TestCase):
    def test_clean_tracker_no_overdue(self):
        rows = [
            {
                "task_id": "T-001",
                "project": "Alpha",
                "owner": "Rashed",
                "status": "Completed",
                "priority": "High",
                "start_date": "2026-01-01",
                "due_date": "2026-01-10",
                "completion_date": "2026-01-09",
                "raid_type": "",
                "raid_description": "",
            },
            {
                "task_id": "T-002",
                "project": "Alpha",
                "owner": "Rashed",
                "status": "Completed",
                "priority": "Medium",
                "start_date": "2026-01-02",
                "due_date": "2026-01-12",
                "completion_date": "2026-01-12",
                "raid_type": "",
                "raid_description": "",
            },
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertEqual(result["kpis"]["overdue_count"], 0)
        self.assertEqual(result["kpis"]["on_time_delivery_pct"], 100.0)
        self.assertEqual(result["rag"]["Alpha"]["rag"], "Green")

    def test_overdue_detection_basic(self):
        rows = [
            {
                "task_id": "T-101",
                "project": "Bravo",
                "owner": "Rashed",
                "status": "In Progress",
                "priority": "Critical",
                "start_date": "2026-01-01",
                "due_date": "2026-01-10",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            }
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertEqual(result["kpis"]["overdue_count"], 1)
        self.assertEqual(len(result["overdue"]), 1)
        self.assertEqual(result["overdue"][0]["task_id"], "T-101")
        self.assertEqual(result["overdue"][0]["days_overdue"], 5)

    def test_on_time_delivery_calculation(self):
        rows = [
            {
                "task_id": "T-201",
                "project": "Charlie",
                "owner": "Rashed",
                "status": "Completed",
                "priority": "High",
                "start_date": "2026-01-01",
                "due_date": "2026-01-08",
                "completion_date": "2026-01-08",
                "raid_type": "",
                "raid_description": "",
            },
            {
                "task_id": "T-202",
                "project": "Charlie",
                "owner": "Rashed",
                "status": "Completed",
                "priority": "High",
                "start_date": "2026-01-01",
                "due_date": "2026-01-08",
                "completion_date": "2026-01-10",
                "raid_type": "",
                "raid_description": "",
            },
            {
                "task_id": "T-203",
                "project": "Charlie",
                "owner": "Rashed",
                "status": "Completed",
                "priority": "Low",
                "start_date": "2026-01-01",
                "due_date": "2026-01-08",
                "completion_date": "",
                "raid_type": "",
                "raid_description": "",
            },
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertEqual(result["kpis"]["completed_count"], 3)
        self.assertEqual(result["kpis"]["on_time_delivery_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()

