#!/usr/bin/env python3
"""创建设计文档测试 Excel — 含加粗、颜色、删除线、背景色、超链接"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.hyperlink import Hyperlink
import os

OUT = os.path.join(os.path.dirname(__file__), "设计文档测试.xlsx")

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "设计说明"

# --- 标题行 ---
ws["A1"] = "设计文档格式转换测试"
ws["A1"].font = Font(bold=True, size=18, color="000000")
ws.merge_cells("A1:E1")

# --- 普通文本 ---
ws["A3"] = "这是普通文本，无特殊格式"

# --- 加粗 ---
ws["A4"] = "这是加粗文本"
ws["A4"].font = Font(bold=True)

# --- 颜色 ---
ws["A5"] = "这是红色文本"
ws["A5"].font = Font(color="FF0000")

ws["A6"] = "这是蓝色文本"
ws["A6"].font = Font(color="0000FF")

# --- 删除线 ---
ws["A7"] = "这是废弃内容（删除线）"
ws["A7"].font = Font(strike=True)

# --- 背景色 ---
ws["A8"] = "这是黄色背景的单元格"
ws["A8"].fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

# --- 加粗+颜色组合 ---
ws["A9"] = "加粗+红色组合"
ws["A9"].font = Font(bold=True, color="FF0000")

# --- 删除线+颜色组合 ---
ws["A10"] = "废弃+灰色删除线"
ws["A10"].font = Font(strike=True, color="808080")

# --- 超链接 ---
ws["A11"] = "GitHub 仓库"
ws["A11"].hyperlink = "https://github.com/Taohenger/ai-tool-lab"
ws["A11"].font = Font(color="0563C1", underline="single")

# --- 斜体 ---
ws["A12"] = "这是斜体文本"
ws["A12"].font = Font(italic=True)

# --- 下划线 ---
ws["A13"] = "这是下划线文本"
ws["A13"].font = Font(underline="single")

# --- 第二区域：设计规格表 ---
ws["A15"] = "设计规格表"
ws["A15"].font = Font(bold=True, size=14)

headers = ["项目", "规格", "状态", "备注"]
for i, h in enumerate(headers):
    cell = ws.cell(row=16, column=i+1, value=h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

data = [
    ["配色方案", "#FF0000 主色", "确定", "需与品牌色一致"],
    ["字体大小", "正文 12pt / 标题 18pt", "确定", ""],
    ["布局方案", "响应式栅格", "废弃", "改用 Flex 布局"],
    ["交互方式", "点击展开", "确定", "参考 Material Design"],
]

for row_idx, row_data in enumerate(data, start=17):
    for col_idx, val in enumerate(row_data, start=1):
        cell = ws.cell(row=row_idx, column=col_idx, value=val)
        # 状态列特殊格式
        if col_idx == 3:
            if val == "确定":
                cell.font = Font(bold=True, color="008000")  # 绿色加粗
            elif val == "废弃":
                cell.font = Font(strike=True, color="FF0000")  # 红色删除线

# 列宽
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 28
ws.column_dimensions["C"].width = 10
ws.column_dimensions["D"].width = 25

# --- 第二个 Sheet：UI 设计说明 ---
ws2 = wb.create_sheet("UI设计说明")
ws2["A1"] = "UI 设计规格"
ws2["A1"].font = Font(bold=True, size=16, color="4472C4")
ws2.merge_cells("A1:D1")

ws2["A3"] = "按钮样式"
ws2["A3"].font = Font(bold=True, size=14)
ws2["A4"] = "圆角矩形，主色填充"
ws2["A5"] = "悬停时加深 10%"
ws2["A5"].font = Font(italic=True, color="808080")

ws2["A7"] = "已废弃的旧方案"
ws2["A7"].font = Font(strike=True, color="FF0000")

ws2["A9"] = "重要提醒"
ws2["A9"].font = Font(bold=True, color="FF0000")
ws2["A9"].fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

ws2.column_dimensions["A"].width = 30

wb.save(OUT)
print(f"✅ 测试设计文档已创建: {OUT}")
print(f"   Sheet1: 设计说明 (13 行格式测试 + 4 行规格表)")
print(f"   Sheet2: UI设计说明 (6 行格式测试)")
