# Excel 转 Markdown：三个可独立安装的版本

三种版本统一为 1.2.0，共享经过测试的转换核心，分别打包为独立 Skill。根据目标电脑可安装的软件选择；不需要同时安装三个版本。

| 版本 | Python 依赖 | 额外程序 | 可编辑流程图的处理 | 独立下载 |
|---|---|---|---|---|
| **纯 Python / openpyxl** | openpyxl、Pillow | 无 | 提取框内文字和源文件明确记录的连接关系；不生成整图预览 | [excel-to-md-openpyxl.zip](../releases/excel-to-md/excel-to-md-openpyxl.zip) |
| **OfficeCLI 辅助版** | openpyxl、Pillow | OfficeCLI | 实际调用 OfficeCLI 导出辅助 HTML；箭头、组合图形可能遗漏，不能视为完整流程图 | [excel-to-md-officecli.zip](../releases/excel-to-md/excel-to-md-officecli.zip) |
| **LibreOffice 增强版** | openpyxl、Pillow、PyMuPDF | LibreOffice | 整表 PNG + 可放大的 PDF，并提取明确连接关系；适合设计师交付的可编辑流程图 | [excel-to-md-libreoffice.zip](../releases/excel-to-md/excel-to-md-libreoffice.zip) |

三个版本均支持单元格、表格、混合删除线、文字色和背景色、真实嵌入图片、公式表达式、批注及形状文字。源文件只读。没有公式缓存时如实标记，不编造结果。纯净版的部分颜色使用文字标记，富文本版使用 HTML/CSS。

**选择建议：** 只处理表格与已插入的图片，选纯 Python 版；已有 OfficeCLI 且想要辅助网页预览，选 OfficeCLI 版；要在 Markdown 中看到可编辑流程图的整图，选 LibreOffice 增强版。OfficeCLI 辅助版没有调用 LibreOffice，也不是增强版的自动替代品。

## 源码目录

- [纯 Python Skill](../.trae/skills/excel-to-md-openpyxl/SKILL.md)
- [OfficeCLI Skill](../.trae/skills/excel-to-md-officecli/SKILL.md)
- [LibreOffice Skill](../.trae/skills/excel-to-md-libreoffice/SKILL.md)

每个 ZIP 包含该版本的完整脚本、依赖清单、Windows/Linux/macOS 安装器和测试，不依赖其他变体目录或仓库其他源码。ZIP 不含 Python、外部程序、`.venv` 或离线依赖包。

## 安装与运行

解压所选 ZIP，将其中的 `excel-to-md-版本名` 文件夹放到工程的 `.trae/skills/` 下。下面以纯 Python 版举例；其他版本替换目录名。

```bash
bash .trae/skills/excel-to-md-openpyxl/scripts/install.sh
.trae/skills/excel-to-md-openpyxl/.venv/bin/python \
  .trae/skills/excel-to-md-openpyxl/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .trae/skills/excel-to-md-openpyxl/scripts/install.ps1
& .trae/skills/excel-to-md-openpyxl/.venv/Scripts/python.exe .trae/skills/excel-to-md-openpyxl/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

OfficeCLI 版另需安装 [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)，并加入 PATH；也可追加 `--officecli /完整路径/officecli`。

LibreOffice 版另需安装 [LibreOffice](https://www.libreoffice.org/)，确保 `libreoffice` 或 `soffice` 位于 PATH。Windows 可将安装目录中的 `program` 文件夹加入 PATH；macOS 可配置 `/Applications/LibreOffice.app/Contents/MacOS`；Debian/Ubuntu 可安装 `libreoffice-calc`。必要时安装中文字体。

LibreOffice 版可追加 `--diagram-render required`：有绘图却未生成预览时返回非零，报告和原文件副本仍保留。OfficeCLI 的辅助 HTML 不满足这一完整预览要求。默认 auto 将缺少外部工具记录为警告；`--diagram-render never` 可明确禁用外部预览。

原生支持 `.xlsx/.xlsm/.xltx/.xltm`。纯 Python 和 OfficeCLI 版拒绝旧 `.xls`，要求先另存为 `.xlsx`，不会暗中调用 LibreOffice。只有 LibreOffice 版支持临时转换 `.xls`。`.xlsb` 需另存，密码加密文件需先解密。

## 已执行的验证

- 后端/流程图/原有综合测试共 13 项；设置 `OFFICECLI_TEST` 实际调用 OfficeCLI，包含真实 LibreOffice 渲染。
- 纯 Python 独立包在全新环境测试，仅安装其 requirements，无 PyMuPDF；外部依赖相关测试按条件跳过。
- 打包测试验证三个 ZIP 均可独立解压运行、默认后端与依赖正确、相同源码重建字节一致。
- 三版均实际转换原完整样例：5 表、2278 非空单元格、13 自动表格、5 原图片、5 形状、93 公式；源 SHA256 不变，全部 Markdown 本地资产引用有效。
- [逐版统计、状态、警告和执行命令](../releases/excel-to-md/verification.json)；[自动化测试日志](../releases/excel-to-md/test-results.txt)；[包 SHA256](../releases/excel-to-md/manifest.json)。

仅实测当前 Linux 环境；不宣称 Windows/macOS 已验证。安装器的 pip 升级步骤仍可能联网，不能直接承诺完全离线安装。

## 不能保证的内容

没有节点 ID 的普通线条不能可靠推断业务流程，SmartArt 的语义连接仍不保证解析。LibreOffice 预览可能改变字体、排版、SmartArt 或重算公式；正文公式缓存仍来自原文件或显式指定的 `--values-from`。因此报告中的 rendered 仅代表成功生成预览，不表示与 Excel 完全一致。

有绘图的输出保留 `assets/original-workbook.*` 作为原件副本。请整体交付 Markdown、assets 和 conversion-report.json。

## 维护与重建

统一源码在 `.trae/skills/excel-to-md/`。修改统一源码后运行：

```bash
python scripts/build_excel_variants.py
python -m unittest discover -s tests -p test_excel_variant_packages.py -v
```

构建器生成三个变体目录和 `releases/excel-to-md/` 下的 ZIP、SHA256 清单。不要手工修改生成目录，以免重建时被覆盖。原有根目录 `excel-to-md-skill.zip` 继续提供统一增强版，推荐新用户使用上述有明确名称的三个包。
