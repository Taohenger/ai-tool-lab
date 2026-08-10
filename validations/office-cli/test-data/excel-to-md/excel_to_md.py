#!/usr/bin/env python3
"""
Excel 设计文档 → Markdown 转换脚本
使用 OfficeCLI 读取 Excel 格式信息，转换为 Markdown

输出 2 个文件：
  1) xxx.md          — 通用纯净版（Emoji+注释标记颜色，GitHub/所有渲染器兼容）
  2) xxx_richtext.md — 富文本版（HTML span+颜色，VS Code / Typora / Obsidian 专用）
"""
import json
import subprocess
import os
import sys
import re
import zipfile
import shutil

# 支持命令行参数指定 Excel 文件，默认使用 设计文档测试.xlsx
if len(sys.argv) > 1:
    XLSX_FILE = os.path.abspath(sys.argv[1])
else:
    XLSX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "设计文档测试.xlsx")
BASE_NAME = os.path.splitext(os.path.basename(XLSX_FILE))[0]
OUT_DIR = os.path.dirname(XLSX_FILE)
OUTPUT_MD_PURE = os.path.join(OUT_DIR, f"{BASE_NAME}.md")
OUTPUT_MD_RICH = os.path.join(OUT_DIR, f"{BASE_NAME}_richtext.md")
IMAGES_DIR = os.path.join(OUT_DIR, "images")

# 颜色 → Emoji + 中文注释 映射（GitHub 等不支持 HTML 颜色时可见）
COLOR_ANNOTATION = {
    "#FF0000": ("🔴", "红色"),
    "#0000FF": ("🔵", "蓝色"),
    "#008000": ("🟢", "绿色"),
    "#006400": ("🟢", "深绿"),
    "#808080": ("⚪", "灰色"),
    "#0563C1": ("🔗", "链接蓝"),
    "#4472C4": ("🔵", "品牌蓝"),
    "#FFFFFF": ("", "白色"),
    "#000000": ("", "黑色"),
}

def officecli_json(args):
    """执行 officecli 命令并返回 JSON"""
    cmd = ["officecli"] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(XLSX_FILE))
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "raw": result.stdout}

def normalize_color(color_str):
    """统一为 #RRGGBB（OfficeCLI 返回 RRGGBBAA 8位，取前6位）"""
    if not color_str or color_str == "none":
        return None
    c = color_str.lstrip("#")
    if len(c) == 8:
        return "#" + c[:6]
    if len(c) == 6:
        return "#" + c
    return None

def color_annotation(color_hex):
    """返回 (emoji, 名称)，未知颜色返回自定义注释"""
    if not color_hex:
        return ("", "")
    key = color_hex.upper()
    if key in COLOR_ANNOTATION:
        return COLOR_ANNOTATION[key]
    return ("🎨", f"颜色{color_hex}")

def fill_annotation(fill_hex):
    """背景色注释"""
    if not fill_hex:
        return ("", "")
    key = fill_hex.upper()
    if key in ("#FFFF00",):
        return ("🟡", "黄高亮")
    if key in ("#FFF2CC",):
        return ("🟨", "浅黄高亮")
    if key in ("#D9E1F2",):
        return ("🟦", "蓝表头")
    return ("🎨", f"背景{fill_hex}")

def apply_inline_format(text, fmt):
    """对一段文本应用纯 Markdown 内联格式（加粗/删除线/斜体/链接，不含颜色 HTML）"""
    md = text
    bold = fmt.get("font.bold", False)
    italic = fmt.get("font.italic", False)
    strike = fmt.get("strike", False)
    underline = fmt.get("underline", "")
    link = fmt.get("link", "")

    # 1. 超链接最外层
    if link:
        md = f"[{md}]({link})"

    # 2. 加粗
    if bold:
        md = f"**{md}**"

    # 3. 删除线
    if strike:
        md = f"~~{md}~~"

    # 4. 斜体
    if italic:
        md = f"*{md}*"

    return md, underline

