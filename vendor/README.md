# Nabledge 离线副本 — 给 Claude Code 用的 Nablarch 全版本知识库

本目录是 [nablarch/nabledge](https://github.com/nablarch/nabledge) 仓库的**完整离线副本**,包含所有 5 个 Nablarch 版本的 plugin,专门用于在**无外网/企业内网/沙盒**环境里给 Claude Code 装上 Nablarch 框架知识。

> 本副本对应本仓库的 [Nablarch batch 调 API 验证](../validations/nablarch-batch-api/) —— 那个验证工程是 Nablarch 6u3,所以默认装 `nabledge-6`;如果你要维护其他版本的 Nablarch 工程,选对应版本装即可。

---

## 一、这是什么 / 能做什么

**Nabledge** 是 Nablarch 官方维护的 **Claude Code Plugin**,把 Nablarch 的全部官方文档、Javadoc、最佳实践、处理方式打包成本地知识文件。装到 Claude Code 之后,Claude 回答 Nablarch 问题时直接读本地文件,**不再需要联网查文档**。

| 能力 | 说明 |
|------|------|
| **知识检索** | 问 `BatchAction` / `HttpMessagingClient` / `UniversalDao` 怎么用,Claude 基于本地文档答 |
| **代码分析** | `/n6 code-analysis LoginAction` —— 从 Nablarch 视角分析项目代码,生成结构/依赖文档 |
| **关键词搜索** | `/n6 keyword-search "<term1> <term2>"` —— 全文本扫描知识文件 |
| **语义搜索** | `/n6 semantic-search "<question>"` —— 自然语言探索式搜索 |

**关键事实**:运行时所有操作都在本地完成 —— 我已 grep 全部 scripts,确认**没有 `curl`/`wget`/`git fetch`/`http://`** 等任何网络命令,只用 `git rev-parse --show-toplevel` 定位项目根(不发网络请求)。

---

## 二、来源与版本

| 项 | 值 |
|----|----|
| 上游仓库 | https://github.com/nablarch/nabledge |
| 分支 | `main` |
| License | Apache-2.0(见 [LICENSE](nabledge/LICENSE)) |
| 本副本总大小 | 191 MB(5 个 plugin) |
| 获取方式 | `git clone --depth 1 https://github.com/nablarch/nabledge.git` 后删除 `.git/` |

### 包含的版本

| Plugin | 对应 Nablarch | 大小 | 命令 |
|--------|-------------|------|------|
| **nabledge-6** | Nablarch 6u3 | 28 MB | `/n6` |
| **nabledge-5** | Nablarch 5 | 38 MB | `/n5` |
| **nabledge-1.4** | Nablarch 1.4 | 50 MB | `/n1.4` |
| **nabledge-1.3** | Nablarch 1.3 | 38 MB | `/n1.3` |
| **nabledge-1.2** | Nablarch 1.2 | 38 MB | `/n1.2` |

---

## 三、目录结构

```
vendor/
├── README.md                 # 本文件(离线安装手顺)
├── install-offline.sh        # 一键安装脚本(支持多版本,见下)
└── nabledge/                 # nablarch/nabledge 仓库完整副本(去 .git)
    ├── README.md              # 官方原版 README
    ├── CHANGELOG.md           # 更新日志
    ├── LICENSE                # Apache-2.0
    ├── setup-cc.sh            # 官方在线安装脚本(需联网,本副本用 install-offline.sh 替代)
    ├── setup-ghc.sh           # 官方 GitHub Copilot 安装脚本
    ├── .claude-plugin/
    │   └── marketplace.json   # plugin marketplace 元数据
    └── plugins/               # ★ 5 个版本 plugin
        ├── nabledge-6/        # Nablarch 6u3(28MB)
        ├── nabledge-5/        # Nablarch 5(38MB)
        ├── nabledge-1.4/      # Nablarch 1.4(50MB)
        ├── nabledge-1.3/      # Nablarch 1.3(38MB)
        └── nabledge-1.2/      # Nablarch 1.2(38MB)
```

### 每个 plugin 内部结构(以 nabledge-6 为例,其他版本同构)

```
plugins/nabledge-6/
├── README.md              # 该版本说明
├── GUIDE-CC.md            # Claude Code 利用指南
├── GUIDE-GHC.md           # GitHub Copilot 利用指南
├── CHANGELOG.md           # 该版本更新日志
├── .claude-plugin/
│   └── plugin.json        # plugin 元数据(name/version/license)
├── commands/
│   └── n6.md              # /n6 命令定义(给 Claude Code 用)
└── skills/nabledge-6/     # ★ 核心 — 知识本体
    ├── SKILL.md           # skill 入口(决定走哪个 workflow)
    ├── docs/              # 官方文档完整镜像
    │   ├── about/         # Nablarch 是什么、架构大图、许可证
    │   ├── check/         # security-check 安全审计
    │   ├── component/     # 框架组件:adapters / handlers / libraries
    │   ├── development-tools/  # java-static-analysis / testing-framework / toolbox
    │   ├── guide/         # biz-samples 业务样例 / nablarch-patterns 模式集
    │   ├── javadoc/       # 类级 Javadoc(BatchAction / UniversalDao / Logger 等几百个)
    │   ├── processing-pattern/  # ★ 处理方式
    │   │   ├── nablarch-batch/       # ← 本仓库验证对应
    │   │   ├── http-messaging/        # Nablarch HTTP 调用(本验证的备选方案)
    │   │   ├── db-messaging/
    │   │   ├── mom-messaging/
    │   │   ├── jakarta-batch/
    │   │   ├── restful-web-service/
    │   │   └── web-application/
    │   ├── releases/      # 版本发布说明
    │   └── setup/         # blank-project / cloud-native / configuration / setting-guide
    ├── knowledge/         # 预处理后的知识资产(与 docs/ 同构 + 索引)
    │   ├── index.md       # ★ 全量总索引,workflow 从这里路由
    │   ├── classes.md     # 类清单
    │   ├── assets/        # 主题聚合包(handlers-csrf-... / libraries-http-... 等)
    │   └── (about/check/component/... 与 docs/ 同构)
    ├── scripts/           # bash 脚本(全部本地操作,无网络)
    │   ├── find-file.sh          # 找文件
    │   ├── read-file.sh          # 读文件
    │   ├── read-sections.sh      # 批量读章节
    │   ├── keyword-search.sh     # 关键词全文本扫描
    │   ├── prefill-template.sh   # 模板预填
    │   ├── generate-mermaid-skeleton.sh  # 生成 mermaid 图骨架
    │   ├── record-start.sh       # 记录分析开始时间
    │   └── finalize-output.sh    # 计算分析耗时
    └── workflows/        # 4 个工作流定义
        ├── qa.md                 # 问答流程
        ├── keyword-search.md     # 关键词搜索流程
        ├── semantic-search.md    # 语义搜索流程
        └── code-analysis.md     # 代码分析流程(+ template/ 子目录)
```

**问答流程**:`/n6 <问题>` → Claude 读 `knowledge/index.md` 路由 → 读对应 `docs/xxx.md` → 基于本地知识回答。整个流程纯本地。

---

## 四、离线安装手顺(详细步骤)

### 前提
- 已安装 Claude Code(本仓库假设你有专用模型,推理离线)
- 有一个 Nablarch 项目目录(本仓库是 `validations/nablarch-batch-api/`)
- 本副本已就位(`vendor/nabledge/`)

### 方式 A:一键安装(推荐)

```bash
# 默认装 Nablarch 6
bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api

# 装 Nablarch 5
bash vendor/install-offline.sh -v 5 /path/to/nablarch5-project

# 全装(5 个版本一起装到同一个项目)
bash vendor/install-offline.sh -v all /path/to/project
```

脚本会自动完成 4 步(每个版本):拷 skill → 拷 command → 配 settings.json 权限 → 验证 4 个关键文件。

### 方式 B:手动安装

如果不方便跑脚本,手动 4 步(以 v6 为例,其他版本把 `6` 换成对应版本号):

#### 步骤 1:把 skill 文件拷到项目的 `.claude/skills/`

```bash
PROJECT_ROOT=/workspace/validations/nablarch-batch-api
mkdir -p "$PROJECT_ROOT/.claude/skills"
cp -r vendor/nabledge/plugins/nabledge-6/skills/nabledge-6 "$PROJECT_ROOT/.claude/skills/"
```

#### 步骤 2:把 `/n6` 命令拷到 `.claude/commands/`

```bash
mkdir -p "$PROJECT_ROOT/.claude/commands"
cp vendor/nabledge/plugins/nabledge-6/commands/n6.md "$PROJECT_ROOT/.claude/commands/n6.md"
```

#### 步骤 3:配置 `.claude/settings.json` 给 scripts 加自动批准

```bash
SETTINGS="$PROJECT_ROOT/.claude/settings.json"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
jq '.permissions //= {} | .permissions.allow //= [] |
    .permissions.allow = (.permissions.allow + [
        "Bash(bash *nabledge-6/scripts/*)",
        "Write(.nabledge/**)"
    ] | unique)' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
```

如果离线环境没装 `jq`,手动在 `.claude/settings.json` 写入:

```json
{
  "permissions": {
    "allow": [
      "Bash(bash *nabledge-6/scripts/*)",
      "Write(.nabledge/**)"
    ]
  }
}
```

#### 步骤 4:验证安装

```bash
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/SKILL.md" && echo "✓ skill OK"
ls "$PROJECT_ROOT/.claude/commands/n6.md" && echo "✓ command OK"
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/knowledge/index.md" && echo "✓ knowledge index OK"
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/scripts/" && echo "✓ scripts OK"
```

四个 `✓` 都出现即安装成功。装其他版本把命令里的 `6` 换成 `5` / `1.4` / `1.3` / `1.2`。

### 步骤 5:启动 Claude Code 使用

```bash
cd "$PROJECT_ROOT"
claude  # 启动你的 Claude Code(用你的专用模型)

# 在 Claude Code 里输入:
/n6 BatchAction の createReader で外部 API を呼び出す方法を教えて
/n6 UniversalDao でページング検索を実装したい
/n6 code-analysis FileDeleteAction
```

---

## 五、一键安装脚本详解

[install-offline.sh](install-offline.sh) 支持 5 个版本 + `all` 全装:

| 用法 | 说明 |
|------|------|
| `bash install-offline.sh <项目>` | 默认装 v6 |
| `bash install-offline.sh -v 5 <项目>` | 装 v5 |
| `bash install-offline.sh -v 1.4 <项目>` | 装 v1.4 |
| `bash install-offline.sh -v all <项目>` | 全装 5 个版本 |
| `bash install-offline.sh -h` | 看帮助 |

**多版本并存**:同一个项目可以装多个版本(如同时装 v5 和 v6),scripts 权限会累积到 settings.json。装完后用 `/n5` 问 Nablarch 5 问题、`/n6` 问 Nablarch 6 问题,两套知识互不干扰。

---

## 六、使用方法

### 基本问答

```bash
/n6 ウェブアプリでUniversalDaoを使ったページング検索を実装したい
/n6 常駐バッチでのエラーハンドリング方式を調べたい
/n6 トランザクション管理ハンドラを設定する方法を教えて
```

> **提示**:问题里带上"处理方式"(web/batch/messaging)和"目的"(想知道实现方法/查配置),Claude 能更准地路由到对应文档,无需追问。

### 代码分析

```bash
/n6 code-analysis LoginAction
```

输出:摘要返回主上下文,详细分析写到 `.nabledge/YYYYMMDD/code-analysis-<target>.md`。

### 关键词搜索(精确,基于词)

```bash
/n6 keyword-search "BatchAction HttpMessagingClient"
```

### 语义搜索(探索式,自然语言)

```bash
/n6 semantic-search "バッチ起動時に外部APIを呼び出したい"
```

> 把命令里的 `/n6` 换成 `/n5` / `/n1.4` / `/n1.3` / `/n1.2` 即可对应其他版本。

---

## 七、选哪个版本?

| 你的场景 | 装哪个 |
|----------|--------|
| 维护 Nablarch 6u3 工程(本仓库验证场景) | `nabledge-6` |
| 维护 Nablarch 5 工程 | `nabledge-5` |
| 维护 Nablarch 1.4 工程 | `nabledge-1.4` |
| 维护 Nablarch 1.3 工程 | `nabledge-1.3` |
| 维护 Nablarch 1.2 工程 | `nabledge-1.2` |
| 同时维护多个版本(如做迁移) | `bash install-offline.sh -v all <项目>` |

**不确定版本?** 看你 Nablarch 工程 `pom.xml` 里的 `nablarch-bom` 版本:
- `6.x.x` → nabledge-6
- `5.x.x` → nabledge-5
- `1.4.x` → nabledge-1.4
- `1.3.x` → nabledge-1.3
- `1.2.x` → nabledge-1.2

---

## 八、与本仓库 Nablarch batch 验证的关系

本仓库的 [validations/nablarch-batch-api/](../validations/nablarch-batch-api/) 是 Nablarch 6u3 的 batch 工程,验证了"batch 程序里调用外部 HTTP API"。装上 nabledge-6 后,Claude 在那个工程里能直接回答:

- `BatchAction` 的 `createReader` / `handle` 怎么写(本验证改的就是这两个方法)
- `HttpMessagingClient`(Nablarch HTTP Messaging)怎么配 —— 本验证的备选方案,javadoc 在 `docs/javadoc/` 下
- `SystemRepository` 怎么读 properties(本验证读 `externalApi.helloUrl` 用的就是它)
- `Logger` / `LoggerManager` 怎么用(本验证用 `LOGGER.logInfo` 输出 API 调用结果)

**推荐**:在 nablarch-batch-api 工程里装一遍 nabledge-6,后续开发/排错时直接 `/n6` 问,不用每次查 GitHub 文档。

```bash
# 一键装到验证工程
bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api
```

---

## 九、注意事项

1. **目录名必须精确**:skill 目标目录名必须是 `nabledge-6` / `nabledge-5` 等(与 `SKILL.md` frontmatter 里的 `name` 字段一致),否则 Claude Code 识别不到。
2. **scripts 权限**:步骤 3 的 `Bash(bash *nabledge-6/scripts/*)` 规则必须加,否则 Claude 每次调脚本都要你确认。多版本并存时每个版本都要加一条。
3. **不要改官方文件**:`vendor/nabledge/` 下的所有文件都是上游原版,改了会让 diff 变脏。要改就在你的项目里改 `.claude/skills/nabledge-X/` 那份拷贝。
4. **更新**:nabledge 上游更新后,重新全量 clone 一份覆盖 `vendor/nabledge/` 即可:
   ```bash
   cd /tmp && git clone --depth 1 https://github.com/nablarch/nabledge.git
   rm -rf /workspace/vendor/nabledge
   cp -r nabledge /workspace/vendor/nabledge
   rm -rf /workspace/vendor/nabledge/.git /tmp/nabledge
   ```
5. **Claude 推理仍需模型**:本副本只让"知识检索"离线。Claude 本身的推理,如果你用 Anthropic API 仍需联网;用本地模型(你的专用模型)则完全离线。本仓库假设你已有专用模型,推理离线。

---

## 十、参考链接

- 上游仓库:https://github.com/nablarch/nabledge
- Nablarch 官方文档:https://nablarch.github.io/docs/
- Nablarch 框架源码:https://github.com/nablarch
- 本仓库的 Nablarch batch 验证:[validations/nablarch-batch-api/](../validations/nablarch-batch-api/)
