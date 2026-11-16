#!/usr/bin/env python3
"""Build three standalone Skills from the canonical converter; no binaries or venvs."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES={
 'openpyxl':('纯 Python 版','Python 3.10+、openpyxl、Pillow','不运行任何外部绘图工具。保留单元格、格式、原图片、形状文字和有明确端点 ID 的连接关系；不生成可编辑流程图的整图预览。'),
 'officecli':('OfficeCLI 辅助版','Python 3.10+、openpyxl、Pillow，另装 OfficeCLI 并加入 PATH','实际调用 OfficeCLI 输出辅助 HTML 预览。已知原生连接线、箭头、组合图形可能遗漏，不将预览视为完整流程图。源 OOXML 的明确连接关系独立保留。'),
 'libreoffice':('LibreOffice 增强版','Python 3.10+、openpyxl、Pillow、PyMuPDF，另装 LibreOffice 并加入 PATH','用 LibreOffice 在临时副本上渲染整表 PDF，由 PyMuPDF 生成 PNG 并嵌入 Markdown；同时保留明确的流程连接关系。SmartArt、字体和复杂排版仍可能有差异。'),
}

def build(output: Path):
    source=ROOT/'.trae/skills/excel-to-md'
    release=output/'releases/excel-to-md';release.mkdir(parents=True,exist_ok=True)
    manifest={}
    for backend,(title,dependencies,capabilities) in PROFILES.items():
        name='excel-to-md-'+backend;dest=output/'.trae/skills'/name
        dest.mkdir(parents=True,exist_ok=True)
        files=[p for p in source.rglob('*') if p.is_file() and not any(t in {'.venv','__pycache__','wheels'} for t in p.relative_to(source).parts)]
        for file in files:
            target=dest/file.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target)
        req='openpyxl>=3.1.5,<4\nPillow>=10,<13\n'+('PyMuPDF>=1.24,<2\n' if backend=='libreoffice' else '')
        (dest/'requirements.txt').write_text(req,encoding='utf-8')
        (dest/'variant.json').write_text(json.dumps({'version':'1.2.0','backend':backend},indent=2)+'\n',encoding='utf-8')
        instruction=f'''---
name: "{name}"
description: "Excel 转 Markdown：{title}。{capabilities}"
---

# Excel 转 Markdown — {title}

版本：1.2.0；默认后端：`{backend}`。

依赖：{dependencies}。

{capabilities}

## 安装和运行

将整个 `{name}` 目录放到工程 `.trae/skills/`，以下命令从工程根目录运行。不要复制其他电脑的 .venv。

Linux/macOS：
```bash
bash .trae/skills/{name}/scripts/install.sh
.trae/skills/{name}/.venv/bin/python .trae/skills/{name}/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

Windows PowerShell：
```powershell
powershell -ExecutionPolicy Bypass -File .trae/skills/{name}/scripts/install.ps1
& .trae/skills/{name}/.venv/Scripts/python.exe .trae/skills/{name}/scripts/excel_to_md.py 输入.xlsx -o 输出目录 --flavor both
```

外部工具安装：OfficeCLI 版请安装官方 OfficeCLI（https://github.com/iOfficeAI/OfficeCLI），也可用 `--officecli /路径/officecli` 指定程序；LibreOffice 版请安装 LibreOffice（https://www.libreoffice.org/），并把 `soffice` 或 `libreoffice` 加入 PATH。纯 Python 版不需要二者。

## 验收要求

必须实际执行转换，检查 conversion-report.json 的 backend、totals、drawings、warnings，再检查 Markdown 和全部 assets 链接。OfficeCLI 成功导出状态是 auxiliary，不能报告成已完整还原流程图；缺失外部工具或转换失败都必须告知用户。

每个版本均保留原图、格式和公式表达式；无缓存公式明确标记，不猜结果。只有文件中两端唯一对应到节点的连接才可输出，不按位置推断业务流程。绘图相关输出附原始工作簿副本，源文件只读。Markdown、assets、报告必须整体携带。

LibreOffice 版可加 `--diagram-render required`，绘图预览失败时返回非零；OfficeCLI 辅助预览不满足这一完整绘图预览要求。`--diagram-render never` 禁止外部预览。

跨平台说明：本次实测 Linux；Windows/macOS 尚未实测。离线 wheels 安装器仍有升级 pip 的联网步骤，不能无条件承诺断网安装。复杂图表、SmartArt、布局和公式计算不是无损迁移；LibreOffice 预览可能重算公式，Markdown 公式缓存仍以原文件或 --values-from 为准。

## 测试

安装后在本 Skill 目录运行 `python -m unittest discover -s tests -v`。真实外部工具测试按本机依赖可用情况跳过；`OFFICECLI_TEST` 可指定 OfficeCLI 二进制来启用真实辅助导出测试。测试会显式选择所验证的后端，不代表当前变体运行时会调用其他后端。

这些目录由 `scripts/build_excel_variants.py` 从统一源码生成，请修改统一源码后重新生成，避免各版本代码漂移。
'''
        (dest/'SKILL.md').write_text(instruction,encoding='utf-8')
        package=release/(name+'.zip')
        # Fixed metadata makes identical source builds byte-for-byte reproducible.
        with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
            for path in sorted(dest.rglob('*')):
                if not path.is_file() or any(t in {'.venv','__pycache__','wheels'} for t in path.relative_to(dest).parts):continue
                entry=zipfile.ZipInfo((Path(name)/path.relative_to(dest)).as_posix(),date_time=(2026,11,16,0,0,0))
                entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16
                z.writestr(entry,path.read_bytes())
        manifest[name]={'backend':backend,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'bytes':package.stat().st_size}
    (release/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',type=Path,default=ROOT);args=parser.parse_args();build(args.output_root.resolve())
