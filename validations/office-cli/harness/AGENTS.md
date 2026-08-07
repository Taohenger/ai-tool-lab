# AGENTS.md — Harness 层

## Harness 层总纲

Harness 层是验证工程的执行系统，负责将验证任务转化为可执行的步骤。

## 核心规则

1. **任务分离**：一次只执行一个任务（feature_list.json 中只有一个 in_progress）
2. **证据留存**：每个测试步骤的命令输出必须保存到 `results/evidence/<task-id>/`
3. **结果可追溯**：每个结论必须能追溯到具体的测试用例和证据
4. **状态同步**：任务完成后必须同步更新所有状态文件

## 执行检查清单

每次开始任务前，确认：
- [ ] 已读取 PROGRESS.md
- [ ] 已读取 feature_list.json
- [ ] 已将目标任务状态更新为 in_progress
- [ ] 已读取 tasks/<task-id>/task.md

每次完成任务后，确认：
- [ ] 所有测试用例已执行
- [ ] 所有证据已保存到 results/evidence/<task-id>/
- [ ] tasks/<task-id>/results/ 已填写
- [ ] feature_list.json 中任务状态已更新
- [ ] PROGRESS.md 已更新
- [ ] session-handoff.md 已更新（如需要）
