#!/usr/bin/env bash
# ============================================================
# run-006-010-with-key.sh
# 任务 006~010 一键验证脚本 —— 需要配置 DEEPSEEK_API_KEY
#
# 用法（任选其一）：
#   1) export DEEPSEEK_API_KEY="sk-..." && bash harness/scripts/run-006-010-with-key.sh
#   2) DEEPSEEK_API_KEY="sk-..." bash harness/scripts/run-006-010-with-key.sh
#
# 执行范围（5 个任务，约需要 ~5-15 分钟，视模型响应速度）：
#   006 工作区管理与文件操作   （读 README → 新建文件 → 修改内容 → 校验）
#   007 Shell 命令执行与安全性 （ls / cat 只读命令，不做写）
#   008 代码搜索与编辑能力     （grep index.js → 修改函数 → 验证修改）
#   009 Agent 端到端任务执行   （多步：给 sample-project 生成 package.json 脚本）
#   010 会话记录与可追溯性     （检查 sessions/ 目录、.jsonl 文件完整性）
# ============================================================

set -u
ROOT="/workspace/validations/deepseek-harness"
cd "$ROOT" || exit 1

EVIDENCE="$ROOT/results/evidence"
mkdir -p "$EVIDENCE"/{006-files,007-shell,008-code,009-agent,010-session}
TASKS="$ROOT/tasks"
mkdir -p "$TASKS"/{006-files,007-shell,008-code,009-agent,010-session}/results

# ======= 0. 前置检查 =======
echo "===== [0/5] 前置检查：DEEPSEEK_API_KEY + Node.js + dsh ====="
if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  echo "❌ DEEPSEEK_API_KEY 未设置"
  echo "   获取 Key：https://platform.deepseek.com/api_keys"
  echo "   执行：export DEEPSEEK_API_KEY=\"sk-...\""
  exit 2
fi
echo "✅ DEEPSEEK_API_KEY 已设置（长度: ${#DEEPSEEK_API_KEY}）"
echo "✅ Node.js $(node --version), dsh $(dsh --version)"
KEY_PREFIX_OK=true
case "$DEEPSEEK_API_KEY" in
  sk-*) : ;;
  *)   echo "⚠️  Key 不以 sk- 开头，可能无效" ; KEY_PREFIX_OK=false ;;
esac
TIMEOUT_PER_TURN=120   # 每个 headless 任务超时 2 分钟
run_dsh_headless() {
  # $1 = 任务描述，$2 = 输出日志前缀
  local prompt="$1" log_prefix="$2"
  echo "   → 执行 dsh headless prompt（长度=${#prompt}）..."
  timeout "$TIMEOUT_PER_TURN" env DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
    dsh --profile headless "$prompt" \
    > "${log_prefix}-stdout.log" \
    2> "${log_prefix}-stderr.log"
  local ec=$?
  echo "   → Exit code=$ec" | tee -a "${log_prefix}-meta.txt"
  echo "   → STDOUT 行数=$(wc -l < "${log_prefix}-stdout.log") STDERR 行数=$(wc -l < "${log_prefix}-stderr.log")" | tee -a "${log_prefix}-meta.txt"
  return $ec
}

# ======= 任务 006：工作区管理与文件操作 =======
echo ""
echo "===== [1/5] 任务 006 — 工作区管理与文件操作 ====="
TC006_DIR="$EVIDENCE/006-files"
# 准备工作区（拷贝样本项目，避免污染源）
WORKDIR="$ROOT/test-data/sample-project"
# TC-006-1: 让 Agent 读取 README.md 并摘要
echo "[TC-006-1] 读取 test-data/sample-project/README.md 并摘要"
run_dsh_headless "你在目录 $WORKDIR 中工作。只许读写该目录内文件。读取 README.md，输出 20 字以内的项目摘要。" "$TC006_DIR/tc-006-1-read" || true
echo "   → STDOUT（摘要）："
head -5 "$TC006_DIR/tc-006-1-read-stdout.log"

# TC-006-2: 让 Agent 创建一个新文件
NEWFILE="$WORKDIR/generated-by-dsh.txt"
rm -f "$NEWFILE"
echo "[TC-006-2] 在 sample-project 下创建 generated-by-dsh.txt，内容为 \"Hello from DeepSeek Harness 2026-08-14\"，然后退出"
run_dsh_headless "工作目录：$WORKDIR。在此目录中创建文件 generated-by-dsh.txt，内容严格为一行：Hello from DeepSeek Harness 2026-08-14。创建完成后不要做任何其它操作。" "$TC006_DIR/tc-006-2-create" || true
if [ -f "$NEWFILE" ]; then
  echo "   ✅ 文件已创建。内容：$(cat "$NEWFILE")" | tee "$TC006_DIR/tc-006-2-verify.txt"
else
  echo "   ❌ 文件未创建" | tee "$TC006_DIR/tc-006-2-verify.txt"
fi

# TC-006-3: 让 Agent 修改 existing 内容（index.js 尾部加注释）
echo "[TC-006-3] 修改 index.js，在末尾加一行注释 // modified-by-dsh-harness"
INDEX_BACKUP="$WORKDIR/index.js.bak"
cp "$WORKDIR/index.js" "$INDEX_BACKUP"
run_dsh_headless "工作目录：$WORKDIR。修改 index.js 文件，在文件末尾追加一行注释：// modified-by-dsh-harness。只做这一处改动。" "$TC006_DIR/tc-006-3-edit" || true
if grep -q "modified-by-dsh-harness" "$WORKDIR/index.js"; then
  echo "   ✅ 注释行已追加成功" | tee "$TC006_DIR/tc-006-3-verify.txt"
  # 恢复
  cp "$INDEX_BACKUP" "$WORKDIR/index.js" && rm "$INDEX_BACKUP"
