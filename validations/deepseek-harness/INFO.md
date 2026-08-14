# INFO.md — DeepSeek Harness 官方信息汇总

## 资源链接

| 资源 | 链接 |
|------|------|
| 官方仓库 | https://github.com/deepseek-ai/deepseek-harness |
| 官网首页 | https://deepseek.com/harness/en/ |
| npm 包 | `@deepseek-ai/dsh` |
| Python SDK | `python/` 目录下 |
| 论文（Cordis） | A Programming Paradigm for Spatiotemporal Composability（北大 × DeepSeek） |

## 发布信息

| 项目 | 内容 |
|------|------|
| 发布日期 | 2026-08-13（v0.1 开发者预览版） |
| 开源协议 | MIT |
| 版本号 | v0.1.0-rc.6（当前） |
| 状态 | 开发者预览版（会有破坏性变更，非生产稳定） |

## 安装方式

### 方式 1：npx 一键体验（最快）
```bash
npx @deepseek-ai/dsh web
# 默认地址 http://127.0.0.1:3080
```

### 方式 2：全局安装（推荐日常使用）
```bash
npm install -g @deepseek-ai/dsh
dsh web
```

### 方式 3：源码构建
```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

### 方式 4：Python SDK
```bash
pip install deepseek-harness-sdk
```

## 前置要求

- **Node.js**：^22.19.0 或 >=24.0.0（用 `node --version` 检查）
- **无桌面 Electron**：Web UI 架构（浏览器访问）
- **配置目录**：`$DSH_HOME`（默认 `~/.deepseek-harness`）
  - 凭据：`$DSH_HOME/.credentials.yaml`（只写，界面只显示脱敏描述符）
  - Profile：`$DSH_HOME/profiles/`

## 核心命令速览

```bash
# 运行 profile
dsh web [--host 127.0.0.1] [--port 3080]   # Web UI
dsh --profile headless "任务描述"          # 单次任务、无界面、打印结果退出
dsh --profile tui                         # 终端界面

# 配置与调试
dsh --profile <name> --dump-config        # 打印组合后的完整配置
dsh --profile <name> --dump-default-config # 打印默认配置（不含用户层）

# 插件管理
dsh plugin --profile <name> add <pkg>     # 给指定 profile 装插件
dsh plugin --profile <name> remove <pkg>  # 卸载插件
dsh plugin --profile <name> list          # 列插件
```

## 四种运行模式

| 模式 | 说明 |
|------|------|
| 标准模式 | 完整工具组合（文件编辑、Shell、检索、技能、规划、子 Agent、工作流） |
| PTC 模式 | Programmatic Tool Calling：模型生成 TS 代码，把多轮工具操作合并成一次执行 |
| 极简模式 | 仅保留 Shell 与文件编辑两个工具，最小环境模型基准测试 |
| 创造模式 | 检查运行时、试验 Cordis 插件，创作自定义模式 |

## 架构设计要点

### 一切皆插件（Cordis 元框架）
- 模型适配器、工具、技能、会话、沙箱、存储、Agent 循环、调度、UI → 全部插件
- 无需改源码，通过新增/替换插件定制任意模块

### 两大核心特性
1. **时间可组合性**：插件卸载时，能完整、安全地撤销它给系统带来的所有副作用（可逆效应）
2. **空间可组合性**：依赖的服务出现/消失/替换时，系统自动协调加载与退出

### 可追溯性原则
- append-only 会话日志：模型看到的一字节都会被记录
- 上下文压缩不删原始历史，仅用替换事件改变模型此后看到的表象
- Trajectory 视图：可恢复、分叉、检索、回放

### 事件链执行模型
```
turn/start → agent/pre-step → agent/request → llm/stream
  → tool/call → tools/pre-execute → tools/execute → tools/post-execute
  → tool/result → step/end → turn/end
```
（每一步都是扩展点：插件可拦截、改写、拒绝、加策略）

## 官方宣称特性（来源：README）

- 文件系统浏览、编辑、创建、删除
- Shell 命令执行（实时输出流）
- 仓库级搜索（grep / AST / 符号）
- 网络搜索与 Web 读取
- Plan + Todo 管理
- 技能（SKILL.md 自动发现）
- 子 Agent 分派
- 审批策略（高风险操作需用户确认）
- 多模型多 Provider（DeepSeek、OpenAI、Anthropic、Azure、Bedrock、Vertex…）
- 可恢复、分叉、回放的会话系统

## 与竞品对比

| 维度 | DSH | Claude Code | OpenAI Codex |
|------|-----|-------------|--------------|
| 定位 | Agent 运行时底座 | 成品 Coding Agent | 成品 Coding Agent |
| 架构哲学 | 一切皆插件，可自由组合 | 固定架构 + 工具插件 | 固定架构 + MCP 工具 |
| 开源 | ✅ MIT | ❌ 闭源 | ❌ 闭源 |
| 可追溯性 | ✅ append-only + 回放 | ✅ 类似能力 | ✅ 类似能力 |
| 是否需要 Electron | ❌（浏览器 Web UI） | ✅（桌面 TUI） | ✅（桌面 TUI） |
| 模型绑定 | 支持所有主流 | 仅 Anthropic 模型 | 仅 OpenAI 模型 |

## 已知早期体验反馈

- 优点：架构先进、可定制性高、Token 效率较好、性能快
- 痛点：任务耗时较长、Token 消耗仍有优化空间、v0.1 预览版会有破坏性变更
