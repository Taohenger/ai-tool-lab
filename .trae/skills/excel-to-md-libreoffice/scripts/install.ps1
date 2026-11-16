$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$SkillDir = Split-Path -Parent $ScriptDir
$PythonExe = "python"
$PythonArgs = @()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $PythonArgs = @("-3")
    } else {
        throw "未找到 Python 3。请安装 Python 3.10+，安装时勾选 Add python.exe to PATH。"
    }
}

& $PythonExe @PythonArgs -c 'import sys; assert sys.version_info >= (3, 10), "需要 Python 3.10+"'
& $PythonExe @PythonArgs -m venv "$SkillDir\.venv"
$VenvPython = "$SkillDir\.venv\Scripts\python.exe"

& $VenvPython -m pip install --upgrade pip
if (Test-Path "$SkillDir\wheels") {
    & $VenvPython -m pip install --no-index --find-links "$SkillDir\wheels" -r "$SkillDir\requirements.txt"
} else {
    & $VenvPython -m pip install -r "$SkillDir\requirements.txt"
}

& $VenvPython -c 'import openpyxl; print("安装完成，openpyxl", openpyxl.__version__)'
Write-Host "用法：& `"$VenvPython`" `"$ScriptDir\excel_to_md.py`" 文件.xlsx"
