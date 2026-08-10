#!/usr/bin/env python3
"""
Excel 设计文档 → Markdown 转换脚本
使用 OfficeCLI 读取 Excel 格式信息，转换为 Markdown
"""
import json
import subprocess
import os
import sys
import re

XLSX_FILE = os.path.join(os.path.dirname(__file__), "设计文档测试.xlsx")
OUTPUT_MD = os.path.join(os.path.dirname(__file__), "设计文档测试.md")

def officecli_json(args):
    """执行 officecli 命令并返回 JSON"""
    cmd = ["officecli"] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(XLSX_FILE))
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "raw": result.stdout}

def normalize_color(color_str):
    """将 #RRGGBBAA 或 #RRGGBB 格式统一为 #RRGGBB（OfficeCLI 返回 RRGGBBAA）"""
    if not color_str:
        return None
    c = color_str.lstrip("#")
    if len(c) == 8:  # RRGGBBAA → RRGGBB（前6位是颜色，后2位是 alpha）
        return "#" + c[:6]
    if len(c) == 6:
        return "#" + c
    return color_str

def cell_to_md(text, fmt):
    """将单元格格式转换为 Markdown 片段"""
    if not text or text.strip() == "":
        return ""
    md = text

    bold = fmt.get("font.bold", False)
    italic = fmt.get("font.italic", False)
    strike = fmt.get("strike", False)
    underline = fmt.get("underline", "")
    color = normalize_color(fmt.get("font.color"))
    fill = normalize_color(fmt.get("fill"))
    link = fmt.get("link", "")
    font_size = fmt.get("font.size", "")

    # 标题映射（基于字号）
    if font_size:
        size_match = re.match(r"(\d+)", font_size)
        if size_match:
            sz = int(size_match.group(1))
            if sz >= 18:
                return f"# {md}"
            elif sz >= 14 and not bold:
                return f"## {md}"
            elif sz >= 14 and bold:
                return f"### {md}"

    # 超链接
    if link:
        md = f"[{md}]({link})"
    else:
        # 加粗
        if bold:
            md = f"**{md}**"
        # 删除线
        if strike:
            md = f"~~{md}~~"

    # 斜体
    if italic:
        md = f"*{md}*"

    # 下划线
    if underline and underline != "none":
        md = f"<u>{md}</u>"

    # 颜色（HTML span，因 Markdown 不支持颜色）
    if color and color != "#000000":
        md = f'<span style="color:{color}">{md}</span>'

    # 背景色（mark 标签）
    if fill and fill.upper() in ("#FFFF00", "#FFF2CC"):
        md = f"<mark>{md}</mark>"
    elif fill and fill.upper() != "#FFFFFF":
        md = f'<span style="background-color:{fill}">{md}</span>'

    return md

def shape_to_md(text, fmt):
    """将吹出形状转换为 Markdown 引用块"""
    if not text:
        return ""
    md = text
    color = normalize_color(fmt.get("color"))
    fill = normalize_color(fmt.get("fill"))
    bold = fmt.get("bold", False)

    if bold:
        md = f"**{md}**"

    # 吹出形状用引用块表示
    prefix = "> 📌"
    if fill and fill.upper() == "#FFFF00":
        prefix = "> 📌 ⚠️"
    elif fill and fill.upper() == "#FF0000":
        prefix = "> 📌 ❌"

    return f"{prefix} {md}"

