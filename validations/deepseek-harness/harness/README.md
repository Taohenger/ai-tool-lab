# Harness 工具集说明

本目录是验证工程的 Agent 工具层：约束 + 脚本 + 模板 + 记忆。

```
harness/
├── AGENTS.md                       # Harness 子 Agent 规范
├── README.md                       # 本文件
├── config/
│   └── harness.yaml                # 验证规则 + 目录映射
├── scripts/
│   ├── install-dsh.sh              # 安装 dsh（npx + 全局 + 版本检查）
│   └── run-validation.sh <id>      # 验证入口
├── templates/
│   ├── test-case.md                # 任务规格模板
│   └── test-result.md              # 结果报告模板
└── .ai/
    ├── memory/
    │   ├── conventions.md          # 命名 & 判断标准约定
    │   └── pitfalls.md             # 已知坑 & 复现 & 绕过
    └── subagents/
        ├── test-executor.md        # 测试执行子 Agent 定义
        ├── result-analyzer.md      # 结果分析子 Agent 定义
        └── report-writer.md        # 报告撰写子 Agent 定义
```

## 基本使用

### 第 1 步. 安装 dsh

```bash
cd /workspace/validations/deepseek-harness
bash harness/scripts/install-dsh.sh
```

### 第 2 步. 选择一个任务跑

```bash
bash harness/scripts/run-validation.sh 001   # 安装与环境验证
```

### 第 3 步. 完成后同步更新

- `tasks/<id>/results/result.md`
- `PROGRESS.md`
- `feature_list.json`
- `session-handoff.md`
