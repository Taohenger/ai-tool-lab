#!/bin/bash
# ============================================================
# Nabledge-6 离线安装脚本
# 把 vendor/nabledge-6/ 的 skill + command 装到目标项目的 .claude/
# ============================================================
#
# 用法:
#   bash install-offline.sh <目标项目根目录>
#
# 示例:
#   bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api
#
# 做的事:
#   1. 把 skills/nabledge-6/ 拷到 <目标>/.claude/skills/
#   2. 把 commands/n6.md 拷到 <目标>/.claude/commands/
#   3. 在 <目标>/.claude/settings.json 加 scripts 权限(用 jq,没有则手写 JSON)
#   4. 验证 4 个关键文件是否就位
# ============================================================
set -euo pipefail

# 解析参数
if [ $# -lt 1 ]; then
    echo "用法: bash $0 <目标项目根目录>"
    echo "示例: bash $0 /workspace/validations/nablarch-batch-api"
    exit 1
fi

PROJECT_ROOT="$1"
VENDOR_DIR="$(cd "$(dirname "$0")" && pwd)/nabledge-6"

# 校验
if [ ! -d "$VENDOR_DIR" ]; then
    echo "错误: 找不到 vendor 目录 $VENDOR_DIR"
    echo "请确认本脚本位于 vendor/ 下,且 vendor/nabledge-6/ 存在"
    exit 1
fi
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "错误: 目标项目目录不存在: $PROJECT_ROOT"
    exit 1
fi
if [ ! -f "$VENDOR_DIR/skills/nabledge-6/SKILL.md" ]; then
    echo "错误: $VENDOR_DIR/skills/nabledge-6/SKILL.md 不存在"
    echo "vendor/nabledge-6/ 内容不完整,请重新 sparse clone"
    exit 1
fi

SKILL_SRC="$VENDOR_DIR/skills/nabledge-6"
CMD_SRC="$VENDOR_DIR/commands/n6.md"

SKILL_DST="$PROJECT_ROOT/.claude/skills/nabledge-6"
CMD_DST_DIR="$PROJECT_ROOT/.claude/commands"
SETTINGS="$PROJECT_ROOT/.claude/settings.json"

echo "=== Nabledge-6 离线安装 ==="
echo "源:   $VENDOR_DIR"
echo "目标: $PROJECT_ROOT"
echo

# 步骤 1: 拷贝 skill
echo "[1/4] 拷贝 skill 文件..."
mkdir -p "$PROJECT_ROOT/.claude/skills"
if [ -d "$SKILL_DST" ]; then
    echo "  已存在旧安装,覆盖..."
    rm -rf "$SKILL_DST"
fi
cp -r "$SKILL_SRC" "$SKILL_DST"
echo "  ✓ $SKILL_DST"

# 步骤 2: 拷贝 command
echo "[2/4] 拷贝 /n6 命令..."
mkdir -p "$CMD_DST_DIR"
cp "$CMD_SRC" "$CMD_DST_DIR/n6.md"
echo "  ✓ $CMD_DST_DIR/n6.md"

# 步骤 3: 配置 settings.json
echo "[3/4] 配置 .claude/settings.json 权限..."
mkdir -p "$PROJECT_ROOT/.claude"
if [ ! -f "$SETTINGS" ]; then
    echo '{}' > "$SETTINGS"
fi

if command -v jq &> /dev/null; then
    tmp=$(mktemp)
    jq '.permissions //= {} | .permissions.allow //= [] |
        .permissions.allow = (.permissions.allow + [
            "Bash(bash *nabledge-6/scripts/*)",
            "Write(.nabledge/**)"
        ] | unique)' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    echo "  ✓ 用 jq 加了权限(jq 可用)"
else
    echo "  ⚠ jq 不可用,请手动在 $SETTINGS 加入:"
    cat <<'EOF'

  {
    "permissions": {
      "allow": [
        "Bash(bash *nabledge-6/scripts/*)",
        "Write(.nabledge/**)"
      ]
    }
  }
EOF
fi

# 步骤 4: 验证
echo "[4/4] 验证安装..."
ok=true
[ -f "$SKILL_DST/SKILL.md" ] && echo "  ✓ SKILL.md" || { echo "  ✗ SKILL.md 缺失"; ok=false; }
[ -f "$CMD_DST_DIR/n6.md" ] && echo "  ✓ commands/n6.md" || { echo "  ✗ commands/n6.md 缺失"; ok=false; }
[ -f "$SKILL_DST/knowledge/index.md" ] && echo "  ✓ knowledge/index.md" || { echo "  ✗ knowledge/index.md 缺失"; ok=false; }
[ -d "$SKILL_DST/scripts" ] && echo "  ✓ scripts/" || { echo "  ✗ scripts/ 缺失"; ok=false; }

echo
if [ "$ok" = true ]; then
    echo "=== 安装成功 ==="
    echo
    echo "下一步: 启动 Claude Code,在项目里输入:"
    echo "  /n6 <你的 Nablarch 6 问题>"
    echo
    echo "示例:"
    echo "  /n6 BatchAction の createReader で外部 API を呼び出す方法を教えて"
    echo "  /n6 UniversalDao でページング検索を実装したい"
    echo "  /n6 code-analysis FileDeleteAction"
else
    echo "=== 安装失败,请检查上面的 ✗ 项 ==="
    exit 1
fi
