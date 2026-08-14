# AGENTS.md — DeepSeek Harness 验证工程 AI Agent 行为规范

## Agent 目标

按照 Harness Engineering 方法论，系统性验证 DeepSeek Harness（DSH）的 10 大功能模块，产出可追踪、可复现、带证据的验证报告。

## 总原则

- 验证一次 = 任务定义（task.md）→ 执行记录（evidence/）→ 结果报告（results/result.md）→ 更新进度（PROGRESS.md / feature_list.json）
- **禁止跳过步骤直接给结论**；每个 P0 结论必须附带 evidence 文件路径
- 先完成 P0 任务、再 P1、再 P2
- 发现的 Bug/限制必须写明复现步骤、命令输出、预期 vs 实际

## 项目约束

- 验证根目录：`/workspace/validations/deepseek-harness/`
- 可写路径：该目录下所有子目录，以及 `/tmp`
- 可执行外部命令：`dsh`（`@deepseek-ai/dsh`）、`node`、`npm`、`pnpm`、标准 Linux 工具
- 破坏性变更：不要碰 `validations/office-cli/` 下的任何文件
- 不要泄露任何 API Key；证据中出现密钥时需脱敏

## 标准执行流程（每个任务都要按这 7 步走）

1. 打开 `PROGRESS.md`，确认上一个任务的状态，把当前任务从 `pending` → `in_progress`
2. 读取 `tasks/<id>/task.md`，逐条理解测试用例
3. 按步骤执行命令，**每条命令的 stdout 原样保存为 `results/evidence/<id>/<tc-id>.txt`**（关键响应可以存 `.json`）
4. 在执行过程中发现新的坑/限制 → 追加到 `harness/.ai/memory/pitfalls.md`
5. 所有 TC 跑完后，写 `tasks/<id>/results/result.md`：每个 TC 给 passing / partially / failing，并把 evidence 路径写进去
6. 回写 `PROGRESS.md`（当前任务改为 passing / failing）和 `feature_list.json`（对应 task 的 features 数组加项）
7. 更新 `session-handoff.md`：写会话完成总结和下一步

## 禁止行为

- ❌ 没保存 evidence 就给结论
- ❌ 用"目测没问题"代替命令执行结果
- ❌ 同时开多个任务交叉执行（同一时间只能有 1 个 in_progress）
- ❌ 重写、简化官方 task.md 里的预期结果以避免失败
- ❌ 把真实 API Key 明文写入任何 evidence 或 README
