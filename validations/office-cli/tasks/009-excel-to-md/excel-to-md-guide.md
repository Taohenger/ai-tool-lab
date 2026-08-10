# Excel 转 Markdown 手顺书

> 面向非开发者：如何不依赖任何 AI Agent，仅用 OfficeCLI + 基础 Python，实现 Excel 设计文档转 Markdown。

---

## 一、整体思路

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Excel 文件  │ ──→ │  OfficeCLI 读取   │ ──→ │  JSON 数据  │
│  (设计文档)  │     │  (格式+内容)       │     │  (结构化)    │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                    │
                    ┌──────────────────┐             │
                    │  Python 映射脚本  │ ←───────────┘
                    │  (JSON → MD)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  output.md        │
                    │  (最终 Markdown)   │
                    └──────────────────┘
```

**核心分工：**
- **OfficeCLI**：负责读取 Excel 的内容和格式（这是它能做的）
- **Python**：负责把 JSON 格式数据"翻译"成 Markdown 语法（OfficeCLI 不做这件事）
- **AI**：帮你写那个 Python 映射脚本（一次性工作，写完就能复用）

---

## 二、前提准备

### 2.1 安装 OfficeCLI

```bash
# 一键安装（Linux / Mac）
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash

# 验证
officecli version
```

### 2.2 确认 Python 环境

```bash
python3 --version    # 需要 3.8+
pip install openpyxl  # 仅在需要创建测试 Excel 时用到
```

### 2.3 准备你的 Excel 设计文档

将你要转换的 Excel 文件放在工作目录，例如：
```
~/my-project/
├── 设计文档.xlsx      ← 你的设计文档
└── (即将生成的脚本和输出也放这里)
```

---

## 三、OfficeCLI 命令详解（核心能力）

### 3.1 查看文件结构

```bash
# 查看所有 Sheet 和大致内容
officecli view 设计文档.xlsx outline
```

输出示例：
```
Sheet1: 设计说明
  A1: 设计文档格式转换测试
  A4: 这是加粗文本
  A5: 这是红色文本
  ...
Sheet2: UI设计说明
  A1: UI 设计规格
  ...
```

### 3.2 扫描所有有内容的单元格

```bash
# 列出所有非空单元格的路径
officecli query 设计文档.xlsx cell --json
```

输出 JSON 示例：
```json
{
  "success": true,
  "data": {
    "results": [
      {"path": "/设计说明/A1", "text": "设计文档格式转换测试"},
      {"path": "/设计说明/A4", "text": "这是加粗文本"},
      {"path": "/设计说明/A5", "text": "这是红色文本"}
    ]
  }
}
```

### 3.3 读取单个单元格的完整格式（关键命令）

```bash
# 读取 A4 单元格的格式信息
officecli get 设计文档.xlsx "/设计说明/A4" --json
```

输出 JSON 示例：
```json
{
  "success": true,
  "data": {
    "path": "/设计说明/A4",
    "text": "这是加粗文本",
    "format": {
      "font.bold": true,
      "font.italic": false,
      "font.color": "#00000000",
      "font.size": "11pt",
      "strike": false,
      "underline": "none",
      "fill": "none",
      "link": ""
    }
  }
}
```

**这就是核心：`format` 字段包含了所有格式信息。**

### 3.4 读取悬浮吹出形状（Callout）

```bash
# 列出所有形状
officecli query 设计文档.xlsx shape --json
```

输出 JSON 示例：
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "path": "/设计说明/shape[1]",
        "text": "注意：按钮配色需与品牌色保持一致",
        "format": {
          "geometry": "wedgeRectCallout",
          "fill": "#FFFF00",
          "color": "#FF0000",
          "bold": true
        }
      }
    ]
  }
}
```

### 3.5 验证文件完整性

```bash
officecli validate 设计文档.xlsx
```

---

## 四、格式映射规则（Excel → Markdown）

### 4.1 对照表

