#!/usr/bin/env bash
# 运行指定任务的验证
# 用法: ./harness/scripts/run-validation.sh <task-id>

set -e

TASK_ID="$1"

if [ -z "$TASK_ID" ]; then
    echo "错误: 请提供任务 ID"
    echo "用法: $0 <task-id>"
    echo ""
    echo "可用任务:"
    ls -1 tasks/ | sort
    exit 1
fi

TASK_DIR="tasks/${TASK_ID}"

if [ ! -d "$TASK_DIR" ]; then
    echo "错误: 找不到任务目录: ${TASK_DIR}"
    exit 1
fi

echo "============================================"
echo "  开始验证任务: ${TASK_ID}"
echo "============================================"
echo ""

# 检查 task.md 是否存在
if [ ! -f "${TASK_DIR}/task.md" ]; then
    echo "⚠️  警告: 未找到 task.md，请先定义任务"
    echo "   参考模板: harness/templates/test-case.md"
    exit 1
fi

# 创建证据目录
EVIDENCE_DIR="results/evidence/${TASK_ID}"
mkdir -p "${EVIDENCE_DIR}"

echo "任务定义: ${TASK_DIR}/task.md"
echo "证据目录: ${EVIDENCE_DIR}"
echo ""
echo "请按照 task.md 中的步骤逐一执行验证"
echo "执行完成后，将结果写入: ${TASK_DIR}/results/result.md"
