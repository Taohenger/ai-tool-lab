#!/bin/bash
# ============================================================
# Nabledge 离线安装脚本(多版本)
# 把 vendor/nabledge/plugins/nabledge-<v>/ 的 skill + command 装到目标项目的 .claude/
# ============================================================
#
# 用法:
#   bash install-offline.sh [-v <版本>] <目标项目根目录>
#
# 参数:
#   -v <版本>  要安装的 Nablarch 版本:6 / 5 / 1.4 / 1.3 / 1.2 / all
#              默认: 6
#              all = 安装全部 5 个版本(适合需要同时维护多版本 Nablarch 工程的场景)
#
# 示例:
#   # 默认装 Nablarch 6
#   bash vendor/install-offline.sh /workspace/validations/nablarch-batch-api
#
#   # 装 Nablarch 5
#   bash vendor/install-offline.sh -v 5 /path/to/nablarch5-project
#
#   # 全装(6 + 5 + 1.4 + 1.3 + 1.2)
#   bash vendor/install-offline.sh -v all /path/to/project
#
# 做的事(每个版本):
#   1. 把 skills/nabledge-<v>/ 拷到 <目标>/.claude/skills/
#   2. 把 commands/n<v>.md 拷到 <目标>/.claude/commands/
#   3. 在 <目标>/.claude/settings.json 加 scripts 权限(用 jq,没有则提示手写)
#   4. 验证关键文件是否就位
# ============================================================
set -euo pipefail

# 支持的版本
ALL_VERSIONS=(6 5 1.4 1.3 1.2)

# 解析参数
VERSION="6"
while [ $# -gt 0 ]; do
    case "$1" in
        -v)
            shift
            VERSION="$1"
            shift
            ;;
        -h|--help)
            sed -n '2,30p' "$0"
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

PROJECT_ROOT="${1:-}"
if [ -z "$PROJECT_ROOT" ]; then
    echo "用法: bash $0 [-v <版本>] <目标项目根目录>"
    echo "版本可选: ${ALL_VERSIONS[*]} 或 all(默认: 6)"
    exit 1
fi

# 决定要装哪些版本
if [ "$VERSION" = "all" ]; then
    VERSIONS=("${ALL_VERSIONS[@]}")
else
    # 校验
    valid=false
    for av in "${ALL_VERSIONS[@]}"; do
        [ "$VERSION" = "$av" ] && { valid=true; break; }
    done
    if [ "$valid" = false ]; then
        echo "错误: 未知版本 '$VERSION'。可用: ${ALL_VERSIONS[*]} 或 all"
        exit 1
    fi
    VERSIONS=("$VERSION")
fi

VENDOR_DIR="$(cd "$(dirname "$0")" && pwd)/nabledge"

# 校验
if [ ! -d "$VENDOR_DIR/plugins" ]; then
    echo "错误: 找不到 vendor 目录 $VENDOR_DIR/plugins"
    echo "请确认本脚本位于 vendor/ 下,且 vendor/nabledge/ 存在"
    exit 1
fi
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "错误: 目标项目目录不存在: $PROJECT_ROOT"
    exit 1
fi

echo "=== Nabledge 离线安装 ==="
echo "源:     $VENDOR_DIR"
echo "目标:   $PROJECT_ROOT"
echo "版本:   ${VERSIONS[*]}"
echo

# 安装单个版本的函数
install_one() {
    local v="$1"
    local plugin_dir="$VENDOR_DIR/plugins/nabledge-${v}"

    if [ ! -d "$plugin_dir" ]; then
        echo "  ✗ nabledge-${v} 目录不存在: $plugin_dir"
        return 1
    fi
    if [ ! -f "$plugin_dir/skills/nabledge-${v}/SKILL.md" ]; then
        echo "  ✗ nabledge-${v} 内容不完整(SKILL.md 缺失)"
        return 1
    fi

    local skill_src="$plugin_dir/skills/nabledge-${v}"
    local cmd_src="$plugin_dir/commands/n${v}.md"
    local skill_dst="$PROJECT_ROOT/.claude/skills/nabledge-${v}"
    local cmd_dst_dir="$PROJECT_ROOT/.claude/commands"

    echo "--- 安装 nabledge-${v} ---"

    # 1. 拷贝 skill
    mkdir -p "$PROJECT_ROOT/.claude/skills"
    if [ -d "$skill_dst" ]; then
        echo "  已存在旧安装,覆盖"
        rm -rf "$skill_dst"
    fi
    cp -r "$skill_src" "$skill_dst"
    echo "  ✓ skill -> $skill_dst"

    # 2. 拷贝 command
    mkdir -p "$cmd_dst_dir"
    if [ -f "$cmd_src" ]; then
        cp "$cmd_src" "$cmd_dst_dir/n${v}.md"
        echo "  ✓ command -> $cmd_dst_dir/n${v}.md"
    else
        echo "  ⚠ command 文件 $cmd_src 不存在,跳过"
    fi

    # 3. 配置 settings.json
    local settings="$PROJECT_ROOT/.claude/settings.json"
    mkdir -p "$PROJECT_ROOT/.claude"
    [ -f "$settings" ] || echo '{}' > "$settings"

    if command -v jq &> /dev/null; then
        local tmp
        tmp=$(mktemp)
        jq --arg v "$v" '.permissions //= {} | .permissions.allow //= [] |
            .permissions.allow = (.permissions.allow + [
                ("Bash(bash *nabledge-" + $v + "/scripts/*)"),
                "Write(.nabledge/**)"
            ] | unique)' "$settings" > "$tmp" && mv "$tmp" "$settings"
        echo "  ✓ settings.json 加了权限(jq 可用)"
    else
        echo "  ⚠ jq 不可用,请手动在 $settings 加入:"
        echo "     \"Bash(bash *nabledge-${v}/scripts/*)\""
    fi

    # 4. 验证
    local ok=true
    [ -f "$skill_dst/SKILL.md" ] && echo "  ✓ SKILL.md" || { echo "  ✗ SKILL.md 缺失"; ok=false; }
    [ -f "$cmd_dst_dir/n${v}.md" ] && echo "  ✓ commands/n${v}.md" || { echo "  ✗ commands/n${v}.md 缺失"; ok=false; }
    [ -f "$skill_dst/knowledge/index.md" ] && echo "  ✓ knowledge/index.md" || { echo "  ✗ knowledge/index.md 缺失"; ok=false; }
    [ -d "$skill_dst/scripts" ] && echo "  ✓ scripts/" || { echo "  ✗ scripts/ 缺失"; ok=false; }

    if [ "$ok" = true ]; then
        echo "  nabledge-${v} 安装成功"
        return 0
    else
        echo "  nabledge-${v} 安装不完整,请检查 ✗ 项"
        return 1
    fi
}

# 循环安装每个版本
overall_ok=true
for v in "${VERSIONS[@]}"; do
    install_one "$v" || overall_ok=false
    echo
done

if [ "$overall_ok" = true ]; then
    echo "=== 全部安装成功 ==="
    echo
    echo "下一步: 启动 Claude Code,在项目里输入 /n<版本> 命令:"
    for v in "${VERSIONS[@]}"; do
        echo "  /n${v} <你的 Nablarch ${v} 问题>"
    done
    echo
    echo "示例(/n6):"
    echo "  /n6 BatchAction の createReader で外部 API を呼び出す方法を教えて"
    echo "  /n6 UniversalDao でページング検索を実装したい"
    echo "  /n6 code-analysis FileDeleteAction"
else
    echo "=== 部分版本安装失败,请检查上面的 ✗ 项 ==="
    exit 1
fi
