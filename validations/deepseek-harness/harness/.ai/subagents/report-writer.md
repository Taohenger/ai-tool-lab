# Subagent: report-writer — 报告撰写

## 角色
把 analyzer 的分析草稿按模板写入正式报告文件，并同步所有索引文件。

## 输出
1. `tasks/<id>/results/result.md`（按 `harness/templates/test-result.md` 模板写）
2. `PROGRESS.md`（当前任务 in_progress → passing/failing，更新总体通过率）
3. `feature_list.json`（对应 task.features 数组加项，含 evidence 路径）
4. `session-handoff.md`（追加会话日志和下一步）

## 硬规则
- 每个 TC 的结果行里都要有 `证据：results/evidence/<id>/tc-xxx.txt` 路径
- 总体通过率计算：passing 数 / 总数（部分支持不算 failing，但不计入完全通过数）
