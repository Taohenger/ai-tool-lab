# Task 009: Excel 转 Markdown 验证结果

## 概要

验证 OfficeCLI 读取 Excel 设计文档中的格式信息（加粗、颜色、删除线、悬浮吹出形状、图片、公式结果）并转换为 Markdown 的能力。

**结论：OfficeCLI 完全支持读取 Excel 格式信息并转换为 Markdown，11/11 测试用例通过（100%）。**

**最新更新**：TC-011 完整设计文档测试 — 5 Sheet / 2278 单元格 / 5 图片 / 13 表格 / 16 格式类型，全部通过 ✅

### 📌 完整版本测试输出（最重要）

| 文件 | 说明 | 链接 |
|------|------|------|
| 完整设计文档测试.md | 纯净版（709 行，GitHub 兼容） | [查看](https://github.com/Taohenger/ai-tool-lab/blob/main/validations/office-cli/test-data/excel-to-md/完整设计文档测试.md) |
| 完整设计文档测试_richtext.md | 富文本版（707 行，VS Code/Typora） | [查看](https://github.com/Taohenger/ai-tool-lab/blob/main/validations/office-cli/test-data/excel-to-md/完整设计文档测试_richtext.md) |
| 完整设计文档测试.xlsx | 源文件（5 Sheet / 2278 单元格 / 5 图片） | [查看](https://github.com/Taohenger/ai-tool-lab/blob/main/validations/office-cli/test-data/excel-to-md/完整设计文档测试.xlsx) |

---

## 测试环境

| 项目 | 内容 |
|------|------|
| OfficeCLI 版本 | v1.0.143 |
| 测试文件 | `test-data/excel-to-md/设计文档测试.xlsx` |
| Sheet 数 | 2（设计说明 + UI设计说明） |
| 单元格数 | 39 |
| 吹出形状数 | 2（wedgeRectCallout） |
| 转换脚本 | `test-data/excel-to-md/excel_to_md.py` |
| 输出文件 | `test-data/excel-to-md/设计文档测试.md` |

---

## 测试用例结果

### TC-001: 创建测试设计文档 Excel ✅

使用 openpyxl 创建包含 13 种格式类型的测试文件，再用 OfficeCLI 添加 2 个吹出形状。

**格式覆盖：**
- 加粗（font.bold=true）
- 颜色（font.color=#FF0000 / #0000FF / #008000 / #808080 / #0563C1）
- 删除线（strike=true）
- 背景色（fill=#FFFF00 / #D9E1F2 / #FFF2CC）
- 斜体（font.italic=true）
- 下划线（underline=single）
- 超链接（link=URL）
- 组合格式（加粗+颜色、删除线+颜色）
- 字号映射（18pt→H1, 14pt→H3）
- 吹出形状（geometry=wedgeRectCallout）

**证据：** `tc011-view-outline.txt`

---

### TC-002: 读取加粗格式 ✅

```bash
officecli get 设计文档测试.xlsx "/设计说明/A4" --json
```

返回：
```json
{
  "format": {
    "font.bold": true
  },
  "text": "这是加粗文本"
}
```

**Markdown 映射：** `**这是加粗文本**`

---

### TC-003: 读取颜色格式 ✅

```bash
officecli get 设计文档测试.xlsx "/设计说明/A5" --json
```

返回：
```json
{
  "format": {
    "font.color": "#FF000000"
  },
  "text": "这是红色文本"
}
```

**发现：** OfficeCLI 返回的颜色格式为 **RRGGBBAA**（8位），前6位是 RGB 颜色，后2位是 Alpha 通道。转换脚本需取前6位。

**Markdown 映射：** `<span style="color:#FF0000">这是红色文本</span>`

---

### TC-004: 读取删除线格式 ✅

```bash
officecli get 设计文档测试.xlsx "/设计说明/A7" --json
```

返回：
```json
{
  "format": {
    "strike": true
  },
  "text": "这是废弃内容（删除线）"
}
```

**Markdown 映射：** `~~这是废弃内容（删除线）~~`

---

### TC-005: 读取背景色格式 ✅

```bash
officecli get 设计文档测试.xlsx "/设计说明/A8" --json
```

返回：
```json
{
  "format": {
    "fill": "#FFFF0000"
  },
  "text": "这是黄色背景的单元格"
}
```

**Markdown 映射：** `<mark>这是黄色背景的单元格</mark>`（黄色背景用 mark 标签，其他颜色用 span）

---

### TC-006: 读取悬浮吹出形状（Callout）✅

```bash
officecli query 设计文档测试.xlsx shape --json
```

返回 2 个吹出形状：
```json
[
  {
    "path": "/设计说明/shape[1]",
    "text": "注意：按钮配色需与品牌色保持一致",
    "format": {
      "geometry": "wedgeRectCallout",
      "fill": "#FFFF00",
      "color": "#FF0000",
      "bold": true
    }
  },
  {
    "path": "/设计说明/shape[2]",
    "text": "旧方案已废弃，请使用 Flex 布局",
    "format": {
      "geometry": "wedgeRectCallout",
      "fill": "#FF0000",
      "color": "#FFFFFF"
    }
  }
]
```

**Markdown 映射：**
```
> 📌 ⚠️ **注意：按钮配色需与品牌色保持一致**

> 📌 ❌ 旧方案已废弃，请使用 Flex 布局
```

**关键发现：** OfficeCLI 完整支持读取 Excel 中"插入→形状→标注"类型的悬浮吹出泡，包括：
- `geometry` — 形状类型（wedgeRectCallout = 矩形标注）
- `text` — 吹出内文字
- `fill` — 吹出背景色
- `color` — 文字颜色
- `bold` — 文字加粗
- `x/y/width/height` — 位置和尺寸

---

### TC-007: 读取超链接 ✅

```bash
officecli get 设计文档测试.xlsx "/设计说明/A11" --json
```

返回：
```json
{
  "format": {
    "link": "https://github.com/Taohenger/ai-tool-lab",
    "underline": "single",
    "font.color": "#0563C100"
  },
  "text": "GitHub 仓库"
}
```

**Markdown 映射：** `<span style="color:#0563C1"><u>[GitHub 仓库](https://github.com/Taohenger/ai-tool-lab)</u></span>`

---

### TC-008: 批量读取所有单元格 ✅

```bash
officecli query 设计文档测试.xlsx cell --json
```

返回 39 个单元格的完整格式信息（2 个 Sheet 合计）。

**证据：** `tc008-query-cell.json`

---

### TC-009: 组合格式读取 ✅

**加粗+红色：**
```json
{
  "format": {
    "font.bold": true,
    "font.color": "#FF000000"
  },
  "text": "加粗+红色组合"
}
```

**Markdown 映射：** `<span style="color:#FF0000">**加粗+红色组合**</span>`

**删除线+灰色：**
```json
{
  "format": {
    "strike": true,
    "font.color": "#80808000"
  },
  "text": "废弃+灰色删除线"
}
```

**Markdown 映射：** `<span style="color:#808080">~~废弃+灰色删除线~~</span>`

---

### TC-010: 完整 Markdown 转换 ✅

转换脚本 `excel_to_md.py` 完整运行，生成 54 行 Markdown，包含：
- 2 个 Sheet 的内容
- 加粗/颜色/删除线/背景色/斜体/下划线/超链接 全部正确转换
- 设计规格表自动识别为 Markdown 表格
- 2 个吹出形状转换为引用块
- 字号自动映射为标题级别

**输出文件：** `test-data/excel-to-md/设计文档测试.md`

---

## 最终转换结果

```markdown
<!-- 由 OfficeCLI 从 Excel 自动转换生成 -->

# 设计说明

# 设计文档格式转换测试

这是普通文本，无特殊格式

**这是加粗文本**

<span style="color:#FF0000">这是红色文本</span>

<span style="color:#0000FF">这是蓝色文本</span>

~~这是废弃内容（删除线）~~

<mark>这是黄色背景的单元格</mark>

<span style="color:#FF0000">**加粗+红色组合**</span>

<span style="color:#808080">~~废弃+灰色删除线~~</span>

<span style="color:#0563C1"><u>[GitHub 仓库](https://github.com/Taohenger/ai-tool-lab)</u></span>

*这是斜体文本*

<u>这是下划线文本</u>

### 设计规格表

| 项目 | 规格 | 状态 | 备注 |
|---|---|---|---|
| 配色方案 | #FF0000 主色 | <span style="color:#008000">**确定**</span> | 需与品牌色一致 |
| 字体大小 | 正文 12pt / 标题 18pt | <span style="color:#008000">**确定**</span> |  |
| 布局方案 | 响应式栅格 | <span style="color:#FF0000">~~废弃~~</span> | 改用 Flex 布局 |
| 交互方式 | 点击展开 | <span style="color:#008000">**确定**</span> | 参考 Material Design |

---

## 悬浮吹出形状（Callout）

> 📌 ⚠️ **注意：按钮配色需与品牌色保持一致**

> 📌 ❌ 旧方案已废弃，请使用 Flex 布局


# UI设计说明

### UI 设计规格

### 按钮样式

圆角矩形，主色填充

<span style="color:#808080">*悬停时加深 10%*</span>

<span style="color:#FF0000">~~已废弃的旧方案~~</span>

<mark><span style="color:#FF0000">**重要提醒**</span></mark>
```

---

## 核心发现

### ✅ 完全支持的能力

| 能力 | OfficeCLI 属性 | Markdown 映射 | 状态 |
|------|---------------|-------------|------|
| 加粗 | `font.bold` | `**text**` | ✅ 完美 |
| 斜体 | `font.italic` | `*text*` | ✅ 完美 |
| 删除线 | `strike` | `~~text~~` | ✅ 完美 |
| 文字颜色 | `font.color` | `<span style="color:...">` | ✅ 完美 |
| 背景色 | `fill` | `<mark>` 或 `<span style="background-color:...">` | ✅ 完美 |
| 下划线 | `underline` | `<u>text</u>` | ✅ 完美 |
| 超链接 | `link` | `[text](url)` | ✅ 完美 |
| 吹出形状 | `query shape` | `> 📌 text` | ✅ 完美 |
| 字号→标题 | `font.size` | `# / ## / ###` | ✅ 完美 |
| 组合格式 | 多属性叠加 | 嵌套标签 | ✅ 完美 |

### ⚠️ 注意事项

| 编号 | 发现 | 影响 | 应对 |
|------|------|------|------|
| 1 | 颜色返回 RRGGBBAA 格式（8位） | 低 | 转换脚本取前6位即可 |
| 2 | openpyxl 生成的 xlsx 有 schema 顺序警告 | 低 | 不影响 officecli 读取 |
| 3 | Markdown 不原生支持颜色 | 设计限制 | 使用 HTML span 标签（GitHub/VS Code 等主流渲染器支持） |
| 4 | 吹出形状的位置信息（x/y）在 md 中丢失 | 低 | 可用锚点链接替代（可选） |

---

## 通过率

| 维度 | 结果 |
|------|------|
| 测试用例 | 11/11 = **100%** |
| 格式类型 | 16 种全部正确转换 |
| 组合格式 | 4 种全部正确转换 |
| 吹出形状 | 2/2 = 100% |
| 图片提取 | 5/5 = 100%（完整设计文档） |
| 表格识别 | 13/13 = 100%（含未标记表格自动检测） |
| 公式结果 | 15/15 = 100%（PI/RAND/SUM/IF/VLOOKUP 等） |

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `tasks/009-excel-to-md/task.md` | 测试计划 |
| `test-data/excel-to-md/create_design_doc.py` | 测试 Excel 生成脚本（openpyxl） |
| `test-data/excel-to-md/设计文档测试.xlsx` | 测试设计文档（基础版，2 Sheet / 39 单元格） |
| `test-data/excel-to-md/excel_to_md.py` | Excel→Markdown 转换脚本 |
| `test-data/excel-to-md/设计文档测试.md` | 转换输出的 Markdown（基础版） |
| `test-data/excel-to-md/create_full_design_doc.py` | **完整设计文档生成脚本（5 Sheet / 100+ 行/Sheet / 图片 / 形状 / 公式）** |
| `test-data/excel-to-md/完整设计文档测试.xlsx` | **完整设计文档（5 Sheet / 2185 单元格 / 5 图片）** |
| `test-data/excel-to-md/完整设计文档测试.md` | **纯净版 Markdown（709 行，Emoji+注释标记颜色，GitHub 兼容）** |
| `test-data/excel-to-md/完整设计文档测试_richtext.md` | **富文本版 Markdown（707 行，HTML span 颜色，VS Code/Typora）** |
| `test-data/excel-to-md/images/` | **提取的 5 张图片** |
| `results/evidence/009-excel-to-md/tc002-bold.json` | 加粗读取证据 |
| `results/evidence/009-excel-to-md/tc003-color.json` | 颜色读取证据 |
| `results/evidence/009-excel-to-md/tc004-strike.json` | 删除线读取证据 |
| `results/evidence/009-excel-to-md/tc005-fill.json` | 背景色读取证据 |
| `results/evidence/009-excel-to-md/tc006-query-shape.json` | 吹出形状查询证据 |
| `results/evidence/009-excel-to-md/tc006-shape1.json` | 吹出形状1详情 |
| `results/evidence/009-excel-to-md/tc006-shape2.json` | 吹出形状2详情 |
| `results/evidence/009-excel-to-md/tc007-link.json` | 超链接读取证据 |
| `results/evidence/009-excel-to-md/tc008-query-cell.json` | 全量单元格查询 |
| `results/evidence/009-excel-to-md/tc009-bold-color.json` | 组合格式读取证据 |
| `results/evidence/009-excel-to-md/tc009-strike-color.json` | 删除线+颜色组合 |
| `results/evidence/009-excel-to-md/tc010-validate.txt` | 文件验证 |
| `results/evidence/009-excel-to-md/tc011-view-outline.txt` | outline 视图 |
| `results/evidence/009-excel-to-md/output-final.md` | 最终输出的 md |

---

## TC-011: 完整设计文档测试（全功能深度验证）✅

### 测试环境

| 项目 | 内容 |
|------|------|
| OfficeCLI 版本 | v1.0.143 |
| 测试文件 | `test-data/excel-to-md/完整设计文档测试.xlsx` |
| Sheet 数 | 5（设计总览 / UI设计规格 / 数据与公式 / 检查清单 / 图片与附件） |
| 单元格数 | 2278 |
| 图片数 | 5（UI 设计稿、UI 副本、架构图、流程图、检查清单 banner） |
| 转换脚本 | `test-data/excel-to-md/excel_to_md.py` |
| 输出（纯净版） | `test-data/excel-to-md/完整设计文档测试.md`（709 行） |
| 输出（富文本版） | `test-data/excel-to-md/完整设计文档测试_richtext.md`（707 行） |

### 测试结果：全部通过 ✅

| 验证维度 | 结果 | 详情 |
|---------|------|------|
| **图片提取** | 5/5 ✅ | image1~5 全部提取到 images/ 目录，MD 中正确引用，跨 Sheet 全局索引修复 |
| **表格识别** | 13/13 ✅ | 共 355 行数据，含未标记表格自动检测（openpyxl 预检测 + 列范围重叠算法） |
| **数值精度** | 15/15 ✅ | PI=3.14159265358979（15位）、RAND=0.05065714514315489（17位）、#DIV/0!/#N/A/#VALUE! 错误值保留 |
| **公式结果** | 15/15 ✅ | SUM=189、AVERAGE=23.625、2^10=1024、IF/IFERROR/VLOOKUP/CONCATENATE 等全部正确 |
| **格式转换** | 16/16 ✅ | 加粗/斜体/删除线/颜色/背景色/下划线/超链接/组合格式/字号→标题 全部正确 |
| **组件状态列** | 58/58 ✅ | 确定20次/废弃19次/待定19次，全部有值 |
| **文档结构** | 5/5 ✅ | 5 个 Sheet 标题齐全 |

### 13 个识别的表格

| # | 表格名 | 列×行 | 所属 Sheet |
|---|--------|-------|-----------|
| 1 | 文档信息表 | 2×6 | 设计总览 |
| 2 | 修订记录 | 4×15 | 设计总览 |
| 3 | 术语定义 | 3×43 | 设计总览 |
| 4 | 页面布局规格 | 8×37 | UI设计规格 |
| 5 | 组件规格表 | 9×58 | UI设计规格 |
| 6 | 基础运算 | 6×27 | 数据与公式 |
| 7 | 逻辑函数 | 6×23 | 数据与公式 |
| 8 | 查找引用 | 6×23 | 数据与公式 |
| 9 | 文本函数 | 6×13 | 数据与公式 |
| 10 | 代码检查清单 | 7×98 | 检查清单 |
| 11 | UI 设计稿 | 2×2 | 图片与附件 |
| 12 | 架构图 | 2×4 | 图片与附件 |
| 13 | 流程图 | 2×6 | 图片与附件 |

### 关键技术发现

1. **OfficeCLI 公式结果读取**：`query cell --json` 返回的 `text` 字段包含公式计算结果（如 PI=3.14159265358979），精度完整保留
2. **表格自动检测算法**：基于 openpyxl 读取完整网格结构，通过列范围重叠检测、列数差异控制（≤2）、间隔行允许等策略，成功识别未标记的表格区域
3. **图片跨 Sheet 全局索引**：`xl/media/imageN.png` 的编号是全局递增的，跨 Sheet 遍历 picture 时必须使用同一全局计数器
4. **双版本输出**：纯净版用 Emoji+注释标记颜色（GitHub 兼容），富文本版用 HTML span 标签（VS Code/Typora/Obsidian 专用）

### 修复记录

| 问题 | 原因 | 修复 |
|------|------|------|
| 图片未提取 | OfficeCLI 未安装，fallback 到 openpyxl 模式不读取图片 | 安装 OfficeCLI v1.0.143 |
| 公式结果为空 | openpyxl `data_only=True` 读取公式单元格返回 None（Excel 未缓存计算结果） | OfficeCLI `query cell --json` 返回完整计算结果 |
| 图片索引错位 | 每个 Sheet 从 1 开始编号，但 imageN.png 是全局递增 | `build_document()` 中使用 `global_pic_idx` 全局计数器 |
