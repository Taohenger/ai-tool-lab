---
name: "excel-to-md-libreoffice"
description: "Excel 转 Markdown：LibreOffice 增强版。用 LibreOffice 在临时副本上渲染整表 PDF，由 PyMuPDF 生成 PNG 并嵌入 Markdown；同时保留明确的流程连接关系。SmartArt、字体和复杂排版仍可能有差异。"
---

# Excel 转 Markdown — LibreOffice 增强版

版本：1.2.0；默认后端：`libreoffice`。

依赖：Python 3.10+、openpyxl、Pillow、PyMuPDF，另装 LibreOffice 并加入 PATH。

用 LibreOffice 在临时副本上渲染整表 PDF，由 PyMuPDF 生成 PNG 并嵌入 Markdown；同时保留明确的流程连接关系。SmartArt、字体和复杂排版仍可能有差异。

## 安装和运行

将整个 `excel-to-md-libreoffice` 目录放到工程 `.trae/skills/`，以下命令从工程根目录运行。不要复制其他电脑的 .venv。

Linux/macOS：
```bash
bash .trae/skills/excel-to-md-libreoffice/scripts/install.sh
.trae/skills/excel-to-md-libreoffice/.venv/bin/python .trae/skills/excel-to-md-libreoffice/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

Windows PowerShell：
```powershell
powershell -ExecutionPolicy Bypass -File .trae/skills/excel-to-md-libreoffice/scripts/install.ps1
& .trae/skills/excel-to-md-libreoffice/.venv/Scripts/python.exe .trae/skills/excel-to-md-libreoffice/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

外部工具安装：OfficeCLI 版请安装官方 OfficeCLI（https://github.com/iOfficeAI/OfficeCLI），也可用 `--officecli /路径/officecli` 指定程序；LibreOffice 版请安装 LibreOffice（https://www.libreoffice.org/），并把 `soffice` 或 `libreoffice` 加入 PATH。纯 Python 版不需要二者。

## 验收要求

必须实际执行转换，检查 conversion-report.json 的 backend、totals、drawings、warnings，再检查 Markdown 和全部 assets 链接。OfficeCLI 成功导出状态是 auxiliary，不能报告成已完整还原流程图；缺失外部工具或转换失败都必须告知用户。

每个版本均保留原图、格式和公式表达式；无缓存公式明确标记，不猜结果。只有文件中两端唯一对应到节点的连接才可输出，不按位置推断业务流程。绘图相关输出附原始工作簿副本，源文件只读。Markdown、assets、报告必须整体携带。

LibreOffice 版可加 `--diagram-render required`，绘图预览失败时返回非零；OfficeCLI 辅助预览不满足这一完整绘图预览要求。`--diagram-render never` 禁止外部预览。

跨平台说明：本次实测 Linux；Windows/macOS 尚未实测。离线 wheels 安装器仍有升级 pip 的联网步骤，不能无条件承诺断网安装。复杂图表、SmartArt、布局和公式计算不是无损迁移；LibreOffice 预览可能重算公式，Markdown 公式缓存仍以原文件或 --values-from 为准。

## 测试

安装后在本 Skill 目录运行 `python -m unittest discover -s tests -v`。真实外部工具测试按本机依赖可用情况跳过；`OFFICECLI_TEST` 可指定 OfficeCLI 二进制来启用真实辅助导出测试。测试会显式选择所验证的后端，不代表当前变体运行时会调用其他后端。

这些目录由 `scripts/build_excel_variants.py` 从统一源码生成，请修改统一源码后重新生成，避免各版本代码漂移。
