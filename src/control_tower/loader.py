"""Stdlib-only tracker loaders for CSV and XLSX inputs."""

import csv
from datetime import date, timedelta
from pathlib import Path
import posixpath
import zipfile
import xml.etree.ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _column_index(reference: str) -> int:
    letters = ""
    for char in reference:
        if char.isalpha():
            letters += char
        else:
            break
    value = 0
    for char in letters.upper():
        value = value * 26 + (ord(char) - 64)
    return value - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall(f"{{{MAIN_NS}}}si"):
        text = "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
        values.append(text)
    return values


def _cell_text(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
    value = cell.find(f"{{{MAIN_NS}}}v")
    raw = "" if value is None or value.text is None else value.text
    if cell_type == "s" and raw:
        return shared[int(raw)]
    return raw


def _first_sheet_path(archive: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    first = workbook.find(f"{{{MAIN_NS}}}sheets/{{{MAIN_NS}}}sheet")
    if first is None:
        raise ValueError("XLSX workbook has no worksheets.")
    rel_id = first.attrib[f"{{{OFFICE_REL_NS}}}id"]

    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall(f"{{{PACKAGE_REL_NS}}}Relationship"):
        if rel.attrib.get("Id") == rel_id:
            target = rel.attrib["Target"].lstrip("/")
            if target.startswith("xl/"):
                return posixpath.normpath(target)
            return posixpath.normpath(posixpath.join("xl", target))
    raise ValueError(f"Worksheet relationship not found: {rel_id}")




def _excel_date_system(archive: zipfile.ZipFile) -> bool:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    props = workbook.find(f"{{{MAIN_NS}}}workbookPr")
    if props is None:
        return False
    return props.attrib.get("date1904", "").lower() in {"1", "true"}


def _normalize_date_value(value: str, date1904: bool) -> str:
    if not value or "-" in value:
        return value
    try:
        serial = float(value)
    except ValueError:
        return value
    epoch = date(1904, 1, 1) if date1904 else date(1899, 12, 30)
    return (epoch + timedelta(days=serial)).isoformat()

def _rows_from_xlsx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path, "r") as archive:
        shared = _shared_strings(archive)
        date1904 = _excel_date_system(archive)
        sheet_path = _first_sheet_path(archive)
        root = ET.fromstring(archive.read(sheet_path))

        matrix: list[list[str]] = []
        for row in root.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row"):
            values: dict[int, str] = {}
            for cell in row.findall(f"{{{MAIN_NS}}}c"):
                index = _column_index(cell.attrib.get("r", "A1"))
                values[index] = _cell_text(cell, shared).strip()
            width = (max(values) + 1) if values else 0
            matrix.append([values.get(index, "") for index in range(width)])

    if not matrix:
        return []

    headers = [value.strip() for value in matrix[0]]
    rows: list[dict[str, str]] = []
    for values in matrix[1:]:
        if not any(value.strip() for value in values):
            continue
        padded = values + [""] * max(0, len(headers) - len(values))
        record = {
            header: padded[index].strip()
            for index, header in enumerate(headers)
            if header
        }
        for field in ("start_date", "due_date", "completion_date"):
            if field in record:
                record[field] = _normalize_date_value(record[field], date1904)
        rows.append(record)
    return rows


def _rows_from_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return [
            {
                (key or "").strip(): ("" if value is None else value.strip())
                for key, value in row.items()
                if key is not None
            }
            for row in reader
            if any((value or "").strip() for value in row.values())
        ]


def load_tracker(input_path: str) -> list[dict[str, str]]:
    """Load a tracker from UTF-8 CSV or the first worksheet of an XLSX file."""
    path = Path(input_path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _rows_from_csv(path)
    if suffix == ".xlsx":
        return _rows_from_xlsx(path)
    raise ValueError("Unsupported input format. Use .csv or .xlsx.")

