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
| 🔴 P0 | **Nablarch batch 调 API** | `feat/nablarch-batch-api-验证` | ✅ 验证完成（FileDeleteAction 启动时调 HTTP API,status=200） |
| 🔴 P0 | **Nablarch ユーザー登録 端到端** | `feat/nablarch-user-registration-验证` | ✅ 验证完成（**nabledge-5 + Python,5 阶段全流程 + Excel 設計書产出**） |
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

### ⭐ 新增：Nablarch ユーザー登録機能 端到端验证（nabledge-5 + Python 全流程）

**位置**：`validations/nablarch-user-registration/`　**分支**：`feat/nablarch-user-registration-验证`

验证 Agent 利用 **nabledge-5 知识库** + **Python(openpyxl)** 完成 Nablarch 5 用户注册功能从要件理解 → Excel 設計書产出的全流程。

| 维度 | 结果 |
|------|------|
| **5 阶段全流程** | ✅ 外部设计 MD / 内部设计 + CSV / 代码生成 / 测试规格 + JUnit / Excel 灌入 |
| **知识源** | `vendor/nabledge/plugins/nabledge-5/skills/nabledge-5/`(38MB Nablarch 5 知识库) |
| **生成代码** | Form.java(@Required/@Length/@Email/@Pattern/@Domain)+ Action.java(@InjectForm/@OnError/@OnDoubleSubmission/PRG)+ User.sql(UniversalDao 規約) |
| **测试用例** | 14 ケース(正常 3 + 异常 11 含边界值) + JUnit Test 类(BasicHttpRequestTestTemplate 継承) |
| **最终成果物** | [W11AC01_ユーザー登録機能_詳細設計書.xlsx](validations/nablarch-user-registration/W11AC01_ユーザー登録機能_詳細設計書.xlsx)(3 Sheet 灌入) |
| **数据对齐** | ✅ Excel 項目定義 Sheet 的「物理名/精査規則」== Form.java 注解 100% 一致 |
| **离线部署清单** | README 第四章明确打包模型/Skill/脚本/Prompt 集 4 类资产 |
| **详细报告** | [validations/nablarch-user-registration/README.md](validations/nablarch-user-registration/README.md) |

### ⭐ 新增：Nablarch batch 调用外部 API 验证

**位置**：`validations/nablarch-batch-api/`　**分支**：`feat/nablarch-batch-api-验证`

验证 Nablarch 6u3 的 batch 程序（`FileDeleteAction`）启动时调用外部 HTTP API 的能力。

| 维度 | 结果 |
|------|------|
| **baseline** | 官方 `nablarch-example-batch` 6u3 完整副本 |
| **核心改动** | `FileDeleteAction.createReader()` 中加 `callExternalApi()`，用 JDK 11+ `HttpClient` 调 GET API |
| **运行结果** | ✅ batch exit code=0，API status=200，耗时 67ms，stdout + Nablarch Logger 双重输出 |
| **mock API** | 本地 Python `mock-api-server.py`（端口 18090），提供 `GET /hello` `GET /healthz` `POST /echo` |
| **闭锁环境适配** | pom.xml 禁用 `gsp-dba`（seasar s2-* 无法解析）+ compiler excludes 跳过依赖 entity 的源码 + 手动 `h2-init.sql` 建表 |
| **增量 patch** | [increment.patch](validations/nablarch-batch-api/increment.patch)（5 文件 218 行）|
| **运行日志** | [run-output.log](validations/nablarch-batch-api/run-output.log) |
| **详细报告** | 见上一轮对话总结 |

### ⭐ 新增：Nabledge 离线副本（给 Claude Code 用的 Nablarch 全版本知识库）

**位置**：`vendor/nabledge/`　**手顺**：[vendor/README.md](vendor/README.md)

把 [nablarch/nabledge](https://github.com/nablarch/nabledge) 仓库**完整 clone**（191MB，5 个版本：6/5/1.4/1.3/1.2）做成离线副本，配套多版本一键安装脚本：

```bash
# 默认装 Nablarch 6（对应本仓库的 nablarch-batch-api 验证工程）
bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api

# 装 Nablarch 5
bash vendor/install-offline.sh -v 5 /path/to/nablarch5-project

# 全装 5 个版本（同时维护多版本工程时用）
bash vendor/install-offline.sh -v all /path/to/project

# 装完后在 Claude Code 里用 /n6 命令问 Nablarch 6 问题（纯本地知识检索，无网络）
/n6 BatchAction の createReader で外部 API を呼び出す方法を教えて
```

| Plugin | 对应 Nablarch | 大小 | 命令 |
|--------|-------------|------|------|
| nabledge-6 | 6u3 | 28 MB | `/n6` |
| nabledge-5 | 5 | 38 MB | `/n5` |
| nabledge-1.4 | 1.4 | 50 MB | `/n1.4` |
| nabledge-1.3 | 1.3 | 38 MB | `/n1.3` |
| nabledge-1.2 | 1.2 | 38 MB | `/n1.2` |

**特性**：运行时全部本地操作（scripts 无任何 `curl`/`wget`/`git fetch`），知识检索完全离线；Claude 推理若用本地模型则端到端离线。多版本可并存于同一项目。

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
│   ├── nablarch-batch-api/  # Nablarch batch 调 API 验证（feat/nablarch-batch-api-验证 分支）
│   └── ...
├── vendor/                  # 第三方工具离线副本
│   ├── nabledge/            # nablarch/nabledge 完整离线副本（191MB，5 个版本）
│   ├── install-offline.sh   # 多版本一键安装脚本：vendor → 项目 .claude/（-v 6/5/1.4/1.3/1.2/all）
│   └── README.md            # 离线安装手顺 + 使用说明
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
| `feat/nablarch-batch-api-验证` | Nablarch batch 调 API 验证 + nabledge 离线副本 |
| `feat/nablarch-user-registration-验证` | Nablarch 5 ユーザー登録機能 端到端验证（nabledge-5 全流程 + Excel 設計書） |
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
