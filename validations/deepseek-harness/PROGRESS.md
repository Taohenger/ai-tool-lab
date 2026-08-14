# PROGRESS.md — DeepSeek Harness 验证进度追踪

## 当前已验证状态

| 项目 | 内容 |
|------|------|
| **验证工程根目录** | `/workspace/validations/deepseek-harness/` |
| **验证对象** | DeepSeek Harness v0.1.0-rc.6（开源 Agent 运行框架，一切皆插件） |
| **标准启动路径** | 见 `tasks/` 目录下各任务的 task.md |
| **下一优先任务** | 006-010（需配置 DEEPSEEK_API_KEY）— 提供一键脚本 `harness/scripts/run-006-010-with-key.sh` |
| **当前阻塞** | 需真实 DeepSeek API Key 才能执行 Agent 交互（任务 006-010 依赖 LLM 调用） |

---

## 功能验证总览（与 feature_list.json 同步）

| 任务 ID | 任务名称 | 状态 | 进度 | 通过率 | 核心发现 |
|---------|---------|------|------|--------|---------|
| 001 | 安装与环境要求 | ✅ completed | 100% | 4/5 = 80% | TC-004 plugin help 部分通过（需带 --profile） |
| 002 | Web UI 启动与界面 | ✅ completed | 100% | 5/5 = 100% | 0.0.0.0 安全拒绝；前端 39 插件模块注入；SIGTERM 优雅退出 |
| 003 | Headless 模式（单次任务） | ✅ completed | 100% | 6/6 = 100% | 错误码标准化；API Key 脱敏；无凭据失败零残留 |
| 004 | Profile / Patch 配置系统 | ✅ completed | 100% | 3/3 = 100% | CLI 层只有 web/headless 两个 profile；--patch 深度合并生效 |
| 005 | 插件系统（plugin 命令） | ✅ completed | 100% | 3/3 = 100% | plugin = pnpm 包装；list 只显示用户额外插件 |
| 006 | 工作区管理与文件操作 | 🔧 需 Key | — | — | 依赖 Agent turn（需 LLM） |
| 007 | Shell 命令执行与安全性 | 🔧 需 Key | — | — | 依赖 Agent turn（需 LLM） |
| 008 | 代码搜索与编辑能力 | 🔧 需 Key | — | — | 依赖 Agent turn（需 LLM） |
| 009 | Agent 端到端任务执行 | 🔧 需 Key | — | — | 依赖 Agent turn（需 LLM） |
| 010 | 会话记录与可追溯性 | 🔧 需 Key | — | — | 依赖 Agent turn（需 LLM） |

**总体通过率（任务 001-005 已执行）**：(4+5+6+3+3)/(5+5+6+3+3) = 21/22 = **95.5%**

---

## 设计阶段结论：验证范围与优先级

### P0 — 必须过（才能叫 Agent Harness）
1. npx/全局两种安装方式都能跑
2. Web UI 能启动并正常绑定端口
3. Headless 模式能执行一次完整 turn（输入 prompt → 输出结果）
4. 文件读写（读一个本地文件、创建新文件、修改内容）
5. Shell 命令执行（`ls` / `cat` 这类只读命令）
6. 插件系统 add/remove/list 基本动作

### P1 — 重要加分项
1. Profile + Patch 组合生效（例如 `--patch extra.yml` 改变行为）
2. 工作区选择与范围限制（只能改工作区内文件）
3. 代码搜索（grep / 符号）
4. 多步骤任务（2 轮以上的 Plan → Do 循环）

### P2 — 深度验证
1. 会话可恢复（save → resume）
2. Trajectory 记录完整性（模型所见即所录）
3. Shell 安全（越权写 / 长命令超时 / 大输出限制）
4. 子 Agent 分派（大任务拆分）

---

## 对人类工作替代程度评估（验证后再填）

| 场景 | 替代度 | 说明 |
|------|--------|------|
| 项目启动与环境准备 | TBD | TBD |
| 代码阅读与仓库理解 | TBD | TBD |
| 单文件代码修改 | TBD | TBD |
| 跨文件重构 | TBD | TBD |
| 调试与错误修复 | TBD | TBD |
| 测试执行与报告 | TBD | TBD |
| 命令行运维任务 | TBD | TBD |
| 多步骤工作流编排 | TBD | TBD |
| 报告与文档撰写 | TBD | TBD |

---

## 会话记录

### 会话 #1（2026-08-14，初始）
- 完成内容：
  - 工程骨架搭建（目录、README、INFO、PROGRESS）
  - 官方信息调研（npx 可用性 / 版本 v0.1.0-rc.6 / 命令清单）
  - 10 个任务范围定义（安装→Web→Headless→配置→插件→文件→Shell→代码→Agent→追溯）
- 下一步行动：
  - 执行任务 001 安装验证
  - 编写安装脚本 `harness/scripts/install-dsh.sh`
  - 生成各任务 `task.md` 测试规格
