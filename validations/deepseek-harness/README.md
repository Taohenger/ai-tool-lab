# DeepSeek Harness (DSH) 验证报告

> 验证 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) —— DeepSeek 开源 AI Agent 运行框架（一切皆插件 · Model + Harness = Agent）

---

## 验证结果：10 个任务进行中

| 维度 | 数据 |
|------|------|
| 版本 | v0.1.0-rc.6 |
| 环境 | Linux x64 / Node.js v24.1.0 |
| 日期 | 2026-08-14 ~ |
| 任务 | 10 个（进行中） |
| 测试用例 | 规划中 |
| 完全通过 | 0 |
| 部分支持 | 0 |
| 失败 | 0 |

---

## 能代替人类做什么？

| 场景 | 替代度 | 说明 |
|------|--------|------|
| 文件浏览与编辑 | TBD | Agent 自主读写文件 |
| Shell 命令执行 | TBD | 跑测试、构建、脚本 |
| 代码搜索与重构 | TBD | 仓库级检索、跨文件修改 |
| 多步骤任务编排 | TBD | Plan → Execute → Verify 循环 |
| 子 Agent 分派 | TBD | 大任务拆分子任务 |
| 会话记录与回放 | TBD | Trajectory 完整可追溯 |
| 自定义插件扩展 | TBD | Cordis 插件热插拔 |

---

## 10 个验证任务

| # | 任务 | 用例 | 通过率 | 报告 |
|---|------|------|--------|------|
| 001 | 安装与环境要求 | — | — | [report](tasks/001-installation/results/result.md) |
| 002 | Web UI 启动与界面 | — | — | [report](tasks/002-web-ui/results/result.md) |
| 003 | Headless 模式（单次任务） | — | — | [report](tasks/003-headless-mode/results/result.md) |
| 004 | Profile / Patch 配置系统 | — | — | [report](tasks/004-profiles-patches/results/result.md) |
| 005 | 插件系统（plugin 命令） | — | — | [report](tasks/005-plugin-system/results/result.md) |
| 006 | 工作区管理与文件操作 | — | — | [report](tasks/006-workspace-files/results/result.md) |
| 007 | Shell 命令执行与安全性 | — | — | [report](tasks/007-shell-commands/results/result.md) |
| 008 | 代码搜索与编辑能力 | — | — | [report](tasks/008-code-edit-search/results/result.md) |
| 009 | Agent 端到端任务执行 | — | — | [report](tasks/009-agent-tasks/results/result.md) |
| 010 | 会话记录与可追溯性 | — | — | [report](tasks/010-session-traceability/results/result.md) |

---

## 关键文件

| 文件 | 说明 |
|------|------|
| [PROGRESS.md](PROGRESS.md) | 总进度与结论 |
| [session-handoff.md](session-handoff.md) | 跨会话交接 |
| [feature_list.json](feature_list.json) | 功能清单（带证据） |
| `tasks/<id>/results/result.md` | 各任务结果报告 |
| `results/evidence/<id>/` | 测试证据 |
| `test-data/` | 测试数据文件 |

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 开发语言 | TypeScript（Node.js） |
| 运行方式 | Web UI（默认 http://127.0.0.1:3080）/ Headless / TUI |
| 核心公式 | **Model + Harness = Agent** |
| 核心信条 | **Everything is a Plugin（一切皆插件）** |
| 核心架构 | Cordis 插件元框架（时空可组合性 + 可逆效应） |
| 运行模式 | 标准模式 / PTC 模式 / 极简模式 / 创造模式 |
| 安装命令 | `npm install -g @deepseek-ai/dsh` 或 `npx @deepseek-ai/dsh web` |
| 前置依赖 | Node.js ^22.19.0 || >=24.0.0 |
| 模型接入 | DeepSeek 官方 + OpenAI/Anthropic 兼容 + 自定义 Provider |
| 关键设计 | append-only 会话日志 / 事件溯源 / Trajectory 视图 |
| 协议 | MIT |
