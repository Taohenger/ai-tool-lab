# Harness 层级 Agent 规范

Harness 层把验证拆成 3 个子 Agent，按顺序调用。

## 1. test-executor（测试执行）

**职责**：读取 task.md → 按 TC 顺序跑命令 → 保存 stdout 到 evidence。

**禁止**：
- 不写结果报告（交给 result-analyzer）
- 不改 PROGRESS.md
- 不臆测结果，实际跑到哪就是哪

**交接物**：`results/evidence/<id>/` 下有完整的 stdout 文件集合。

## 2. result-analyzer（结果分析）

**职责**：读取 evidence → 和 task.md 预期比对 → 判定 passing / partially / failing。

**产出**：对每个 TC 的结论 + 实际行为描述 + 新坑列表（追加到 pitfalls.md）。

## 3. report-writer（报告撰写）

**职责**：把 analyzer 的结论写成 result.md，同步 PROGRESS.md / feature_list.json / session-handoff.md。

**硬规则**：每个结论必须写 evidence 路径。
