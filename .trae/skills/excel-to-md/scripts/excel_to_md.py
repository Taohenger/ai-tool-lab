#!/usr/bin/env python3
"""Excel to Markdown converter.

Native support: .xlsx, .xlsm, .xltx, .xltm.
Legacy .xls files are converted through LibreOffice when it is installed.
The source workbook is never modified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

try:
    import openpyxl
    from openpyxl.cell.rich_text import CellRichText, TextBlock
    from openpyxl.styles.colors import COLOR_INDEX
    from openpyxl.utils import get_column_letter, range_boundaries
    from openpyxl.utils.exceptions import InvalidFileException
except ImportError:
    print("缺少依赖，请先运行本 Skill 的 install.sh 或 install.ps1。", file=sys.stderr)
    raise SystemExit(2)

VERSION = "1.1.0"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
EMU_PER_PX = 9525
EMU_PER_PT = 12700


class ConversionError(RuntimeError):
    pass


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_name(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value).strip(" .")
    return value[:80] or "item"


def part_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def rels_path(part: str) -> str:
    return f"{posixpath.dirname(part)}/_rels/{posixpath.basename(part)}.rels"


def read_rels(archive: zipfile.ZipFile, part: str) -> dict[str, dict[str, str]]:
    path = rels_path(part)
    if path not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(path))
    return {
        rel.attrib["Id"]: dict(rel.attrib)
        for rel in root
        if rel.attrib.get("Id")
    }


def escape_text(value: Any, in_table: bool = False) -> str:
    text = html.escape(str(value), quote=False)
    text = text.replace("\\", "\\\\")
    text = re.sub(r"([`*_\[\]~])", r"\\\1", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    if in_table:
        text = text.replace("|", "\\|")
    return text


def escape_url(value: str) -> str:
    return html.escape(value, quote=True).replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def code_text(value: str) -> str:
    return f"<code>{html.escape(value, quote=False)}</code>"


def apply_tint(rgb: str, tint: float | None) -> str:
    if not tint:
        return rgb
    channels = [int(rgb[i:i + 2], 16) for i in (1, 3, 5)]
    result = []
    for channel in channels:
        value = channel * (1 + tint) if tint < 0 else channel * (1 - tint) + 255 * tint
        result.append(max(0, min(255, round(value))))
    return "#" + "".join(f"{value:02X}" for value in result)


def theme_colors(workbook: Any) -> list[str]:
    if not workbook.loaded_theme:
        return []
    try:
        root = ET.fromstring(workbook.loaded_theme)
        scheme = next(el for el in root.iter() if local_name(el.tag) == "clrScheme")
        colors: dict[str, str] = {}
        for entry in scheme:
            if not len(entry):
                continue
            color = entry[0]
            value = color.attrib.get("lastClr") or color.attrib.get("val")
            if value and re.fullmatch(r"[0-9A-Fa-f]{6}", value):
                colors[local_name(entry.tag)] = "#" + value.upper()
        order = ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3",
                 "accent4", "accent5", "accent6", "hlink", "folHlink"]
        return [colors.get(name, "#000000") for name in order]
    except (ET.ParseError, StopIteration):
        return []


def openpyxl_color(color: Any, themes: list[str]) -> str | None:
    if color is None:
        return None
    try:
        kind = color.type
        if kind == "rgb" and color.rgb:
            value = str(color.rgb)
            if len(value) == 8:
                value = value[-6:]
            if re.fullmatch(r"[0-9A-Fa-f]{6}", value):
                return "#" + value.upper()
        if kind == "indexed" and color.indexed is not None:
            index = int(color.indexed)
            if 0 <= index < len(COLOR_INDEX):
                return "#" + COLOR_INDEX[index][-6:].upper()
        if kind == "theme" and color.theme is not None:
            index = int(color.theme)
            if 0 <= index < len(themes):
                return apply_tint(themes[index], color.tint)
    except (TypeError, ValueError, IndexError):
        return None
    return None


def xml_color(element: ET.Element | None, themes: list[str]) -> str | None:
    if element is None:
        return None
    containers = [el for el in element.iter() if local_name(el.tag) in
                  {"srgbClr", "schemeClr", "sysClr", "prstClr"}]
    if not containers:
        return None
    color = containers[0]
    kind = local_name(color.tag)
    value = color.attrib.get("val") or color.attrib.get("lastClr")
    rgb = None
    if kind in {"srgbClr", "sysClr"} and value and re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        rgb = "#" + value.upper()
    elif kind == "schemeClr" and value:
        order = ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3",
                 "accent4", "accent5", "accent6", "hlink", "folHlink"]
        aliases = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2",
                   "phClr": "accent1"}
        name = aliases.get(value, value)
        if name in order:
            index = order.index(name)
            if index < len(themes):
                rgb = themes[index]
    if rgb is None:
        return None
    lum_mod = next((el for el in color if local_name(el.tag) == "lumMod"), None)
    lum_off = next((el for el in color if local_name(el.tag) == "lumOff"), None)
    if lum_mod is not None:
        try:
            factor = int(lum_mod.attrib.get("val", "100000")) / 100000
            offset = int(lum_off.attrib.get("val", "0")) / 100000 if lum_off is not None else 0
            return apply_tint(rgb, factor + offset - 1)
        except ValueError:
            pass
    return rgb


def decimal_places(number_format: str) -> tuple[int, bool]:
    match = re.search(r"[0#]\.(0+|#+)", number_format)
    if not match:
        return 0, "," in number_format
    digits = match.group(1)
    return len(digits), "," in number_format


def display_number(value: int | float, number_format: str) -> str:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return str(value)
    fmt = (number_format or "General").split(";")[0]
    try:
        if "%" in fmt:
            places, grouping = decimal_places(fmt)
            rendered = f"{value * 100:,.{places}f}" if grouping else f"{value * 100:.{places}f}"
            return rendered + "%"
        if "E+" in fmt.upper() or "E-" in fmt.upper():
            places, _ = decimal_places(fmt)
            return f"{value:.{places}E}"
        if re.search(r"[0#]\.(0+|#+)", fmt) or ("0" in fmt and any(c in fmt for c in ",$¥€£")):
            places, grouping = decimal_places(fmt)
            rendered = f"{value:,.{places}f}" if grouping else f"{value:.{places}f}"
            prefix = ""
            if any(symbol in fmt for symbol in "$¥€£"):
                prefix = next(symbol for symbol in "$¥€£" if symbol in fmt)
            return prefix + rendered
    except (ValueError, TypeError):
        pass
    return repr(value) if isinstance(value, float) else str(value)


def display_value(value: Any, number_format: str = "General") -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, dt.datetime):
        if value.microsecond:
            return value.isoformat(sep=" ", timespec="microseconds")
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, (dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, dt.timedelta):
        return str(value)
    if isinstance(value, (int, float)):
        return display_number(value, number_format)
    return str(value)


def has_value(cell: Any) -> bool:
    return cell.value is not None and str(cell.value) != ""


@dataclass
class TableBlock:
    row: int
    rows: list[int]
    min_col: int
    max_col: int
    headers: list[str] | None = None
    title_row: int | None = None
    actual_name: str | None = None


@dataclass
class SheetObject:
    row: int
    col: int
    kind: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Block:
    row: int
    priority: int
    content: str


class ExcelConverter:
    def __init__(self, source: Path, output_dir: Path, flavors: list[str], auto_tables: bool = True,
                 values_source: Path | None = None, diagram_render: str = "auto"):
        self.original_source = source
        self.source = source
        self.values_source = values_source
        self.output_dir = output_dir
        self.flavors = flavors
        self.auto_tables = auto_tables
        self.diagram_render = diagram_render
        self.assets_dir = output_dir / "assets"
        self.archive: zipfile.ZipFile | None = None
        self.wb: Any = None
        self.values_wb: Any = None
        self.themes: list[str] = []
        self.media_assets: dict[str, str] = {}
        self.used_media: set[str] = set()
        self.report: dict[str, Any] = {
            "source": str(source.resolve()),
            "converter_version": VERSION,
            "sheets": [],
            "warnings": [],
            "unreferenced_media": [],
            "embedded_files": [],
        }

    def warn(self, message: str) -> None:
        self.report["warnings"].append(message)

    def copy_asset(self, part: str, prefix: str) -> str:
        assert self.archive is not None
        if part in self.media_assets:
            return self.media_assets[part]
        suffix = Path(part).suffix or ".bin"
        name = f"{safe_name(prefix)}-{safe_name(Path(part).stem)}{suffix}"
        target = self.assets_dir / name
        counter = 2
        while target.exists():
            target = self.assets_dir / f"{safe_name(prefix)}-{safe_name(Path(part).stem)}-{counter}{suffix}"
            counter += 1
        target.parent.mkdir(parents=True, exist_ok=True)
        with self.archive.open(part) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        relative = target.relative_to(self.output_dir).as_posix()
        self.media_assets[part] = relative
        return relative

    def column_emu(self, ws: Any, zero_col: int) -> int:
        letter = get_column_letter(zero_col + 1)
        dimension = ws.column_dimensions.get(letter)
        if dimension is not None and dimension.hidden:
            return 0
        width = dimension.width if dimension is not None and dimension.width else (
            ws.sheet_format.defaultColWidth or 8.43)
        return max(1, int((width * 7 + 5) * EMU_PER_PX))

    def row_emu(self, ws: Any, zero_row: int) -> int:
        dimension = ws.row_dimensions.get(zero_row + 1)
        if dimension is not None and dimension.hidden:
            return 0
        height = dimension.height if dimension is not None and dimension.height else (
            ws.sheet_format.defaultRowHeight or 15)
        return max(1, int(height * EMU_PER_PT))

    def marker(self, element: ET.Element | None) -> dict[str, int] | None:
        if element is None:
            return None
        result = {}
        for name in ("col", "colOff", "row", "rowOff"):
            child = next((el for el in element if local_name(el.tag) == name), None)
            result[name] = int(child.text or 0) if child is not None else 0
        return result

    def position(self, ws: Any, anchor: ET.Element) -> tuple[int, int, str]:
        start = self.marker(next((el for el in anchor if local_name(el.tag) == "from"), None))
        if start is None:
            return 0, 0, "绝对位置"
        end = self.marker(next((el for el in anchor if local_name(el.tag) == "to"), None))
        if end is None:
            ext = next((el for el in anchor if local_name(el.tag) == "ext"), None)
            end = dict(start)
            if ext is not None:
                remaining_x = int(ext.attrib.get("cx", "0"))
                remaining_y = int(ext.attrib.get("cy", "0"))
                col = start["col"]
                row = start["row"]
                while remaining_x > 0 and col < 16384:
                    available = self.column_emu(ws, col) - (start["colOff"] if col == start["col"] else 0)
                    if remaining_x <= max(1, available):
                        break
                    remaining_x -= max(0, available)
                    col += 1
                while remaining_y > 0 and row < 1048576:
                    available = self.row_emu(ws, row) - (start["rowOff"] if row == start["row"] else 0)
                    if remaining_y <= max(1, available):
                        break
                    remaining_y -= max(0, available)
                    row += 1
                end.update({"col": col, "row": row})
        start_ref = f"{get_column_letter(start['col'] + 1)}{start['row'] + 1}"
        end_ref = f"{get_column_letter(end['col'] + 1)}{end['row'] + 1}"
        position = start_ref if start_ref == end_ref else f"{start_ref}~{end_ref}"
        ext = next((el for el in anchor if local_name(el.tag) == "ext"), None)
        if ext is not None:
            width_cm = int(ext.attrib.get("cx", "0")) / 360000
            height_cm = int(ext.attrib.get("cy", "0")) / 360000
            position += f"，{width_cm:.2f}×{height_cm:.2f}cm"
        return start["row"] + 1, start["col"] + 1, position

    def parse_shape(self, ws: Any, anchor: ET.Element, shape: ET.Element, kind: str) -> SheetObject:
        row, col, position = self.position(ws, anchor)
        geometry_node = next((el for el in shape.iter() if local_name(el.tag) == "prstGeom"), None)
        geometry = geometry_node.attrib.get("prst", "") if geometry_node is not None else ""
        text_body = next((el for el in shape if local_name(el.tag) == "txBody"), None)
        paragraphs = []
        if text_body is not None:
            for paragraph in (el for el in text_body if local_name(el.tag) == "p"):
                text = "".join(el.text or "" for el in paragraph.iter() if local_name(el.tag) == "t")
                if text:
                    paragraphs.append(text)
        text = "\n".join(paragraphs)
        c_nv_pr = next((el for el in shape.iter() if local_name(el.tag) == "cNvPr"), None)
        name = c_nv_pr.attrib.get("name", "形状") if c_nv_pr is not None else "形状"
        sp_pr = next((el for el in shape if local_name(el.tag) == "spPr"), None)
        sp_children = list(sp_pr) if sp_pr is not None else []
        fill = xml_color(next((el for el in sp_children if local_name(el.tag) == "solidFill"), None), self.themes)
        line_node = next((el for el in sp_children if local_name(el.tag) == "ln"), None)
        line = xml_color(line_node, self.themes)
        run_props = next((el for el in shape.iter() if local_name(el.tag) in {"rPr", "defRPr"}), None)
        bold = run_props is not None and run_props.attrib.get("b") in {"1", "true"}
        font_color = xml_color(run_props, self.themes)
        return SheetObject(row, col, "shape", {
            "name": name, "geometry": geometry, "text": text, "position": position,
            "fill": fill, "line": line, "font_color": font_color, "bold": bold,
            "connector": kind == "connector",
        })

    def parse_chart(self, part: str, ws: Any, anchor: ET.Element) -> SheetObject:
        assert self.archive is not None
        row, col, position = self.position(ws, anchor)
        data: dict[str, Any] = {"position": position, "title": "未命名图表", "types": [], "ranges": []}
        try:
            root = ET.fromstring(self.archive.read(part))
            title_node = next((el for el in root.iter() if local_name(el.tag) == "title"), None)
            if title_node is not None:
                title = "".join(el.text or "" for el in title_node.iter() if local_name(el.tag) == "t")
                if title:
                    data["title"] = title
            plot_area = next((el for el in root.iter() if local_name(el.tag) == "plotArea"), None)
            if plot_area is not None:
                data["types"] = sorted({local_name(el.tag) for el in plot_area if local_name(el.tag).endswith("Chart")})
            data["ranges"] = sorted({el.text for el in root.iter() if local_name(el.tag) == "f" and el.text})
        except (ET.ParseError, KeyError):
            self.warn(f"图表 XML 无法解析：{part}")
        self.warn(f"{ws.title} 的图表“{data['title']}”已保留标题和数据区域，但 Markdown 无法重绘图表视觉。")
        return SheetObject(row, col, "chart", data)

    def drawing_objects(self, ws: Any, sheet_part: str, sheet_index: int) -> list[SheetObject]:
        assert self.archive is not None
        if sheet_part not in self.archive.namelist():
            return []
        root = ET.fromstring(self.archive.read(sheet_part))
        drawing = next((el for el in root if local_name(el.tag) == "drawing"), None)
        if drawing is None:
            return []
        rel_id = drawing.attrib.get(f"{{{DOC_REL}}}id")
        sheet_rels = read_rels(self.archive, sheet_part)
        if rel_id not in sheet_rels:
            return []
        drawing_part = part_target(sheet_part, sheet_rels[rel_id]["Target"])
        drawing_rels = read_rels(self.archive, drawing_part)
        drawing_root = ET.fromstring(self.archive.read(drawing_part))
        objects: list[SheetObject] = []
        image_index = 0
        for anchor in drawing_root:
            if local_name(anchor.tag) not in {"oneCellAnchor", "twoCellAnchor", "absoluteAnchor"}:
                continue
            for element in anchor:
                kind = local_name(element.tag)
                if kind == "pic":
                    row, col, position = self.position(ws, anchor)
                    c_nv_pr = next((el for el in element.iter() if local_name(el.tag) == "cNvPr"), None)
                    name = c_nv_pr.attrib.get("name", "图片") if c_nv_pr is not None else "图片"
                    alt = c_nv_pr.attrib.get("descr", name) if c_nv_pr is not None else name
                    blip = next((el for el in element.iter() if local_name(el.tag) == "blip"), None)
                    rel_id = blip.attrib.get(f"{{{DOC_REL}}}embed") if blip is not None else None
                    if rel_id and rel_id in drawing_rels:
                        rel = drawing_rels[rel_id]
                        if rel.get("TargetMode") == "External":
                            path = rel["Target"]
                        else:
                            media_part = part_target(drawing_part, rel["Target"])
                            image_index += 1
                            path = self.copy_asset(media_part, f"sheet{sheet_index:02d}-image{image_index:02d}")
                            self.used_media.add(media_part)
                        objects.append(SheetObject(row, col, "image", {
                            "alt": alt, "path": path, "position": position,
                        }))
                elif kind in {"sp", "cxnSp"}:
                    objects.append(self.parse_shape(ws, anchor, element, "connector" if kind == "cxnSp" else "shape"))
                elif kind == "grpSp":
                    for shape in element.iter():
                        if local_name(shape.tag) in {"sp", "cxnSp"}:
                            objects.append(self.parse_shape(ws, anchor, shape, "connector" if local_name(shape.tag) == "cxnSp" else "shape"))
                elif kind == "graphicFrame":
                    chart = next((el for el in element.iter() if local_name(el.tag) == "chart"), None)
                    if chart is not None:
                        rel_id = chart.attrib.get(f"{{{DOC_REL}}}id")
                        if rel_id in drawing_rels:
                            chart_part = part_target(drawing_part, drawing_rels[rel_id]["Target"])
                            objects.append(self.parse_chart(chart_part, ws, anchor))
                    else:
                        self.warn(f"{ws.title} 存在无法转换的 graphicFrame 对象。")
        return objects

    def sheet_parts(self) -> dict[str, str]:
        assert self.archive is not None
        workbook_part = "xl/workbook.xml"
        root = ET.fromstring(self.archive.read(workbook_part))
        rels = read_rels(self.archive, workbook_part)
        result = {}
        for sheet in (el for el in root.iter() if local_name(el.tag) == "sheet"):
            rel_id = sheet.attrib.get(f"{{{DOC_REL}}}id")
            if sheet.attrib.get("name") and rel_id in rels:
                result[sheet.attrib["name"]] = part_target(workbook_part, rels[rel_id]["Target"])
        return result

    def actual_tables(self, ws: Any) -> list[TableBlock]:
        blocks = []
        for table in ws.tables.values():
            min_col, min_row, max_col, max_row = range_boundaries(table.ref)
            headers = None
            header_row = min_row
            rows = list(range(min_row, max_row + 1))
            if getattr(table, "headerRowCount", 1) == 0:
                headers = [column.name for column in table.tableColumns]
                header_row = min_row - 1
            blocks.append(TableBlock(header_row, rows, min_col, max_col, headers=headers,
                                     actual_name=table.displayName or table.name))
        return blocks

    def detect_tables(self, ws: Any, occupied: set[tuple[int, int]]) -> list[TableBlock]:
        row_info: dict[int, dict[str, Any]] = {}
        for row in ws.iter_rows():
            columns = [cell.column for cell in row if (cell.row, cell.column) not in occupied and has_value(cell)]
            if columns:
                row_info[row[0].row] = {"min": min(columns), "max": max(columns),
                                        "count": max(columns) - min(columns) + 1}
        rows = sorted(row_info)
        result: list[TableBlock] = []
        i = 0
        while i < len(rows):
            current = rows[i]
            info = row_info[current]
            if info["count"] < 2:
                i += 1
                continue
            j = i + 1
            gap = 0
            base_min, base_max = info["min"], info["max"]
            while j < len(rows):
                next_row = rows[j]
                if next_row - rows[j - 1] > 3:
                    break
                next_info = row_info[next_row]
                if next_info["count"] >= 2:
                    overlap = not (next_info["max"] < base_min or next_info["min"] > base_max)
                    difference = abs(next_info["count"] - row_info[rows[j - 1]]["count"])
                    if difference > 2 or not (overlap or difference <= 2):
                        break
                    gap = 0
                else:
                    gap += 1
                    if gap > 1:
                        break
                j += 1
            table_rows = [row for row in rows[i:j] if row_info[row]["count"] >= 2]
            if len(table_rows) >= 2:
                min_col = min(row_info[row]["min"] for row in table_rows)
                max_col = max(row_info[row]["max"] for row in table_rows)
                title_row = None
                for candidate in (table_rows[0] - 1, table_rows[0] - 2):
                    if candidate < 1:
                        continue
                    available = [cell for cell in ws[candidate] if has_value(cell) and
                                 (cell.row, cell.column) not in occupied]
                    if len(available) == 1:
                        title_row = candidate
                        break
                result.append(TableBlock(table_rows[0], table_rows, min_col, max_col, title_row=title_row))
                i = j
            else:
                i += 1
        return result

    def inline_font(self, font: Any, text: str, flavor: str) -> tuple[str, list[str]]:
        notes = []
        if font is None:
            return text, notes
        if font.b:
            text = f"**{text}**"
        if font.strike:
            text = f"~~{text}~~"
        if font.i:
            text = f"*{text}*"
        if font.u and font.u != "none":
            if flavor == "rich":
                text = f"<u>{text}</u>"
            else:
                notes.append("下划线")
        if font.vertAlign == "superscript":
            text = f"<sup>{text}</sup>"
        elif font.vertAlign == "subscript":
            text = f"<sub>{text}</sub>"
        color = openpyxl_color(font.color, self.themes)
        if color and color != "#000000":
            if flavor == "rich":
                text = f'<span style="color:{color}">{text}</span>'
            else:
                notes.append(f"文字色 {color}")
        return text, notes

    def render_rich_text(self, value: CellRichText, flavor: str, in_table: bool) -> str:
        rendered = []
        for part in value:
            if isinstance(part, TextBlock):
                text = escape_text(part.text, in_table)
                text, _ = self.inline_font(part.font, text, flavor)
                rendered.append(text)
            else:
                rendered.append(escape_text(str(part), in_table))
        return "".join(rendered)

    def render_cell(self, cell: Any, value_cell: Any, flavor: str, in_table: bool) -> str:
        is_formula = cell.data_type == "f"
        formula = str(cell.value) if is_formula else ""
        if is_formula:
            raw_value = value_cell.value
            if raw_value is None:
                raw_text = "（无缓存结果）"
            else:
                raw_text = display_value(raw_value, cell.number_format)
            text = escape_text(raw_text, in_table)
        elif isinstance(cell.value, CellRichText):
            text = self.render_rich_text(cell.value, flavor, in_table)
        else:
            text = escape_text(display_value(cell.value, cell.number_format), in_table)

        notes: list[str] = []
        if not isinstance(cell.value, CellRichText) or is_formula:
            text, notes = self.inline_font(cell.font, text, flavor)
        fill = openpyxl_color(cell.fill.fgColor, self.themes) if cell.fill and cell.fill.fill_type else None
        if fill and fill != "#FFFFFF":
            if flavor == "rich":
                if fill in {"#FFFF00", "#FFF2CC"}:
                    text = f"<mark>{text}</mark>"
                else:
                    text = f'<span style="background-color:{fill}">{text}</span>'
            else:
                notes.append(f"背景 {fill}")
        if cell.hyperlink:
            target = cell.hyperlink.target or cell.hyperlink.location or ""
            if target:
                if cell.hyperlink.target:
                    text = f"[{text}]({escape_url(target)})"
                else:
                    notes.append(f"内部链接 {target}")
        if cell.comment:
            notes.append("有批注")
        if is_formula:
            formula_html = code_text(formula)
            text = f"{text}<br>{formula_html}" if in_table else f"{text}（公式：{formula_html}）"
        if notes:
            text += " " + " ".join(f"`[{escape_text(note)}]`" for note in notes)
        return text or ("（无缓存结果）" if is_formula else "")

    def render_table(self, ws: Any, values_ws: Any, table: TableBlock, flavor: str) -> str:
        lines = []
        if table.title_row:
            title_cells = [cell for cell in ws[table.title_row] if has_value(cell)]
            if title_cells:
                cell = title_cells[0]
                lines.extend([self.render_cell(cell, values_ws[cell.coordinate], flavor, False), ""])
        if table.actual_name:
            lines.extend([f"Excel 表：`{escape_text(table.actual_name)}`", ""])
        if table.headers is not None:
            headers = [escape_text(value, True) for value in table.headers]
            data_rows = table.rows
        else:
            header_row = table.rows[0]
            headers = [self.render_cell(ws.cell(header_row, col), values_ws.cell(header_row, col), flavor, True)
                       for col in range(table.min_col, table.max_col + 1)]
            headers = [value or f"列{index + 1}" for index, value in enumerate(headers)]
            data_rows = table.rows[1:]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in data_rows:
            values = [self.render_cell(ws.cell(row, col), values_ws.cell(row, col), flavor, True)
                      for col in range(table.min_col, table.max_col + 1)]
            lines.append("| " + " | ".join(values) + " |")
        return "\n".join(lines)

    def render_object(self, obj: SheetObject, flavor: str) -> str:
        data = obj.data
        if obj.kind == "image":
            return f"![{escape_text(data['alt'])}]({escape_url(data['path'])})\n\n位置：{data['position']}"
        if obj.kind == "chart":
            types = "、".join(data["types"]) or "未知类型"
            ranges = "；".join(data["ranges"]) or "未记录"
            return (f"> 图表：{escape_text(data['title'])}（{escape_text(types)}）  \n"
                    f"> 位置：{data['position']}  \n> 数据区域：{code_text(ranges)}  \n"
                    "> 注：图表视觉无法直接转为 Markdown，源数据仍保留在工作表单元格中。")
        geometry = data["geometry"]
        if data["connector"]:
            label = "连接线/箭头"
        elif "callout" in geometry.lower():
            label = "吹出泡（标注）"
        elif "rect" in geometry.lower():
            label = "矩形/红框"
        else:
            label = f"形状 {geometry}".strip()
        text = escape_text(data["text"] or "（无文字）")
        if data["bold"]:
            text = f"**{text}**"
        if flavor == "rich" and data["font_color"]:
            text = f'<span style="color:{data["font_color"]}">{text}</span>'
        annotations = [f"位置：{data['position']}"]
        if data["fill"]:
            annotations.append(f"背景：{data['fill']}")
        if data["line"]:
            annotations.append(f"边框：{data['line']}")
        return f"> {label}：{text}  \n> {'；'.join(annotations)}"

    def comments_section(self, ws: Any) -> str:
        comments = [(cell.coordinate, cell.comment) for row in ws.iter_rows() for cell in row if cell.comment]
        if not comments:
            return ""
        lines = ["### 批注", ""]
        for coordinate, comment in comments:
            author = f"（{comment.author}）" if comment.author else ""
            lines.append(f"- **{coordinate}**{author}：{escape_text(comment.text)}")
        return "\n".join(lines)

    def convert_sheet(self, ws: Any, values_ws: Any, objects: list[SheetObject],
                      flavor: str) -> tuple[str, dict[str, Any]]:
        actual = self.actual_tables(ws)
        occupied: set[tuple[int, int]] = set()
        for table in actual:
            for row in table.rows:
                for col in range(table.min_col, table.max_col + 1):
                    occupied.add((row, col))
        automatic = self.detect_tables(ws, occupied) if self.auto_tables else []
        for table in automatic:
            for row in table.rows:
                for col in range(table.min_col, table.max_col + 1):
                    if has_value(ws.cell(row, col)):
                        occupied.add((row, col))
            if table.title_row:
                for cell in ws[table.title_row]:
                    if has_value(cell):
                        occupied.add((cell.row, cell.column))

        blocks: list[Block] = []
        for table in actual + automatic:
            blocks.append(Block(max(0, table.row), 1, self.render_table(ws, values_ws, table, flavor)))
        text_rows = sorted({cell.row for row in ws.iter_rows() for cell in row if has_value(cell) and
                            (cell.row, cell.column) not in occupied})
        for row in text_rows:
            cells = [cell for cell in ws[row] if has_value(cell) and (cell.row, cell.column) not in occupied]
            if not cells:
                continue
            if len(cells) == 1:
                cell = cells[0]
                content = self.render_cell(cell, values_ws[cell.coordinate], flavor, False)
                size = cell.font.sz or 0
                if isinstance(size, (int, float)) and not cell.data_type == "f":
                    if size >= 18:
                        content = "# " + content
                    elif size >= 14:
                        content = "## " + content
                blocks.append(Block(row, 1, content))
            else:
                content = "\n".join(f"- **{cell.coordinate}**：" +
                                    self.render_cell(cell, values_ws[cell.coordinate], flavor, False)
                                    for cell in cells)
                blocks.append(Block(row, 1, content))
        for obj in objects:
            blocks.append(Block(obj.row, 2, self.render_object(obj, flavor)))

        state = {"visible": "可见", "hidden": "隐藏", "veryHidden": "深度隐藏"}.get(ws.sheet_state, ws.sheet_state)
        sheet_index = self.wb.worksheets.index(ws) + 1
        lines = [f"# 工作表：{escape_text(ws.title)}", "",
                 f"> 原序号：{sheet_index}；状态：{state}；范围：{ws.calculate_dimension()}；"
                 f"合并单元格：{len(ws.merged_cells.ranges)} 个", ""]
        for block in sorted(blocks, key=lambda item: (item.row, item.priority)):
            if block.content:
                lines.extend([block.content, ""])
        if not blocks:
            lines.extend(["_（空白工作表）_", ""])
        comments = self.comments_section(ws)
        if comments:
            lines.extend([comments, ""])

        nonempty = sum(1 for row in ws.iter_rows() for cell in row if has_value(cell))
        formulas = sum(1 for row in ws.iter_rows() for cell in row if cell.data_type == "f")
        missing_formula_results = sum(
            1 for row in ws.iter_rows() for cell in row
            if cell.data_type == "f" and values_ws[cell.coordinate].value is None
        )
        comments_count = sum(1 for row in ws.iter_rows() for cell in row if cell.comment)
        stats = {
            "title": ws.title, "state": ws.sheet_state, "range": ws.calculate_dimension(),
            "nonempty_cells": nonempty, "formula_cells": formulas,
            "formula_cells_without_cached_result": missing_formula_results,
            "merged_ranges": [str(item) for item in ws.merged_cells.ranges],
            "hidden_rows": [index for index, dim in ws.row_dimensions.items() if dim.hidden],
            "hidden_columns": [key for key, dim in ws.column_dimensions.items() if dim.hidden],
            "actual_tables": len(actual), "auto_tables": len(automatic),
            "comments": comments_count,
            "images": sum(obj.kind == "image" for obj in objects),
            "shapes": sum(obj.kind == "shape" for obj in objects),
            "charts": sum(obj.kind == "chart" for obj in objects),
        }
        return "\n".join(lines).rstrip(), stats

    def extract_attachments(self) -> str:
        assert self.archive is not None
        lines = []
        for part in self.archive.namelist():
            if part.startswith("xl/media/"):
                continue
            if part.startswith("xl/embeddings/") or part == "xl/vbaProject.bin":
                path = self.copy_asset(part, "attachment")
                self.report["embedded_files"].append({"part": part, "path": path})
                lines.append(f"- [{Path(part).name}]({escape_url(path)})")
        if not lines:
            return ""
        return "# 嵌入附件与宏\n\n" + "\n".join(lines)

    def unreferenced_media_section(self) -> str:
        assert self.archive is not None
        lines = []
        for part in self.archive.namelist():
            if part.startswith("xl/media/") and not part.endswith("/") and part not in self.used_media:
                path = self.copy_asset(part, "unreferenced")
                self.report["unreferenced_media"].append({"part": part, "path": path})
                lines.append(f"![{Path(part).name}]({escape_url(path)})")
        if not lines:
            return ""
        self.warn("存在未能通过工作表 drawing 定位的图片，已统一放入“未定位的嵌入媒体”章节。")
        return "# 未定位的嵌入媒体\n\n" + "\n\n".join(lines)

    def convert(self) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive = zipfile.ZipFile(self.source)
        self.wb = openpyxl.load_workbook(self.source, data_only=False, rich_text=True)
        self.values_wb = openpyxl.load_workbook(self.values_source or self.source, data_only=True)
        if self.values_source:
            self.report["cached_values_source"] = str(self.values_source.resolve())
            self.warn("公式结果来自单独的重算副本；原始工作簿的结构、格式和公式表达式保持不变。")
        self.themes = theme_colors(self.wb)
        parts = self.sheet_parts()
        objects_by_sheet = {
            ws.title: self.drawing_objects(ws, parts.get(ws.title, ""), index)
            for index, ws in enumerate(self.wb.worksheets, 1)
        }
        from flowcharts import enrich_drawings, drawing_markdown
        drawings = enrich_drawings(self, parts, self.diagram_render)
        self.report["drawings"] = drawings
        outputs = {}
        attachments = self.extract_attachments()
        unreferenced = self.unreferenced_media_section()
        for flavor in self.flavors:
            lines = [f"# {escape_text(self.original_source.stem)}", "",
                     "<!-- 由 excel-to-md Skill 生成；源 Excel 未被修改。 -->", "",
                     f"> 来源文件：`{escape_text(self.original_source.name)}`；工作表：{len(self.wb.worksheets)} 个", "",
                     "> 公式保留表达式及缓存结果；无法直接转换的对象见 conversion-report.json。", ""]
            stats_list = []
            for ws in self.wb.worksheets:
                content, stats = self.convert_sheet(ws, self.values_wb[ws.title], objects_by_sheet[ws.title], flavor)
                lines.extend([content, ""])
                for drawing in drawings:
                    if drawing["sheet"] == ws.title:
                        lines.extend([drawing_markdown(drawing), ""])
                if flavor == self.flavors[0]:
                    stats_list.append(stats)
            if attachments:
                lines.extend([attachments, ""])
            if unreferenced:
                lines.extend([unreferenced, ""])
            suffix = ".md" if flavor == "pure" else "_richtext.md"
            output = self.output_dir / f"{self.original_source.stem}{suffix}"
            output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
            outputs[flavor] = str(output)
            if flavor == self.flavors[0]:
                self.report["sheets"] = stats_list
        self.report["outputs"] = outputs
        self.report["totals"] = {
            "sheets": len(self.report["sheets"]),
            "nonempty_cells": sum(s["nonempty_cells"] for s in self.report["sheets"]),
            "formula_cells": sum(s["formula_cells"] for s in self.report["sheets"]),
            "formula_cells_without_cached_result": sum(
                s["formula_cells_without_cached_result"] for s in self.report["sheets"]),
            "actual_tables": sum(s["actual_tables"] for s in self.report["sheets"]),
            "auto_tables": sum(s["auto_tables"] for s in self.report["sheets"]),
            "images": sum(s["images"] for s in self.report["sheets"]),
            "shapes": sum(s["shapes"] for s in self.report["sheets"]),
            "charts": sum(s["charts"] for s in self.report["sheets"]),
            "comments": sum(s["comments"] for s in self.report["sheets"]),
        }
        missing_results = self.report["totals"]["formula_cells_without_cached_result"]
        if missing_results:
            self.warn(
                f"{missing_results} 个公式没有缓存结果，已保留公式表达式并标记“无缓存结果”。"
                "如需结果，请先用 Excel 或 LibreOffice 重新计算并保存，再执行转换。"
            )
        report_path = self.output_dir / "conversion-report.json"
        report_path.write_text(json.dumps(self.report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.report["report"] = str(report_path)
        return self.report


def prepare_source(source: Path) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    suffix = source.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        return source, None
    if suffix == ".xls":
        executable = shutil.which("soffice") or shutil.which("libreoffice")
        if not executable:
            raise ConversionError(".xls 旧格式需要安装 LibreOffice；也可以先在 Excel 中另存为 .xlsx。")
        temporary = tempfile.TemporaryDirectory(prefix="excel-to-md-")
        result = subprocess.run([executable, "--headless", "--convert-to", "xlsx", "--outdir",
                                 temporary.name, str(source)], capture_output=True, text=True, timeout=180)
        converted = Path(temporary.name) / f"{source.stem}.xlsx"
        if result.returncode != 0 or not converted.exists():
            temporary.cleanup()
            raise ConversionError(f"LibreOffice 转换失败：{result.stderr or result.stdout}")
        return converted, temporary
    raise ConversionError("仅支持 .xlsx/.xlsm/.xltx/.xltm；.xls 需 LibreOffice，.xlsb 请先另存为 .xlsx。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="尽可能完整地将 Excel 转换为 Markdown，源文件不会被修改。")
    parser.add_argument("input", type=Path, help="Excel 文件路径")
    parser.add_argument("-o", "--output-dir", type=Path, help="输出目录，默认 <文件名>-markdown")
    parser.add_argument("--flavor", choices=["pure", "rich", "both"], default="both", help="输出版本，默认 both")
    parser.add_argument("--no-auto-tables", action="store_true", help="仅转换 Excel 已定义的表，不自动识别表格")
    parser.add_argument("--diagram-render", choices=["auto", "never", "required"], default="auto",
                        help="绘图预览：auto 自动尝试 LibreOffice；never 禁用；required 失败返回非零")
    parser.add_argument("--values-from", type=Path, help="从重算副本读取公式结果，正文仍使用原始工作簿")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"文件不存在：{source}", file=sys.stderr)
        return 2
    output_dir = (args.output_dir or source.with_name(source.stem + "-markdown")).expanduser().resolve()
    temporary = None
    try:
        prepared, temporary = prepare_source(source)
        flavors = ["pure", "rich"] if args.flavor == "both" else [args.flavor]
        values_source = args.values_from.expanduser().resolve() if args.values_from else None
        if values_source and not values_source.is_file():
            raise ConversionError(f"公式结果副本不存在：{values_source}")
        converter = ExcelConverter(source, output_dir, flavors, not args.no_auto_tables, values_source, args.diagram_render)
        converter.source = prepared
        report = converter.convert()
        if args.diagram_render == "required" and any(d["render_status"] != "rendered" for d in report["drawings"]):
            raise ConversionError("必需的绘图预览未生成，详情见 conversion-report.json。")
        print(json.dumps({"status": "ok", "outputs": report["outputs"], "report": report["report"],
                          "totals": report["totals"], "warnings": len(report["warnings"])},
                         ensure_ascii=False, indent=2))
        return 0
    except (ConversionError, InvalidFileException, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"转换失败：{exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"文件或目录没有访问权限：{exc}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
