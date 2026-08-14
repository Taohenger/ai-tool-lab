# 任务 002 — Web UI 启动与端口绑定验证

## 任务概述

本任务验证 DeepSeek Harness 的 Web UI 模式（`--profile web`）能否在当前环境下正常启动、绑定端口、提供 HTTP 服务并返回可访问的前端页面。

## 任务目标

- ✅ 确认 `dsh --profile web` 启动日志中明确打印监听地址与端口
- ✅ 确认默认端口 `3080`（或指定端口）可通过 HTTP GET 返回 200 响应
- ✅ 确认根路径 `/` 返回 HTML 页面（包含 Web UI 特征字符串）
- ✅ 确认 `--host 0.0.0.0` 可绑定所有网卡（远程可访问模式）
- ✅ 确认 `--port 0` 可让 OS 自动分配空闲端口并正确打印
- ✅ 确认 Web UI 进程可被优雅终止（Ctrl+C / SIGTERM 正常退出）

## 测试用例列表

| 用例 ID | 用例名称 | 优先级 |
|---------|---------|--------|
| TC-001 | 默认启动：监听日志、端口绑定、HTTP 200 | P0 |
| TC-002 | 自定义端口 `--port 8080` 启动验证 | P1 |
| TC-003 | `--host 0.0.0.0` 全网卡绑定 | P1 |
| TC-004 | `--port 0` 自动端口分配 | P2 |
| TC-005 | 进程优雅终止（SIGTERM） | P2 |

---

## TC-001: 默认启动与 HTTP 可访问性

**目标**：`dsh --profile web` 默认启动后，监听 `127.0.0.1:3080`，HTTP GET `/` 返回 200 且 HTML 中含 DSH 特征标记。

**前置条件**：
- [ ] TC-001（安装）已通过，`dsh` 在 PATH 中
- [ ] 端口 3080 未被占用（若占用则 TC-002 优先）

**步骤**：

### 步骤 1.1：检查端口 3080 是否空闲

```bash
ss -tlnp | grep :3080 || echo "Port 3080 is free"
```

**预期结果**：无监听或显示为空（若已被占用，跳过此 TC，改用 TC-002 的自定义端口）。

### 步骤 1.2：后台启动 dsh web

```bash
cd /workspace/validations/deepseek-harness
nohup dsh --profile web --host 127.0.0.1 --port 3080 \
  > results/evidence/002-web-ui/tc-001-stdout.log \
  2> results/evidence/002-web-ui/tc-001-stderr.log &
echo "PID: $!"
sleep 5
```

**预期结果**：
- 进程 PID 被打印
- 5 秒后进程仍存活（`kill -0 $PID` 无错误）

### 步骤 1.3：检查启动日志

```bash
cat results/evidence/002-web-ui/tc-001-stdout.log
echo "---STDERR---"
cat results/evidence/002-web-ui/tc-001-stderr.log
```

**预期结果**：
- 日志中包含 `127.0.0.1:3080` 或 `http://` 字样的访问 URL
- 无 `Error: listen EADDRINUSE` 报错

### 步骤 1.4：HTTP GET / 验证

```bash
curl -sS -o results/evidence/002-web-ui/tc-001-index.html \
  -w "HTTP_CODE:%{http_code}\nCONTENT_TYPE:%{content_type}\nSIZE:%{size_download}\n" \
  http://127.0.0.1:3080/ \
  | tee results/evidence/002-web-ui/tc-001-curl-meta.txt
head -50 results/evidence/002-web-ui/tc-001-index.html
```

**预期结果**：
- HTTP_CODE: 200
- CONTENT_TYPE 含 `text/html`
- SIZE > 0
- HTML 文件中包含 `DeepSeek`、`Harness`、`dsh` 任一关键词（或 `<script` 标签，表明是前端入口）

### 步骤 1.5：停止进程

```bash
kill $PID 2>/dev/null || true
sleep 2
```

---

## TC-002: 自定义端口 `--port 8080`

**目标**：通过 `--port 8080` 指定非默认端口后，服务实际在 8080 上监听。

**前置条件**：
- [ ] 端口 8080 未被占用

**步骤**：

### 步骤 2.1：启动并指定端口

```bash
cd /workspace/validations/deepseek-harness
nohup dsh --profile web --host 127.0.0.1 --port 8080 \
  > results/evidence/002-web-ui/tc-002-stdout.log \
  2> results/evidence/002-web-ui/tc-002-stderr.log &
PID2=$!
echo "PID: $PID2"
sleep 5
```

### 步骤 2.2：验证 8080 端口

```bash
curl -sS -o /dev/null -w "TC-002 HTTP_CODE:%{http_code}\n" http://127.0.0.1:8080/ \
  | tee results/evidence/002-web-ui/tc-002-curl-meta.txt
ss -tlnp | grep :8080 | tee -a results/evidence/002-web-ui/tc-002-curl-meta.txt
```

**预期结果**：HTTP_CODE 为 200，ss 输出中 8080 端口处于 LISTEN 状态。

### 步骤 2.3：停止进程

```bash
kill $PID2 2>/dev/null || true
sleep 2
```

---

## TC-003: `--host 0.0.0.0` 全网卡绑定

**目标**：指定 `--host 0.0.0.0` 时，监听地址为 `0.0.0.0`（INADDR_ANY），可通过所有 IP 访问。