def main():
    print(f"读取 Excel: {XLSX_FILE}")

    # 1) 获取所有 sheet
    view = officecli_json(["view", XLSX_FILE, "outline"])
    print(f"Sheet 列表: {view}")

    # 2) 查询所有单元格
    cells_resp = officecli_json(["query", XLSX_FILE, "cell"])
    if not cells_resp.get("success"):
        print(f"❌ 查询 cell 失败: {cells_resp}")
        sys.exit(1)

    cells = cells_resp["data"]["results"]
    print(f"找到 {len(cells)} 个单元格")

    # 3) 查询所有 shape（吹出形状）
    shapes_resp = officecli_json(["query", XLSX_FILE, "shape"])
    shapes = []
    if shapes_resp.get("success"):
        shapes = shapes_resp["data"]["results"]
        print(f"找到 {len(shapes)} 个吹出形状")

    # 4) 按 sheet 分组
    sheet_data = {}
    for cell in cells:
        parts = cell["path"].split("/")
        sheet_name = parts[1]
        if sheet_name not in sheet_data:
            sheet_data[sheet_name] = {"cells": [], "shapes": []}
        sheet_data[sheet_name]["cells"].append(cell)

    for shape in shapes:
        parts = shape["path"].split("/")
        sheet_name = parts[1]
        if sheet_name not in sheet_data:
            sheet_data[sheet_name] = {"cells": [], "shapes": []}
        sheet_data[sheet_name]["shapes"].append(shape)

    # 5) 生成 Markdown
    md_lines = []
    md_lines.append("<!-- 由 OfficeCLI 从 Excel 自动转换生成 -->\n")

    for sheet_name, data in sheet_data.items():
        md_lines.append(f"# {sheet_name}\n")

        # 检测是否为表格区域（有连续行且有多个列）
        cells_list = data["cells"]
        is_table = False
        row_cells = {}
        for c in cells_list:
            parts = c["path"].split("/")
            cell_ref = parts[-1]  # A1, B2, etc.
            row_match = re.match(r"([A-Z]+)(\d+)", cell_ref)
            if row_match:
                row_num = int(row_match.group(2))
                if row_num not in row_cells:
                    row_cells[row_num] = []
                row_cells[row_num].append(c)

        # 检测表格区域（行16-20为设计规格表）
        table_rows = {r: cells for r, cells in row_cells.items() if 16 <= r <= 20}
        # A15 是表格标题，和表格一起输出，不单独输出
        normal_rows = {r: cells for r, cells in row_cells.items() if r < 15 or r > 20}

        # 先输出普通行
        for row_num in sorted(normal_rows.keys()):
            row_cells_sorted = sorted(normal_rows[row_num], key=lambda c: c["path"])
            row_texts = []
            for c in row_cells_sorted:
                text = c.get("text", "")
                fmt = c.get("format", {})
                if fmt.get("empty"):
                    continue
                md_line = cell_to_md(text, fmt)
                if md_line:
                    row_texts.append(md_line)
            if row_texts:
                md_lines.extend(row_texts)
                md_lines.append("")

        # 如果有表格区域，输出为 Markdown 表格
        if table_rows:
            # A15 是表格标题
            title_row = row_cells.get(15, [])
            if title_row:
                title_cell = title_row[0]
                title_md = cell_to_md(title_cell.get("text", ""), title_cell.get("format", {}))
                if title_md:
                    md_lines.append(title_md + "\n")
            else:
                md_lines.append("### 设计规格表\n")
            sorted_table_rows = sorted(table_rows.keys())
            # 表头
            header_cells = table_rows[sorted_table_rows[0]]
            header_cells_sorted = sorted(header_cells, key=lambda c: c["path"])
            headers = [c.get("text", "") for c in header_cells_sorted]
            md_lines.append("| " + " | ".join(headers) + " |")
            md_lines.append("|" + "|".join(["---"] * len(headers)) + "|")

            # 数据行
            for row_num in sorted_table_rows[1:]:
                row_cells_sorted = sorted(table_rows[row_num], key=lambda c: c["path"])
                row_mds = []
                for c in row_cells_sorted:
                    text = c.get("text", "")
                    fmt = c.get("format", {})
                    row_mds.append(cell_to_md(text, fmt))
                md_lines.append("| " + " | ".join(row_mds) + " |")
            md_lines.append("")

        # 输出吹出形状（悬浮吹出泡）
        if data["shapes"]:
            md_lines.append("---\n")
            md_lines.append("## 悬浮吹出形状（Callout）\n")
            for shape in data["shapes"]:
                text = shape.get("text", "")
                fmt = shape.get("format", {})
                md_line = shape_to_md(text, fmt)
                if md_line:
                    md_lines.append(md_line)
                    md_lines.append("")
            md_lines.append("")

    # 写入文件
    md_content = "\n".join(md_lines)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ Markdown 已生成: {OUTPUT_MD}")
    print(f"   总行数: {len(md_lines)}")

if __name__ == "__main__":
    main()