def cell_to_md_pure(text, fmt):
    """纯 Markdown 版 — 所有渲染器兼容，用 Emoji+注释代替颜色"""
    if not text or text.strip() == "":
        return ""

    color = normalize_color(fmt.get("font.color"))
    fill = normalize_color(fmt.get("fill"))
    font_size = fmt.get("font.size", "")

    # 标题映射
    if font_size:
        m = re.match(r"(\d+)", font_size)
        if m:
            sz = int(m.group(1))
            if sz >= 18:
                return f"# {text}"
            elif sz >= 14:
                bold = fmt.get("font.bold", False)
                return f"## {text}" if not bold else f"### {text}"

    md, underline = apply_inline_format(text, fmt)

    # 注释列表（颜色/下划线/背景色 → emoji 标记）
    notes = []

    # 下划线
    if underline and underline != "none":
        notes.append("⎽⎽下划线")

    # 文字颜色
    if color and color.upper() != "#000000":
        emoji, name = color_annotation(color)
        if emoji or name:
            notes.append(f"{emoji}{name}")

    # 背景色
    if fill and fill.upper() not in ("#FFFFFF",):
        emoji, name = fill_annotation(fill)
        if emoji or name:
            notes.append(f"{emoji}{name}")

    # 合并注释
    if notes:
        md = f"{md} `[{', '.join(notes)}]`"

    return md

def cell_to_md_rich(text, fmt):
    """富文本版 — HTML span 颜色，VS Code/Typora 支持"""
    if not text or text.strip() == "":
        return ""

    color = normalize_color(fmt.get("font.color"))
    fill = normalize_color(fmt.get("fill"))
    font_size = fmt.get("font.size", "")

    # 标题映射
    if font_size:
        m = re.match(r"(\d+)", font_size)
        if m:
            sz = int(m.group(1))
            if sz >= 18:
                return f"# {text}"
            elif sz >= 14:
                bold = fmt.get("font.bold", False)
                return f"## {text}" if not bold else f"### {text}"

    md, underline = apply_inline_format(text, fmt)

    # 下划线（HTML）
    if underline and underline != "none":
        md = f"<u>{md}</u>"

    # 文字颜色（HTML span）
    if color and color.upper() != "#000000":
        md = f'<span style="color:{color}">{md}</span>'

    # 背景色
    if fill and fill.upper() in ("#FFFF00", "#FFF2CC"):
        md = f"<mark>{md}</mark>"
    elif fill and fill.upper() not in ("#FFFFFF",):
        md = f'<span style="background-color:{fill}">{md}</span>'

    return md

def col_num_to_letter(n):
    """列数字 → Excel 列字母（1→A, 26→Z, 27→AA）"""
    result = ""
    while n > 0:
        n -= 1
        result = chr(65 + n % 26) + result
        n //= 26
    return result

def shape_position(fmt):
    """解析 shape 的 x/y/width/height，返回位置描述"""
    x = fmt.get("x")
    y = fmt.get("y")
    w = fmt.get("width")
    h = fmt.get("height")
    if x is None or y is None:
        return "", ""
    try:
        xi = int(float(x))
        yi = int(float(y))
        wi = int(float(w)) if w else 1
        hi = int(float(h)) if h else 1
        start_cell = f"{col_num_to_letter(xi)}{yi}"
        end_cell = f"{col_num_to_letter(xi + wi - 1)}{yi + hi - 1}"
        range_str = start_cell if wi == 1 and hi == 1 else f"{start_cell}~{end_cell}"
        anchor_ref = f"对应单元格：{col_num_to_letter(xi)}{yi}"
        return range_str, anchor_ref
    except (ValueError, TypeError):
        return "", ""

def shape_type_icon(fmt):
    """根据 shape 类型返回图标"""
    geo = (fmt.get("geometry") or "").lower()
    if "callout" in geo:
        return "📌"  # 吹出泡
    if "rect" in geo or "box" in geo:
        return "🔲"  # 矩形/红框
    if "line" in geo:
        return "➖"  # 线条
    return "💠"  # 其他形状

def extract_images(xlsx_path, out_dir):
    """从 xlsx（本质是 zip）提取所有内嵌图片到 out_dir，返回 {media路径: 相对路径} 映射"""
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    mapping = {}  # {xl/media/image1.png: images/image1.png}
    try:
        with zipfile.ZipFile(xlsx_path, 'r') as z:
            media_files = [f for f in z.namelist() if f.startswith('xl/media/')]
            for f in media_files:
                basename = os.path.basename(f)
                target = os.path.join(out_dir, basename)
                with z.open(f) as src_f, open(target, 'wb') as dst_f:
                    shutil.copyfileobj(src_f, dst_f)
                mapping[f] = f"images/{basename}"
        return mapping
    except Exception as e:
        print(f"⚠️ 图片提取失败: {e}")
        return {}

