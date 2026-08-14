# 已知陷阱（记忆）

验证 DeepSeek Harness 时遇到的坑 — 持续追加，每个坑写清楚：
1. 触发条件
2. 实际现象
3. 正确做法（如果有）

## 坑 1：Headless 模式需要 API Key

- 触发条件：`dsh --profile headless "列出 test-data 目录"` 之类需要实际跑 Agent 的命令
- 现象：TBD（待实测）
- 正确做法：需要先在 `$DSH_HOME/.credentials.yaml` 写入 DeepSeek API Key，否则只做无模型验证或标记为 blocked

## 坑 2：Web UI 默认 host 是回环地址 + 坑 6：--host 0.0.0.0 被故意禁用（安全）

- 触发条件：跑在远程服务器 / 容器中，想用浏览器访问外部 IP
- 现象：`dsh web` 启动后只能本机访问；加 `--host 0.0.0.0` 会直接报错退出
- 报错：`error: --host 0.0.0.0 is intentionally not supported yet for safety: it would expose remote code execution to the network; use 127.0.0.1 instead`
- 正确做法：**不要用 `--host 0.0.0.0`**，改用 SSH 端口转发或反向代理：
  - SSH 本地转发：`ssh -L 3080:127.0.0.1:3080 user@remote-host`
  - Nginx 反向代理：`proxy_pass http://127.0.0.1:3080;` + WAF/IP 白名单

## 坑 3：版本要求是 Node.js 22.19+ 或 24+

- 触发条件：22.18 或 20.x LTS
- 现象：pnpm / npm 安装直接 engines 报错
- 正确做法：升级 Node.js

## 坑 4：v0.1 是开发者预览版

- 触发条件：写了很多 profile patch / 插件脚本
- 现象：升级后配置不兼容（官方明确警告）
- 正确做法：结论里标注"仅适用于 v0.1.0-rc.x"

## 坑 5：`dsh plugin` 必须带 `--profile <name>`

- 触发条件：直接跑 `dsh plugin --help` 或 `dsh plugin add foo`
- 现象：报错 `error: required option '--profile <name>' not specified`
- 正确做法：把 `--profile <name>` 加在 `plugin` 子命令**前**，例如：
  - `dsh plugin --profile web --help`
  - `dsh plugin --profile tui add <package>`

## 坑 7：`dsh plugin` 子命令底层是 pnpm（help 会显示 pnpm help）

- 触发条件：`dsh plugin --profile web --help`
- 现象：显示的是 **pnpm 10.5.2 help**（`add / install / remove / list` 等命令），而非 DSH 自定义 help
- 原因：DSH 插件管理直接封装了 pnpm（npm 包管理），因为"DSH 插件 = npm 包"
- 正确做法：这是预期行为不是 bug。`dsh plugin add <pkg>` = 给指定 profile 执行 `pnpm add <pkg>`

## 坑 8：v0.1.0-rc.6 CLI 只有 2 个内置 profile（web / headless），其余"四种模式"在 Web UI 内切换

- 触发条件：尝试 `dsh --profile tui/minimal/ptc/creative/standard`
- 现象：报错 `dsh: profile "tui" does not exist; create it with 'dsh plugin --profile tui add <package>'`
- 原因：官方 INFO 文档中"标准/PTC/极简/创造 四种运行模式"指的是 Web UI 内的 Agent 工作模式切换（前端预设），不是 CLI 层的 profile 名
- 正确做法：CLI 层只有 `--profile web` 和 `--profile headless` 两个内置 profile；要创建自定义 profile，使用 `dsh plugin --profile <newname> add <pkg>` 组合
- web profile 配置行数 490（含大量 UI 插件），headless 333 行（无 UI）
