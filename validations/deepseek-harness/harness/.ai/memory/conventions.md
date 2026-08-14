# 验证约定（记忆）

本工程所有验证 Agent 都应该遵守以下约定。

## 目录与命名

- 证据目录：`results/evidence/<task-short-id>/`
  - short-id 例如：`001-installation`
- 单条证据命名：`<tc-id>[-suffix].txt`，例如 `tc-001-install-output.txt`
  - 如果是 JSON 就用 `.json`
  - 如果是截图或二进制就用相应后缀
- 每个任务下至少有 task.md 和 results/result.md

## 判断标准（passing / partially / failing）

- **passing**：实际行为与 task.md 预期完全一致，没发现限制或替代方案
- **partially**：能达到相同效果但需要走替代路径（例如要换属性名、换命令），或者功能在常见场景没问题、边缘场景有 bug
- **failing**：核心路径不通，没有替代方案

## 命令输出处理

- 不要手动裁剪 stdout；证据是给后人复核的，越完整越好
- 大输出可只留头尾（标注 `... 中间省略 N 行 ...`）
- 涉及 API Key / 密钥一律替换成 `***`
