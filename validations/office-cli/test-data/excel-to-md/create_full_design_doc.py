#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建「完整设计文档测试.xlsx」— OfficeCLI 全功能验证。

覆盖：5 个 Sheet、每 Sheet 100+ 行、图片插入、形状(吹出泡/红框)、
公式、条件格式、数据验证、超链接、合并单元格、各种字体/颜色/背景组合。

运行：python3 create_full_design_doc.py
依赖：openpyxl, Pillow
"""
import os

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import (
    SpreadsheetDrawing, OneCellAnchor, AnchorMarker,
)
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.drawing.connector import (
    Shape, ShapeMeta, NonVisualDrawingProps, NonVisualDrawingShapeProps,
)
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.geometry import PresetGeometry2D
from openpyxl.drawing.fill import ColorChoice
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import (
    Paragraph, ParagraphProperties, CharacterProperties,
    RichTextProperties, RegularTextRun,
)
from openpyxl.drawing.text import Font as DFont

import openpyxl.writer.excel as _excel_mod
from PIL import Image as PILImage, ImageDraw

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(OUT_DIR, "完整设计文档测试.xlsx")
TMP = "/tmp"
GH = "https://github.com/Taohenger/ai-tool-lab"

# ---------------------------------------------------------------------------
# 形状/图片注入补丁：openpyxl 默认只把 charts/images 写入 drawing，
# 不支持任意 Shape。这里通过补丁把存放在 ws._shape_anchors 里的形状锚点
# 注入到 drawing，并为图片设置自定义 alt 文本(descr)。
# ---------------------------------------------------------------------------
_ORIG_WRITE_WORKSHEET = _excel_mod.ExcelWriter.write_worksheet


def _patched_write_worksheet(self, ws):
    _ORIG_WRITE_WORKSHEET(self, ws)
    for anchor in getattr(ws, "_shape_anchors", []):
        if isinstance(anchor, OneCellAnchor):
            ws._drawing.oneCellAnchor.append(anchor)


_excel_mod.ExcelWriter.write_worksheet = _patched_write_worksheet


_ORIG_PICTURE_FRAME = SpreadsheetDrawing._picture_frame


def _patched_picture_frame(self, idx):
    pic = _ORIG_PICTURE_FRAME(self, idx)
    try:
        imgs = self.images
        img = imgs[idx - 1] if 0 <= idx - 1 < len(imgs) else None
        alt = getattr(img, "_alt_text", None)
        if alt:
            pic.nvPicPr.cNvPr.descr = alt
            pic.nvPicPr.cNvPr.name = alt[:60]
    except Exception:
        pass
    return pic


SpreadsheetDrawing._picture_frame = _patched_picture_frame

# ---------------------------------------------------------------------------
# 颜色/样式常量
# ---------------------------------------------------------------------------
C_TITLE = "1F3864"
C_H2 = "2E5496"
C_BLUE_BG = "4472C4"
C_LIGHT_BLUE = "D9E1F2"
C_RED = "FF0000"
C_GREEN = "008000"
C_BLUE = "0000FF"
C_GRAY = "808080"
C_ORANGE = "ED7D31"
C_YELLOW = "FFFF00"
C_BLUEBG = "BDD7EE"
C_LINK = "0563C1"

SHAPE_ID = [100]  # 形状 id 计数器(避免与图片 id 冲突)


def solid_fill(rgb):
    return PatternFill(start_color=rgb, end_color=rgb, fill_type="solid")


def set_cell(ws, row, col, value=None, *, font=None, fill=None, align=None,
             hyperlink=None, border=None):
    cell = ws.cell(row=row, column=col)
    if value is not None:
        cell.value = value
    if font is not None:
        cell.font = font
    if fill is not None:
        cell.fill = fill
    if align is not None:
        cell.alignment = align
    if hyperlink is not None:
        cell.hyperlink = hyperlink
    if border is not None:
        cell.border = border
    return cell


# ---------------------------------------------------------------------------
# PIL 测试图片生成
# ---------------------------------------------------------------------------
def make_images():
    paths = {}

    # 1) UI 设计稿(登录页线框)
    img = PILImage.new("RGB", (640, 400), (245, 247, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 640, 60], fill=(31, 56, 100))
    d.rectangle([220, 110, 420, 360], fill=(255, 255, 255), outline=(180, 190, 210))
    d.rectangle([240, 140, 400, 170], fill=(220, 230, 245))
    d.rectangle([240, 190, 400, 220], fill=(220, 230, 245))
    d.rectangle([240, 240, 400, 280], fill=(68, 114, 196))
    d.ellipse([470, 130, 600, 260], fill=(255, 230, 153), outline=(200, 170, 80))
    p = os.path.join(TMP, "ui_mockup.png"); img.save(p); paths["ui"] = p

    # 2) 架构图(分层方块)
    img = PILImage.new("RGB", (640, 400), (252, 252, 252))
    d = ImageDraw.Draw(img)
    blocks = [
        (220, 30, 420, 80, (68, 114, 196)),
        (120, 130, 280, 180, (112, 173, 71)),
        (360, 130, 520, 180, (197, 90, 17)),
        (220, 230, 420, 280, (91, 155, 213)),
        (40, 230, 200, 280, (165, 165, 165)),
        (440, 230, 600, 280, (165, 165, 165)),
    ]
    for x1, y1, x2, y2, c in blocks:
        d.rectangle([x1, y1, x2, y2], fill=c, outline=(40, 40, 40))
    for (x1, y1, x2, y2, _), (sx1, sy1, sx2, sy2, _) in [
        (blocks[0], blocks[1]), (blocks[0], blocks[2]),
        (blocks[1], blocks[3]), (blocks[2], blocks[3]),
        (blocks[3], blocks[4]), (blocks[3], blocks[5]),
    ]:
        d.line([(x1 + x2) // 2, y2, (sx1 + sx2) // 2, sy1], fill=(80, 80, 80), width=2)
    p = os.path.join(TMP, "architecture.png"); img.save(p); paths["arch"] = p

    # 3) 流程图(圆角/菱形/矩形)
    img = PILImage.new("RGB", (640, 400), (250, 250, 250))
    d = ImageDraw.Draw(img)
    d.ellipse([260, 20, 380, 70], fill=(198, 224, 180), outline=(80, 120, 60))
    d.polygon([(320, 90), (420, 150), (320, 210), (220, 150)], fill=(255, 230, 153), outline=(180, 140, 60))
    d.rectangle([250, 230, 390, 290], fill=(180, 200, 235), outline=(60, 80, 130))
    d.ellipse([260, 320, 380, 370], fill=(235, 180, 180), outline=(140, 60, 60))
    for y1, y2 in [(70, 90), (210, 230), (290, 320)]:
        d.line([320, y1, 320, y2], fill=(80, 80, 80), width=2)
    p = os.path.join(TMP, "flowchart.png"); img.save(p); paths["flow"] = p

    # 4) 质量检查清单 banner(Sheet4 形状载体图)
    img = PILImage.new("RGB", (300, 80), (46, 116, 76))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, 294, 74], outline=(255, 255, 255), width=3)
    d.rectangle([20, 24, 60, 56], fill=(255, 255, 255))
    d.line([28, 38, 36, 48], fill=(46, 116, 76), width=4)
    d.line([36, 48, 54, 30], fill=(46, 116, 76), width=4)
    p = os.path.join(TMP, "checklist_banner.png"); img.save(p); paths["banner"] = p

    return paths


# ---------------------------------------------------------------------------
# 形状构造
# ---------------------------------------------------------------------------
def _make_callout(text, fill_rgb, line_rgb):
    gp = GraphicalProperties()
    gp.prstGeom = PresetGeometry2D(prst="wedgeRectCallout")
    gp.solidFill = fill_rgb
    gp.line.solidFill = line_rgb
    gp.line.w = 15000
    cp = CharacterProperties(
        latin=DFont(typeface="Arial"), sz=1100, b=True,
        solidFill=ColorChoice(srgbClr=line_rgb),
    )
    pp = ParagraphProperties(defRPr=cp)
    para = Paragraph(pPr=pp, r=[RegularTextRun(rPr=cp, t=text)])
    SHAPE_ID[0] += 1
    nv_sp = NonVisualDrawingShapeProps()
    nv_sp.txBax = None  # 规避 openpyxl 中 __elements__ 拼写错误(txBax)
    nv = ShapeMeta(
        cNvPr=NonVisualDrawingProps(id=SHAPE_ID[0], name="Callout %d" % SHAPE_ID[0], descr=text),
        cNvSpPr=nv_sp,
    )
    return Shape(spPr=gp, nvSpPr=nv, txBody=RichText(bodyPr=RichTextProperties(), p=[para]))


def _make_redbox():
    gp = GraphicalProperties()
    gp.noFill = True
    gp.line.solidFill = C_RED
    gp.line.w = 25000
    gp.prstGeom = PresetGeometry2D(prst="rect")
    SHAPE_ID[0] += 1
    nv_sp = NonVisualDrawingShapeProps()
    nv_sp.txBax = None  # 规避 openpyxl 中 __elements__ 拼写错误(txBax)
    nv = ShapeMeta(
        cNvPr=NonVisualDrawingProps(id=SHAPE_ID[0], name="RedBox %d" % SHAPE_ID[0]),
        cNvSpPr=nv_sp,
    )
    return Shape(spPr=gp, nvSpPr=nv)


def add_callout(ws, text, col, row, *, cx=2200000, cy=1100000,
                fill="FFFF00", line=C_RED):
    sp = _make_callout(text, fill, line)
    anchor = OneCellAnchor(
        _from=AnchorMarker(col=col, colOff=30000, row=row, rowOff=30000),
        ext=XDRPositiveSize2D(cx=cx, cy=cy),
        sp=sp,
    )
    if not hasattr(ws, "_shape_anchors"):
        ws._shape_anchors = []
    ws._shape_anchors.append(anchor)


def add_redbox(ws, col, row, *, cx=1900000, cy=650000):
    sp = _make_redbox()
    anchor = OneCellAnchor(
        _from=AnchorMarker(col=col, colOff=15000, row=row, rowOff=15000),
        ext=XDRPositiveSize2D(cx=cx, cy=cy),
        sp=sp,
    )
    if not hasattr(ws, "_shape_anchors"):
        ws._shape_anchors = []
    ws._shape_anchors.append(anchor)


def add_image(ws, path, cell, alt):
    img = XLImage(path)
    img._alt_text = alt
    ws.add_image(img, cell)
    return img


# ===========================================================================
# Sheet 1: 设计总览
# ===========================================================================
def build_sheet1(wb):
    ws = wb.create_sheet("设计总览")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 36
    ws.column_dimensions["C"].width = 46

    ws.merge_cells("A1:C1")
    set_cell(ws, 1, 1, "完整设计文档 — OfficeCLI 全功能验证",
             font=Font(bold=True, size=24, color=C_TITLE))

    set_cell(ws, 3, 1, "1. 文档信息", font=Font(bold=True, size=16, color=C_H2))
    info = [
        ("文档版本", "V3.0"),
        ("作者", "张三"),
        ("创建日期", "2026-08-10"),
        ("审核人", "李四"),
        ("项目名称", "OfficeCLI 全功能验证"),
        ("文档状态", "正式发布"),
        ("保密级别", "内部"),
    ]
    for i, (k, v) in enumerate(info):
        r = 4 + i
        set_cell(ws, r, 1, k, font=Font(bold=True))
        set_cell(ws, r, 2, v)

    set_cell(ws, 12, 1, "2. 修订记录", font=Font(bold=True, size=16, color=C_H2))
    rev_hdr = ["版本", "日期", "修改者", "修改内容"]
    for i, h in enumerate(rev_hdr):
        set_cell(ws, 13, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                 fill=solid_fill(C_BLUE_BG))
    revisions = [
        ("V1.0", "2025-03-01", "张三", "初稿创建"),
        ("V1.1", "2025-04-10", "李四", "补充 UI 规格"),
        ("V1.2", "2025-05-18", "王五", "修订数据模型"),
        ("V2.0", "2025-07-02", "张三", "架构重构"),
        ("V2.1", "2025-08-15", "李四", "新增公式验证"),
        ("V2.2", "2025-09-20", "王五", "更新检查清单"),
        ("V2.3", "2025-10-11", "赵六", "废弃旧接口", "废弃"),
        ("V2.4", "2025-11-05", "张三", "性能优化"),
        ("V2.5", "2025-12-12", "李四", "安全性增强"),
        ("V2.6", "2026-01-08", "王五", "文档结构整理"),
        ("V2.7", "2026-02-14", "赵六", "术语表更新"),
        ("V2.8", "2026-03-20", "张三", "修订记录补全"),
        ("V2.9", "2026-04-25", "李四", "格式矩阵扩充"),
        ("V3.0", "2026-08-10", "张三", "正式发布版本", "latest"),
    ]
    # 旧版本：灰色+删除线
    deprecated_row = 14
    set_cell(ws, deprecated_row, 1, "V0.9", font=Font(strike=True, color=C_GRAY))
    set_cell(ws, deprecated_row, 2, "2025-02-01", font=Font(strike=True, color=C_GRAY))
    set_cell(ws, deprecated_row, 3, "张三", font=Font(strike=True, color=C_GRAY))
    set_cell(ws, deprecated_row, 4, "草稿(已废弃)", font=Font(strike=True, color=C_GRAY))
    r = 15
    for item in revisions:
        if len(item) == 5:
            v, dt, who, desc, flag = item
        else:
            v, dt, who, desc = item
            flag = None
        vals = [v, dt, who, desc]
        if flag == "废弃":
            f = Font(color=C_RED, bold=True, strike=True)
            for c, val in enumerate(vals, start=1):
                set_cell(ws, r, c, val, font=f)
        elif flag == "latest":
            f = Font(color=C_GREEN, bold=True)
            for c, val in enumerate(vals, start=1):
                set_cell(ws, r, c, val, font=f)
        else:
            for c, val in enumerate(vals, start=1):
                set_cell(ws, r, c, val)
        r += 1
    # 填充到第 30 行
    while r <= 30:
        set_cell(ws, r, 1, f"(历史修订 {r - 14})")
        r += 1

    set_cell(ws, 32, 1, "3. 术语定义", font=Font(bold=True, size=16, color=C_H2))
    term_hdr = ["术语", "英文", "说明"]
    for i, h in enumerate(term_hdr):
        set_cell(ws, 33, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                 fill=solid_fill(C_BLUE_BG))
    terms = [
        ("OfficeCLI", "Office CLI", "Office 命令行转换工具", False, True),
        ("Markdown", "Markdown", "轻量标记语言", False, True),
        ("OpenPyXL", "OpenPyXL", "Python Excel 库", True, False),
        ("工作簿", "Workbook", "Excel 文件", False, False),
        ("工作表", "Worksheet", "Excel Sheet 页", False, False),
        ("单元格", "Cell", "表格最小单元", False, False),
        ("合并单元格", "Merged Cell", "多个单元格合并", False, False),
        ("条件格式", "Conditional Format", "基于规则的格式", True, False),
        ("数据验证", "Data Validation", "单元格输入约束", False, False),
        ("公式", "Formula", "单元格计算表达式", False, False),
        ("超链接", "Hyperlink", "指向外部资源", True, False),
        ("形状", "Shape", "绘制的几何对象", False, False),
        ("吹出泡", "Callout", "带指向的标注形状", False, False),
        ("图片", "Image", "嵌入的位图", False, True),
        ("字体", "Font", "文字样式", False, False),
        ("填充", "Fill", "单元格背景", False, False),
        ("边框", "Border", "单元格边线", False, False),
        ("删除线", "Strikethrough", "文字横线", False, False),
        ("斜体", "Italic", "倾斜文字", False, False),
        ("下划线", "Underline", "文字下划线", True, False),
        ("EMU", "English Metric Unit", "绘图单位(914400/英寸)", True, False),
        ("锚点", "Anchor", "图形定位标记", False, False),
        ("Alt 文本", "Alt Text", "图片替代说明", True, False),
    ]
    r = 34
    for term, en, desc, blue, link in terms:
        fnt = Font(bold=True, color=C_BLUE if blue else "000000")
        if link:
            set_cell(ws, r, 1, term, font=Font(bold=True, color=C_LINK, underline="single"),
                     hyperlink=GH)
        else:
            set_cell(ws, r, 1, term, font=fnt)
        set_cell(ws, r, 2, en)
        set_cell(ws, r, 3, desc)
        r += 1
    while r <= 55:
        set_cell(ws, r, 1, f"(预留术语 {r - 33})")
        r += 1

    set_cell(ws, 57, 1, "4. 格式验证矩阵", font=Font(bold=True, size=16, color=C_H2))
    set_cell(ws, 58, 1, "格式类型", font=Font(bold=True, color="FFFFFF"), fill=solid_fill(C_BLUE_BG))
    ws.merge_cells("B58:C58")
    set_cell(ws, 58, 2, "示例", font=Font(bold=True, color="FFFFFF"), fill=solid_fill(C_BLUE_BG))

    formats = [
        ("加粗文本", [("这是加粗文本", {"bold": True}),
                     ("Bold 加粗示例", {"bold": True})]),
        ("斜体文本", [("这是斜体文本", {"italic": True}),
                     ("Italic 示例", {"italic": True})]),
        ("删除线文本", [("这是删除线文本", {"strike": True}),
                      ("废弃内容(删除线)", {"strike": True})]),
        ("红色字体", [("红色字体", {"color": C_RED}),
                    ("Red", {"color": C_RED})]),
        ("蓝色字体", [("蓝色字体", {"color": C_BLUE}),
                    ("Blue", {"color": C_BLUE})]),
        ("绿色字体", [("绿色字体", {"color": C_GREEN}),
                    ("Green", {"color": C_GREEN})]),
        ("灰色字体", [("灰色字体", {"color": C_GRAY}),
                    ("Gray", {"color": C_GRAY})]),
        ("黄色背景高亮", [("黄色背景高亮", {}, {"start_color": C_YELLOW}),
                       ("Highlight 标注", {}, {"start_color": C_YELLOW})]),
        ("蓝色背景", [("蓝色背景", {}, {"start_color": C_BLUEBG}),
                    ("Blue bg", {}, {"start_color": C_BLUEBG})]),
        ("下划线", [("下划线文本", {"underline": "single"}),
                   ("Underline", {"underline": "single"})]),
        ("加粗+红色组合", [("加粗+红色组合", {"bold": True, "color": C_RED}),
                       ("Bold Red", {"bold": True, "color": C_RED})]),
        ("删除线+灰色组合", [("废弃+灰色删除线", {"strike": True, "color": C_GRAY}),
                        ("Old version", {"strike": True, "color": C_GRAY})]),
        ("超链接(GitHub)", [("GitHub 仓库", {"color": C_LINK, "underline": "single"}, None, GH),
                          ("ai-tool-lab", {"color": C_LINK, "underline": "single"}, None, GH)]),
        ("加粗+斜体+下划线", [("三重组合", {"bold": True, "italic": True, "underline": "single"}),
                         ("Triple", {"bold": True, "italic": True, "underline": "single"})]),
        ("字号 24", [("字号24示例", {"size": 24}),
                    ("Big", {"size": 24})]),
        ("字号 18", [("字号18示例", {"size": 18}),
                    ("Large", {"size": 18})]),
        ("字号 14", [("字号14示例", {"size": 14}),
                    ("Medium", {"size": 14})]),
        ("字号 12", [("字号12示例", {"size": 12}),
                    ("Normal", {"size": 12})]),
        ("字号 11", [("字号11示例", {"size": 11}),
                    ("Small", {"size": 11})]),
    ]
    r = 59
    for desc, samples in formats:
        set_cell(ws, r, 1, desc, font=Font(bold=True))
        for s in samples:
            text = s[0]
            fkw = s[1] if len(s) > 1 else {}
            fillkw = s[2] if len(s) > 2 else None
            link = s[3] if len(s) > 3 else None
            fill = solid_fill(fillkw["start_color"]) if fillkw else None
            set_cell(ws, r, 2, text, font=Font(**fkw), fill=fill, hyperlink=link)
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
            r += 1
    # 补足到 110 行
    while r <= 110:
        set_cell(ws, r, 1, f"(格式矩阵预留 {r - 58})")
        r += 1


# ===========================================================================
# Sheet 2: UI设计规格
# ===========================================================================
def build_sheet2(wb):
    ws = wb.create_sheet("UI设计规格")
    widths = {"A": 16, "B": 12, "C": 12, "D": 14, "E": 16, "F": 12, "G": 12, "H": 14, "I": 24}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    ws.merge_cells("A1:I1")
    set_cell(ws, 1, 1, "UI 设计规格", font=Font(bold=True, size=24, color=C_TITLE))

    set_cell(ws, 3, 1, "1. 页面布局规格", font=Font(bold=True, size=16, color=C_H2))
    layout_hdr = ["页面名称", "宽度", "高度", "布局方式", "响应式断点", "主色", "辅色", "备注"]
    for i, h in enumerate(layout_hdr):
        set_cell(ws, 4, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                 fill=solid_fill(C_BLUE_BG))
    layouts = [
        ("首页", 1920, 1080, "Grid", "1280/768", "#4472C4", "#BDD7EE", "主入口"),
        ("登录页", 1280, 800, "Flex", "768", "#4472C4", "#ED7D31", "居中卡片"),
        ("仪表盘", 1920, 1080, "Grid", "1440/1024", "#2E5496", "#70AD47", "多卡片"),
        ("列表页", 1920, 1080, "Flex", "1280", "#4472C4", "#FFC000", "表格为主"),
        ("详情页", 1280, 1080, "Flex", "1024", "#4472C4", "#BDD7EE", "左右栏"),
        ("表单页", 1280, 1080, "Flex", "768", "#4472C4", "#FF0000", "校验提示"),
        ("设置页", 1280, 800, "Grid", "1024", "#5A5A5A", "#BDD7EE", "侧边导航"),
        ("帮助页", 1280, 800, "Flex", "768", "#70AD47", "#BDD7EE", "文档展示"),
        ("错误页", 1280, 800, "Flex", "768", "#FF0000", "#FFC000", "404/500"),
        ("搜索页", 1920, 1080, "Grid", "1280", "#4472C4", "#ED7D31", "结果列表"),
        ("个人中心", 1280, 1080, "Grid", "1024", "#4472C4", "#BDD7EE", "信息卡"),
        ("消息中心", 1280, 1080, "Flex", "1024", "#4472C4", "#FFC000", "通知流"),
        ("旧版首页", 1024, 768, "Table", "无", "#999999", "#CCCCCC", "废弃", "废弃"),
        ("新版首页", 1920, 1080, "Grid", "1280/768", "#4472C4", "#BDD7EE", "响应式"),
        ("移动端首页", 375, 812, "Flex", "375", "#4472C4", "#ED7D31", "iOS 尺寸"),
        ("平板首页", 768, 1024, "Grid", "768", "#4472C4", "#BDD7EE", "iPad 尺寸"),
        ("弹窗-确认", 480, 240, "Flex", "N/A", "#4472C4", "#70AD47", "模态"),
        ("弹窗-警告", 480, 240, "Flex", "N/A", "#FFC000", "#FF0000", "模态"),
        ("抽屉-筛选", 400, 800, "Flex", "768", "#4472C4", "#BDD7EE", "右侧滑出"),
        ("抽屉-详情", 600, 1080, "Flex", "1024", "#4472C4", "#BDD7EE", "右侧滑出"),
        ("导航栏", 1920, 64, "Flex", "1280", "#1F3864", "#FFFFFF", "顶部"),
        ("侧边栏", 240, 1080, "Flex", "1024", "#2E5496", "#BDD7EE", "左侧"),
        ("页脚", 1920, 120, "Grid", "1280", "#5A5A5A", "#FFFFFF", "底部"),
        ("卡片", 380, 240, "Flex", "N/A", "#FFFFFF", "#4472C4", "通用卡片"),
        ("按钮组", 320, 48, "Flex", "N/A", "#4472C4", "#ED7D31", "操作区"),
        ("标签页", 1280, 48, "Flex", "768", "#4472C4", "#BDD7EE", "切换"),
        ("面包屑", 1280, 40, "Flex", "768", "#5A5A5A", "#BDD7EE", "路径"),
        ("分页", 1280, 48, "Flex", "768", "#4472C4", "#FFFFFF", "翻页"),
        ("空状态", 480, 320, "Flex", "N/A", "#5A5A5A", "#BDD7EE", "占位"),
        ("加载态", 1280, 800, "Flex", "768", "#4472C4", "#BDD7EE", "骨架屏"),
        ("骨架屏", 1280, 800, "Grid", "768", "#E0E0E0", "#F5F5F5", "占位"),
        ("图表页", 1920, 1080, "Grid", "1440", "#4472C4", "#70AD47", "数据可视化"),
        ("地图页", 1920, 1080, "Grid", "1440", "#4472C4", "#70AD47", "GIS"),
        ("打印页", 794, 1123, "Grid", "N/A", "#000000", "#FFFFFF", "A4"),
        ("暗色主题", 1920, 1080, "Grid", "1280", "#1F1F1F", "#3C3C3C", "Dark mode"),
        ("高对比", 1920, 1080, "Flex", "1280", "#000000", "#FFFF00", "无障碍"),
        ("预览页", 1280, 720, "Flex", "1024", "#4472C4", "#BDD7EE", "只读"),
    ]
    r = 5
    highlight_rows = {7, 13, 17, 23}  # 1-based 相对索引(重要参数)
    for idx, row in enumerate(layouts):
        flag = row[-1] if len(row) == 9 else None
        vals = row[:8] if flag else row
        rel = idx + 1
        for c, val in enumerate(vals, start=1):
            cell_fill = None
            fnt = None
            if flag == "废弃":
                fnt = Font(color=C_RED, strike=True, bold=True)
            elif rel in highlight_rows:
                cell_fill = solid_fill(C_YELLOW)
            set_cell(ws, r, c, val, font=fnt, fill=cell_fill)
        r += 1
    # 合并部分单元格(备注列合并示例)
    ws.merge_cells("H7:I7")
    ws.merge_cells("H13:I13")

    set_cell(ws, 42, 1, "2. 组件规格表", font=Font(bold=True, size=16, color=C_H2))
    ws.merge_cells("A43:I43")
    set_cell(ws, 43, 1, "组件规格表 (Component Specification)",
             font=Font(bold=True, size=13, color="FFFFFF"), fill=solid_fill(C_BLUE_BG),
             align=Alignment(horizontal="center"))
    comp_hdr = ["组件名", "类型", "尺寸", "颜色", "字体", "边框", "阴影", "状态", "备注"]
    for i, h in enumerate(comp_hdr):
        set_cell(ws, 44, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                 fill=solid_fill(C_H2))
    statuses = ["确定", "废弃", "待定"]
    comp_types = ["按钮", "输入框", "选择器", "复选框", "单选框", "开关", "标签", "卡片",
                  "对话框", "抽屉", "表格", "分页", "导航", "菜单", "提示", "徽标",
                  "头像", "进度条", "骨架", "空状态"]
    r = 45
    n = 0
    while r <= 102:
        ctype = comp_types[n % len(comp_types)]
        st = statuses[n % 3]
        border = "1px solid #DDD"
        shadow = "0 2px 4px rgba(0,0,0,.1)" if n % 2 == 0 else "无"
        row_vals = [
            "%s-%02d" % (ctype, n + 1), ctype, "%dx%d" % (80 + n * 2, 32),
            "#%06X" % (0x4472C4 + n * 0x010101), "14px/Roboto", border, shadow, st,
            "组件备注 %d" % (n + 1),
        ]
        for c, val in enumerate(row_vals, start=1):
            set_cell(ws, r, c, val)
        r += 1
        n += 1

    # 条件格式：状态列 H45:H102
    rng = "H45:H102"
    ws.conditional_formatting.add(rng, CellIsRule(
        operator="equal", formula=['"确定"'], font=Font(bold=True, color=C_GREEN)))
    ws.conditional_formatting.add(rng, CellIsRule(
        operator="equal", formula=['"废弃"'], font=Font(strike=True, color=C_RED)))
    ws.conditional_formatting.add(rng, CellIsRule(
        operator="equal", formula=['"待定"'], fill=solid_fill(C_YELLOW)))
    # 数据验证下拉框
    dv = DataValidation(type="list", formula1='"确定,废弃,待定"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(rng)


# ===========================================================================
# Sheet 3: 数据与公式
# ===========================================================================
def build_sheet3(wb):
    ws = wb.create_sheet("数据与公式")
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 40

    ws.merge_cells("A1:F1")
    set_cell(ws, 1, 1, "数据与公式验证", font=Font(bold=True, size=24, color=C_TITLE))

    def section(row, title):
        set_cell(ws, row, 1, title, font=Font(bold=True, size=16, color=C_H2))

    def header(row, cols):
        for i, h in enumerate(cols):
            set_cell(ws, row, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                     fill=solid_fill(C_BLUE_BG))

    # 1. 基础运算 A4-A30
    section(3, "1. 基础运算")
    header(4, ["项", "数值1", "数值2", "公式", "结果", "说明"])
    base_rows = [
        ("加法", 10, 20, "=B5+C5", "SUM 两数"),
        ("减法", 30, 12, "=B6-C6", "差值"),
        ("乘法", 6, 7, "=B7*C7", "积"),
        ("除法", 100, 4, "=B8/C8", "商"),
        ("求和", None, None, "=SUM(B5:C8)", "区域求和"),
        ("平均值", None, None, "=AVERAGE(B5:C8)", "区域平均"),
        ("最大值", None, None, "=MAX(B5:C8)", "区域最大"),
        ("最小值", None, None, "=MIN(B5:C8)", "区域最小"),
        ("计数", None, None, "=COUNT(B5:C8)", "数值计数"),
        ("非空计数", None, None, "=COUNTA(A5:A8)", "非空计数"),
        ("幂运算", 2, 10, "=B15^C15", "2 的 10 次方"),
        ("取整", 3.7, None, "=INT(B16)", "向下取整"),
        ("四舍五入", 3.456, 2, "=ROUND(B17,C17)", "保留 2 位"),
        ("绝对值", -8, None, "=ABS(B18)", "绝对值"),
        ("模运算", 10, 3, "=MOD(B19,C19)", "余数"),
        ("平方根", 81, None, "=SQRT(B20)", "平方根"),
        ("条件求和", None, None, "=SUMIF(B5:B8,\">5\")", "大于5求和"),
        ("条件平均", None, None, "=AVERAGEIF(B5:B8,\">5\")", "大于5平均"),
        ("排名", None, None, "=RANK(B7,B5:B8)", "B7 在区域内排名"),
        ("随机数", None, None, "=RAND()", "0~1 随机"),
        ("随机整数", 1, 100, "=RANDBETWEEN(B23,C23)", "1~100 随机"),
        ("PI", None, None, "=PI()", "圆周率"),
        ("取余数2", 17, 5, "=MOD(B26,C26)", "余数"),
        ("乘方2", 5, 3, "=B27^C27", "5 的 3 次方"),
        ("向上取整", 4.2, None, "=CEILING(B28,1)", "向上取整"),
        ("向下取整2", 4.8, None, "=FLOOR(B29,1)", "向下取整"),
        ("百分位", None, None, "=PERCENTILE(B5:B8,0.5)", "中位数"),
    ]
    r = 5
    for item in base_rows:
        for c, val in enumerate(item, start=1):
            set_cell(ws, r, c, val)
        r += 1

    # 2. 逻辑函数 A33-A55
    section(32, "2. 逻辑函数")
    header(33, ["函数", "参数A", "参数B", "公式", "结果", "说明"])
    logic_rows = [
        ("IF", 85, 60, '=IF(B34>=C34,"及格","不及格")', "条件判断"),
        ("IF 嵌套", 75, None, '=IF(B35>=90,"优",IF(B35>=60,"良","差"))', "多条件"),
        ("IFS", 88, None, '=IFS(B36>=90,"A",B36>=80,"B",B36>=60,"C")', "多条件(2016+)"),
        ("AND", True, True, "=AND(B37,C37)", "逻辑与"),
        ("OR", True, False, "=OR(B38,C38)", "逻辑或"),
        ("NOT", True, None, "=NOT(B39)", "逻辑非"),
        ("IFERROR", 1, 0, "=IFERROR(B40/C40,\"除零错误\")", "错误捕获"),
        ("XOR", True, False, "=XOR(B41,C41)", "异或"),
        ("TRUE", None, None, "=TRUE()", "布尔真"),
        ("FALSE", None, None, "=FALSE()", "布尔假"),
        ("ISNUMBER", 123, None, "=ISNUMBER(B44)", "是否数字"),
        ("ISTEXT", "abc", None, "=ISTEXT(B45)", "是否文本"),
        ("ISBLANK", None, None, "=ISBLANK(B46)", "是否空"),
        ("ISERROR", None, None, "=ISERROR(1/0)", "是否错误"),
        ("ISEVEN", 8, None, "=ISEVEN(B48)", "是否偶数"),
        ("ISODD", 7, None, "=ISODD(B49)", "是否奇数"),
        ("IF + AND", 80, 90, '=IF(AND(B50>=60,C50>=60),"通过","否")', "组合判断"),
        ("IF + OR", 55, 95, '=IF(OR(B51>=60,C51>=60),"部分通过","否")', "组合判断"),
        ("SWITCH", 2, None, '=SWITCH(B52,1,"一",2,"二",3,"三","其他")', "分支选择"),
        ("IFNA", None, None, '=IFNA(VLOOKUP("x",B34:C35,1,0),"未找到")', "NA 捕获"),
        ("ISLOGICAL", True, None, "=ISLOGICAL(B54)", "是否布尔"),
        ("ISNONTEXT", 123, None, "=ISNONTEXT(B55)", "是否非文本"),
        ("AND 多参", None, None, "=AND(B34>0,B35>0,B36>0)", "多参数与"),
    ]
    r = 34
    for item in logic_rows:
        for c, val in enumerate(item, start=1):
            set_cell(ws, r, c, val)
        r += 1

    # 3. 查找引用 A58-A80
    section(57, "3. 查找引用")
    header(58, ["函数", "参数A", "参数B", "公式", "结果", "说明"])
    lookup_rows = [
        ("VLOOKUP", "苹果", None, '=VLOOKUP(B59,B34:C40,1,0)', "垂直查找"),
        ("HLOOKUP", None, None, '=HLOOKUP("函数",B33:F33,1,0)', "水平查找"),
        ("INDEX", None, None, "=INDEX(B34:B40,3)", "按索引取值"),
        ("MATCH", "IF", None, '=MATCH(B62,B34:B40,0)', "返回位置"),
        ("INDEX+MATCH", None, None, "=INDEX(B34:B40,MATCH(\"IF\",B34:B40,0))", "组合查找"),
        ("CHOOSE", 2, None, '=CHOOSE(C63,"一","二","三")', "按索引选择"),
        ("OFFSET", None, None, "=OFFSET(B34,2,0)", "偏移引用"),
        ("INDIRECT", None, None, '=INDIRECT("B34")', "间接引用"),
        ("ROW", None, None, "=ROW(B34)", "行号"),
        ("COLUMN", None, None, "=COLUMN(B34)", "列号"),
        ("ROWS", None, None, "=ROWS(B34:B40)", "行数"),
        ("COLUMNS", None, None, "=COLUMNS(B34:F34)", "列数"),
        ("ADDRESS", 5, 2, "=ADDRESS(B71,C71)", "构造地址"),
        ("AREAS", None, None, "=AREAS(B34:B40)", "区域数"),
        ("VLOOKUP 近似", 85, None, '=VLOOKUP(B73,{0,"F";60,"D";90,"A"},2,1)', "近似匹配"),
        ("XLOOKUP", "苹果", None, '=XLOOKUP(B74,B34:B40,B34:B40)', "新版查找"),
        ("XMATCH", "IF", None, '=XMATCH(B75,B34:B40)', "新版匹配"),
        ("INDEX 二维", None, None, "=INDEX(B34:F40,2,3)", "二维取值"),
        ("OFFSET 求和", None, None, "=SUM(OFFSET(B34,0,0,3,1))", "偏移求和"),
        ("HYPERLINK", None, None, '=HYPERLINK("https://github.com/Taohenger/ai-tool-lab","仓库")', "超链接公式"),
        ("VLOOKUP 跨表", None, None, '=VLOOKUP(B34,B34:C40,1,0)', "同表查找"),
        ("MATCH 近似", 85, None, '=MATCH(B79,{0;60;90},1)', "近似位置"),
        ("CHOOSE 多值", 3, None, '=CHOOSE(B80,"A","B","C","D")', "多值选择"),
    ]
    r = 59
    for item in lookup_rows:
        for c, val in enumerate(item, start=1):
            set_cell(ws, r, c, val)
        r += 1

    # 4. 文本函数 A83-A102
    section(82, "4. 文本函数")
    header(83, ["函数", "参数A", "参数B", "公式", "结果", "说明"])
    text_rows = [
        ("CONCATENATE", "Hello", "World", '=CONCATENATE(B84," ",C84)', "拼接"),
        ("CONCAT", "A", "B", '=CONCAT(B85,C85)', "新版拼接"),
        ("TEXTJOIN", "a", "b", '=TEXTJOIN("-",TRUE,B86,C86)', "带分隔拼接"),
        ("LEFT", "Excel", 2, '=LEFT(B87,C87)', "左截取"),
        ("RIGHT", "Excel", 2, '=RIGHT(B88,C88)', "右截取"),
        ("MID", "Excel", 2, '=MID(B89,C89,2)', "中间截取"),
        ("LEN", "Excel", None, "=LEN(B90)", "长度"),
        ("LENB", "Excel", None, "=LENB(B91)", "字节长度"),
        ("LOWER", "EXCEL", None, "=LOWER(B92)", "小写"),
        ("UPPER", "excel", None, "=UPPER(B93)", "大写"),
        ("PROPER", "hello world", None, "=PROPER(B94)", "首字母大写"),
        ("TRIM", "  a b  ", None, "=TRIM(B95)", "去首尾空格"),
        ("CLEAN", "a\nb", None, "=CLEAN(B96)", "去不可见字符"),
        ("SUBSTITUTE", "a-b-c", "-", '=SUBSTITUTE(B97,"-","/")', "替换"),
        ("REPLACE", "abcdef", 2, '=REPLACE(B98,C98,2,"XY")', "按位置替换"),
        ("REPT", "Ab", 3, '=REPT(B99,C99)', "重复"),
        ("FIND", "a-b-c", "-", '=FIND(C100,B100)', "查找位置"),
        ("SEARCH", "a-b-c", "-", '=SEARCH(C101,B101)', "查找(不区分大小写)"),
        ("TEXT", 1234.5, None, '=TEXT(B102,"0.00")', "格式化为文本"),
        ("VALUE", "123", None, "=VALUE(B103)", "文本转数值"),
    ]
    r = 84
    for item in text_rows:
        for c, val in enumerate(item, start=1):
            set_cell(ws, r, c, val)
        r += 1
    # 补足到 105 行
    while r <= 105:
        set_cell(ws, r, 1, f"(文本函数预留 {r - 83})")
        r += 1


# ===========================================================================
# Sheet 4: 检查清单
# ===========================================================================
def build_sheet4(wb, img_paths):
    ws = wb.create_sheet("检查清单")
    widths = {"A": 6, "B": 36, "C": 14, "D": 8, "E": 10, "F": 12, "G": 30}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    ws.merge_cells("A1:G1")
    set_cell(ws, 1, 1, "质量检查清单", font=Font(bold=True, size=24, color=C_TITLE))

    set_cell(ws, 3, 1, "1. 代码检查项", font=Font(bold=True, size=16, color=C_H2))
    hdr = ["序号", "检查项", "分类", "优先级", "状态", "负责人", "备注"]
    for i, h in enumerate(hdr):
        set_cell(ws, 4, 1 + i, h, font=Font(bold=True, color="FFFFFF"),
                 fill=solid_fill(C_BLUE_BG))

    cats = ["代码规范", "安全", "性能", "可维护性", "测试", "文档", "兼容性"]
    pris = ["高", "中", "低"]
    stats = ["通过", "未通过", "待检查"]
    owners = ["张三", "李四", "王五", "赵六"]
    checks = [
        "命名是否符合规范", "是否有 SQL 注入风险", "是否处理空指针", "函数圈复杂度是否过高",
        "是否覆盖单元测试", "接口文档是否齐全", "是否兼容旧版本", "敏感信息是否脱敏",
        "循环是否有性能隐患", "异常是否被捕获", "日志级别是否合理", "配置是否可外部化",
        "是否避免魔法数字", "是否使用参数化查询", "是否有内存泄漏", "是否限制并发数",
        "测试覆盖率是否达标", "README 是否更新", "是否支持主流浏览器", "密码是否加密存储",
        "是否有重复代码", "是否校验输入长度", "是否缓存热点数据", "是否定义清晰边界",
        "是否有集成测试", "注释是否完整", "是否处理时区", "是否避免硬编码密钥",
        "是否使用批量操作", "是否定义超时时间", "是否有回归测试", "变更日志是否记录",
        "是否支持移动端", "是否启用 HTTPS", "是否消除冗余查询", "类是否单一职责",
        "是否有压力测试", "API 示例是否提供", "是否向后兼容", "是否校验文件类型",
    ]
    r = 5
    n = 0
    while r <= 102:
        check = checks[n % len(checks)]
        pr = pris[n % 3]
        st = stats[n % 3]
        owner = owners[n % 4]
        row_vals = [n + 1, "%s - 第%d项" % (check, n + 1), cats[n % len(cats)],
                    pr, st, owner, "备注 %d" % (n + 1)]
        for c, val in enumerate(row_vals, start=1):
            set_cell(ws, r, c, val)
        r += 1
        n += 1

    # 优先级列 D5:D102
    prng = "D5:D102"
    ws.conditional_formatting.add(prng, CellIsRule(
        operator="equal", formula=['"高"'], font=Font(bold=True, color=C_RED)))
    ws.conditional_formatting.add(prng, CellIsRule(
        operator="equal", formula=['"中"'], font=Font(color=C_ORANGE)))
    ws.conditional_formatting.add(prng, CellIsRule(
        operator="equal", formula=['"低"'], font=Font(color=C_GRAY)))
    # 状态列 E5:E102
    srng = "E5:E102"
    ws.conditional_formatting.add(srng, CellIsRule(
        operator="equal", formula=['"通过"'], font=Font(bold=True, color=C_GREEN)))
    ws.conditional_formatting.add(srng, CellIsRule(
        operator="equal", formula=['"未通过"'], font=Font(bold=True, color=C_RED)))
    ws.conditional_formatting.add(srng, CellIsRule(
        operator="equal", formula=['"待检查"'], fill=solid_fill(C_YELLOW)))
    # 数据验证
    dv = DataValidation(type="list", formula1='"通过,未通过,待检查"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(srng)

    # 载体图片(确保 drawing 部件被创建)+ 形状
    add_image(ws, img_paths["banner"], "I2", "质量检查清单标题横幅")
    add_callout(ws, "重点关注：高优先级项必须全部通过", 7, 9, cx=2400000, cy=1100000)
    add_callout(ws, "需复核：安全类检查项", 7, 29, cx=2400000, cy=1100000)
    add_callout(ws, "提示：待检查项请尽快确认", 7, 55, cx=2400000, cy=1100000)
    add_redbox(ws, 0, 14, cx=1600000, cy=520000)   # 圈出第 15 行附近
    add_redbox(ws, 0, 49, cx=1600000, cy=520000)   # 圈出第 50 行附近


# ===========================================================================
# Sheet 5: 图片与附件
# ===========================================================================
def build_sheet5(wb, img_paths):
    ws = wb.create_sheet("图片与附件")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 60

    ws.merge_cells("A1:B1")
    set_cell(ws, 1, 1, "图片与附件", font=Font(bold=True, size=24, color=C_TITLE))

    set_cell(ws, 3, 1, "1. UI 设计稿", font=Font(bold=True, size=16, color=C_H2))
    ui_desc = [
        ("图 1-1", "登录页面线框图(640x400)，包含顶部导航、登录卡片与装饰元素"),
        ("图 1-2", "采用 1280x800 响应式断点，主色 #4472C4，辅色 #ED7D31"),
        ("说明", "所有 UI 稿均由 PIL 自动生成，仅用于 OfficeCLI 图片解析验证"),
    ]
    r = 4
    for k, v in ui_desc:
        set_cell(ws, r, 1, k, font=Font(bold=True))
        set_cell(ws, r, 2, v)
        r += 1
    # 插入 UI 设计稿图片(带 alt 文本)
    add_image(ws, img_paths["ui"], "A8", "UI 设计稿 - 登录页面线框图(640x400)")
    add_image(ws, img_paths["ui"], "A30", "UI 设计稿副本 - 用于图片多张插入验证")
    while r <= 30:
        set_cell(ws, r, 1, f"(UI 区域预留 {r - 3})")
        r += 1

    set_cell(ws, 32, 1, "2. 架构图", font=Font(bold=True, size=16, color=C_H2))
    arch_desc = [
        ("图 2-1", "系统分层架构图：表现层、业务层、数据层、基础设施层"),
        ("图 2-2", "组件间通过标准接口通信，支持水平扩展"),
        ("说明", "架构图用于验证 Excel 中嵌入图片的解析与导出能力"),
        ("依赖", "前端 -> 网关 -> 服务 -> 缓存 -> 数据库"),
        ("扩展", "支持多副本部署，无状态服务可横向扩展"),
    ]
    r = 33
    for k, v in arch_desc:
        set_cell(ws, r, 1, k, font=Font(bold=True))
        set_cell(ws, r, 2, v)
        r += 1
    add_image(ws, img_paths["arch"], "A40", "架构图 - 系统分层结构(640x400)")
    while r <= 60:
        set_cell(ws, r, 1, f"(架构图区域预留 {r - 32})")
        r += 1

    set_cell(ws, 62, 1, "3. 流程图", font=Font(bold=True, size=16, color=C_H2))
    flow_desc = [
        ("图 3-1", "用户操作流程：开始 -> 判断 -> 处理 -> 结束"),
        ("图 3-2", "包含菱形判断节点与矩形处理节点"),
        ("说明", "流程图用于验证图形元素在 Excel 中的呈现"),
        ("步骤1", "用户发起请求"),
        ("步骤2", "系统校验权限"),
        ("步骤3", "执行业务逻辑"),
        ("步骤4", "返回结果"),
    ]
    r = 63
    for k, v in flow_desc:
        set_cell(ws, r, 1, k, font=Font(bold=True))
        set_cell(ws, r, 2, v)
        r += 1
    add_image(ws, img_paths["flow"], "A72", "流程图 - 用户操作流程(640x400)")
    while r <= 102:
        set_cell(ws, r, 1, f"(流程图区域预留 {r - 62})")
        r += 1


# ===========================================================================
# 主流程
# ===========================================================================
def main():
    img_paths = make_images()
    wb = openpyxl.Workbook()
    # 删除默认 Sheet
    default = wb.active
    wb.remove(default)

    build_sheet1(wb)
    build_sheet2(wb)
    build_sheet3(wb)
    build_sheet4(wb, img_paths)
    build_sheet5(wb, img_paths)

    wb.save(OUT)
    print("✅ 完整设计文档已生成")
    print("   文件: %s" % OUT)
    for ws in wb.worksheets:
        print("   Sheet [%s] 最大行: %d" % (ws.title, ws.max_row))


if __name__ == "__main__":
    main()
