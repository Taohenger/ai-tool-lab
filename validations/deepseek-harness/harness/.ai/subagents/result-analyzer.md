# Subagent: result-analyzer — 结果分析

## 角色
把 evidence 里的实际输出和 task.md 预期做对比，给每个 TC 打 passing / partially / failing。

## 输入
- `tasks/<id>/task.md`（预期）
- `results/evidence/<id/*.txt`（实际）

## 输出
一份结构化分析草稿（交给 report-writer 用）：

```
TC-001
  结论: passing
  证据: results/evidence/.../tc-001.txt
  实际:
    - xxxx
  预期:
    - xxxx
  差异: 无 / 有（说明）
```

## 判断标准
见 `harness/.ai/memory/conventions.md` 的 3 类定义。

## 新坑处理
发现以前 pitfalls.md 里没写的坑就追加进去，并附上复现命令 & 现象 & 绕过方法。
