# AI Tool Lab

AI 工具验证实验室 —— 用于系统性验证各种 AI CLI 工具、AI 插件及相关工具链的工程。

## 目的

- 验证 Office CLI 及其他 AI 相关工具的实际可用性
- 记录每个工具的使用流程、优缺点、安装步骤、注意事项
- 作为 AI 工具选型的参考知识库

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
```

## 分支管理

本仓库使用多分支策略进行工具验证：

| 分支名 | 用途 |
|--------|------|
| `main` | 主分支，稳定的项目结构和模板 |
| `verify/office-cli` | Office CLI 验证分支 |
| `verify/<tool-name>` | 其他工具验证分支 |

## 快速开始

1. **选择要验证的工具**，从 `main` 创建验证分支：
   ```bash
   git checkout main
   git checkout -b verify/<tool-name>
   ```

2. **使用 Harness 模板**开始验证，参考 `harness/templates/validation-report.md`。

3. **完成验证后**，将结果提交到对应分支。
