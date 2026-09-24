"""Command-line entry point for Operations Control Tower v0.1."""

import argparse
from datetime import date
from pathlib import Path
import sys
import zipfile

from .analytics import analyze_rows
from .excel_writer import write_report
from .loader import load_tracker
from .validation import ValidationError, validate_rows


def _summary(result: dict, as_of_date: date) -> str:
    kpis = result["kpis"]
    rag_values = [item["rag"] for item in result["rag"].values()]
    rag_counts = {
        "Green": rag_values.count("Green"),
        "Amber": rag_values.count("Amber"),
        "Red": rag_values.count("Red"),
    }
    on_time = kpis["on_time_delivery_pct"]
    on_time_text = "N/A" if on_time is None else f"{on_time:.2f}%"
    return (
        f"As of {as_of_date.isoformat()}: {len(result['rag'])} project(s), "
        f"{kpis['total_tasks']} task(s), {kpis['completed_count']} completed, "
        f"{kpis['open_count']} open, {kpis['overdue_count']} overdue. "
        f"On-time delivery: {on_time_text}. "
        f"RAG: Green {rag_counts['Green']}, Amber {rag_counts['Amber']}, "
        f"Red {rag_counts['Red']}."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ra-control-tower")
    parser.add_argument("--input", required=True, help="Tracker .csv or .xlsx path")
    parser.add_argument("--output", required=True, help="Output .xlsx report path")
    parser.add_argument("--as-of-date", help="ISO YYYY-MM-DD; defaults to today")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        as_of_date = (
            date.fromisoformat(args.as_of_date)
            if args.as_of_date
            else date.today()
        )
        rows = load_tracker(args.input)
        validate_rows(rows)
        result = analyze_rows(rows, as_of_date=as_of_date)
        result["executive_summary"] = _summary(result, as_of_date)

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        write_report(result, str(output))
    except (OSError, ValueError, ValidationError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(result["executive_summary"])
    print(f"Report: {output}")
    return 0

