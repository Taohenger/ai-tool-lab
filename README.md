# AI Tool Lab

AI 工具验证实验室 —— 用于系统性验证各种 AI CLI 工具、AI 插件及相关工具链的工程。

## 目的

- 验证 Office CLI 及其他 AI 相关工具的实际可用性
- 记录每个工具的使用流程、优缺点、安装步骤、注意事项
- 作为 AI 工具选型的参考知识库

## 验证路线图

| 优先级 | 工具 | 对应分支 | 状态 |
|--------|------|----------|------|
| 🔴 P0 | **Office CLI** | `verify/office-cli` | ⏳ 待验证 |
| 🟡 P1 | 其他 AI 工具（后续添加） | `verify/<tool-name>` | — |

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