def picture_to_md(picture, img_index, img_mapping):
    """将 picture 元素转为 Markdown 图片引用"""
    fmt = picture.get("format", {})
    alt = fmt.get("alt", fmt.get("name", f"图片{img_index}"))
    x = fmt.get("x", "?")
    y = fmt.get("y", "?")
    # 图片文件名：按顺序对应 xl/media/imageN.xxx
    # img_mapping 的 key 是 xl/media/image1.png 等
    media_key = f"xl/media/image{img_index}.png"
    # 尝试匹配（可能还有 jpg/jpeg 等格式）
    if media_key not in img_mapping:
        for ext in ["png", "jpg", "jpeg", "gif", "bmp", "emf", "wmf"]:
            key = f"xl/media/image{img_index}.{ext}"
            if key in img_mapping:
                media_key = key
                break
    img_path = img_mapping.get(media_key, "")
    if img_path:
        pos_note = f"`[📍{col_num_to_letter(int(float(x)))}{y}]`" if x != "?" and y != "?" else ""
        return f"![{alt}]({img_path}) {pos_note}"
    else:
        return f"> 🖼️ {alt} `[📍位置 x={x}, y={y} — 图片未提取]`"

def shape_to_md_pure(text, fmt):
    """吹出形状 — 纯 Markdown 版（含位置信息）"""
    pos_range, anchor = shape_position(fmt)
    icon = shape_type_icon(fmt)
    color = normalize_color(fmt.get("color"))
    fill = normalize_color(fmt.get("fill"))
    bold = fmt.get("bold", False)

    # 位置注释
    notes = []
    if pos_range:
        notes.append(f"📍{pos_range}")
    if color and color.upper() != "#000000":
        emoji, name = color_annotation(color)
        if emoji: notes.append(f"{emoji}{name}")
    if fill and fill.upper() not in ("#FFFFFF",):
        emoji, name = fill_annotation(fill)
        if emoji: notes.append(f"{emoji}{name}")

    # 文本内容
    md_inner = text if text else "(无文字形状)"
    if bold:
        md_inner = f"**{md_inner}**"
    if notes:
        md_inner = f"{md_inner} `[{', '.join(notes)}]`"

    # 引用块前缀（按背景颜色区分严重程度）
    prefix = f"> {icon}"
    if fill and fill.upper() == "#FFFF00":
        prefix = f"> {icon} ⚠️"
    elif fill and fill.upper() == "#FF0000":
        prefix = f"> {icon} ❌"

    return f"{prefix} {md_inner}"

def shape_to_md_rich(text, fmt):
    """吹出形状 — 富文本版（含位置信息）"""
    pos_range, anchor = shape_position(fmt)
    icon = shape_type_icon(fmt)
    color = normalize_color(fmt.get("color"))
    fill = normalize_color(fmt.get("fill"))
    bold = fmt.get("bold", False)

    # 文本内容
    md = text if text else "(无文字形状)"
    if bold:
        md = f"**{md}**"
    if color and color.upper() != "#000000":
        md = f'<span style="color:{color}">{md}</span>'

    # 位置标签
    if pos_range:
        md = f'{md} <code style="color:#888">[📍{pos_range}]</code>'

    prefix = f"> {icon}"
    if fill and fill.upper() == "#FFFF00":
        prefix = f"> {icon} ⚠️"
    elif fill and fill.upper() == "#FF0000":
        prefix = f"> {icon} ❌"

    return f"{prefix} {md}"

def build_document(sheet_data, cell_fn, shape_fn, header_lines, img_mapping):
    """构建完整 Markdown 文档"""
    lines = list(header_lines)

    for sheet_name, data in sheet_data.items():
        lines.append(f"# {sheet_name}\n")

        cells_list = data["cells"]
        row_cells = {}
        for c in cells_list:
            parts = c["path"].split("/")
            cell_ref = parts[-1]
            m = re.match(r"([A-Z]+)(\d+)", cell_ref)
            if m:
                row_num = int(m.group(2))
                row_cells.setdefault(row_num, []).append(c)

        table_rows = {r: cells for r, cells in row_cells.items() if 16 <= r <= 20}
        normal_rows = {r: cells for r, cells in row_cells.items() if r < 15 or r > 20}

        for row_num in sorted(normal_rows.keys()):
            row_texts = []
            for c in sorted(normal_rows[row_num], key=lambda c: c["path"]):
                text = c.get("text", "")
                fmt = c.get("format", {})
                if fmt.get("empty"):
                    continue
                line = cell_fn(text, fmt)
                if line:
                    row_texts.append(line)
            if row_texts:
                lines.extend(row_texts)
                lines.append("")

        if table_rows:
            title_row = row_cells.get(15, [])
            if title_row:
                t = cell_fn(title_row[0].get("text", ""), title_row[0].get("format", {}))
                if t:
                    lines.append(t + "\n")
            else:
                lines.append("### 设计规格表\n")

            sorted_rows = sorted(table_rows.keys())
            headers = [c.get("text", "") for c in sorted(table_rows[sorted_rows[0]], key=lambda c: c["path"])]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["---"] * len(headers)) + "|")

            for row_num in sorted_rows[1:]:
                row_mds = []
                for c in sorted(table_rows[row_num], key=lambda c: c["path"]):
                    row_mds.append(cell_fn(c.get("text", ""), c.get("format", {})))
                lines.append("| " + " | ".join(row_mds) + " |")
            lines.append("")

        if data["shapes"]:
            lines.append("---\n")
            lines.append("## 悬浮吹出形状（Callout）\n")
            for shape in data["shapes"]:
                line = shape_fn(shape.get("text", ""), shape.get("format", {}))
                if line:
                    lines.append(line)
                    lines.append("")
            lines.append("")

        if data["pictures"]:
            lines.append("---\n")
            lines.append("## 图片（Picture）\n")
            for idx, pic in enumerate(data["pictures"], 1):
                line = picture_to_md(pic, idx, img_mapping)
                if line:
                    lines.append(line)
                    lines.append("")
            lines.append("")

    return lines

