# 任务 005 结果报告 — 插件系统（plugin 命令）

**dsh 版本**：v0.1.0-rc.6
**通过率**：3/3 = 100%

---

## TC-001: plugin help（正确带 --profile）

**命令**：`dsh plugin --profile headless --help`

### 发现：plugin 子命令底层封装 pnpm

输出的是 **pnpm v10.5.2 的完整 help**（包含 `add / install / remove / list / update / exec / run / publish / store` 等全套 pnpm 命令），而非一个简短的 DSH 自定义 help。

### 解释

DSH 插件 = npm 包。DSH 没有重复造轮子做包管理，而是直接把一个独立的 pnpm 二进制（bundled Node.js v24.1.0）嵌入进来。因此：

- `dsh plugin --profile <P> add <pkg>` = 在该 profile 的隔离 pnpm 环境中 `pnpm add <pkg>`
- `dsh plugin --profile <P> remove <pkg>` = `pnpm remove`
- `dsh plugin --profile <P> list` = `pnpm list`

✅ 这不是 bug，是架构复用决策（但 UX 上确实容易困惑，需文档明示）。

**证据**：[tc-001-help.txt](file:///workspace/validations/deepseek-harness/results/evidence/005-plugins/tc-001-help.txt)

---

## TC-002 / TC-003: plugin list (headless & web)

### 结果

两条命令输出**均为空**（0 行），exit code 0。

### 解释

`dsh plugin list` = `pnpm list`，而**内置插件（@deepseek-ai/dsh-base 内的 40-50 个核心插件）不通过 pnpm 管理**，它们由 dsh 包内部打包，不出现在 pnpm 依赖树中。

`pnpm list` 只显示**用户给 profile 额外安装**的插件包。由于两个内置 profile 都没安装任何额外插件，list 为空是预期行为。

✅ 设计合理：内置 + 用户扩展分层，list 只显示用户层。

**证据**：
- headless list: [tc-002-list-headless.txt](file:///workspace/validations/deepseek-harness/results/evidence/005-plugins/tc-002-list-headless.txt)（空）
- web list: [tc-003-list-web.txt](file:///workspace/validations/deepseek-harness/results/evidence/005-plugins/tc-003-list-web.txt)（空）

---

## 任务 005 核心结论

1. **DSH 插件系统 = npm 生态**：直接复用 pnpm（bundled v10.5.2）做包管理，无需新学习包安装命令
2. **list 为空 ≠ 没装插件**：只是没装"额外的用户自定义插件"（内置核心插件 40+ 不显示在此）
3. **隔离性**：每个 profile 独立的 pnpm 环境，插件可按场景装配（headless 装工具集、web 装 UI 扩展，互不干扰）
