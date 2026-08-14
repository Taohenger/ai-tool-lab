# 任务 001 — 安装与环境验证 结果报告

## 执行环境

| 项目 | 内容 |
|------|------|
| 执行时间 | 2026-08-14 |
| 执行环境 | Linux x64（容器） |
| DSH 版本 | v0.1.0-rc.6（全局安装 + npx 均可用） |
| Node.js 版本 | v24.1.0（npm 11.4.2） |

---

## 总览

| 用例 ID | 用例名称 | 优先级 | 结果 | 证据 |
|---------|---------|--------|------|------|
| TC-001 | Node.js 版本检查（engines 规则） | P0 | passing | `results/evidence/001-installation/tc-001-node-version.txt` |
| TC-002 | 使用 install-dsh.sh 安装脚本 | P0 | passing | `results/evidence/001-installation/tc-002-install-script.txt` |
| TC-003 | `--version` 和 `--help` 命令 | P0 | passing | `tc-003-version.txt` + `tc-003-help.txt` |
| TC-004 | web/plugin/dump-default-config | P1 | partially | `tc-004-web-help.txt` + `tc-004-plugin-help.txt` + `tc-004-dump-config.txt` |
| TC-005 | 配置目录可访问性 | P2 | passing | `results/evidence/001-installation/tc-005-dsh-home.txt` |

**通过率**：4/5 = 80%（完全通过：4，部分支持：1，失败：0）

---

## 详细结果

### TC-001: Node.js 版本检查

**结论**：passing ✅

**证据**：`results/evidence/001-installation/tc-001-node-version.txt`

**发现**：
- 实际输出：`node v24.1.0`、`npm 11.4.2`
- 官方要求：`^22.19.0 || >=24.0.0`
- 主版本 24 >= 24，完全满足；无 engines 报错

### TC-002: install-dsh.sh 安装脚本执行

**结论**：passing ✅

**证据**：`results/evidence/001-installation/tc-002-install-script.txt`

**发现**：
- 脚本 Node.js 检查输出 `✅ Node.js v24+ 满足要求`
- 方式 1（npx）：成功拉取包并打印 `DSH 版本: 0.1.0-rc.6`
- 方式 2（全局安装）：`added 587 packages in 2m`，结束时输出版本 `0.1.0-rc.6`
- 全局安装有一个 `node-domexception@1.0.0 deprecated` 警告，但不影响功能（提示改用平台原生 DOMException）

### TC-003: `--version` 与 `--help`

**结论**：passing ✅

**证据**：
- `tc-003-version.txt` → `0.1.0-rc.6`
- `tc-003-help.txt` → 完整 Usage

**发现**：
- `--help` 输出中包含了所需的所有选项：`--profile`、`--patch`、`--dump-config`、`--dump-default-config`
- Commands 列出了 `web` 和 `plugin` 两个子命令
- Examples 行示例齐全：`dsh --profile web`、`headless`、`tui --patch`、`--resume`、`--help`、`plugin add <package>` 共 6 条

### TC-004: 子命令 help 与 dump-default-config

**结论**：partially ⚠️（3 项里 2 项 passing、1 项有替代路径）

**证据**：
- `tc-004-web-help.txt`（passing）
- `tc-004-plugin-help.txt`（partially — 需要加 `--profile`）
- `tc-004-dump-config.txt`（passing）

**发现**：

1. `dsh --profile web --help` ✅：
   - 列出 `--host`、`--port`、`--trusted-host` 三个选项 + `-h`
   - 示例正确展示了 `--port 8080`

2. `dsh plugin --help` ⚠️：
   - 报错：`error: required option '--profile <name>' not specified`
   - 说明 `plugin` 子命令**强制要求**在它**之前**加 `--profile <name>`（因为插件是 per-profile 的）
   - **替代写法**：`dsh plugin --profile web --help`（或 tui / headless）
   - 这不算 bug，是"插件属于某个 profile"的设计；但 CLI 的错误文案可以更友好（例如提示正确写法）

3. `dsh --profile web --dump-default-config` ✅：
   - stdout 打印了 ~50 个插件节点的 YAML 树
   - 确认存在核心插件：
     - `llm` (`@deepseek-ai/dsh-llm`)
     - `session` (`@deepseek-ai/dsh-session`)
     - `agent` + `agent-default-model`（默认 `deepseek-v4-flash`）
     - `credentials`（`@deepseek-ai/dsh-credentials-local`）
     - `session-persistence-jsonl`（会话落盘）
     - `session-query-sqlite`（可配置 SQLite 持久化或内存模式 `:memory:`）
     - `hmr`（Web 开发热更新插件，默认 disabled）
   - 同时能看到遥测开关：`DSH_TELEMETRY_MODE`（默认 DISABLED）与 OTLP exporter

### TC-005: 配置目录可访问性

**结论**：passing ✅

**证据**：`tc-005-dsh-home.txt`

**发现**：
- `DSH_HOME` 环境变量未设置（空字符串）
- 默认路径推断为 `/root/.deepseek-harness`，该目录首次安装后尚未创建
- 写测试通过：`mkdir -p` → OK → `rmdir` 成功清理
- 说明后续首次交互式运行时 DSH 可以正常创建自己的配置目录

---

## 任务级别总结

| 维度 | 内容 |
|------|------|
| 最亮点 | dump-default-config 能把 ~50 个核心插件的组合完整列出来，证明"一切皆插件"不是口号 — 从 LLM、会话、凭据到 SQLite 查询、遥测全部是独立插件 |
| 新发现的限制（已追加到 pitfalls.md） | `dsh plugin --help` 必须在前面加 `--profile <name>`，否则报错；正确用法是 `dsh plugin --profile <name> --help` / `add <pkg>` |
| 安装体验 | ⭐⭐⭐⭐ — npx 体验极好（1 分钟内首次可验证），全局安装要 2 分钟拉 587 个包，属正常量级 |
| 后续待测 | Web UI 实际绑定端口、Headless 无密钥运行行为（有/无 API Key 各会发生什么） |
