# Operations Control Tower v0.1 — Specification

## Objective
A deterministic CLI that reads a task/project tracker from .xlsx or .csv, validates a fixed schema, calculates operational KPIs, assigns project RAG status, extracts overdue and RAID records, and writes a five-sheet Excel report plus a template-based executive summary.

No LLM or external service is permitted in v0.1.

## Repository
- Name: `ra-operations-control-tower`
- Runtime: Python 3.11+
- Test framework: `unittest`
- Runtime dependencies: none
- `pyproject.toml`: `dependencies = []`

## Input schema
Required columns:
- `task_id`: unique, non-empty string
- `project`: non-empty string
- `owner`: non-empty string
- `status`: Not Started / In Progress / Blocked / Completed
- `priority`: Low / Medium / High / Critical
- `due_date`: ISO `YYYY-MM-DD`

Optional columns:
- `start_date`: ISO `YYYY-MM-DD`
- `completion_date`: ISO `YYYY-MM-DD`
- `raid_type`: Risk / Assumption / Issue / Dependency
- `raid_description`: string
## Full planned test matrix after RED-gate approval
1. clean tracker / no overdue
2. basic overdue detection
3. on-time delivery calculation
4. RAG Green/Amber/Red boundaries
5. RAID extraction
6. missing required column fails gracefully
7. duplicate task_id detected
8. average open age computation
9. output workbook has all five sheets
10. empty completed set handled without division error

## Final v0.1 evidence gate
After implementation:
- all approved tests green
- GitHub Actions green
- README.md
- architecture.md
- clean/mixed/edge-case sample trackers
- screenshots of Excel output
- public GitHub repository
- Verifier Agent v0.1 PASS
- proof-register entry

## Known limitations
v0.1 uses ratio-only RAG thresholds. For very small projects (<3 tasks), a single overdue task may disproportionately push RAG to Red. v0.2 may add absolute thresholds for small-N projects.

## Internal vs presentation values
Internal analytics values use `None` for "no data". Presentation layer (CLI, Excel) converts `None` to `N/A` for display.