| Excel 属性（OfficeCLI 返回） | 含义 | Markdown 输出 |
|------|------|------|
| `font.bold: true` | 加粗 | `**文本**` |
| `font.italic: true` | 斜体 | `*文本*` |
| `strike: true` | 删除线 | `~~文本~~` |
| `font.color: #FF0000` | 文字颜色 | `<span style="color:#FF0000">文本</span>` |
| `fill: #FFFF00` | 背景色 | `<mark>文本</mark>`（黄色）或 `<span style="background-color:#RRGGBB">` |
| `underline: single` | 下划线 | `<u>文本</u>` |
| `link: https://...` | 超链接 | `[文本](URL)` |
| `font.size >= 18pt` | 大字号 | `# 文本`（H1） |
| `font.size >= 14pt` | 中字号 | `## 文本`（H2） |
| shape `geometry: *Callout` | 吹出形状 | `> 📌 文本` |

### 4.2 颜色格式注意事项

OfficeCLI 返回的颜色是 **RRGGBBAA** 格式（8位），前 6 位是 RGB 颜色，后 2 位是透明度（Alpha）。

```python
# 正确取法：取前 6 位
color = "#FF0000"  # ✅ 正确（红色）
# 不要取后 6 位
color = "#0000FF"  # ❌ 错误（变成了蓝色）
```

### 4.3 组合格式处理顺序

当一个单元格同时有多个格式时，按以下顺序嵌套：

```
1. 超链接  →  [文本](URL)
2. 加粗    →  **文本**
3. 删除线  →  ~~文本~~
4. 斜体    →  *文本*
5. 下划线  →  <u>文本</u>
6. 颜色    →  <span style="color:...">文本</span>
7. 背景色  →  <mark>文本</mark>
```

---

## 五、用 AI 写 Python 映射脚本（一次性工作）

### 5.1 为什么要 Python？

OfficeCLI 能读出 JSON，但不会帮你把 `font.bold: true` 拼成 `**文本**`。这个"翻译"逻辑需要一个脚本。

**你不需要自己写这个脚本** —— 让 AI 帮你写，你只需要把映射规则告诉 AI。

### 5.2 给 AI 的 Prompt 模板

把以下 Prompt 复制给任意 AI（Claude / GPT / Trae 都行），替换文件名即可：

```
请帮我写一个 Python 脚本，用 OfficeCLI 读取 Excel 并转换为 Markdown。

## 要求

1. 调用 officecli 命令读取 Excel 格式信息
2. 把格式映射为 Markdown

## 映射规则

- font.bold=true → **文本**
- font.italic=true → *文本*
- strike=true → ~~文本~~
- font.color=#RRGGBB → <span style="color:#RRGGBB">文本</span>（注意返回是 RRGGBBAA 8位，取前6位）
- fill=#FFFF00 → <mark>文本</mark>
- underline=single → <u>文本</u>
- link=URL → [文本](URL)
- font.size>=18pt → # 标题
- font.size>=14pt → ## 标题
- shape(geometry=*Callout) → > 📌 文本

## OfficeCLI 命令

- 扫描单元格: officecli query 文件名.xlsx cell --json
- 读单元格格式: officecli get 文件名.xlsx /Sheet1/A1 --json
- 扫描吹出形状: officecli query 文件名.xlsx shape --json

## 输入

Excel 文件路径作为参数传入

## 输出

同目录下生成 .md 文件
```

AI 会生成一个类似 `excel_to_md.py` 的脚本。

### 5.3 运行脚本

```bash
# 确保 officecli 在 PATH 中
export PATH="$HOME/.local/bin:$PATH"

# 运行
python3 excel_to_md.py

# 或指定文件
python3 excel_to_md.py 你的文件.xlsx
```

### 5.4 验证输出

```bash
# 查看生成的 Markdown
cat 设计文档.md
```

---

## 六、是否需要 Skill？

### 结论：不需要 Skill

| 方案 | 需要 Skill？ | 优点 | 缺点 |
|------|:---:|------|------|
| **纯命令行** | ❌ | 最简单，任何人都能用 | 需要手动执行多条命令 |
| **Python 脚本** | ❌ | 自动化，可复用 | 需要一次性写脚本 |
| **封装为 Skill** | ✅ | 一键调用 | 过度封装，无额外价值 |

**原因：**
1. OfficeCLI 本身就是命令行工具，不需要额外封装
2. Python 映射脚本写好后直接 `python3 excel_to_md.py` 就能跑
3. Skill 适合"多步骤编排"场景（如：先查飞书日历→再创建任务→发通知），而本场景只有"读 Excel → 写 MD"两步

