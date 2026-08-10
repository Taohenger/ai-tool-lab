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

#### Windows 64 位（推荐）

**方式 1：PowerShell 一键安装（推荐，自动配置 PATH）**
```powershell
# 在 PowerShell 中执行
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
```
脚本会自动：下载 exe → 放到 `%LOCALAPPDATA%\OfficeCLI\` → 添加到 PATH → 安装 AI Agent Skill

**方式 2：手动下载**
1. 访问 https://github.com/iOfficeAI/OfficeCLI/releases/latest
2. 下载 **`officecli-win-x64.exe`**（31.8 MB，单个 exe 文件，不是 zip）
3. 重命名为 `officecli.exe`
4. 放到固定目录，例如 `C:\Tools\officecli\officecli.exe`
5. 将 `C:\Tools\officecli\` 添加到系统环境变量 PATH：
   - 右键「此电脑」→ 属性 → 高级系统设置 → 环境变量
   - 在「用户变量」的 `Path` 中添加 `C:\Tools\officecli\`
   - 确定保存

**验证安装：**
```cmd
:: 重新打开 CMD 窗口后执行
officecli version
```

#### Linux / Mac

```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
officecli version
```

### 2.2 确认 Python 环境

#### Windows
```cmd
:: 检查 Python（Win10 自带或从 python.org 下载）
python --version
:: 如果显示 3.8+ 即可

:: 安装 openpyxl（仅在需要创建测试 Excel 时用到）
pip install openpyxl
```

#### Linux / Mac
```bash
python3 --version    # 需要 3.8+
pip install openpyxl
```

### 2.3 准备你的 Excel 设计文档

将你要转换的 Excel 文件放在工作目录：

#### Windows
```
C:\Users\你的用户名\Documents\excel-to-md\
├── 设计文档.xlsx      ← 你的设计文档
├── excel_to_md.py    ← 即将生成的脚本
└── 设计文档.md        ← 即将生成的输出
```

#### Linux / Mac
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

### 3.4 读取悬浮吹出形状、红框等形状（Shape）

```bash
# 列出所有形状（吹出泡、矩形红框、线条等都属于 shape）
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
          "name": "Shape 1",
          "geometry": "wedgeRectCallout",
          "x": "5",          "y": "3",      // ← 位置：第5列、第3行的左上角
          "width": "4",      "height": "3",  // ← 大小：宽4列 × 高3行
          "fill": "#FFFF00",
          "color": "#FF0000",
          "bold": true
        }
      }
    ]
  }
}
```

**关键字段说明：**
| 字段 | 含义 | 单位 | 示例解读 |
|---|---|---|---|
| `x` | 形状左上角的列位置 | 单元格数量 | `x=5` → 第 5 列（E 列） |
| `y` | 形状左上角的行位置 | 单元格数量 | `y=3` → 第 3 行 |
| `width` | 形状宽度 | 单元格数量 | `width=4` → 跨越 4 列 |
| `height` | 形状高度 | 单元格数量 | `height=3` → 跨越 3 行 |
| `geometry` | 形状类型 | - | `wedgeRectCallout`=吹出泡, `rectangle`=矩形红框 |

**位置推算公式：**
```
起始单元格 = col_letter(x) + y
结束单元格 = col_letter(x + width - 1) + (y + height - 1)
覆盖范围 = 起始 ~ 结束

例：x=5, y=3, width=4, height=3
→ E3 ~ H5（第5列第3行 到 第8列第5行）
```

### 3.5 读取图片（Picture）

```bash
# 列出所有图片
officecli query 设计文档.xlsx picture --json
```

输出 JSON 示例：
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "path": "/设计说明/picture[1]",
        "type": "picture",
        "format": {
          "alt": "UI 设计 Mockup",
          "name": "Image 1",
          "anchorMode": "oneCell",
          "x": "4",          "y": "9",       // ← 位置：第4列第9行（E9 附近）
          "width": "2857500emu",
          "height": "1714500emu"
        }
      }
    ]
  }
}
```

**提取图片文件到本地：**

xlsx 文件本质是 zip 压缩包，图片存储在 `xl/media/` 目录下。用 Python 标准库 `zipfile` 即可提取：

```python
import zipfile, os, shutil

with zipfile.ZipFile("设计文档.xlsx", 'r') as z:
    media_files = [f for f in z.namelist() if f.startswith('xl/media/')]
    for f in media_files:
        basename = os.path.basename(f)
        target = os.path.join("images", basename)
        os.makedirs("images", exist_ok=True)
        with z.open(f) as src, open(target, 'wb') as dst:
            shutil.copyfileobj(src, dst)
```

提取后，在 Markdown 中用标准图片语法引用：

```markdown
![UI 设计 Mockup](images/image1.png) `[📍D9]`
```

渲染效果：图片正常显示，旁边标注其在 Excel 中的位置（D9 单元格附近）。

### 3.6 验证文件完整性

```bash
officecli validate 设计文档.xlsx
```

---

## 四、格式映射规则（Excel → Markdown）

### 4.1 对照表

#### 单元格内格式
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