**前置条件**：
- [ ] TC-001 或 TC-002 已通过
- [ ] 选择一个未被占用的端口（如 9090）

**步骤**：

### 步骤 3.1：启动 dsh web 绑定 0.0.0.0

```bash
cd /workspace/validations/deepseek-harness
nohup dsh --profile web --host 0.0.0.0 --port 9090 \
  > results/evidence/002-web-ui/tc-003-stdout.log \
  2> results/evidence/002-web-ui/tc-003-stderr.log &
PID3=$!
echo "PID: $PID3"
sleep 5
```

### 步骤 3.2：验证监听地址

```bash
ss -tlnp | grep :9090 | tee results/evidence/002-web-ui/tc-003-listen.txt
# 通过 localhost 访问
curl -sS -o /dev/null -w "TC-003-loopback HTTP_CODE:%{http_code}\n" http://127.0.0.1:9090/
# 通过 0.0.0.0 访问（通常映射到本机）
hostname -I | awk '{print $1}' | read MYIP
if [ -n "$MYIP" ]; then
  curl -sS -o /dev/null -w "TC-003-eth HTTP_CODE:%{http_code}\n" "http://$MYIP:9090/"
fi | tee -a results/evidence/002-web-ui/tc-003-listen.txt
```

**预期结果**：
- ss 输出中显示 `0.0.0.0:9090` 或 `*:9090`（LISTEN 状态）
- loopback 访问返回 200

### 步骤 3.3：停止进程

```bash
kill $PID3 2>/dev/null || true
sleep 2
```

---

## TC-004: `--port 0` 自动端口分配

**目标**：当 `--port 0` 时，OS 自动分配一个空闲端口，启动日志中必须打印实际绑定的端口号。

**前置条件**：
- [ ] TC-001 已通过

**步骤**：

### 步骤 4.1：启动 dsh web --port 0

```bash
cd /workspace/validations/deepseek-harness
nohup dsh --profile web --host 127.0.0.1 --port 0 \
  > results/evidence/002-web-ui/tc-004-stdout.log \
  2> results/evidence/002-web-ui/tc-004-stderr.log &
PID4=$!
echo "PID: $PID4"
sleep 6
```

### 步骤 4.2：从日志解析端口并验证

```bash
cat results/evidence/002-web-ui/tc-004-stdout.log
echo "---STDERR---"
cat results/evidence/002-web-ui/tc-004-stderr.log
# 用 lsof/ss 反查该进程监听的端口
AUTO_PORT=$(ss -tlnp | grep "pid=$PID4" | grep -oE ':[0-9]+' | head -1 | tr -d ':')
echo "Auto-assigned port: $AUTO_PORT" | tee results/evidence/002-web-ui/tc-004-port.txt
if [ -n "$AUTO_PORT" ]; then
  curl -sS -o /dev/null -w "TC-004 HTTP_CODE:%{http_code}\n" "http://127.0.0.1:$AUTO_PORT/"
fi | tee -a results/evidence/002-web-ui/tc-004-port.txt
```

**预期结果**：
- 自动分配的端口号被检测到（非 0，范围 1024-65535）
- 访问该端口返回 200

### 步骤 4.3：停止进程

```bash
kill $PID4 2>/dev/null || true
sleep 2
```

---

## TC-005: 进程优雅终止

**目标**：向 dsh web 进程发送 SIGTERM 后，进程在合理时间内（<5 秒）退出，退出码为 0 或 143（128+15）。

**前置条件**：
- [ ] TC-001 已通过

**步骤**：

### 步骤 5.1：启动并发送 SIGTERM

```bash
cd /workspace/validations/deepseek-harness
dsh --profile web --host 127.0.0.1 --port 9191 \
  > results/evidence/002-web-ui/tc-005-stdout.log \
  2> results/evidence/002-web-ui/tc-005-stderr.log &
PID5=$!
echo "Started PID: $PID5"
sleep 4
# 检查进程存活
kill -0 $PID5 && echo "Process alive before SIGTERM"
# 发送 SIGTERM
kill -TERM $PID5
sleep 3
# 检查是否退出
if kill -0 $PID5 2>/dev/null; then
  echo "Process still alive after 3s, sending SIGKILL"
  kill -KILL $PID5
  EXIT_CODE="killed"
else
  wait $PID5 2>/dev/null
  EXIT_CODE=$?
fi
echo "TC-005 exit code: $EXIT_CODE" | tee results/evidence/002-web-ui/tc-005-exit.txt
```

**预期结果**：
- 进程在 SIGTERM 后 3 秒内退出
- 退出码为 0 或 143（非强制 KILL）

---

## 证据保存要求

| TC | 证据文件 |
|----|---------|
| TC-001 | `tc-001-stdout.log` + `tc-001-stderr.log` + `tc-001-index.html` + `tc-001-curl-meta.txt` |
| TC-002 | `tc-002-stdout.log` + `tc-002-stderr.log` + `tc-002-curl-meta.txt` |
| TC-003 | `tc-003-stdout.log` + `tc-003-stderr.log` + `tc-003-listen.txt` |
| TC-004 | `tc-004-stdout.log` + `tc-004-stderr.log` + `tc-004-port.txt` |
| TC-005 | `tc-005-stdout.log` + `tc-005-stderr.log` + `tc-005-exit.txt` |
