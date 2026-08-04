#!/usr/bin/env bash
# 创建新的工具验证分支
# 用法: ./harness/scripts/create-branch.sh <tool-name>

set -e

TOOL_NAME="$1"

if [ -z "$TOOL_NAME" ]; then
    echo "错误: 请提供工具名称"
    echo "用法: $0 <tool-name>"
    exit 1
fi

BRANCH_NAME="verify/${TOOL_NAME}"

echo "==> 切换到 main 分支..."
git checkout main

echo "==> 创建并切换到分支: ${BRANCH_NAME}"
git checkout -b "${BRANCH_NAME}"

echo "==> 完成！现在可以在 ${BRANCH_NAME} 分支上开始验证 ${TOOL_NAME}。"