### 什么时候才需要 Skill？

如果你要做一个**自动化流水线**，比如：
```
飞书下载 Excel → OfficeCLI 读取 → 生成 MD → 自动发飞书消息通知
```

这种跨系统、多步骤的场景才值得封装为 Skill。单纯的 Excel→MD 不需要。

---

## 七、完整操作流程（Step by Step）

### Step 1: 安装 OfficeCLI

```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
officecli version
```

### Step 2: 准备工作目录

```bash
mkdir -p ~/excel-to-md && cd ~/excel-to-md
# 把你的 Excel 文件放进来
cp ~/Downloads/设计文档.xlsx .
```

### Step 3: 用 OfficeCLI 查看文件结构

```bash
# 看看有哪些 Sheet
officecli view 设计文档.xlsx outline
```

### Step 4: 扫描所有单元格

```bash
# 获取所有非空单元格列表
officecli query 设计文档.xlsx cell --json > cells.json
```

### Step 5: 读取格式信息（抽样验证）

```bash
# 抽查几个关键单元格
officecli get 设计文档.xlsx "/Sheet1/A1" --json
officecli get 设计文档.xlsx "/Sheet1/A4" --json
officecli get 设计文档.xlsx "/Sheet1/A7" --json
```

### Step 6: 读取吹出形状（如果有）

```bash
officecli query 设计文档.xlsx shape --json
```

### Step 7: 让 AI 写映射脚本

把第四章的 Prompt 模板发给 AI，获得 `excel_to_md.py` 脚本。

### Step 8: 运行脚本生成 Markdown

```bash
python3 excel_to_md.py
```

### Step 9: 检查输出

```bash
cat 设计文档.md
```

### Step 10: （可选）调整映射规则

如果某些格式转换不对，修改 `excel_to_md.py` 中的映射函数后重新运行。

---

## 八、常见问题

### Q1: 颜色不对？

OfficeCLI 返回的颜色是 **RRGGBBAA**（8位），取前 6 位是 RGB 颜色。

```python
# 错误：取了后 6 位
color = color_str[-6:]  # ❌

# 正确：取前 6 位
color = "#" + color_str.lstrip("#")[:6]  # ✅
```

### Q2: 吹出形状读不到？

确认形状是"插入 → 形状 → 标注"类型，不是"批注"（右键插入批注）。

```bash
# 查看所有 shape
officecli query 设计文档.xlsx shape --json

# 如果返回空列表，说明文件里没有形状
```

### Q3: Markdown 渲染器不支持颜色？

Markdown 原生不支持颜色。`<span style="color:...">` 是 HTML 标签，在以下渲染器中支持：
- ✅ VS Code 预览
- ✅ Typora
- ✅ Obsidian
- ❌ GitHub（不支持 HTML span 标签的颜色样式）

如果在 GitHub 上使用，可以考虑去掉颜色，只保留加粗/删除线等纯 Markdown 格式。

### Q4: 一个单元格内有混合格式（富文本）怎么办？

OfficeCLI 会返回 `type=richtext` 和 `runs` 数组，每段文本有独立的格式。需要在脚本中遍历 `runs` 数组逐段转换。

### Q5: 是否支持 Word/PPT 转 Markdown？

OfficeCLI 也支持 Word 和 PPT 读取，但格式映射规则不同。本手顺仅覆盖 Excel。

---

## 九、总结

| 角色 | 职责 | 是否必须 |
|------|------|:---:|
| OfficeCLI | 读取 Excel 内容和格式，返回 JSON | ✅ 必须 |
| Python 脚本 | 把 JSON 映射为 Markdown 语法 | ✅ 必须（但 AI 帮你写） |
| AI | 帮你写 Python 映射脚本 | 一次性，写完不需要了 |
| Skill | 封装多步骤编排 | ❌ 本场景不需要 |
| openpyxl | 创建测试 Excel | ❌ 只有准备测试数据时用到 |

**一句话总结：OfficeCLI 读 Excel，AI 帮你写翻译脚本，跑一次就出 Markdown。**
