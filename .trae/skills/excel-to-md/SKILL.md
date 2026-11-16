---
name: "excel-to-md"
description: "Convert Excel workbooks to Markdown with tables, formulas, styles, images, comments and shapes. Invoke when a user asks to convert, export, or migrate Excel/xlsx/xlsm to Markdown."
---

# Excel to Markdown

将 Excel 尽可能完整地转换为 Markdown。源工作簿只读，不会被修改。原生支持 `.xlsx`、`.xlsm`、`.xltx`、`.xltm`；`.xls` 通过 LibreOffice 临时转换。

## 何时使用

用户要求“Excel 转 Markdown / md”“导出工作表”“把 Excel 设计文档转为可阅读文档”，或需要保留 Excel 中的表格、公式、颜色、删除线、图片、批注、吹出泡时使用。

## 核心原则

1. 必须实际运行 `scripts/excel_to_md.py`，不要只描述转换方法。
2. 不依赖 OfficeCLI；openpyxl 读取单元格，Python 直接读取 OOXML 中的图片和形状关系。
3. 转换后必须检查 `conversion-report.json`，把警告和统计结果告知用户。
4. Markdown、assets 目录和转换报告是一个整体，不要只移动 Markdown 文件。
5. 不得覆盖或重新保存源 Excel。所有中间文件放临时目录。
6. 不得宣称任意 Excel 都能 100% 像素级还原；图表视觉、数据透视图和 SmartArt 等不能原生画成 Markdown 时必须明确说明。

## 安装

需要 Python 3.10+。首次使用或出现依赖导入错误时执行：

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .trae\skills\excel-to-md\scripts\install.ps1
```

Linux / macOS：

```bash
bash .trae/skills/excel-to-md/scripts/install.sh
```

安装器在 Skill 内创建 `.venv`，不需要管理员权限。已安装依赖时可直接使用系统 Python。

## 调用

在包含 `.trae/skills/excel-to-md` 的工程根目录执行：

Windows PowerShell：

```powershell
& .trae\skills\excel-to-md\.venv\Scripts\python.exe .trae\skills\excel-to-md\scripts\excel_to_md.py "输入.xlsx"
```

Linux / macOS：

```bash
.trae/skills/excel-to-md/.venv/bin/python .trae/skills/excel-to-md/scripts/excel_to_md.py "输入.xlsx"
```

通用写法：

```bash
python scripts/excel_to_md.py "输入.xlsx" -o "输出目录" --flavor both
```

参数：

| 参数 | 含义 |
|---|---|
| `input` | Excel 文件路径，必填 |
| `-o / --output-dir` | 输出目录，默认源文件旁的 `<文件名>-markdown` |
| `--flavor pure` | 仅生成 GitHub 兼容的纯净版 |
| `--flavor rich` | 仅生成带 HTML 颜色和背景的富文本版 |
| `--flavor both` | 两个版本都生成，默认 |
| `--no-auto-tables` | 关闭未命名区域自动表格识别，仅保留 Excel 已定义的表 |
| `--values-from` | 从重算副本读取公式结果；结构、格式和公式表达式仍使用原始工作簿 |

## 输出

| 文件 | 内容 |
|---|---|
| `<文件名>.md` | 纯净版；颜色、背景下沉为文本标记，适合 GitHub |
| `<文件名>_richtext.md` | 富文本版；用 HTML 保留颜色、背景、下划线，适合 VS Code / Typora |
| `assets/` | 按真实 OOXML 关系提取的图片、嵌入附件和宏 |
| `conversion-report.json` | 每个工作表的统计、隐藏内容、合并区域、公式缺缓存数及所有警告 |

## 转换范围

- 全部工作表及原始顺序，包括隐藏和深度隐藏工作表。
- 非空单元格、行列位置、日期、百分比、常见数字格式和浮点精度。
- Excel 已定义的表；未命名数据区域自动识别为 Markdown 表格，按真实列号补齐空洞。
- 加粗、斜体、删除线、下划线、上下标、字体色、背景色、超链接及单元格内行内富文本。
- 公式表达式和文件中已有的缓存结果；无缓存结果时明确标记，不自行猜测计算值。
- 批注作者和内容，集中在每个工作表的“批注”章节。
- 图片按 drawing relationship 精确提取，不按文件名顺序猜测；保留 alt、锚点和尺寸。
- 吹出泡、文本框、矩形红框、连接线等形状，保留文字、类型、颜色和大致覆盖单元格范围。
- 图表保留标题、类型、位置和源数据区域；嵌入附件及 VBA 宏作为文件保留。
- 合并单元格、隐藏行列和无法视觉转换的对象记录在报告中。

## 必须告知用户的边界

- Markdown 不能重绘 Excel 图表、数据透视图、SmartArt 或精确排版；对应信息或附件会保留并产生警告。
- 转换器不是公式计算引擎。若公式没有缓存结果，先用 Excel / LibreOffice 重新计算并保存，再转换。
- `.xls` 需要 LibreOffice；`.xlsb` 请先另存为 `.xlsx`；密码加密文件需要先解密。
- 复杂条件格式、数据验证和工作簿语义不会全部变成 Markdown 正文，不能将本工具当作工作簿逻辑迁移器。

## 离线迁移

在联网机器上进入 Skill 目录，使用与离线目标机器相同的操作系统、CPU 架构和 Python 版本下载依赖：

```bash
python -m pip download -r requirements.txt -d wheels
```

把整个 `excel-to-md` 目录复制到离线机器的 `.trae/skills/` 下，再运行安装脚本。检测到 `wheels/` 时安装器自动使用 `--no-index`，不会访问网络。

## 验证

```bash
python tests/test_excel_to_md.py
```

交付前至少确认：工作表数、非空单元格数、表格数、图片数、形状数与源文件相符；所有 Markdown 引用的本地资源存在；警告已逐条解释。

## 可编辑流程图与组合绘图（1.1.0）

默认 `--diagram-render auto`：有形状、连接线、组合图形、图表或未知 graphicFrame 的工作表会额外生成整体预览。

- 直接从 OOXML 读取嵌套组合中的形状文字、节点 ID、连接线两端 ID 和箭头方向。只有两端唯一对应到节点时才输出连接关系，不按相邻位置猜测；双向线和无向线分别保留。
- 用 **LibreOffice** 导出临时工作簿副本的整页 PDF，再由 **PyMuPDF** 生成 PNG。PNG 嵌入 Markdown；PDF 供放大查看。保持整个工作表作为上下文，避免裁掉箭头、分支标签和旁注。
- `assets/original-workbook.*` 是源文件逐字节副本，保留可编辑图形。报告 `drawings[]` 记录节点、连接线、未解析对象、渲染状态及相对资源路径。
- `render_status=rendered` 只代表成功输出预览，**不是图形与 Excel 完全一致的认证**。LibreOffice 可能改变字体、SmartArt、复杂排版，也可能重算公式；正文公式与缓存仍只来自原始文件或显式指定的 `--values-from`。
- SmartArt 仍不保证能提取节点关系；普通线条若未记录端点 ID，也不能可靠推断业务流程。保留整图预览和源工作簿，逐项告警，禁止声称“任意流程图均完整识别”。

普通转换不强制安装 LibreOffice；要保留可编辑流程图的视觉预览，目标电脑需安装 LibreOffice，并确保 `libreoffice` 或 `soffice` 在 PATH 中。Python 安装器会安装 PyMuPDF。

```bash
# 有绘图但无法渲染时返回非零；报告、文字信息和源文件副本仍保留
python scripts/excel_to_md.py 输入.xlsx -o 输出目录 --diagram-render required

