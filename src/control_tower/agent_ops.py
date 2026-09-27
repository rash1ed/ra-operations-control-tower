from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ALLOWED_STATUS = {"active", "paused", "offline"}

@dataclass(frozen=True)
class AgentRecord:
    agent_id: str
    role: str
    manager: str
    status: str
    monthly_budget_usd: float
    spend_usd: float
    open_tasks: int
    blocked_tasks: int
    heartbeat_age_min: int

    @property
    def budget_utilization_pct(self) -> float:
        if self.monthly_budget_usd <= 0:
            return 0.0
        return round((self.spend_usd / self.monthly_budget_usd) * 100, 1)

def load_agent_csv(path: str | Path) -> list[AgentRecord]:
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "agent_id","role","manager","status","monthly_budget_usd",
            "spend_usd","open_tasks","blocked_tasks","heartbeat_age_min"
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("missing columns: " + ", ".join(sorted(missing)))
        seen = set()
        for row in reader:
            agent_id = (row["agent_id"] or "").strip()
            if not agent_id:
                raise ValueError("agent_id is required")
            if agent_id in seen:
                raise ValueError(f"duplicate agent_id: {agent_id}")
            seen.add(agent_id)
            status = (row["status"] or "").strip().lower()
            if status not in ALLOWED_STATUS:
                raise ValueError(f"invalid status for {agent_id}: {status}")
            rec = AgentRecord(
                agent_id=agent_id,
                role=(row["role"] or "").strip(),
                manager=(row["manager"] or "").strip(),
                status=status,
                monthly_budget_usd=float(row["monthly_budget_usd"]),
                spend_usd=float(row["spend_usd"]),
                open_tasks=int(row["open_tasks"]),
                blocked_tasks=int(row["blocked_tasks"]),
                heartbeat_age_min=int(row["heartbeat_age_min"]),
            )
            if rec.monthly_budget_usd < 0 or rec.spend_usd < 0:
                raise ValueError(f"negative budget/spend for {agent_id}")
            if rec.open_tasks < 0 or rec.blocked_tasks < 0:
                raise ValueError(f"negative task count for {agent_id}")
            if rec.blocked_tasks > rec.open_tasks:
                raise ValueError(f"blocked_tasks exceeds open_tasks for {agent_id}")
            rows.append(rec)
    return rows

def agent_rag(record: AgentRecord) -> str:
    blocked_ratio = record.blocked_tasks / record.open_tasks if record.open_tasks else 0.0
    if (
        record.status == "offline"
        or record.budget_utilization_pct >= 100.0
        or record.heartbeat_age_min > 120
        or blocked_ratio > 0.50
    ):
        return "RED"
    if (
        record.status == "paused"
        or record.budget_utilization_pct >= 80.0
        or record.heartbeat_age_min > 45
        or record.blocked_tasks > 0
    ):
        return "AMBER"
    return "GREEN"

def summarize(records: Iterable[AgentRecord]) -> dict[str, object]:
    items = list(records)
    total_budget = round(sum(r.monthly_budget_usd for r in items), 2)
    total_spend = round(sum(r.spend_usd for r in items), 2)
    rag = {"GREEN": 0, "AMBER": 0, "RED": 0}
    for item in items:
        rag[agent_rag(item)] += 1
    return {
        "total_agents": len(items),
        "active_agents": sum(r.status == "active" for r in items),
        "paused_agents": sum(r.status == "paused" for r in items),
        "offline_agents": sum(r.status == "offline" for r in items),
        "total_budget_usd": total_budget,
        "total_spend_usd": total_spend,
        "budget_utilization_pct": round((total_spend / total_budget) * 100, 1) if total_budget else 0.0,
        "open_tasks": sum(r.open_tasks for r in items),
        "blocked_tasks": sum(r.blocked_tasks for r in items),
        "rag": rag,
    }

def render_markdown(records: Iterable[AgentRecord]) -> str:
    items = list(records)
    s = summarize(items)
    lines = [
        "# RA Agent Operations Control Tower — Demo Report","",
        "Synthetic data only. No production agents, credentials, or private operational data.","",
        "## Executive KPIs","",
        f"- Total agents: **{s['total_agents']}**",
        f"- Active / paused / offline: **{s['active_agents']} / {s['paused_agents']} / {s['offline_agents']}**",
        f"- Budget utilization: **{s['budget_utilization_pct']}%**",
        f"- Open tasks: **{s['open_tasks']}**",
        f"- Blocked tasks: **{s['blocked_tasks']}**",
        f"- RAG: **G {s['rag']['GREEN']} / A {s['rag']['AMBER']} / R {s['rag']['RED']}**","",
        "## Agent Health","",
        "| Agent | Role | Manager | Status | Budget % | Open | Blocked | Heartbeat age | RAG |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for r in items:
        lines.append(
            f"| {r.agent_id} | {r.role} | {r.manager or 'Board'} | {r.status} | "
            f"{r.budget_utilization_pct:.1f}% | {r.open_tasks} | {r.blocked_tasks} | "
            f"{r.heartbeat_age_min}m | {agent_rag(r)} |"
        )
    return "\n".join(lines) + "\n"
