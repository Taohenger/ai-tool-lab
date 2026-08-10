# OfficeCLI 信息收集

> 本文件汇总 OfficeCLI 的官方信息，供验证时参考。

---

## 官方资源

| 资源 | 链接 |
|------|------|
| 官方网站 | https://officecli.ai/ |
| GitHub 仓库 | https://github.com/iOfficeAI/OfficeCLI |
| GitHub Releases | https://github.com/iOfficeAI/OfficeCLI/releases |
| SKILL.md | https://officecli.ai/SKILL.md |
| Discord 社区 | https://discord.gg/2QAwJn7Egx |
| AionUi (GUI 版本) | https://github.com/iOfficeAI/AionUi |

---

## 安装方式（待验证）

### macOS / Linux

```bash
# 方式 1：curl 安装
curl -fsSL https://officecli.ai/install.sh | bash

# 方式 2：brew
brew install officecli

# 方式 3：npm
npm install -g @officecli/officecli
```

### Windows

```powershell
# winget
winget install --id=HaiYing.OfficeCLI -e
```

### 验证安装

```bash
officecli --version
officecli --help
officecli install
```

---

## 核心命令速览（待验证）

### 读取文档

```bash
# 读取 Word
officecli read 报告.docx

# 读取 Excel（指定工作表）
officecli read 数据.xlsx --sheet "Q3 Data"

# 读取 PowerPoint
officecli read 演示.pptx
```

### 编辑文档

```bash
# 修改 PPT 指定幻灯片文本
officecli edit 演示.pptx --slide 2 --text "更新后的标题"

# 设置 Excel 单元格
officecli set 数据.xlsx /Sheet1/A1 --prop value="姓名" --prop bold=true
```

### 新增内容

```bash
# PPT 加一页
officecli add 演示.pptx / --type slide --prop title="季度报告"

# Word 加一段
officecli add 报告.docx /body --type paragraph --prop text="执行摘要" --prop style=Heading1
```

### 渲染预览

```bash
# 浏览器预览
officecli view 报告.docx

# 实时预览
officecli watch 报告.docx
```

### MCP 服务器

```bash
officecli mcp
```

---

## 官方宣称的特性

1. **专为 AI 代理设计**：JSON 输出，MCP 集成，SKILL 自动安装
2. **零依赖**：单二进制，嵌入 .NET 运行时
3. **无需 Office**：不依赖 Microsoft Office
4. **跨平台**：Linux / macOS / Windows
5. **高保真渲染**：自带 HTML 渲染引擎
6. **三大格式全支持**：Word (.docx) / Excel (.xlsx) / PowerPoint (.pptx)

---

## 与其他方案的对比（待验证）

| 方案 | 需要 Python | 需要 Office | 跨平台 | AI 友好 |
|------|------------|------------|--------|---------|
| OfficeCLI | ❌ | ❌ | ✅ | ✅ |
| python-docx + openpyxl + python-pptx | ✅ | ❌ | ✅ | ⚠️ |
| Microsoft Office Interop | ❌ | ✅ | ❌ | ❌ |
| LibreOffice 命令行 | ❌ | ⚠️ | ✅ | ⚠️ |
