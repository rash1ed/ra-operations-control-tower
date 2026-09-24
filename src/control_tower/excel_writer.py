"""Minimal stdlib-only OOXML writer for Operations Control Tower v0.1."""

import zipfile
import xml.etree.ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("", MAIN_NS)
ET.register_namespace("r", OFFICE_REL_NS)


def _cell_reference(column_number: int, row_number: int) -> str:
    letters = ""
    number = column_number
    while number:
        number, remainder = divmod(number - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_number}"


def _append_cell(row_element: ET.Element, reference: str, value: object) -> None:
    if value is None:
        value = "N/A"

    cell = ET.SubElement(row_element, f"{{{MAIN_NS}}}c", {"r": reference})
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        cell.set("t", "n")
        ET.SubElement(cell, f"{{{MAIN_NS}}}v").text = str(value)
        return

    cell.set("t", "inlineStr")
    inline = ET.SubElement(cell, f"{{{MAIN_NS}}}is")
    ET.SubElement(inline, f"{{{MAIN_NS}}}t").text = str(value)


def _worksheet_xml(rows: list[list[object]]) -> bytes:
    ET.register_namespace("", MAIN_NS)
    worksheet = ET.Element(f"{{{MAIN_NS}}}worksheet")
    sheet_data = ET.SubElement(worksheet, f"{{{MAIN_NS}}}sheetData")

    for row_number, values in enumerate(rows, start=1):
        row_element = ET.SubElement(
            sheet_data,
            f"{{{MAIN_NS}}}row",
            {"r": str(row_number)},
        )
        for column_number, value in enumerate(values, start=1):
            _append_cell(
                row_element,
                _cell_reference(column_number, row_number),
                value,
            )

    return ET.tostring(worksheet, encoding="utf-8", xml_declaration=True)


def _content_types_xml() -> bytes:
    ET.register_namespace("", CONTENT_TYPES_NS)
    root = ET.Element(f"{{{CONTENT_TYPES_NS}}}Types")
    ET.SubElement(
        root,
        f"{{{CONTENT_TYPES_NS}}}Default",
        {
            "Extension": "xml",
            "ContentType": "application/xml",
        },
    )
    ET.SubElement(
        root,
        f"{{{CONTENT_TYPES_NS}}}Default",
        {
            "Extension": "rels",
            "ContentType": (
                "application/vnd.openxmlformats-package.relationships+xml"
            ),
        },
    )
    ET.SubElement(
        root,
        f"{{{CONTENT_TYPES_NS}}}Override",
        {
            "PartName": "/xl/workbook.xml",
            "ContentType": (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet.main+xml"
            ),
        },
    )
    for sheet_number in range(1, 6):
        ET.SubElement(
            root,
            f"{{{CONTENT_TYPES_NS}}}Override",
            {
                "PartName": f"/xl/worksheets/sheet{sheet_number}.xml",
                "ContentType": (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.worksheet+xml"
                ),
            },
        )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _root_relationships_xml() -> bytes:
    ET.register_namespace("", REL_NS)
    root = ET.Element(f"{{{REL_NS}}}Relationships")
    ET.SubElement(
        root,
        f"{{{REL_NS}}}Relationship",
        {
            "Id": "rId1",
            "Type": f"{OFFICE_REL_NS}/officeDocument",
            "Target": "xl/workbook.xml",
        },
    )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _workbook_xml(sheet_names: list[str]) -> bytes:
    ET.register_namespace("", MAIN_NS)
    ET.register_namespace("r", OFFICE_REL_NS)
    workbook = ET.Element(f"{{{MAIN_NS}}}workbook")
    sheets = ET.SubElement(workbook, f"{{{MAIN_NS}}}sheets")

    for index, name in enumerate(sheet_names, start=1):
        ET.SubElement(
            sheets,
            f"{{{MAIN_NS}}}sheet",
            {
                "name": name,
                "sheetId": str(index),
                f"{{{OFFICE_REL_NS}}}id": f"rId{index}",
            },
        )

    return ET.tostring(workbook, encoding="utf-8", xml_declaration=True)


def _workbook_relationships_xml() -> bytes:
    ET.register_namespace("", REL_NS)
    root = ET.Element(f"{{{REL_NS}}}Relationships")

    for index in range(1, 6):
        ET.SubElement(
            root,
            f"{{{REL_NS}}}Relationship",
            {
                "Id": f"rId{index}",
                "Type": f"{OFFICE_REL_NS}/worksheet",
                "Target": f"worksheets/sheet{index}.xml",
            },
        )

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _kpi_rows(result: dict) -> list[list[object]]:
    rows: list[list[object]] = [["metric", "value"]]
    for key, value in result.get("kpis", {}).items():
        rows.append([key, value])
    return rows


def _rag_rows(result: dict) -> list[list[object]]:
    rows: list[list[object]] = [
        ["project", "rag", "overdue_ratio", "blocked_ratio"]
    ]
    for project, values in result.get("rag", {}).items():
        rows.append(
            [
                project,
                values.get("rag", ""),
                values.get("overdue_ratio"),
                values.get("blocked_ratio"),
            ]
        )
    return rows
def _overdue_rows(result: dict) -> list[list[object]]:
    headers = [
        "task_id",
        "project",
        "owner",
        "status",
        "priority",
        "due_date",
        "days_overdue",
    ]
    rows: list[list[object]] = [headers]
    for item in result.get("overdue", []):
        rows.append([item.get(header, "") for header in headers])
    return rows


def _raid_rows(result: dict) -> list[list[object]]:
    headers = ["project", "owner", "raid_type", "raid_description"]
    rows: list[list[object]] = [headers]
    for item in result.get("raid_register", []):
        rows.append([item.get(header, "") for header in headers])
    return rows


def _executive_summary_rows(result: dict) -> list[list[object]]:
    summary = result.get("executive_summary", "")
    return [["Executive Summary"], [summary]]


def write_report(result: dict, output_path: str) -> None:
    """Writes the 5-sheet report as a valid .xlsx file using stdlib only."""
    sheet_names = [
        "KPIs",
        "RAG",
        "Overdue",
        "RAID",
        "Executive_Summary",
    ]
    sheet_rows = [
        _kpi_rows(result),
        _rag_rows(result),
        _overdue_rows(result),
        _raid_rows(result),
        _executive_summary_rows(result),
    ]

    package_parts = {
        "[Content_Types].xml": _content_types_xml(),
        "_rels/.rels": _root_relationships_xml(),
        "xl/workbook.xml": _workbook_xml(sheet_names),
        "xl/_rels/workbook.xml.rels": _workbook_relationships_xml(),
    }

    for index, rows in enumerate(sheet_rows, start=1):
        package_parts[f"xl/worksheets/sheet{index}.xml"] = _worksheet_xml(rows)

    with zipfile.ZipFile(
        output_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for member_name, payload in package_parts.items():
            archive.writestr(member_name, payload)
