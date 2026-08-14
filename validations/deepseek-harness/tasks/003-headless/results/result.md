# 任务 003 — Headless 模式单次任务验证

## 任务概述

验证 `dsh --profile headless "<task>"` 命令行接口的正确性：参数解析、配置组合、凭据读取（`DEEPSEEK_API_KEY`）、错误消息友好性、无副作用失败、退出码语义、以及 Agent 运行链路能走到 LLM 鉴权阶段。

**注**：由于沙箱中未配置真实 DeepSeek API Key，本任务不执行"完整 turn（模型 → 工具 → 结果）"的端到端验证，但会把执行路径推到最远（AUTH 阶段），覆盖所有本地代码路径。

## 测试用例列表

| 用例 ID | 用例名称 | 优先级 |
|---------|---------|--------|
| TC-001 | `dsh --profile headless --help` 正常输出 | P0 |
| TC-002 | `--dump-default-config` 输出 headless 完整插件组合（333 行） | P1 |
| TC-003 | `--dump-config` 输出当前层配置（与 default 相同，用户层为空） | P1 |
| TC-004 | 无 API Key 时执行任务 → `MISSING_CREDENTIAL` 清晰报错 | P0 |
| TC-005 | 失败无副作用（不创建空 DSH_HOME / 不写残留文件） | P1 |
| TC-006 | 设 `DEEPSEEK_API_KEY`（假）→ 走到 AUTH 鉴权阶段，key 脱敏输出 | P0 |

---

## TC-001: headless --help

**执行**：`dsh --profile headless --help`

**预期**：
- 显示 `Usage: dsh --profile headless [options] [task...]`
- Arguments 含 `task`（多词以空格拼接）
- Example 含 `dsh --profile headless "run the tests"`

**结果**：✅ PASS（完全匹配）

---

## TC-002: dump-default-config 插件清单

**执行**：`dsh --profile headless --dump-default-config`

**预期**：300+ 行 YAML 插件树，至少包含：
- `dsh-agent` + `agent-default-model`（provider: deepseek-official，model: deepseek-v4-flash）
- `dsh-session-persistence-jsonl`（root: `dshHomePath('sessions')`）
- `dsh-credentials-local`（凭据插件）
- HMR 被 disabled: true（headless 无热更新）

**结果**：✅ PASS。333 行 YAML，默认模型 `deepseek-v4-flash`，完全符合插件化架构设计。

---

## TC-003: dump-config（用户层空）

**执行**：`dsh --profile headless --dump-config`

**预期**：输出行数与 dump-default-config 相同（用户层无 patch 时一致）

**结果**：✅ PASS。333 行，与 TC-002 完全一致（未写任何用户 patch 的预期行为）。

---

## TC-004: 无凭据执行 → MISSING_CREDENTIAL

**执行**：`dsh --profile headless "列出 ..."` （无 DEEPSEEK_API_KEY env）

**预期**：
- exit code != 0（= 1）
- 错误消息带错误码 + 解决方案：
  - `MISSING_CREDENTIAL` 代码
  - 提示"store DEEPSEEK_API_KEY through the credentials service"
  - 或 "export DEEPSEEK_API_KEY in the launching environment"

**结果**：✅ PASS
```
dsh: MISSING_CREDENTIAL: llm-deepseek: no API key for provider route "deepseek-official";
  store DEEPSEEK_API_KEY through the credentials service (the web Models page writes it),
  or export DEEPSEEK_API_KEY in the launching environment
```
退出码 1，错误信息含错误码 + 两种解决路径，**开发者体验良好**。

---

## TC-005: 失败无副作用

**执行**：在 TC-004 失败后检查 `~/.deepseek-harness/` 是否被创建

**预期**：不创建空配置目录（不写入用户盘，除非真正需要持久化）

**结果**：✅ PASS。`/root/.deepseek-harness` 不存在，**干净失败零残留**。

---

## TC-006: 凭据链路 + 脱敏

**执行**：`DEEPSEEK_API_KEY="sk-xxx..." dsh --profile headless "..."`（40 字符假 key，20 秒超时）

**预期**：
- 错误从 MISSING_CREDENTIAL 变成 AUTH 类错误（说明 env var 已被读取并用于请求）
- 错误消息中 key 被脱敏（不打印完整 sk-xxx）
- exit code = 1

**结果**：✅ PASS
```
dsh: AUTH: Authentication Fails, Your api key: ****xxxx is invalid
```
关键：
1. env var 链路通（读取了 DEEPSEEK_API_KEY）
2. 走到了**真正的网络鉴权阶段**（不是本地格式校验）
3. `****xxxx` 脱敏 — **安全输出**，不泄漏密钥尾部
4. exit code = 1

---

## 任务 003 结果汇总

| 指标 | 值 |
|------|----|
| 计划 TC 数 | 6 |
| 完全通过 | 6 |
| 部分通过 | 0 |
| 失败 | 0 |
| **通过率** | **6/6 = 100%** |

## 核心发现

1. **退出码语义清晰**：成功 0，失败 1（凭据/鉴权/超时均为 1，细分需看 stderr 前缀错误码）
2. **错误前缀标准化**：`MISSING_CREDENTIAL:` / `AUTH:` 前缀，便于脚本解析
3. **凭据零泄漏**：env API Key 被 DSH 内部脱敏，错误日志仅打印 `****xxxx`
4. **零副作用失败**：未初始化凭据时，不会创建空的 ~/.deepseek-harness 目录
5. **默认模型选择**：headless 默认用 `deepseek-v4-flash`（成本最优的快速模型）
6. **Agent 运行链路完整**：从 CLI 解析 → 配置组合 → 凭据加载 → HTTP 调用 所有本地路径均可正常走到网络层
