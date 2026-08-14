# 任务 004 结果报告 — Profile / Patch 配置系统

**dsh 版本**：v0.1.0-rc.6
**通过率**：3/3 = 100%

---

## TC-001: 内置 Profile 枚举

**探测方式**：依次对 web / headless / tui / minimal / ptc / creative / standard / default 共 8 个候选名执行 `dsh --profile <X> --dump-default-config`。

### 结果

| 候选 Profile | 是否存在 | 备注 |
|-------------|---------|------|
| **web** | ✅ 存在 | 配置 490 行（含 UI 插件，25 项 disabled） |
| **headless** | ✅ 存在 | 配置 333 行（无 UI，2 项 disabled） |
| tui | ❌ 不存在 | Error: profile "tui" does not exist |
| minimal | ❌ 不存在 | 同上 |
| ptc | ❌ 不存在 | 同上 |
| creative | ❌ 不存在 | 同上 |
| standard | ❌ 不存在 | 同上 |
| default | ❌ 不存在 | 同上 |

### 关键结论

**v0.1.0-rc.6 CLI 层仅内置 2 个 profile：`web` 与 `headless`**。官方文档提到的"四种运行模式（标准 / PTC / 极简 / 创造）"指 **Web UI 界面内的工作模式预设切换**（前端 Agent 行为预设），不是 CLI `--profile` 参数可指定的名字。

**证据**：[tc-001-profiles.txt](file:///workspace/validations/deepseek-harness/results/evidence/004-config/tc-001-profiles.txt)、[tc-002-four-modes.txt](file:///workspace/validations/deepseek-harness/results/evidence/004-config/tc-002-four-modes.txt)

---

## TC-002: web vs headless 配置差异

| 维度 | web | headless |
|------|-----|----------|
| 插件配置行数 | 490 | 333 |
| disabled 项数 | 25（关闭与 headless 冲突的 UI 热更新等） | 2（只关 HMR 1 项） |
| 适用场景 | 浏览器 Web UI | 单次任务无界面退出 |

**差异点**：web profile 额外包含 `@deepseek-ai/dsh-client-*` 系列 30+ 前端插件（侧边栏、会话视图、设置页、Trajectory 视图、Plan 视图、Agent 预设、权限预设…），headless 仅保留 Agent 核心链路。

---

## TC-003: --patch <patch.yaml> 用户层覆盖

### 构造 patch

```yaml
# test-patch.yaml
- id: agent-default-model
  config:
    provider: deepseek-official
    model: deepseek-v3        # 默认是 deepseek-v4-flash
```

### 验证结果

**应用 patch 前**（baseline）：
```yaml
- id: agent-default-model
  name: '@deepseek-ai/dsh-agent-default-model'
  config:
    provider: deepseek-official
    model: deepseek-v4-flash
```

**应用 patch 后**（`--patch test-patch.yaml`）：
```yaml
- id: agent-default-model
  name: '@deepseek-ai/dsh-agent-default-model'
  config:
    provider: deepseek-official
    model: deepseek-v3         # ✅ 被覆盖成功
```

✅ **Patch 机制完整可用**：按 `id` 匹配插件节点，`config` 字段被深度合并。

**证据**：[tc-003-patch.txt](file:///workspace/validations/deepseek-harness/results/evidence/004-config/tc-003-patch.txt)

---

## 任务 004 核心结论

1. **CLI 层只有 2 个内置 profile**，不要被文档中"四种模式"误导（四种模式是 UI 内切换）
2. **`--patch` 覆盖机制完整**：可用于临时改模型、改插件参数，无需修改 DSH_HOME 配置文件
3. **错误消息友好**：未知 profile 时明确提示"create it with 'dsh plugin --profile <name> add <package>'"，给出下一步操作路径
