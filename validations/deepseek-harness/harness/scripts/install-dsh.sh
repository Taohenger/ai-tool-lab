#!/usr/bin/env bash
# 安装 DeepSeek Harness (@deepseek-ai/dsh)
# 用法: ./harness/scripts/install-dsh.sh

set -e

echo "============================================"
echo "  DeepSeek Harness (dsh) 安装脚本"
echo "============================================"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 node，请先安装 Node.js >= 22.19.0"
    exit 1
fi

NODE_VERSION="$(node --version | sed 's/v//')"
REQUIRED_MAJOR="22"
REQUIRED_MINOR="19"

MAJOR="$(echo "$NODE_VERSION" | cut -d. -f1)"
MINOR="$(echo "$NODE_VERSION" | cut -d. -f2)"

echo "Node.js 版本: v${NODE_VERSION}"

# 版本比较：>= 22.19 或 >= 24.x
if [ "$MAJOR" -ge 24 ]; then
    echo "✅ Node.js v24+ 满足要求"
elif [ "$MAJOR" -eq 22 ] && [ "$MINOR" -ge "$REQUIRED_MINOR" ]; then
    echo "✅ Node.js v22.19+ 满足要求"
else
    echo "❌ Node.js 版本过低 (当前 v${NODE_VERSION})，需要 >= v22.19 或 >= v24"
    exit 1
fi
echo ""

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 未找到 npm"
    exit 1
fi

echo "npm 版本: $(npm --version)"
echo ""

# 方式 1：尝试 npx 快速验证
echo "方式 1: npx 快速可用性检查..."
if npx --yes @deepseek-ai/dsh --version &> /tmp/dsh-version.txt 2>&1; then
    DSH_VER="$(cat /tmp/dsh-version.txt | head -1)"
    echo "✅ npx 可用，DSH 版本: ${DSH_VER}"
else
    echo "⚠️  npx 拉取失败，但不影响全局安装（可能是网络问题）"
fi
echo ""

# 方式 2：全局安装
echo "方式 2: 尝试全局安装 @deepseek-ai/dsh ..."
if ! command -v dsh &> /dev/null; then
    npm install -g @deepseek-ai/dsh 2>&1 | tail -10
    echo ""
fi

# 检查结果
if command -v dsh &> /dev/null; then
    echo "✅ dsh 全局安装成功！"
    dsh --version
    echo ""
    echo "下一步："
    echo "  dsh --help               # 查看帮助"
    echo "  dsh web                  # 启动 Web UI (默认 http://127.0.0.1:3080)"
    echo "  dsh --profile headless \"任务描述\"  # 单次执行（无界面）"
else
    echo ""
    echo "⚠️  全局 dsh 不在 PATH，但 npx 应该可用。"
    echo "   试试：npx @deepseek-ai/dsh --help"
fi
