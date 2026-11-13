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