# 只提取文字和明确的连接关系，不运行外部渲染器
python scripts/excel_to_md.py 输入.xlsx -o 输出目录 --diagram-render never

# 运行全部测试（含流程图测试；无 LibreOffice 时跳过真实渲染测试）
python -m unittest discover -s tests -v
```

LibreOffice 安装示例：Debian/Ubuntu 使用 `sudo apt install libreoffice-calc`；macOS 可使用 `brew install --cask libreoffice`；Windows 安装 LibreOffice 后将其 `program` 目录加入 PATH。部分系统还需安装适当的中文字体。不是用 OfficeCLI 截图兜底：已验证其当前 Excel 渲染路径会遗漏原生连接线。

## 三种独立发行包（1.2.0）

纯 Python、OfficeCLI 辅助、LibreOffice 增强版现分别位于同级的 `excel-to-md-openpyxl`、`excel-to-md-officecli`、`excel-to-md-libreoffice`。本目录为统一开发源码，默认采用 LibreOffice 后端；生成目录通过 `variant.json` 固定各自默认值。

`--backend openpyxl|officecli|libreoffice` 可明确选择后端。纯 Python 不调用外部程序；OfficeCLI 仅调用 OfficeCLI 导出辅助 HTML（`--officecli` 可指定路径），不调用 LibreOffice，且不保证流程箭头完整；增强版才生成 LibreOffice PNG/PDF。纯 Python 和 OfficeCLI 版拒绝 `.xls`，要求先另存为 `.xlsx`。

用户安装时优先选有明确名称的独立 ZIP，具体对比见仓库 `docs/EXCEL_TO_MD_VERSIONS.md`。
