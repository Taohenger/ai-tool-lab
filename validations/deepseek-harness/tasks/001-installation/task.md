# 任务 001 — DeepSeek Harness 安装与环境验证

## 任务概述

本任务验证 DeepSeek Harness（`dsh`，npm 包 `@deepseek-ai/dsh`）在当前 Linux x64 / Node.js v24.1.0 环境下的安装、基础 CLI 和配置目录初始化行为。

## 任务目标

- ✅ 确认 Node.js 版本满足官方 engines 要求（^22.19.0 || >=24.0.0）
- ✅ 确认 `npx @deepseek-ai/dsh` 临时拉取能正常输出 help / version
- ✅ 确认 `npm install -g @deepseek-ai/dsh` 全局安装后，`dsh` 命令在 PATH 中
- ✅ 确认核心 `--profile web --help` / `--dump-default-config --profile web` / `plugin --help` 命令无错误
- ✅ 确认首次启动后配置目录 `DSH_HOME`（或默认 `~/.deepseek-harness`）可写 / 可识别

## 测试用例列表

| 用例 ID | 用例名称 | 优先级 |
|---------|---------|--------|
| TC-001 | Node.js 版本检查（engines 规则） | P0 |
| TC-002 | 使用 install-dsh.sh 安装脚本 | P0 |
| TC-003 | `dsh --version` 和 `dsh --help` 正常输出 | P0 |
| TC-004 | 子命令 help：`dsh web --help`、`dsh plugin --help`、`--profile web --dump-default-config` | P1 |
| TC-005 | 配置目录存在性（DSH_HOME / 默认路径） | P2 |

---

## TC-001: Node.js 版本检查

**目标**：当前环境的 Node.js 版本必须满足 `^22.19.0 || >=24.0.0`

**前置条件**：`node` 命令存在于 PATH

**步骤**：

### 步骤 1.1：检查 node 命令与版本号

执行命令：
```bash
cd /workspace/validations/deepseek-harness
node --version
npm --version
```

**预期结果**：
- `node --version` 以 v 开头
- 主版本号 = 22 且次版本号 >= 19，或者主版本号 >= 24

---

## TC-002: 使用 install-dsh.sh 执行安装

**目标**：项目自带安装脚本能跑完两种方式：npx 拉取 + 全局安装，不报错退出

**前置条件**：
- [ ] TC-001 已通过
- [ ] `harness/scripts/install-dsh.sh` 具有执行权限（若无，先 `chmod +x`）

**步骤**：

### 步骤 2.1：执行安装脚本

执行命令：
```bash
cd /workspace/validations/deepseek-harness
chmod +x harness/scripts/install-dsh.sh harness/scripts/run-validation.sh
bash harness/scripts/install-dsh.sh 2>&1
```

**预期结果**：
- 脚本打印 Node.js 版本检查并显示 ✅ 满足要求
- 脚本至少成功一种安装方式（npx 可用 或 全局 dsh 可用）
- 结束时打印 `dsh --version` 的版本号

---

## TC-003: `--version` 和 `--help` 命令

**目标**：安装完成后，`dsh --version` 输出版本，`dsh --help` 列出核心命令与 profile

**前置条件**：
- [ ] TC-002 已通过（至少一种 dsh 可用）

**步骤**：

### 步骤 3.1：输出版本

如果全局 `dsh` 存在：
```bash
dsh --version
```
否则：
```bash
npx @deepseek-ai/dsh --version
```

**预期结果**：
- 语义化版本号，例如 `0.1.0-rc.6`
- 无 stderr 错误输出

### 步骤 3.2：输出 help

优先全局 `dsh --help`，否则走 npx：

```bash
dsh --help 2>&1
```

**预期结果**：
- 包含 `Usage: dsh [options] [command] [args...]`
- 包含 `--profile <name>`、`--dump-config`、`--patch <path>` 等选项
- 包含子命令：`web [options]`、`plugin [options]`
- 包含 Example 行里的 `dsh --profile web`、`dsh --profile headless`、`dsh plugin add`

---

## TC-004: 子命令 help 与 dump-default-config

**目标**：子命令 help 能列出 profile 专属参数；dump-default-config 能打印完整组合树

**前置条件**：
- [ ] TC-003 已通过

**步骤**：

### 步骤 4.1：web profile help

```bash
dsh --profile web --help 2>&1
```

**预期结果**：
- 包含 `--host <host>`、`--port <port>`、`--trusted-host <authority...>`
- 示例里有 `dsh --profile web --port 8080`

### 步骤 4.2：plugin 子命令 help

```bash
dsh plugin --help 2>&1
```

**预期结果**：
- 输出不报错（至少给出 Usage；若版本暂缺，记录为 partially）

### 步骤 4.3：dump-default-config

```bash
dsh --profile web --dump-default-config 2>&1 | head -80
```

**预期结果**：
- stdout 有非空输出（可能是 YAML 或 JSON 树结构，具体看版本实现）
- 没有 `error: --profile <name> is required` 这类报错

---

## TC-005: 配置目录可访问性

**目标**：DSH 运行时会默认写配置目录 `$DSH_HOME`（通常是 `~/.deepseek-harness`）。这里不做破坏性初始化，只验证目录存在或可创建

**前置条件**：
- [ ] TC-003 已通过

**步骤**：

### 步骤 5.1：读取默认 DSH_HOME

执行命令：
```bash
echo "DSH_HOME env: \"${DSH_HOME:-}\""
DEFAULT_HOME="${DSH_HOME:-$HOME/.deepseek-harness}"
echo "Expected default: $DEFAULT_HOME"
if [ -e "$DEFAULT_HOME" ]; then
  echo "Directory exists:"
  ls -la "$DEFAULT_HOME"
else
  echo "Directory does NOT yet exist (will be created on first interactive run)"
  # 尝试创建一个临时探测目录再删除
  mkdir -p "$DEFAULT_HOME" 2>&1 && echo "Write test: OK" && rmdir "$DEFAULT_HOME" 2>/dev/null || echo "Write test: blocked"
fi
```

**预期结果**：
- 要么目录已存在（有列出内容），要么不存在但目录所在路径（`$HOME`）可写

---

## 证据保存要求

| TC | 证据文件 |
|----|---------|
| TC-001 | `results/evidence/001-installation/tc-001-node-version.txt` |
| TC-002 | `results/evidence/001-installation/tc-002-install-script.txt` |
| TC-003 | `results/evidence/001-installation/tc-003-version.txt` + `tc-003-help.txt` |
| TC-004 | `results/evidence/001-installation/tc-004-web-help.txt` + `tc-004-plugin-help.txt` + `tc-004-dump-config.txt` |
| TC-005 | `results/evidence/001-installation/tc-005-dsh-home.txt` |