#### 形状（吹出泡/红框/线条）
| Excel 形状类型 | geometry 关键字 | Markdown 渲染效果 | 说明 |
|---|---|---|---|
| 吹出泡（标注） | 含 `callout` | `> 📌 ⚠️ **文字** [📍E3~H5, 🔴红色, 🟡黄高亮]` | 引用块+📌图标，末尾标注位置和颜色 |
| 矩形红框 | 含 `rect` / `box` | `> 🔲 (无文字形状) [📍B3~D5, 🔴红色边框]` | 引用块+🔲图标，标注覆盖区域 |
| 直线/箭头 | 含 `line` | `> ➖ (线条) [📍C2~C10]` | 用➖表示，标注起止位置 |
| 其他形状 | — | `> 💠 文字 [📍位置]` | 💠兜底图标 |

> **设计说明**：Markdown 是线性文本，无法在视觉上真的「画一个框包围住几行内容」。所以红框的处理策略是：**用引用块+图标+位置范围注释**来表达「这里 Excel 有个红框，框住了 B3~D5 这个区域」，读者可根据位置注释回到 Excel 定位。

#### 图片（Picture）
| Excel 元素 | OfficeCLI 查询命令 | Markdown 渲染效果 | 说明 |
|---|---|---|---|
| 插入的图片 | `query picture` | `![alt 文本](images/image1.png) [📍D9]` | 提取图片到本地 images/ 目录，用标准 Markdown 图片语法引用 |
| 图片 alt 文本 | format.alt | `![alt 文本](...)` 的 alt 部分 | 如果没有 alt，用图片名称代替 |
| 图片位置 | format.x, format.y | `[📍D9]` 位置标注 | 标注图片在 Excel 中的位置 |

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

**Windows（PowerShell）：**
```powershell
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
officecli version
```

**Linux / Mac：**
```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
officecli version
```

### Step 2: 准备工作目录

**Windows（CMD）：**
```cmd
mkdir C:\Users\%USERNAME%\Documents\excel-to-md
cd C:\Users\%USERNAME%\Documents\excel-to-md
:: 把你的 Excel 文件复制进来
copy C:\Users\%USERNAME%\Downloads\设计文档.xlsx .
```

**Linux / Mac：**
```bash
mkdir -p ~/excel-to-md && cd ~/excel-to-md
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

**Windows（CMD / PowerShell）：**
```cmd
python excel_to_md.py
```

**Linux / Mac：**
```bash
python3 excel_to_md.py
```

### Step 9: 检查输出

**Windows：**
```cmd
type 设计文档.md
```

**Linux / Mac：**
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

### Q5: 吹出泡/红框的位置怎么看？怎么知道它对应哪块内容？

OfficeCLI 返回的 shape 数据里有 `x/y/width/height` 四个位置字段（单位是单元格数量）。脚本会自动把它们转换成 Excel 单元格引用（如 `E3~H5`）显示在 Markdown 里：

```
> 📌 ⚠️ 注意：按钮配色需与品牌色保持一致 [📍E3~H5]
```

看到 `📍E3~H5` 就知道：这个吹出泡在 Excel 里覆盖了 **E3（第5列第3行）到 H5（第8列第5行）** 这块区域，对应附近的单元格内容就是它的说明对象。

### Q6: 在 Excel 画了个红框，Markdown 里长什么样？能真的框住文字吗？

**不能真的画框** —— 因为 Markdown 是「从上到下线性」的文本格式，没有「自由布局」能力，无法在视觉上用矩形包围住中间某几行。

红框在 Markdown 中的渲染效果是：

```
> 🔲 (无文字形状) [📍B3~D5]
```

含义解释：
- `🔲` → 告诉你「这里 Excel 里有个矩形/红框」
- `📍B3~D5` → 红框在 Excel 里覆盖的单元格范围（B3 到 D5，共 3 行 × 3 列）
- 如果红框里有文字，会把文字也提取出来显示

如果红框里有文字（比如红色边框+黄底+写了「重点关注」），效果是：
```
> 🔲 **重点关注** [📍B3~D5, 🟡黄高亮]
```

### Q7: Excel 里的图片能转换到 Markdown 吗？

**可以！** 具体方案如下：

1. **识别图片**：用 `officecli query 文件.xlsx picture --json` 获取所有图片的位置、名称、alt 文本
2. **提取图片文件**：xlsx 本质是 zip，图片存在 `xl/media/` 下，用 Python `zipfile` 直接解压到本地 `images/` 目录
3. **Markdown 引用**：用标准图片语法 `![alt 文本](images/image1.png)` 引用，并标注位置

最终 Markdown 效果：
```markdown
## 图片（Picture）

