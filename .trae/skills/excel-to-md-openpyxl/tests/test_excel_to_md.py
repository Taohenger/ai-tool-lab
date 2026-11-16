#!/usr/bin/env python3
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from PIL import Image as PILImage

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "excel_to_md.py"


class ExcelToMarkdownTest(unittest.TestCase):
    def test_complex_workbook_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix="excel-to-md-test-") as temp:
            root = Path(temp)
            source = root / "综合测试.xlsx"
            image_buffer = io.BytesIO()
            PILImage.new("RGB", (20, 10), (255, 0, 0)).save(image_buffer, format="PNG")
            image_buffer.seek(0)

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "综合测试"
            ws.merge_cells("A1:D1")
            ws["A1"] = "完整性格式测试"
            ws["A1"].font = Font(size=18, bold=True, color="FF1F3864")

            for col, value in enumerate(["名称", "数值", "状态", "日期"], 1):
                ws.cell(3, col, value)
            ws["A4"] = "删除线"
            ws["A4"].font = Font(strike=True, color="FF808080")
            ws["A4"].comment = Comment("保留这条批注", "测试员")
            ws["B4"] = 0.1234567890123456
            ws["C4"] = "废弃"
            ws["C4"].fill = PatternFill("solid", fgColor="FFFFFF00")
            ws["D4"] = datetime(2026, 11, 13, 8, 30)
            ws["A5"] = "链接"
            ws["A5"].hyperlink = "https://example.com"
            ws["B5"] = 0.123
            ws["B5"].number_format = "0.00%"
            ws["C5"] = "正常"
            ws["D5"] = datetime(2026, 11, 14)

            for row in ws.iter_rows(min_row=8, max_row=10, min_col=1, max_col=3):
                for cell in row:
                    cell.value = f"R{cell.row}C{cell.column}"
            table = Table(displayName="TestTable", ref="A8:C10")
            table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
            ws.add_table(table)

            ws["A12"] = "隐藏行内容"
            ws.row_dimensions[12].hidden = True
            ws["E12"] = "隐藏列内容"
            ws.column_dimensions["E"].hidden = True
            ws["A14"] = "=1+2"
            excel_image = Image(image_buffer)
            ws.add_image(excel_image, "A16")
            ws["A18"] = CellRichText("普通", TextBlock(InlineFont(b=True, color="FFFF0000"), "粗体"))
            ws["A19"], ws["B19"] = "类别", "销量"
            for row, value in enumerate([10, 20, 30], 20):
                ws.cell(row, 1, f"类别{row - 19}")
                ws.cell(row, 2, value)
            chart = BarChart()
            chart.title = "销售图"
            chart.add_data(Reference(ws, min_col=2, min_row=19, max_row=22), titles_from_data=True)
            chart.set_categories(Reference(ws, min_col=1, min_row=20, max_row=22))
            ws.add_chart(chart, "G3")

            hidden = wb.create_sheet("隐藏工作表")
            hidden["A1"] = "隐藏工作表也不能丢"
            hidden.sheet_state = "hidden"
            wb.save(source)
            image_buffer.close()
            before = hashlib.sha256(source.read_bytes()).hexdigest()

            output = root / "输出"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "-o", str(output)],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())

            pure = (output / "综合测试.md").read_text(encoding="utf-8")
            rich = (output / "综合测试_richtext.md").read_text(encoding="utf-8")
            report = json.loads((output / "conversion-report.json").read_text(encoding="utf-8"))

            self.assertIn("~~删除线~~", pure)
            self.assertIn("0.1234567890123456", pure)
            self.assertIn("12.30%", pure)
            self.assertIn("[链接](https://example.com)", pure)
            self.assertIn("保留这条批注", pure)
            self.assertIn("隐藏行内容", pure)
            self.assertIn("隐藏列内容", pure)
            self.assertIn("隐藏工作表也不能丢", pure)
            self.assertIn("<code>=1+2</code>", pure)
            self.assertIn("TestTable", pure)
            self.assertIn("图表：销售图", pure)
            self.assertIn("'综合测试'!$B$20:$B$22", pure)
            self.assertIn("**粗体**", rich)
            self.assertIn("color:#FF0000", rich)
            self.assertIn("<mark>", rich)
            self.assertIn("assets/sheet01-image01-image1.png", pure)
            self.assertTrue((output / "assets" / "sheet01-image01-image1.png").is_file())

            self.assertEqual(report["totals"]["sheets"], 2)
            self.assertEqual(report["totals"]["actual_tables"], 1)
            self.assertEqual(report["totals"]["images"], 1)
            self.assertEqual(report["totals"]["comments"], 1)
            self.assertEqual(report["totals"]["charts"], 1)
            self.assertEqual(report["totals"]["formula_cells_without_cached_result"], 1)
            self.assertEqual(report["unreferenced_media"], [])
            self.assertGreaterEqual(report["totals"]["auto_tables"], 1)
            self.assertTrue(report["warnings"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
