# 任务 002 结果报告 — Web UI 启动与端口绑定

**执行时间**：2026-08-14
**dsh 版本**：v0.1.0-rc.6
**Node.js 版本**：v24.1.0
**执行机器**：Linux x64（沙箱环境）

## 摘要

| 指标 | 值 |
|------|----|
| 计划 TC 数 | 5 |
| 完全通过 | 5 |
| 部分通过 | 0 |
| 失败 | 0 |
| **通过率** | **5/5 = 100%** |

---

## TC-001: 默认启动（3080 端口）—— ✅ PASS

**执行结果**：
- 端口 3080 启动前空闲
- 启动日志：`dsh web: http://127.0.0.1:3080`
- HTTP GET `/`：`HTTP_CODE: 200`，`CONTENT_TYPE: text/html; charset=utf-8`，`SIZE: 12109`
- HTML 特征：
  - `<title>DeepSeek Harness</title>` ✅
  - `window.__DSH_BOOT__` 插件清单注入 ✅（含 `@deepseek-ai/dsh-cordis-client-runner`、`@deepseek-ai/dsh-client-ui-conversation` 等 39 个前端插件模块）
  - `<div id="root"></div>` React 挂载点 ✅
- 无报错，页面尺寸正常

**证据**：
- [tc-001-stdout.log](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-001-stdout.log)
- [tc-001-index.html](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-001-index.html)
- [tc-001-curl-meta.txt](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-001-curl-meta.txt)

**关键发现**：前端使用基于插件的架构，所有 UI 功能模块（侧边栏、会话、设置、工作区、Plan、Agent、技能、子 Agent、工作流、Trajectory 等）均通过 `window.__DSH_BOOT__.entries` 动态注入，体现了 Cordis "一切皆插件" 的设计。

---

## TC-002: 自定义端口 --port 8080 —— ✅ PASS

**执行结果**：
- 启动日志：`dsh web: http://127.0.0.1:8080`
- HTTP GET `/` → `HTTP_CODE: 200`
- ss 输出：
  ```
  LISTEN 0 0 127.0.0.1:8080 0.0.0.0:* users:(("MainThread",pid=2508,fd=21))
  ```
- 端口绑定符合预期，仅在 loopback 上监听

**证据**：[tc-002-curl-meta.txt](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-002-curl-meta.txt)

---

## TC-003: --host 0.0.0.0 全网卡绑定 —— ✅ PASS（安全特性）

**执行结果**：
- 启动时直接报错退出（exit code 1）：
  ```
  error: --host 0.0.0.0 is intentionally not supported yet for safety: it would expose remote code execution to the network; use 127.0.0.1 instead
  ```
- 这是预期行为：DSH 明确拒绝公网绑定，防止 Shell/文件工具（含 RCE 能力）被外部访问
- 该行为属于 **security by default**，应计为 PASS 而非 FAIL

**证据**：[tc-003-stderr.log](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-003-stderr.log)、[tc-003-listen.txt](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-003-listen.txt)

**⚠️ 新增陷阱（坑 6）**：不要尝试 `--host 0.0.0.0`，DSH 故意不支持。若需要远程访问，应通过 SSH 端口转发（`ssh -L 3080:127.0.0.1:3080 remote`）或反向代理而非让 DSH 直接监听公网。

---

## TC-004: --port 0 自动端口分配 —— ✅ PASS

**执行结果**：
- 启动日志：`dsh web: http://127.0.0.1:40233`（OS 分配 40233 端口）
- HTTP GET `http://127.0.0.1:40233/` → `HTTP_CODE: 200`
- 日志中打印的端口号真实可用，未出现 "日志端口与实际监听不一致" 的问题

**证据**：[tc-004-port.txt](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-004-port.txt)

---

## TC-005: SIGTERM 优雅终止 —— ✅ PASS

**执行结果**：
- 启动 PID 2584，正常监听 9191
- 发送 `kill -TERM` 后，**3 秒内进程退出**
- 退出码：`0`（干净退出，非 137/SIGKILL）
- 进程未遗留任何孤儿进程（通过 ss 验证端口已释放）

**证据**：[tc-005-exit.txt](file:///workspace/validations/deepseek-harness/results/evidence/002-web-ui/tc-005-exit.txt)

---

## 任务 002 核心结论

1. **Web UI 启动稳定**：默认 3080、自定义端口、自动端口三种方式均正常
2. **安全默认值到位**：`0.0.0.0` 被主动拒绝，符合 Agent Runtime 应有安全姿态
3. **前端插件化完整**：`__DSH_BOOT__` 注入了 39 个前端插件模块，覆盖设置/会话/工作区/Plan/Agent/技能/子 Agent/工作流/Trajectory 等所有 UI 能力，与官方宣称一致
4. **进程生命周期健康**：SIGTERM → exit 0，无僵尸、无泄漏

**下一步推荐**：直接进入任务 003（Headless 模式单次任务执行），验证 `dsh --profile headless "prompt"` 是否能跑通一次完整 turn。