![UI 设计 Mockup](images/image1.png) `[📍D9]`
```

渲染后在 Markdown 预览中可直接看到原图，旁边标注它在 Excel 中的位置。

> **注意**：`openpyxl` 重新保存 Excel 时会丢失吹出泡等形状（已知限制）。如果需要同时保留图片和形状，建议不要用 openpyxl 编辑已有 Excel。

### Q8: 是否支持 Word/PPT 转 Markdown？

OfficeCLI 也支持 Word 和 PPT 读取，但格式映射规则不同。本手顺仅覆盖 Excel。

### Q9: 完整设计文档（多 Sheet / 大量数据 / 图片 / 公式）能完整转换吗？

**可以！** 已用 `完整设计文档测试.xlsx`（5 Sheet / 2278 单元格 / 5 图片 / 13 表格 / 含公式与格式）进行全功能深度验证，结果：

- **图片**：5/5 全部提取到 `images/` 目录，Markdown 中正确引用
- **表格**：13/13 识别（含未标记表格的自动检测）
- **数值精度**：PI=3.14159265358979（15位小数完整保留）、RAND()=0.05065714514315489（17位小数）
- **公式结果**：SUM/AVERAGE/IF/VLOOKUP/CONCATENATE 等全部正确
- **格式转换**：16 种格式（加粗/颜色/删除线/背景色/斜体/下划线/超链接/组合格式等）全部正确
- **输出**：纯净版 709 行（GitHub 兼容）+ 富文本版 707 行（VS Code/Typora）

**关键点**：务必先安装 OfficeCLI（`officecli version` 确认可用）。如果 OfficeCLI 不可用，脚本会 fallback 到 openpyxl，但 openpyxl 无法读取公式计算结果（data_only=True 时公式单元格返回 None），且不读取图片。

### Q10: 未标记表格（没有用 Excel Table 功能）能识别吗？

**可以！** 转换脚本 `excel_to_md.py` 内置表格自动检测算法：
1. 用 openpyxl 读取 Excel 完整网格结构（包括空单元格）
2. 收集每行的列信息（列数、列范围、是否有文本）
3. 按行号排序，找连续行段：同一列范围内、列数差异 ≤2、允许中间 1 行空行或单列标题行
4. 至少 2 行（header + 数据行）才算表格候选

在完整设计文档测试中，13 个表格全部成功识别，包括未用 Excel Table 标记的文档信息表、修订记录表、术语定义表等。

---

## 九、总结

| 角色 | 职责 | 是否必须 |
|------|------|:---:|
| OfficeCLI | 读取 Excel 内容和格式，返回 JSON | ✅ 必须 |
| Python 脚本 | 把 JSON 映射为 Markdown 语法 | ✅ 必须（但 AI 帮你写） |
| AI | 帮你写 Python 映射脚本 | 一次性，写完不需要了 |
| Skill | 封装多步骤编排 | ❌ 本场景不需要 |
| openpyxl | 创建测试 Excel / 表格自动检测预扫描 | ❌ 只有准备测试数据时用到 |

**一句话总结：OfficeCLI 读 Excel，AI 帮你写翻译脚本，跑一次就出 Markdown。**

---

## 十、完整设计文档测试结果（TC-011）

> 测试文件：`test-data/excel-to-md/完整设计文档测试.xlsx`
> 测试日期：2026-08-10
> OfficeCLI 版本：v1.0.143

### 测试数据

| 指标 | 数值 |
|------|------|
| Sheet 数 | 5 |
| 单元格总数 | 2278 |
| 图片数 | 5 |
| 识别表格数 | 13 |
| 表格数据行数 | 355 |
| 纯净版输出 | 709 行 |
| 富文本版输出 | 707 行 |

### 验证维度与结果

| 维度 | 通过率 | 说明 |
|------|--------|------|
| 图片提取 | 5/5 = 100% | image1~5 全部提取，MD 中正确引用 |
| 表格识别 | 13/13 = 100% | 含未标记表格自动检测 |
| 数值精度 | 15/15 = 100% | PI/RAND/错误值全部保留 |
| 公式结果 | 15/15 = 100% | SUM/IF/VLOOKUP 等全部正确 |
| 格式转换 | 16/16 = 100% | 全格式覆盖 |
| 组件状态列 | 58/58 = 100% | 确定/废弃/待定 全部有值 |
| 文档结构 | 5/5 = 100% | 5 Sheet 标题齐全 |

### 输出文件

| 文件 | 说明 | 行数 |
|------|------|------|
| `完整设计文档测试.md` | 纯净版（Emoji+注释标记颜色，GitHub 兼容） | 709 |
| `完整设计文档测试_richtext.md` | 富文本版（HTML span 颜色，VS Code/Typora） | 707 |
| `images/image1.png` ~ `image5.png` | 提取的图片 | - |

### 已知限制与注意事项

| # | 事项 | 说明 |
|---|------|------|
| 1 | **必须安装 OfficeCLI** | 未安装时 fallback 到 openpyxl，但无法读取公式结果和图片 |
| 2 | **图片编号全局递增** | `xl/media/imageN.png` 跨 Sheet 编号递增，遍历时需用全局计数器 |
| 3 | **颜色返回 RRGGBBAA** | OfficeCLI 返回 8 位颜色，取前 6 位为 RGB |
| 4 | **openpyxl 编辑丢形状** | 用 openpyxl 重新保存会丢失吹出泡等形状 |
| 5 | **GitHub 不支持 HTML 颜色** | 纯净版用 Emoji+注释标记颜色，富文本版用 HTML span |