else
  echo "   ❌ 未找到追加的注释" | tee "$TC006_DIR/tc-006-3-verify.txt"
  cp "$INDEX_BACKUP" "$WORKDIR/index.js" && rm "$INDEX_BACKUP"
fi
# 删除 006-2 生成的中间文件
rm -f "$NEWFILE"

# ======= 任务 007：Shell 命令执行与安全性 =======
echo ""
echo "===== [2/5] 任务 007 — Shell 命令执行与安全性 ====="
TC007_DIR="$EVIDENCE/007-shell"
echo "[TC-007-1] 让 Agent 执行 ls -la $WORKDIR 并报告文件列表"
run_dsh_headless "在 $WORKDIR 中工作。执行 shell 命令 ls -la，然后以自然语言汇报：列出了多少个文件/目录，其中最大的文件是哪一个（字节数）。" "$TC007_DIR/tc-007-1-ls" || true
head -10 "$TC007_DIR/tc-007-1-ls-stdout.log" | sed 's/^/   /'

echo "[TC-007-2] 让 Agent 执行 cat $WORKDIR/package.json 并复述 name 字段"
run_dsh_headless "在 $WORKDIR 中工作。执行 shell 命令 cat package.json，读取完整 JSON，然后只回答其中的 name 字段值（不要回答其它任何内容）。" "$TC007_DIR/tc-007-2-cat" || true
head -5 "$TC007_DIR/tc-007-2-cat-stdout.log" | sed 's/^/   /'

# ======= 任务 008：代码搜索与编辑能力 =======
echo ""
echo "===== [3/5] 任务 008 — 代码搜索与编辑能力 ====="
TC008_DIR="$EVIDENCE/008-code"
echo "[TC-008-1] 让 Agent 搜索 index.js 中包含 console 的行，回答行号和内容"
run_dsh_headless "在 $WORKDIR 中工作。对 index.js 做内容搜索，找出所有包含 console 的代码行，列出它们的行号和完整内容。只输出搜索结果，不要修改文件。" "$TC008_DIR/tc-008-1-grep" || true
head -15 "$TC008_DIR/tc-008-1-grep-stdout.log" | sed 's/^/   /'

# ======= 任务 009：Agent 端到端多步任务 =======
echo ""
echo "===== [4/5] 任务 009 — Agent 端到端多步任务执行 ====="
TC009_DIR="$EVIDENCE/009-agent"
REPORT="$TC009_DIR/agent-report.txt"
echo "[TC-009] 综合任务：理解 sample-project → 给建议 → 输出 3 点改进"
run_dsh_headless "在 $WORKDIR 中工作。执行多步分析：(1) 读取 README.md 了解项目；(2) 读取 package.json 了解依赖；(3) 读取 index.js 了解实现。最后输出 3 条具体的代码改进建议，每条建议 <= 50 字，编号 1/2/3。" "$TC009_DIR/tc-009-multi-step" || true
echo ""
echo "   === Agent 输出（改进建议）==="
cat "$TC009_DIR/tc-009-multi-step-stdout.log" | sed 's/^/   /'

# ======= 任务 010：会话记录与可追溯性 =======
echo ""
echo "===== [5/5] 任务 010 — 会话记录与可追溯性 ====="
TC010_DIR="$EVIDENCE/010-session"
DSH_HOME_EFF="${DSH_HOME:-$HOME/.deepseek-harness}"
SESSIONS_DIR="$DSH_HOME_EFF/sessions"
{
  echo "DSH_HOME = $DSH_HOME_EFF"
  echo "sessions/ 存在？ "
  if [ -d "$SESSIONS_DIR" ]; then
    echo "YES"
    echo ""
    echo "--- sessions/ 递归列出前 80 行 ---"
    ls -laR "$SESSIONS_DIR" 2>&1 | head -80
    echo ""
    echo "--- 找到的 .jsonl 文件（按 mtime 排序，取最新 3 个）---"
    find "$SESSIONS_DIR" -name "*.jsonl" -printf '%T+ %p %s bytes\n' 2>/dev/null | sort -r | head -3
    echo ""
    echo "--- 最新 jsonl 的前 15 行（无敏感内容打印）---"
    LATEST=$(find "$SESSIONS_DIR" -name "*.jsonl" -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | awk '{print $2}')
    if [ -n "${LATEST:-}" ]; then
      echo "文件：$LATEST"
      head -15 "$LATEST" 2>/dev/null || echo "(无法读取)"
    else
      echo "(无 jsonl 文件)"
    fi
  else
    echo "NO（会话持久化目录未生成）"
  fi
} | tee "$TC010_DIR/tc-010-session-evidence.txt"

# ======= 总结 =======
echo ""
echo "================================================================="
echo "  任务 006-010 执行完毕"
echo "================================================================="
echo "  证据目录：$EVIDENCE/{006,007,008,009,010}-*/"
echo "  STDOUT 日志名格式：<tc>-stdout.log"
echo "  请逐一打开验证 Agent 是否按预期做了文件修改/Shell 执行。"
echo "  然后在 tasks/006-010/results/ 下编写 result.md 总结结果。"
echo "================================================================="
