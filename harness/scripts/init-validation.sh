#!/usr/bin/env bash
# 初始化新的工具验证目录
# 用法: ./harness/scripts/init-validation.sh <tool-name>

set -e

TOOL_NAME="$1"

if [ -z "$TOOL_NAME" ]; then
    echo "错误: 请提供工具名称"
    echo "用法: $0 <tool-name>"
    exit 1
fi

VALIDATION_DIR="validations/${TOOL_NAME}"
TEMPLATE_FILE="harness/templates/validation-report.md"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "错误: 找不到模板文件 ${TEMPLATE_FILE}"
    exit 1
fi

if [ -d "$VALIDATION_DIR" ]; then
    echo "警告: 目录 ${VALIDATION_DIR} 已存在，跳过创建"
else
    echo "==> 创建验证目录: ${VALIDATION_DIR}"
    mkdir -p "${VALIDATION_DIR}"
fi

if [ ! -f "${VALIDATION_DIR}/README.md" ]; then
    echo "==> 复制验证报告模板..."
    cp "$TEMPLATE_FILE" "${VALIDATION_DIR}/README.md"
    echo "==> 完成！请编辑 ${VALIDATION_DIR}/README.md 开始验证。"
else
    echo "警告: ${VALIDATION_DIR}/README.md 已存在，跳过复制"
fi
