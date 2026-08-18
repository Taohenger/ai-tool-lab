# Nabledge 离线副本 — 给 Claude Code 用的 Nablarch 6 知识库

本目录是 [nablarch/nabledge](https://github.com/nablarch/nabledge) 仓库的离线副本,专门用于在**无外网/企业内网/沙盒**环境里给 Claude Code 装上 Nablarch 6 框架知识。

> 本副本对应本仓库的 [Nablarch batch 调 API 验证](../validations/nablarch-batch-api/) —— 那个验证工程是 Nablarch 6u3 的,所以这里只拉了 `nabledge-6` 这一个版本。

---

## 一、这是什么 / 能做什么

**Nabledge** 是 Nablarch 官方维护的 **Claude Code Plugin**,把 Nablarch 6 的全部官方文档、Javadoc、最佳实践、处理方式打包成本地知识文件,装到 Claude Code 之后,Claude 回答 Nablarch 问题时直接读本地文件,**不再需要联网查文档**。

| 能力 | 说明 |
|------|------|
| **知识检索** | 问 `BatchAction` / `HttpMessagingClient` / `UniversalDao` 怎么用,Claude 基于本地 28MB 文档答 |
| **代码分析** | `/n6 code-analysis LoginAction` —— 从 Nablarch 视角分析你的项目代码,生成结构/依赖文档 |
| **关键词搜索** | `/n6 keyword-search "<term1> <term2>"` —— 全文本扫描知识文件 |
| **语义搜索** | `/n6 semantic-search "<question>"` —— 自然语言探索式搜索 |

**关键事实**:运行时所有操作都在本地完成 —— 我已 grep 全部 8 个 scripts,确认**没有 `curl`/`wget`/`git fetch`/`http://`** 等任何网络命令,只用 `git rev-parse --show-toplevel` 定位项目根(不发网络请求)。

---

## 二、来源与版本

| 项 | 值 |
|----|----|
| 上游仓库 | https://github.com/nablarch/nabledge |
| 分支 | `main` |
| Plugin 版本 | nabledge-6 v1.0(对应 Nablarch 6u3) |
| License | Apache-2.0 |
| 本副本大小 | 28 MB |
| 获取方式 | `git clone --depth 1 --filter=blob:none --sparse --branch main` + `git sparse-checkout set plugins/nabledge-6` |

---

## 三、目录结构

```
vendor/nabledge-6/
├── README.md              # 官方原版 README(日文,简短)
├── GUIDE-CC.md            # 官方 Claude Code 利用指南(日文)
├── GUIDE-GHC.md           # 官方 GitHub Copilot 利用指南
├── CHANGELOG.md           # 更新日志
├── .claude-plugin/
│   └── plugin.json        # plugin 元数据(name/version/license)
├── commands/
│   └── n6.md              # /n6 命令定义(给 Claude Code 用)
└── skills/nabledge-6/     # ★ 核心 —— 知识本体
    ├── SKILL.md           # skill 入口(决定走哪个 workflow)
    ├── docs/              # Nablarch 6 官方文档完整镜像(6.3 MB,~3400 文件)
    │   ├── about/         # Nablarch 是什么、架构大图、许可证
    │   ├── check/         # security-check 安全审计指南
    │   ├── component/    # 框架组件:adapters / handlers / libraries
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
    ├── knowledge/         # 预处理后的知识资产(21 MB,与 docs/ 同构 + 索引)
    │   ├── index.md       # ★ 全量总索引,workflow 从这里路由
    │   ├── classes.md     # 类清单
    │   ├── assets/        # 主题聚合包(handlers-csrf-... / libraries-http-... 等)
    │   └── (about/check/component/... 与 docs/ 同构)
    ├── scripts/           # 8 个 bash 脚本(全部本地操作,无网络)
    │   ├── find-file.sh          # 找文件
    │   ├── read-file.sh          # 读文件
    │   ├── read-sections.sh      # 批量读章节
    │   ├── keyword-search.sh     # 关键词全文本扫描
    │   ├── prefill-template.sh  # 模板预填
    │   ├── generate-mermaid-skeleton.sh  # 生成 mermaid 图骨架
    │   ├── record-start.sh       # 记录分析开始时间
    │   └── finalize-output.sh    # 计算分析耗时
    └── workflows/        # 4 个工作流定义
        ├── qa.md                 # 问答流程
        ├── keyword-search.md     # 关键词搜索流程
        ├── semantic-search.md   # 语义搜索流程
        └── code-analysis.md     # 代码分析流程(+ template/ 子目录)
```

**问答流程**:`/n6 <问题>` → Claude 读 `knowledge/index.md` 路由 → 读对应 `docs/xxx.md` → 基于本地知识回答。整个流程纯本地。

---

## 四、离线安装手顺(详细步骤)

### 前提
- 已安装 Claude Code(本仓库假设你有专用模型,推理离线)
- 有一个 Nablarch 项目目录(本仓库是 `validations/nablarch-batch-api/`)
- 本副本已就位(`vendor/nabledge-6/`)

### 步骤 1:把 skill 文件拷到项目的 `.claude/skills/`

```bash
# 假设你的 Nablarch 项目根目录是 PROJECT_ROOT
PROJECT_ROOT=/workspace/validations/nablarch-batch-api

# 创建目录(如果不存在)
mkdir -p "$PROJECT_ROOT/.claude/skills"

# 拷贝 skill(注意:目标目录名必须是 nabledge-6,与 SKILL.md 里的 name 一致)
cp -r /workspace/vendor/nabledge-6/skills/nabledge-6 "$PROJECT_ROOT/.claude/skills/"
```

### 步骤 2:把 `/n6` 命令拷到 `.claude/commands/`

```bash
mkdir -p "$PROJECT_ROOT/.claude/commands"
cp /workspace/vendor/nabledge-6/commands/n6.md "$PROJECT_ROOT/.claude/commands/n6.md"
```

### 步骤 3:配置 `.claude/settings.json` 给 scripts 加自动批准

```bash
SETTINGS="$PROJECT_ROOT/.claude/settings.json"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"

# 用 jq 合并权限规则(如果没有 jq,手动编辑也行)
jq '.permissions //= {} | .permissions.allow //= [] |
    .permissions.allow = (.permissions.allow + [
        "Bash(bash *nabledge-6/scripts/*)",
        "Write(.nabledge/**)"
    ] | unique)' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
```

如果离线环境没装 `jq`,手动在 `.claude/settings.json` 写入以下内容即可:

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

### 步骤 4:验证安装

```bash
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/SKILL.md" && echo "✓ skill OK"
ls "$PROJECT_ROOT/.claude/commands/n6.md" && echo "✓ command OK"
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/knowledge/index.md" && echo "✓ knowledge index OK"
ls "$PROJECT_ROOT/.claude/skills/nabledge-6/scripts/" && echo "✓ scripts OK"
```

四个 `✓` 都出现即安装成功。

### 步骤 5:一键安装脚本(可选)

把上面 4 步打包成一个脚本,直接在离线环境跑:

```bash
bash /workspace/vendor/install-offline.sh /workspace/validations/nablarch-batch-api
```

(本仓库已提供 [install-offline.sh](install-offline.sh),见下文。)

### 步骤 6:启动 Claude Code 使用

```bash
cd "$PROJECT_ROOT"
claude  # 启动你的 Claude Code(用你的专用模型)

# 在 Claude Code 里输入:
/n6 BatchAction の createReader で外部 API を呼び出す方法を教えて
/n6 UniversalDao でページング検索を実装したい
/n6 code-analysis FileDeleteAction
```

---

## 五、一键安装脚本

本目录提供 [install-offline.sh](nabledge-6/../install-offline.sh),把步骤 1-4 自动化:

```bash
# 用法
bash vendor/install-offline.sh <目标项目根目录>

# 示例:装到本仓库的 nablarch-batch-api 验证工程
bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api
```

脚本会:
1. 把 `skills/nabledge-6/` 拷到 `<目标>/.claude/skills/`
2. 把 `commands/n6.md` 拷到 `<目标>/.claude/commands/`
3. 在 `<目标>/.claude/settings.json` 加权限(用 `jq`,如果没有则手动写 JSON)
4. 最后验证 4 个关键文件是否就位

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

---

## 七、其他版本(5 / 1.4 / 1.3 / 1.2)获取方式

本副本只拉了 `nabledge-6`(对应 Nablarch 6u3,与本仓库验证工程匹配)。如果需要其他版本,在有网环境执行:

```bash
# 全量 clone(230 MB,含所有版本)
git clone --depth 1 https://github.com/nablarch/nabledge.git

# 或只拉某个版本(推荐,省空间)
mkdir nabledge-sparse && cd nabledge-sparse
git clone --depth 1 --filter=blob:none --sparse --branch main https://github.com/nablarch/nabledge.git
cd nabledge
git sparse-checkout set plugins/nabledge-5   # 或 1.4 / 1.3 / 1.2

# 各版本体积参考
# nabledge-6   28 MB  (Nablarch 6u3)
# nabledge-5   38 MB  (Nablarch 5)
# nabledge-1.4 50 MB  (Nablarch 1.4)
# nabledge-1.3 38 MB  (Nablarch 1.3)
# nabledge-1.2 38 MB  (Nablarch 1.2)
```

拷到离线环境后,按上面步骤 1-3 安装(把 `nabledge-6` 换成对应版本号,命令文件名也对应换:`n5.md` / `n1.4.md` 等)。

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

1. **目录名必须精确**:skill 目标目录名必须是 `nabledge-6`(与 `SKILL.md` frontmatter 里的 `name` 字段一致),否则 Claude Code 识别不到。
2. **scripts 权限**:步骤 3 的 `Bash(bash *nabledge-6/scripts/*)` 规则必须加,否则 Claude 每次调脚本都要你确认。
3. **不要改官方文件**:`vendor/nabledge-6/` 下的 `README.md` / `GUIDE-CC.md` / `SKILL.md` 等都是上游原版,改了会让 diff 变脏。要改就在你的项目里改 `.claude/skills/nabledge-6/` 那份拷贝。
4. **更新**:nabledge 上游更新后,重新 sparse clone 一份覆盖 `vendor/nabledge-6/` 即可。本副本是 `main` 分支的快照,commit 信息见 [git log](https://github.com/nablarch/nabledge/commits/main)。
5. **Claude 推理仍需模型**:本副本只让"知识检索"离线。Claude 本身的推理,如果你用 Anthropic API 仍需联网;用本地模型(你的专用模型)则完全离线。本仓库假设你已有专用模型,推理离线。

---

## 十、参考链接

- 上游仓库:https://github.com/nablarch/nabledge
- Nablarch 官方文档:https://nablarch.github.io/docs/
- Nablarch 框架源码:https://github.com/nablarch
- 本仓库的 Nablarch batch 验证:[validations/nablarch-batch-api/](../validations/nablarch-batch-api/)
