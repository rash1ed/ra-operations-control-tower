# RA Operations Control Tower

Deterministic, dependency-free operations reporting CLI for task and project trackers.

It reads a `.csv` or `.xlsx` tracker, validates the schema, calculates operational KPIs, assigns per-project RAG status, extracts overdue and RAID records, and writes a five-sheet Excel report.

## v0.1 scope

- Python 3.11+
- Runtime dependencies: none
- CSV input: UTF-8 / UTF-8-SIG
- XLSX input: first worksheet, parsed directly from OOXML
- XLSX output: written directly with `zipfile` + `xml.etree.ElementTree`
- No LLM calls
- No external APIs
- No web UI
- No notifications

## Output workbook

Every report contains exactly five worksheets:

1. `KPIs`
2. `RAG`
3. `Overdue`
4. `RAID`
5. `Executive_Summary`

Internal missing values use `None`. The Excel presentation layer renders them as `N/A`.

## Input schema

Required columns: `task_id`, `project`, `owner`, `status`, `priority`, `due_date`.

Optional columns: `start_date`, `completion_date`, `raid_type`, `raid_description`.

Allowed status values: `Not Started`, `In Progress`, `Blocked`, `Completed`.

Allowed priority values: `Low`, `Medium`, `High`, `Critical`.

Allowed RAID types: `Risk`, `Assumption`, `Issue`, `Dependency`.

Dates use ISO `YYYY-MM-DD`. XLSX serial dates produced by Microsoft Excel are normalized to ISO during loading.

## Usage

From the repository root:

```cmd
set PYTHONPATH=src
python -m control_tower --input samples\mixed.csv --output output\report.xlsx --as-of-date 2026-01-15
```

XLSX input works the same way:

```cmd
set PYTHONPATH=src
python -m control_tower --input samples\mixed.xlsx --output output\report.xlsx --as-of-date 2026-01-15
```

If `--as-of-date` is omitted, only the CLI uses the current local date. Analytics functions never call `date.today()`.

## KPI rules

- `total_tasks`: all validated rows
- `completed_count`: rows with `status == Completed`
- `open_count`: all non-completed rows
- `overdue_count`: open rows with `due_date < as_of_date`
- `on_time_delivery_pct`: completed rows with a valid `completion_date`; on-time means `completion_date <= due_date`
- `avg_open_age_days`: average calendar age of open rows with a valid `start_date`

If no completed row has a valid completion date, `on_time_delivery_pct` is internally `None` and displays as `N/A`.

## RAG rules

For each project:

- denominator = open tasks
- Green: overdue ratio = 0 **and** blocked ratio = 0
- Amber: after Green is excluded, overdue ratio <= 20% **and** blocked ratio <= 20%
- Red: otherwise

Known limitation: ratio-only thresholds can be harsh for very small projects.

## Validation

Validation is fail-fast and checks, in order:

1. required keys
2. required non-empty values
3. duplicate `task_id`
4. status / priority / RAID enums
5. ISO date format

A `raid_description` without a `raid_type` produces a warning and is excluded from the RAID register.

## Evidence status

Local evidence currently includes:

- 10 / 10 approved `unittest` tests passing
- CSV end-to-end smoke passing
- XLSX end-to-end smoke passing using a workbook created by Microsoft Excel
- generated reports opened successfully by Microsoft Excel through the Excel COM application
- RA Verifier Agent v0.1 PASS on the 10-test Phase 2d artifact
- secret scan PASS

See `docs/architecture.md`, `docs/validation.txt`, and `docs/proof-register.md`.

### Excel evidence

![KPIs rendered by Microsoft Excel](docs/evidence/kpis.png)

![RAG rendered by Microsoft Excel](docs/evidence/rag.png)

## Samples

- `samples/clean.csv`
- `samples/mixed.csv`
- `samples/mixed.xlsx`
- `samples/edge-case.csv`

## License

No license is granted by default. All rights reserved unless a license is added later.
