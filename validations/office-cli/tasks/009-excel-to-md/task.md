# Task 009: Excel 转 Markdown 验证

## 概述

验证 OfficeCLI 读取 Excel 设计文档中的格式信息（加粗、颜色、删除线、悬浮吹出形状）并转换为 Markdown 的能力。

## 背景

设计师产出的 Excel 设计文档通常包含丰富的格式信息：
- **加粗** — 强调重要内容
- **颜色** — 标注优先级或分类
- **删除线** — 标记废弃内容
- **悬浮吹出泡**（插入 → 形状 → 标注/Callout）— 补充说明或评审意见

将这些格式信息完整转换为 Markdown，是实现"设计文档自动化转换"的关键环节。

## 测试用例

### TC-001: 创建测试设计文档 Excel
- 使用 openpyxl 创建包含以下格式的设计文档：
  - 加粗文本（font.bold=true）
  - 彩色文本（font.color=#FF0000）
  - 删除线文本（strike=true）
  - 带背景色的单元格（fill=#FFFF00）
  - 悬浮吹出形状（shape, geometry=wedgeRectCallout）
  - 超链接
- 验证文件创建成功

### TC-002: 读取单元格格式 — 加粗
- `officecli get design.xlsx /Sheet1/A1 --json`
- 确认返回 `font.bold: true`
- 转换为 `**文本**`

### TC-003: 读取单元格格式 — 颜色
- `officecli get design.xlsx /Sheet1/A2 --json`
- 确认返回 `font.color: #FF0000`
- 转换为 `<span style="color:#FF0000">文本</span>`

### TC-004: 读取单元格格式 — 删除线
- `officecli get design.xlsx /Sheet1/A3 --json`
- 确认返回 `strike: true`
- 转换为 `~~文本~~`

### TC-005: 读取单元格格式 — 背景色
- `officecli get design.xlsx /Sheet1/A4 --json`
- 确认返回 `fill: #FFFF00`
- 转换为 `<mark>文本</mark>`

### TC-006: 读取悬浮吹出形状（Shape/Callout）
- `officecli query design.xlsx shape --json`
- 确认返回 shape 列表，包含 text/geometry/fill/color
- `officecli get design.xlsx /Sheet1/shape[1] --json`
- 确认返回吹出形状的完整属性
- 转换为 `> 📌 吹出内容`（引用块）

### TC-007: 读取超链接
- `officecli get design.xlsx /Sheet1/A5 --json`
- 确认返回 `link: https://...`
- 转换为 `[文本](URL)`

### TC-008: 批量读取所有单元格
- `officecli query design.xlsx cell --json`
- 确认返回所有有内容的单元格列表

### TC-009: 完整 Markdown 转换
- 编写转换脚本，将所有格式信息映射为 Markdown
- 验证生成的 .md 文件内容正确

### TC-010: 验证文件完整性
- `officecli validate design.xlsx`
- 确认文件无损坏

## 格式映射规则

| Excel 属性 | OfficeCLI 读取字段 | Markdown 输出 |
|-----------|-------------------|-------------|
| font.bold=true | `get` → `font.bold` | `**文本**` |
| font.italic=true | `get` → `font.italic` | `*文本*` |
| strike=true | `get` → `strike` | `~~文本~~` |
| font.color=#RRGGBB | `get` → `font.color` | `<span style="color:#RRGGBB">文本</span>` |
| fill=#RRGGBB | `get` → `fill` | `<mark>文本</mark>` |
| underline=single | `get` → `underline` | `<u>文本</u>` |
| link=URL | `get` → `link` | `[文本](URL)` |
| shape (callout) | `query shape` → `text` | `> 📌 {text}` |
| font.size>=18pt | `get` → `font.size` | `# 标题` |
| font.size>=14pt | `get` → `font.size` | `## 标题` |

## 验证标准

- 每个 TC 输出 officecli 命令执行结果（保存到 evidence 目录）
- 最终生成的 .md 文件需人工确认格式正确
- 所有测试用例通过率 ≥ 90%
