# Excel 转 Markdown Skill 跨电脑交接与验证

本文用于把已经完成的工作交给另一台电脑或另一个 AI 复验。目标是实际安装 Skill、运行测试、转换样例 Excel，并核对 Markdown 的内容、格式和真实图片，而不是只检查文件是否存在。

## 1. 已交付内容

| 内容 | 仓库路径 |
|---|---|
| 可迁移 Skill | `.trae/skills/excel-to-md/` |
| Skill 使用说明 | `.trae/skills/excel-to-md/SKILL.md` |
| 核心转换器 | `.trae/skills/excel-to-md/scripts/excel_to_md.py` |
| Windows / Linux 安装器 | `.trae/skills/excel-to-md/scripts/install.ps1`、`install.sh` |
| 自动化测试 | `.trae/skills/excel-to-md/tests/test_excel_to_md.py` |
| 完整测试 Excel | `validations/office-cli/test-data/excel-to-md/完整设计文档测试.xlsx` |
| 已生成的最终 Markdown | `完整设计文档测试-markdown/` |
| 最终 Markdown 交付包 | `完整设计文档测试-markdown.zip` |
| Skill 独立压缩包 | `excel-to-md-skill.zip` |

当前 Skill 不依赖 OfficeCLI。openpyxl 负责单元格和工作表，Python 直接读取 OOXML 中的图片、形状及其关系。

## 2. 环境要求

- Python 3.10 或更高版本。
- 首次在线安装需要访问 Python 包源；离线安装见第 6 节。
- LibreOffice 仅用于 `.xls` 转换或可选的公式重算，普通 `.xlsx` 转换不强制要求。
- 不需要 OfficeCLI，不需要管理员权限。

支持 `.xlsx`、`.xlsm`、`.xltx`、`.xltm`。`.xlsb` 需先另存为 `.xlsx`，密码加密文件需先解密。

## 3. 获取仓库

```bash
git clone https://github.com/Taohenger/ai-tool-lab.git
cd ai-tool-lab
```

以下命令均在仓库根目录执行。

## 4. 安装并运行自动化测试

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .trae\skills\excel-to-md\scripts\install.ps1
& .trae\skills\excel-to-md\.venv\Scripts\python.exe .trae\skills\excel-to-md\tests\test_excel_to_md.py
```

### Linux / macOS

```bash
bash .trae/skills/excel-to-md/scripts/install.sh
.trae/skills/excel-to-md/.venv/bin/python .trae/skills/excel-to-md/tests/test_excel_to_md.py
```

预期看到 `测试通过`。安装器只在 Skill 内创建 `.venv`，不会修改系统 Python。

## 5. 实际转换完整样例

Windows PowerShell：

```powershell
& .trae\skills\excel-to-md\.venv\Scripts\python.exe .trae\skills\excel-to-md\scripts\excel_to_md.py "validations\office-cli\test-data\excel-to-md\完整设计文档测试.xlsx" -o "verification-output" --flavor both
```

Linux / macOS：

```bash
.trae/skills/excel-to-md/.venv/bin/python .trae/skills/excel-to-md/scripts/excel_to_md.py "validations/office-cli/test-data/excel-to-md/完整设计文档测试.xlsx" -o "verification-output" --flavor both
```

预期输出：

```text
verification-output/
├── 完整设计文档测试.md
├── 完整设计文档测试_richtext.md
├── conversion-report.json
└── assets/
```

## 6. 验收清单

另一个 AI 必须实际核对以下项目，并记录结果：

| 检查项 | 完整样例预期 |
|---|---|
| 工作表 | 5 个，名称和顺序与源文件一致 |
| 非空单元格 | 2278 个 |
| 自动识别表格 | 13 张 |
| 真实图片 | 5 张；Markdown 引用路径存在，图片可打开，不是文字占位 |
| 形状 | 5 个，其中 3 个吹出泡、2 个矩形/红框 |
| 公式 | 93 个公式表达式完整保留 |
| 删除线 | 存在 `~~这是删除线文本~~` 等删除线内容 |
| 背景色和文字色 | 富文本版含 `<mark>`、`background-color`、`color`；纯净版使用文本标记降级 |
| 表格结构 | 每行按真实列号对齐，不错位，无孤立的竖线行 |
| 资源完整性 | `assets/` 与 Markdown 一起移动后，所有相对图片链接仍有效 |
| 源文件保护 | 转换前后源 Excel 的哈希不变 |

建议先查看 `_richtext.md` 验证视觉格式，再查看纯净版验证 GitHub 兼容性。`conversion-report.json` 中的统计和警告必须纳入验收结论。

## 7. 公式缓存结果说明

原完整样例的 93 个公式没有缓存结果。直接转换时保留公式并标记“无缓存结果”，这是预期行为，不应被误判为转换失败。

若需要同时展示计算结果，先在 Excel 中对副本重新计算并保存，然后执行：

```bash
python .trae/skills/excel-to-md/scripts/excel_to_md.py "原始.xlsx" --values-from "重算副本.xlsx" -o "输出目录" --flavor both
```

`--values-from` 只从重算副本读取单元格结果，正文结构、格式、公式表达式、图片和形状仍来自原始工作簿。重算副本必须与原始工作簿具有相同的工作表和单元格布局。

LibreOffice 与 Excel 的函数兼容性不完全相同，例如 `IFS` 可能在 LibreOffice 中显示 `#NAME?`。这种结果必须作为重算工具限制写入验收报告，不能当作源文件的原始缓存值。

