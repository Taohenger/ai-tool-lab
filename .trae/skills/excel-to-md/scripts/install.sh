#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "未找到 Python 3。请先安装 Python 3.10 或更高版本，并勾选 Add to PATH。" >&2
  exit 1
fi

"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 10), "需要 Python 3.10+"'
"$PYTHON" -m venv "$SKILL_DIR/.venv"

if [ -x "$SKILL_DIR/.venv/bin/python" ]; then
  VENV_PYTHON="$SKILL_DIR/.venv/bin/python"
else
  VENV_PYTHON="$SKILL_DIR/.venv/Scripts/python.exe"
fi

"$VENV_PYTHON" -m pip install --upgrade pip
if [ -d "$SKILL_DIR/wheels" ]; then
  "$VENV_PYTHON" -m pip install --no-index --find-links "$SKILL_DIR/wheels" -r "$SKILL_DIR/requirements.txt"
else
  "$VENV_PYTHON" -m pip install -r "$SKILL_DIR/requirements.txt"
fi

"$VENV_PYTHON" -c 'import openpyxl; print("安装完成，openpyxl", openpyxl.__version__)'
echo "用法：\"$VENV_PYTHON\" \"$SCRIPT_DIR/excel_to_md.py\" 文件.xlsx"
