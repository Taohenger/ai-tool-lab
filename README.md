# AI Tool Lab

AI 工具验证实验室 —— 用于系统性验证各种 AI CLI 工具、AI 插件及相关工具链的工程。

## 目的

- 验证 Office CLI 及其他 AI 相关工具的实际可用性
- 记录每个工具的使用流程、优缺点、安装步骤、注意事项
- 作为 AI 工具选型的参考知识库

## 验证路线图

| 优先级 | 工具 | 对应分支 | 状态 |
|--------|------|----------|------|
| 🔴 P0 | **Office CLI** | `verify/office-cli` | ✅ 验证完成（**79 用例，89.9% 完全通过**） |
| 🟡 P1 | 其他 AI 工具（后续添加） | `verify/<tool-name>` | — |

### Office CLI 验证结果速览

| 维度 | 结果 |
|------|------|
| **验证版本** | v1.0.143 |
| **测试用例** | **79 个**（9 任务：Excel 64 · Word 9 · PPT 6） |
| **完全通过** | **71 个（89.9%）** |
| **核心亮点** | 一键安装零依赖、公式实时重算、图表一键生成、全平台统一路径引用、**Agent × 横展开报告テンプレート自動生成実証**、**Excel→Markdown 格式转换（含吹出形状）** |
| **对人类工作替代度** | Excel 数据录入 100% · 公式计算 100% · 图表 95% · **横展开报告自動生成 100%** · **Excel→MD 格式转换 100%** · Word 85% · PPT 85% |
| **发现问题** | 6 个（cachedValue 不更新、排序不识别表头、CSV import 有 bug 等） |
| **详细报告** | [validations/office-cli/README.md](validations/office-cli/README.md) |

### ⭐ 新增：横展开报告テンプレート × CloudCode Agent 実証デモ（任务 008）

**位置**：`validations/office-cli/test-data/template-demo/`

本検証では新たに「CloudCode 等の Agent がコード横展開調査した結果を、定型の Excel レポートに自動注入する」という実務フローを 100% 実証。

| 成果物 | 内容 |
|--------|------|
| 3 Sheet 定型テンプレート Excel | ①表紙（目的・分支・作業時間・方法・検査観点・結論・署名）、②监测一览（ファイル単位集計＋合計行）、③詳細明細（20 行 × 9 列） |
| サンプルコード 2 件 | `auth-service.ts`（NestJS 風）、`payment-processor.go`（決済処理 Go）。合計 15 件の VP-001/002/003 問題埋め込み |
| 検査観点 JSON | 3 観点（VP-001 横展開日本語化 / VP-002 ハードコード / VP-003 情報漏洩）＋ 正規表現付き |
| OfficeCLI 注入実績 | 130 回超の連続 `officecli set` 実行 → **0 エラー**（resident 常駐の効果） |
| Round-trip 検証 | `set → get --json` でセル値だけでなく **bold・色など書式も完全保持** されることを確認 |
| 自動化スクリプト | `create_template.py`（openpyxl でテンプレ作成）＋ `fill-report.sh`（OfficeCLI でデータ注入） |

**推奨ワークフロー**：
```
CloudCode / Agent
   │ grep/regex で VP-001/002/003 観点の横展開調査
   ▼ JSON 出力
check-viewpoints.json
   │ 1 件ずつ No/ファイルパス/行番号/コード断片/観点/重要度/要修正/コメント に分解
   ▼
bash fill-report.sh  →  横展开报告-OOO-XXXX-XXXX.xlsx
   │ officecli view outline（概要確認）、officecli validate（破損チェック）
   ▼
承認 → 是正 JIRA 起票
```

→ **いますぐデモを再現するには**：`cd validations/office-cli/test-data/template-demo && bash fill-report.sh`（1 分程度で完成版 Excel が新規作成されます）

### ⭐ 新增：Excel 设计文档转 Markdown（任务 009）

**位置**：`validations/office-cli/test-data/excel-to-md/`

验证 OfficeCLI 读取 Excel 设计文档格式信息（加粗、颜色、删除线、**悬浮吹出形状**）并完整转换为 Markdown 的能力。

| 格式类型 | OfficeCLI 属性 | Markdown 输出 | 状态 |
|----------|---------------|-------------|------|
| 加粗 | `font.bold` | `**文本**` | ✅ |
| 颜色 | `font.color` (RRGGBBAA) | `<span style="color:#RRGGBB">文本</span>` | ✅ |
| 删除线 | `strike` | `~~文本~~` | ✅ |
| 背景色 | `fill` | `<mark>文本</mark>` | ✅ |
| 斜体 | `font.italic` | `*文本*` | ✅ |
| 下划线 | `underline` | `<u>文本</u>` | ✅ |
| 超链接 | `link` | `[文本](URL)` | ✅ |
| **悬浮吹出形状** | `query shape` (geometry=wedgeRectCallout) | `> 📌 text` | ✅ |

**快速复现**：`cd validations/office-cli/test-data/excel-to-md && python3 excel_to_md.py`

## 目录结构

```
ai-tool-lab/
├── README.md                # 项目说明（本文件）
├── harness/                 # 辅助工程（Harness），提供脚本和模板
│   ├── scripts/             # 自动化脚本（安装、验证、报告生成等）
│   └── templates/           # 验证结果模板
├── validations/             # 各工具的验证结果（每个工具一个子目录）
│   ├── office-cli/          # Office CLI 验证结果
│   └── ...
└── docs/                    # 项目文档
    ├── BRANCHING.md         # 分支管理规范
    └── VALIDATION_GUIDE.md  # 验证指南（每个工具需要验证什么）
```

## 分支管理

本仓库使用多分支策略进行工具验证：

| 分支名 | 用途 |
|--------|------|
| `main` | 主分支，稳定的项目结构和模板 |
| `verify/office-cli` | Office CLI 验证分支 |
| `verify/<tool-name>` | 其他工具验证分支 |

完整分支管理规范见 [docs/BRANCHING.md](docs/BRANCHING.md)。

## 每个工具需要验证的 8 大维度

| # | 维度 | 说明 |
|---|------|------|
| 1 | **安装与配置** | 前置依赖、安装步骤、常见坑、验证安装 |
| 2 | **基础使用流程** | 基本使用方式、典型命令示例、输出可读性 |
| 3 | **核心功能验证清单** | 工具宣称的每个功能是否真的能用（✅/❌/⚠️） |
| 4 | **优点** | 做得好的地方、惊喜点、对比同类工具的优势 |
| 5 | **缺点 / 问题** | Bug、不好用的地方、缺失的功能 |
| 6 | **注意事项** | 使用前须知的坑、特殊配置要求 |
| 7 | **总体评价** | 多维度评分（安装易用性、文档质量、功能完整性、稳定性、性能、综合推荐度） |
| 8 | **相关资源** | 官方文档、社区讨论、参考文章 |

完整验证指南见 [docs/VALIDATION_GUIDE.md](docs/VALIDATION_GUIDE.md)，标准报告模板见 [harness/templates/validation-report.md](harness/templates/validation-report.md)。

## 快速开始

### 验证一个新工具

```bash
# 方式一：使用 Harness 脚本（推荐）
./harness/scripts/create-branch.sh <tool-name>
./harness/scripts/init-validation.sh <tool-name>

# 方式二：手动
git checkout main
git checkout -b verify/<tool-name>
mkdir -p validations/<tool-name>
cp harness/templates/validation-report.md validations/<tool-name>/README.md
```

### 完成验证后

```bash
git add .
git commit -m "验证(<tool-name>): 完成完整验证报告"
git push -u origin verify/<tool-name>
```