## 8. 转换自己的 Excel

```bash
python .trae/skills/excel-to-md/scripts/excel_to_md.py "你的文件.xlsx" -o "你的文件-markdown" --flavor both
```

默认也会生成源文件旁的 `<文件名>-markdown` 目录。交付时必须包含 Markdown、`assets/` 和 `conversion-report.json`，不能只复制 MD 文件。

## 9. 离线迁移

在联网机器上，使用与离线目标机器相同的操作系统、CPU 架构和 Python 版本下载依赖：

```bash
python -m pip download -r .trae/skills/excel-to-md/requirements.txt -d .trae/skills/excel-to-md/wheels
```

将整个 `excel-to-md` 目录复制到离线机器的 `.trae/skills/` 下，再运行对应安装器。检测到 `wheels/` 时，安装器自动使用本地包，不访问网络。

也可以直接携带仓库根目录的 `excel-to-md-skill.zip`，解压后按上述目录放置。

## 10. 已知边界

- Markdown 无法像素级重绘 Excel 图表、数据透视图、SmartArt 和复杂排版；对应数据区域、附件或警告会保留。
- 转换器不是完整公式计算引擎；没有缓存结果时不会自行猜测。
- 复杂条件格式、数据验证和工作簿逻辑不会全部变成 Markdown 正文。
- 纯净版为了 GitHub 兼容，会将部分颜色样式降级为文字标记；需要颜色时请查看富文本版。

因此验收目标应是“内容尽可能完整、图片真实可用、无法转换的内容有明确警告”，不能无条件宣称任意 Excel 都能 100% 视觉还原。

## 11. 可直接交给另一个 AI 的指令

```text
请克隆 https://github.com/Taohenger/ai-tool-lab，阅读 docs/EXCEL_TO_MD_HANDOFF.md，并在当前电脑实际执行安装、自动化测试和完整样例转换。不要只检查文件存在。请核对工作表数、非空单元格数、表格数、真实图片、吹出泡、删除线、背景色和公式，检查 conversion-report.json 的全部警告，并验证图片相对链接。最后报告操作系统、Python 版本、实际执行命令、通过项、失败项和限制。不要修改源 Excel。
```

## 12. 可编辑流程图增强（1.1.0）

新增 `scripts/flowcharts.py` 和 PyMuPDF 依赖；迁移时请携带整个 Skill，不要仅替换主脚本。

转换默认会为包含绘图对象的工作表尝试生成 `assets/sheetNN-drawing.png`、`assets/drawing-preview.pdf`，并附 `assets/original-workbook.*` 源文件副本。Markdown 直接展示预览图，随后列出能够从 OOXML 端点 ID 确认的连接关系。源文件仍只读。

图形渲染需要目标电脑额外安装 LibreOffice，并使 `soffice` 或 `libreoffice` 可从 PATH 调用。只有 Python 和 Skill 依赖时，仍能完成单元格、原图提取及明确连接关系的转换，但缺失绘图预览必须告警。可用 `--diagram-render required` 将缺失或失败的预览视为命令失败，防止把不完整流程图误当成功。

`conversion-report.json` 新增 `drawings[]`：每张表的节点、连接线起止 ID、方向、端点是否解析、渲染状态、PNG/PDF/原始工作簿相对路径。状态 `rendered` 只说明输出了预览；不能证明 SmartArt 或复杂版式已像素级还原。LibreOffice 可能重算截图中的公式，正文仍保留原文件缓存状态，不能将截图数值当原始缓存。

完整样例原有的 5 张图片统计不变；新增绘图预览另外记录在 `drawings[]`，因此 Markdown 中图片引用数可能大于 5。验证相对链接时也须检查 PDF 和原始工作簿附件。运行全部测试：

```bash
.trae/skills/excel-to-md/.venv/bin/python -m unittest discover -s .trae/skills/excel-to-md/tests -v
```
