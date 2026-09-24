import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class TestPhase2DExcelWriter(unittest.TestCase):
    def test_output_excel_has_all_sheets(self):
        from control_tower.excel_writer import write_report

        result = {
            "kpis": {
                "total_tasks": 2,
                "completed_count": 0,
                "open_count": 2,
                "overdue_count": 0,
                "on_time_delivery_pct": None,
                "avg_open_age_days": 3.5,
            },
            "rag": {
                "Alpha": {
                    "rag": "Green",
                    "overdue_ratio": 0.0,
                    "blocked_ratio": 0.0,
                }
            },
            "overdue": [],
            "raid_register": [],
            "executive_summary": "As of 2026-01-15, the portfolio contains 1 project and 2 tasks.",
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "control_tower_report.xlsx"
            write_report(result, str(output_path))

            self.assertTrue(zipfile.is_zipfile(output_path))

            with zipfile.ZipFile(output_path, "r") as archive:
                names = set(archive.namelist())
                required_members = {
                    "[Content_Types].xml",
                    "_rels/.rels",
                    "xl/workbook.xml",
                    "xl/_rels/workbook.xml.rels",
                    "xl/worksheets/sheet1.xml",
                    "xl/worksheets/sheet2.xml",
                    "xl/worksheets/sheet3.xml",
                    "xl/worksheets/sheet4.xml",
                    "xl/worksheets/sheet5.xml",
                }
                self.assertTrue(required_members.issubset(names))

                workbook_xml = archive.read("xl/workbook.xml")
                root = ET.fromstring(workbook_xml)
                ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                sheet_names = [
                    element.attrib["name"]
                    for element in root.findall("m:sheets/m:sheet", ns)
                ]
                self.assertEqual(
                    sheet_names,
                    ["KPIs", "RAG", "Overdue", "RAID", "Executive_Summary"],
                )

                rel_attr = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                workbook_rids = [
                    element.attrib[rel_attr]
                    for element in root.findall("m:sheets/m:sheet", ns)
                ]
                self.assertEqual(workbook_rids, ["rId1", "rId2", "rId3", "rId4", "rId5"])

                rels_xml = archive.read("xl/_rels/workbook.xml.rels")
                rels_root = ET.fromstring(rels_xml)
                rels_ns = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}
                relationships = {
                    element.attrib["Id"]: element.attrib["Target"]
                    for element in rels_root.findall("p:Relationship", rels_ns)
                }
                self.assertEqual(
                    [relationships[rid] for rid in workbook_rids],
                    [
                        "worksheets/sheet1.xml",
                        "worksheets/sheet2.xml",
                        "worksheets/sheet3.xml",
                        "worksheets/sheet4.xml",
                        "worksheets/sheet5.xml",
                    ],
                )

                kpi_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")
                self.assertIn("on_time_delivery_pct", kpi_xml)
                self.assertIn("N/A", kpi_xml)


if __name__ == "__main__":
    unittest.main()

