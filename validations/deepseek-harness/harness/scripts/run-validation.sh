#!/usr/bin/env bash
# 通用验证执行入口
# 用法: ./harness/scripts/run-validation.sh <task-id>
# 例:   ./harness/scripts/run-validation.sh 001

set -e

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
    echo "用法: $0 <task-id>"
    echo "例: $0 001"
    exit 1
fi

TASK_DIR="$(cd "$(dirname "$0")/../.." && pwd)/tasks/${TASK_ID}-"*
TASK_DIR="$(compgen -G "$TASK_DIR" | head -1)"

if [ -z "$TASK_DIR" ] || [ ! -d "$TASK_DIR" ]; then
    echo "❌ 未找到任务目录: tasks/${TASK_ID}-*"
    exit 1
fi

echo "============================================"
echo "  开始验证任务: $TASK_ID"
echo "  目录: $TASK_DIR"
echo "============================================"
echo ""

if [ -f "$TASK_DIR/task.md" ]; then
    echo "📋 任务规格文件:"
    echo "   $TASK_DIR/task.md"
    echo ""
    echo "按照 task.md 中的 TC 顺序执行命令。"
    echo "每个 TC 的 stdout 都保存到 results/evidence/${TASK_ID}-*/<tc-id>.txt"
    echo ""
    echo "执行完成后写:"
    echo "   $TASK_DIR/results/result.md"
    echo "然后同步更新 PROGRESS.md 和 feature_list.json"
else
    echo "⚠️  未找到 task.md"
fi
