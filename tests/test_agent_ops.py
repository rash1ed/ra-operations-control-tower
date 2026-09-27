import tempfile
import unittest
from pathlib import Path
from control_tower.agent_ops import AgentRecord, agent_rag, load_agent_csv, render_markdown, summarize

class AgentOpsTests(unittest.TestCase):
    def make(self, **overrides):
        data = dict(
            agent_id="A-001", role="Operations Analyst", manager="A-CEO",
            status="active", monthly_budget_usd=100.0, spend_usd=25.0,
            open_tasks=4, blocked_tasks=0, heartbeat_age_min=10,
        )
        data.update(overrides)
        return AgentRecord(**data)

    def test_green_agent(self):
        self.assertEqual(agent_rag(self.make()), "GREEN")

    def test_budget_warning_is_amber(self):
        self.assertEqual(agent_rag(self.make(spend_usd=85.0)), "AMBER")

    def test_offline_is_red(self):
        self.assertEqual(agent_rag(self.make(status="offline")), "RED")

    def test_blocked_ratio_over_half_is_red(self):
        self.assertEqual(agent_rag(self.make(open_tasks=3, blocked_tasks=2)), "RED")

    def test_summary_and_markdown(self):
        records = [self.make(agent_id="A-001"), self.make(agent_id="A-002", status="paused", spend_usd=90.0, blocked_tasks=1)]
        s = summarize(records)
        self.assertEqual(s["total_agents"], 2)
        self.assertEqual(s["paused_agents"], 1)
        self.assertEqual(s["rag"]["GREEN"], 1)
        self.assertEqual(s["rag"]["AMBER"], 1)
        report = render_markdown(records)
        self.assertIn("RA Agent Operations Control Tower", report)
        self.assertIn("Synthetic data only", report)

    def test_loader_rejects_duplicate_id(self):
        csv_text = (
            "agent_id,role,manager,status,monthly_budget_usd,spend_usd,open_tasks,blocked_tasks,heartbeat_age_min\n"
            "A-001,Role,Board,active,100,10,1,0,5\n"
            "A-001,Role,Board,active,100,10,1,0,5\n"
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"agents.csv"
            p.write_text(csv_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate agent_id"):
                load_agent_csv(p)

if __name__ == "__main__":
    unittest.main()
