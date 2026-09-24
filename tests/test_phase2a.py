import unittest
from datetime import date

from control_tower.analytics import analyze_rows


AS_OF = date(2026, 1, 15)


def row(task_id, project, status, due_date, start_date="2026-01-01"):
    return {
        "task_id": task_id,
        "project": project,
        "owner": "Rashed",
        "status": status,
        "priority": "High",
        "start_date": start_date,
        "due_date": due_date,
        "completion_date": "",
        "raid_type": "",
        "raid_description": "",
    }


class TestPhase2A(unittest.TestCase):
    def test_rag_green_amber_red_boundaries(self):
        rows = []

        # Green: 0% overdue, 0% blocked.
        for i in range(5):
            rows.append(row(f"G-{i}", "GreenProject", "In Progress", "2026-01-20"))

        # Amber boundary: exactly 20% overdue, 0% blocked.
        rows.append(row("A-O-0", "AmberOverdue", "In Progress", "2026-01-14"))
        for i in range(1, 5):
            rows.append(row(f"A-O-{i}", "AmberOverdue", "In Progress", "2026-01-20"))

        # Amber boundary: 0% overdue, exactly 20% blocked.
        rows.append(row("A-B-0", "AmberBlocked", "Blocked", "2026-01-20"))
        for i in range(1, 5):
            rows.append(row(f"A-B-{i}", "AmberBlocked", "In Progress", "2026-01-20"))

        # Red: 25% overdue.
        rows.append(row("R-O-0", "RedOverdue", "In Progress", "2026-01-14"))
        for i in range(1, 4):
            rows.append(row(f"R-O-{i}", "RedOverdue", "In Progress", "2026-01-20"))

        # Red: 25% blocked.
        rows.append(row("R-B-0", "RedBlocked", "Blocked", "2026-01-20"))
        for i in range(1, 4):
            rows.append(row(f"R-B-{i}", "RedBlocked", "In Progress", "2026-01-20"))
        result = analyze_rows(rows, as_of_date=AS_OF)

        self.assertEqual(result["rag"]["GreenProject"]["rag"], "Green")
        self.assertEqual(result["rag"]["AmberOverdue"]["rag"], "Amber")
        self.assertEqual(result["rag"]["AmberBlocked"]["rag"], "Amber")
        self.assertEqual(result["rag"]["RedOverdue"]["rag"], "Red")
        self.assertEqual(result["rag"]["RedBlocked"]["rag"], "Red")

    def test_avg_open_age_computation(self):
        rows = [
            row("AGE-1", "AgeProject", "In Progress", "2026-01-30", "2026-01-01"),
            row("AGE-2", "AgeProject", "Not Started", "2026-01-30", "2026-01-05"),
            row("AGE-3", "AgeProject", "Blocked", "2026-01-30", ""),
            {
                **row("AGE-4", "AgeProject", "Completed", "2026-01-10", "2026-01-01"),
                "completion_date": "2026-01-10",
            },
        ]

        result = analyze_rows(rows, as_of_date=AS_OF)

        # Eligible open ages are 14 and 10 calendar days; empty start_date is excluded.
        self.assertEqual(result["kpis"]["avg_open_age_days"], 12.0)
        no_eligible_start = [
            row("AGE-5", "NoStart", "In Progress", "2026-01-30", ""),
            row("AGE-6", "NoStart", "Blocked", "2026-01-30", ""),
        ]
        result_no_start = analyze_rows(no_eligible_start, as_of_date=AS_OF)
        self.assertIsNone(result_no_start["kpis"]["avg_open_age_days"])


if __name__ == "__main__":
    unittest.main()
