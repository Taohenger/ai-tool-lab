# Harness — OfficeCLI 验证辅助工程

本目录提供 OfficeCLI 验证的所有辅助工具、脚本、配置和自动化能力。

## 目录结构

```
harness/
├── AGENTS.md              # Harness 层总纲
├── config/
│   └── harness.yaml       # 执行层配置
├── scripts/               # 自动化脚本
│   ├── install-officecli.sh
│   ├── run-validation.sh
│   └── generate-report.sh
├── templates/             # 测试用例与报告模板
│   ├── test-case.md
│   └── test-result.md
└── .ai/
    ├── subagents/         # 子 Agent 角色定义
    │   ├── test-executor.md
    │   ├── result-analyzer.md
    │   └── report-writer.md
    ├── memory/            # 经验沉淀
    │   ├── pitfalls.md
    │   └── conventions.md
    └── hooks/             # 验证钩子
```

## 角色分工

本验证工程采用三角色分离架构（参考 Anthropic Harness 工程思想）：

| 角色 | 职责 | 对应文件 |
|------|------|---------|
| **Test Executor**（测试执行者） | 按测试用例逐一执行命令，记录输出和证据 | `.ai/subagents/test-executor.md` |
| **Result Analyzer**（结果分析者） | 分析测试输出，判断是否符合预期，识别问题 | `.ai/subagents/result-analyzer.md` |
| **Report Writer**（报告撰写者） | 将测试结果整理为结构化报告，更新进度文件 | `.ai/subagents/report-writer.md` |

## 使用流程

1. 读取根目录 `AGENTS.md` 和 `PROGRESS.md`
2. 确定当前任务 ID
3. 按 `tasks/<task-id>/task.md` 执行测试
4. 完成后更新 `PROGRESS.md`、`feature_list.json` 和 `session-handoff.md`
