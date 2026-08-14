# session-handoff.md — DeepSeek Harness 验证工程 跨会话交接

## 当前进度快照

| 项目 | 内容 |
|------|------|
| 工程目录 | `/workspace/validations/deepseek-harness/` |
| 验证对象 | DeepSeek Harness v0.1.0-rc.6（2026-08-13 开源，MIT） |
| 当前状态 | 工程骨架已搭建，10 个任务范围已定义，等待启动任务 001 执行 |
| 总体通过率 | 0 / 0 = N/A（未开始执行） |
| 已完成任务数 | 0 / 10 |
| 下一个要做 | 任务 001 — 安装与环境要求（TC-001 ~ TC-005） |

---

## 关键决策与上下文

### 已确认事实
1. **安装方式**：`npx @deepseek-ai/dsh` 已在本地工作，版本 v0.1.0-rc.6
2. **运行模式**：web / headless / tui 三种 profile 都在 CLI 中存在
3. **环境**：Node.js v24.1.0（满足要求 >= 24）
4. **GitHub 仓库**：`deepseek-ai/deepseek-harness`，MIT 协议
5. **首次使用配置**：需填入 DeepSeek API Key（`$DSH_HOME/.credentials.yaml`），选工作区

### 设计决策
1. 验证任务按使用顺序排布：安装 → Web → Headless → 配置 → 插件 → 文件 → Shell → 代码 → Agent → 追溯
2. P0 层先过"能用"，P1 层测"好用"，P2 层测"深度/边界"
3. 证据一律保存为文本（命令 stdout、配置文件 dump、截图需要另存 PNG）

### 约束与注意
- DSH v0.1 是开发者预览版，官方明确未来会有破坏性变更
- Headless 模式是自动化验证的关键入口 — 优先把它跑通，可替代人工 UI 验证
- 如果 Agent 任务实际需要模型调用，必须确认 API Key 已配置；否则只能做"有密钥才跑"的条件用例

---

## 10 个任务与当前状态

| 任务 ID | 名称 | 状态 | 关键文件 |
|---------|------|------|---------|
| 001 | 安装与环境要求 | ⏳ pending | `tasks/001-installation/task.md` |
| 002 | Web UI 启动与界面 | ⏳ pending | `tasks/002-web-ui/task.md` |
| 003 | Headless 模式（单次任务） | ⏳ pending | `tasks/003-headless-mode/task.md` |
| 004 | Profile / Patch 配置系统 | ⏳ pending | `tasks/004-profiles-patches/task.md` |
| 005 | 插件系统（plugin 命令） | ⏳ pending | `tasks/005-plugin-system/task.md` |
| 006 | 工作区管理与文件操作 | ⏳ pending | `tasks/006-workspace-files/task.md` |
| 007 | Shell 命令执行与安全性 | ⏳ pending | `tasks/007-shell-commands/task.md` |
| 008 | 代码搜索与编辑能力 | ⏳ pending | `tasks/008-code-edit-search/task.md` |
| 009 | Agent 端到端任务执行 | ⏳ pending | `tasks/009-agent-tasks/task.md` |
| 010 | 会话记录与可追溯性 | ⏳ pending | `tasks/010-session-traceability/task.md` |

---

## 已发现的坑（待后续实证）

1. **Headless 模式参数**：`dsh --profile headless "任务"` 官方文档提了，但具体行为（是否需要模型 key / 是否需要工作区）需要实测确认
2. **Web UI 启动后需要两次手工配置**：填 API Key → 选工作区；自动化测试需要跳过或程序化写入凭据文件
3. **插件命令 `dsh plugin`**：文档显示需要 `--profile <name>`，然后 `add <pkg>` 走 pnpm，需要确认网络和安装路径

---

## 下一步行动清单

1. **立即做（下一回合第一件事）**
   - 编写 `harness/scripts/install-dsh.sh` 安装脚本
   - 编写 `tasks/001-installation/task.md`（5 个 TC：npx / 全局 / 版本命令 / help 命令 / 配置目录）
   - 执行任务 001，保存证据到 `results/evidence/001-installation/`
   - 写 `tasks/001-installation/results/result.md`

2. **随后做**
   - 完成 002～010 的 task.md 框架
   - 启动 Web UI 确认页面正常打开（headless 下用 curl 探活）
   - 如果有 API Key，跑 headless 模式一个小任务（例如："列出 test-data 目录"）并观察输出

3. **阻塞解除条件**
   - 如需要真实模型能力（任务 006 之后），确认用户是否要提供 DeepSeek API Key