def main():
    print(f"读取 Excel: {XLSX_FILE}")

    # 查询所有单元格
    cells_resp = officecli_json(["query", XLSX_FILE, "cell"])
    if not cells_resp.get("success"):
        print(f"❌ 查询 cell 失败")
        sys.exit(1)
    cells = cells_resp["data"]["results"]
    print(f"找到 {len(cells)} 个单元格")

    # 查询所有 shape
    shapes_resp = officecli_json(["query", XLSX_FILE, "shape"])
    shapes = shapes_resp["data"]["results"] if shapes_resp.get("success") else []
    print(f"找到 {len(shapes)} 个吹出形状")

    # 查询所有 picture
    pictures_resp = officecli_json(["query", XLSX_FILE, "picture"])
    pictures = pictures_resp["data"]["results"] if pictures_resp.get("success") else []
    print(f"找到 {len(pictures)} 张图片")

    # 提取图片到 images/ 目录
    img_mapping = {}
    if pictures:
        img_mapping = extract_images(XLSX_FILE, IMAGES_DIR)
        print(f"提取 {len(img_mapping)} 张图片到 {IMAGES_DIR}")

    # 分组
    sheet_data = {}
    for cell in cells:
        parts = cell["path"].split("/")
        sn = parts[1]
        sheet_data.setdefault(sn, {"cells": [], "shapes": [], "pictures": []})["cells"].append(cell)
    for shape in shapes:
        parts = shape["path"].split("/")
        sn = parts[1]
        sheet_data.setdefault(sn, {"cells": [], "shapes": [], "pictures": []})["shapes"].append(shape)
    for pic in pictures:
        parts = pic["path"].split("/")
        sn = parts[1]
        sheet_data.setdefault(sn, {"cells": [], "shapes": [], "pictures": []})["pictures"].append(pic)

    # ========== 版 1：纯净 Markdown（所有渲染器兼容）==========
    pure_header = [
        "<!-- 由 OfficeCLI 从 Excel 自动转换生成 — 纯净版（兼容 GitHub/所有 Markdown 渲染器） -->",
        "<!-- 格式标记说明：`[🔴红色]` 表示文字颜色；`[🟡黄高亮]` 表示背景色；`[⎽⎽下划线]` 表示下划线 -->\n",
    ]
    pure_lines = build_document(sheet_data, cell_to_md_pure, shape_to_md_pure, pure_header, img_mapping)
    with open(OUTPUT_MD_PURE, "w", encoding="utf-8") as f:
        f.write("\n".join(pure_lines))
    print(f"✅ 纯净 Markdown: {OUTPUT_MD_PURE}  ({len(pure_lines)} 行)")

    # ========== 版 2：富文本 HTML（VS Code / Typora / Obsidian）==========
    rich_header = [
        "<!-- 由 OfficeCLI 从 Excel 自动转换生成 — 富文本版（VS Code / Typora / Obsidian 打开查看颜色） -->\n",
    ]
    rich_lines = build_document(sheet_data, cell_to_md_rich, shape_to_md_rich, rich_header, img_mapping)
    with open(OUTPUT_MD_RICH, "w", encoding="utf-8") as f:
        f.write("\n".join(rich_lines))
    print(f"✅ 富文本 Markdown: {OUTPUT_MD_RICH}  ({len(rich_lines)} 行)")

if __name__ == "__main__":
    main()
