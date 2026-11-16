"""Drawing evidence and optional whole-sheet previews. Never infer edges from layout."""
from __future__ import annotations
import html
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
X = '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}'


def inspect_drawing(archive, part: str, sheet: str) -> dict:
    root = ET.fromstring(archive.read(part))
    nodes, connectors, unsupported = [], [], []
    for el in root.iter():
        if el.tag not in {X+'sp', X+'cxnSp', X+'pic', X+'graphicFrame'}:
            continue
        nv = next((e for e in el.iter() if e.tag == X+'cNvPr'), None)
        ident = nv.get('id', '') if nv is not None else ''
        name = nv.get('name', '') if nv is not None else ''
        if el.tag in {X+'sp', X+'pic'}:
            text = '\n'.join(''.join(t.text or '' for t in p.iter(A+'t')) for p in el.findall('.//'+A+'p'))
            geom = el.find('.//'+A+'prstGeom')
            nodes.append({'id': ident, 'name': name, 'text': text,
                          'geometry': geom.get('prst', '') if geom is not None else 'picture'})
        elif el.tag == X+'cxnSp':
            start, end = el.find('.//'+A+'stCxn'), el.find('.//'+A+'endCxn')
            head, tail = el.find('.//'+A+'headEnd'), el.find('.//'+A+'tailEnd')
            head_type = head.get('type', 'none') if head is not None else 'none'
            tail_type = tail.get('type', 'none') if tail is not None else 'none'
            # Oval/diamond are decorations, not direction indicators.
            directional = {'triangle', 'stealth', 'arrow'}
            h, t = head_type in directional, tail_type in directional
            direction = 'both' if h and t else 'start_to_end' if t else 'end_to_start' if h else 'undirected'
            connectors.append({'id': ident, 'name': name,
                               'start_id': start.get('id') if start is not None else None,
                               'end_id': end.get('id') if end is not None else None,
                               'head': head_type, 'tail': tail_type, 'direction': direction})
        elif el.find('.//{http://schemas.openxmlformats.org/drawingml/2006/chart}chart') is None:
            unsupported.append('graphicFrame（可能是 SmartArt 或其他对象）')
    ids = [n['id'] for n in nodes]
    for c in connectors:
        c['resolved'] = (bool(c['start_id']) and bool(c['end_id']) and
                         ids.count(c['start_id']) == 1 and ids.count(c['end_id']) == 1)
    return {'sheet': sheet, 'part': part, 'nodes': nodes, 'connectors': connectors,
            'unsupported_objects': unsupported, 'render_status': 'pending'}


def enrich_drawings(converter, sheets: dict[str, str], mode: str) -> list[dict]:
    # Local imports avoid circular imports with the CLI entry point.
    from excel_to_md import read_rels, part_target, DOC_REL
    records = []
    for sheet, sheet_part in sheets.items():
        root = ET.fromstring(converter.archive.read(sheet_part))
        for drawing in root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}drawing'):
            rel = read_rels(converter.archive, sheet_part).get(drawing.get('{'+DOC_REL+'}id'))
            if not rel or rel.get('TargetMode') == 'External':
                continue
            part = part_target(sheet_part, rel['Target'])
            info = inspect_drawing(converter.archive, part, sheet)
            # Existing embedded pictures already have exact extraction; preview shapes/charts/SmartArt.
            drawing_xml = ET.fromstring(converter.archive.read(part))
            if not any(e.tag in {X+'sp', X+'cxnSp', X+'grpSp', X+'graphicFrame'} for e in drawing_xml.iter()):
                continue
            records.append(info)
            for c in info['connectors']:
                if not c['resolved']:
                    converter.warn(f"{sheet} 连接线 {c['id']} 的端点未解析：{c['start_id']} / {c['end_id']}；未猜测连接关系。")
            for unsupported in info['unsupported_objects']:
                converter.warn(f'{sheet} 存在 {unsupported}，文字关系未解析；请核对预览与源文件。')
    if not records:
        return records
    converter.assets_dir.mkdir(parents=True, exist_ok=True)
    original = converter.assets_dir / ('original-workbook'+converter.original_source.suffix.lower())
    if converter.original_source.resolve() != original.resolve():
        shutil.copy2(converter.original_source, original)
    for info in records:
        info['source_workbook'] = original.relative_to(converter.output_dir).as_posix()
    if mode == 'never' or converter.backend == 'openpyxl':
        for info in records:
            info['render_status'] = 'disabled'
        converter.warn('绘图预览已禁用；保留连接信息和原始工作簿附件，不能将文字描述视为完整流程图。')
        return records
    if converter.backend == 'officecli':
        export_officecli(converter, records)
        return records
    executable = shutil.which('libreoffice') or shutil.which('soffice')
    if not executable:
        for info in records:
            info['render_status'] = 'unavailable'
        converter.warn('未找到 LibreOffice/soffice，无法生成流程图预览；连接信息和原始工作簿已保留。')
        return records
    try:
        import pymupdf
        with tempfile.TemporaryDirectory(prefix='excel-drawing-') as temp:
            work = Path(temp)
            # Byte-for-byte copy: preserve drawings, group transforms, SmartArt and formulas.
            source = work / ('source'+converter.source.suffix)
            shutil.copy2(converter.source, source)
            pdf_out = work/'pdf'; pdf_out.mkdir()
            profile = (work/'profile').as_uri()
            process = subprocess.run([executable, '-env:UserInstallation='+profile, '--headless',
                                      '--norestore', '--convert-to',
                                      'pdf:calc_pdf_Export:{"SinglePageSheets":{"type":"boolean","value":"true"}}',
                                      '--outdir', str(pdf_out), str(source)],
                                     capture_output=True, text=True, timeout=120)
            pdf = pdf_out/'source.pdf'
            if process.returncode != 0 or not pdf.is_file():
                raise RuntimeError((process.stderr or process.stdout or '未输出 PDF')[-1000:])
            with pymupdf.open(pdf) as doc:
                # SinglePageSheets exports hidden sheets too. Reject ambiguous mapping rather than label a wrong page.
                if len(doc) != len(converter.wb.sheetnames):
                    raise RuntimeError(f'PDF 页数 {len(doc)} 与工作表数 {len(converter.wb.sheetnames)} 不一致，拒绝猜测页码')
                preview_pdf = converter.assets_dir/'drawing-preview.pdf'
                shutil.copy2(pdf, preview_pdf)
                for info in records:
                    index = converter.wb.sheetnames.index(info['sheet'])
                    page = doc[index]
                    if page.rect.width <= 0 or page.rect.height <= 0:
                        raise RuntimeError(f"{info['sheet']} 页面尺寸无效")
                    scale = min(2.0, 4000/max(page.rect.width, page.rect.height))
                    image = converter.assets_dir/f'sheet{index+1:02d}-drawing.png'
                    page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).save(image)
                    info.update(render_status='rendered', pdf_page=index+1,
                                preview=image.relative_to(converter.output_dir).as_posix(),
                                pdf=preview_pdf.relative_to(converter.output_dir).as_posix())
        converter.warn('绘图预览由 LibreOffice 渲染，可能重算公式或改变字体、SmartArt 和复杂排版；仅作视觉参考，公式正文仍使用源文件缓存。原始工作簿附件为准。')
    except (ImportError, OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        for info in records:
            info['render_status'] = 'failed'
            info.pop('preview', None)
        converter.warn(f'LibreOffice 绘图预览失败：{exc}；已保留连接信息和原始工作簿，未将失败预览视为成功。')
    return records


def drawing_markdown(info: dict) -> str:
    lines = ['## 流程图与绘图', '']
    if info['render_status'] == 'auxiliary':
        lines += [f"[OfficeCLI 辅助预览]({info['officecli_html']})", '',
                  '> 此预览可能遗漏连接线、箭头、组合图形；不能作为流程图完整还原的凭证。', '']
    elif info['render_status'] == 'rendered':
        lines += [f"![工作表绘图预览]({info['preview']})", '',
                  f"[高清矢量 PDF（第 {info['pdf_page']} 页）]({info['pdf']})", '',
                  '> 预览由 LibreOffice 渲染，复杂图形及公式显示请与原文件核对。', '']
    else:
        lines += ['> 未生成绘图预览，不能只凭下列文字判断完整流程。', '']
    lines += [f"[原始 Excel（含可编辑绘图）]({info['source_workbook']})", '',
              '连接关系（仅采用文件中记录的端点和箭头，不按位置猜测；分支标签请结合原图）：', '']
    nodes = {n['id']: n['text'] or n['name'] or n['id'] for n in info['nodes']}
    def esc(s):
        # Keep a single inert Markdown line for untrusted designer text.
        s = html.escape(str(s), quote=False).replace('\n', ' / ')
        for ch in ['\\','`','*','_','[',']','~','|']:
            s = s.replace(ch, '\\'+ch)
        return s
    for c in info['connectors']:
        if not c['resolved']:
            text = f"连接线 {c['id']}：端点未解析（{c['start_id']} / {c['end_id']}）"
        else:
            left, right = nodes[c['start_id']], nodes[c['end_id']]
            if c['direction'] == 'end_to_start':
                left, right = right, left
            arrow = '↔' if c['direction'] == 'both' else '—' if c['direction'] == 'undirected' else '→'
            text = f'{left} {arrow} {right}'
        lines.append('- '+esc(text))
    if not info['connectors']:
        lines.append('- 未发现带端点信息的独立连接线；不据此判断工作表没有流程图。')
    return '\n'.join(lines)


def export_officecli(converter, records: list[dict]) -> None:
    """Export OfficeCLI's HTML as auxiliary evidence, never certify complete diagrams."""
    executable = converter.officecli or shutil.which('officecli')
    if not executable:
        for info in records:
            info['render_status'] = 'unavailable'
        converter.warn('未找到 OfficeCLI；未生成辅助预览，已保留连接信息和原始工作簿。可用 --officecli 指定路径。')
        return
    try:
        with tempfile.TemporaryDirectory(prefix='excel-officecli-') as temp:
            work = Path(temp)
            source = work/('source'+converter.source.suffix)
            shutil.copy2(converter.source, source)
            preview = work/'preview.html'
            process = subprocess.run([str(executable), 'view', str(source), 'html', '-o', str(preview)],
                                     capture_output=True, text=True, timeout=120)
            if process.returncode != 0 or not preview.is_file() or not preview.stat().st_size:
                raise RuntimeError((process.stderr or process.stdout or '未输出 HTML')[-1000:])
            target = converter.assets_dir/'officecli-preview.html'
            shutil.copy2(preview, target)
            for info in records:
                info.update(render_status='auxiliary', officecli_html=target.relative_to(converter.output_dir).as_posix())
        converter.warn('OfficeCLI 输出仅为辅助 HTML 预览，可能遗漏原生连接线、箭头、组合图形或 SmartArt，不能当作完整流程图；连接关系仍以源 OOXML 为准，原始工作簿已附带。')
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        for info in records:
            info['render_status'] = 'failed'
        converter.warn(f'OfficeCLI 辅助预览失败：{exc}；已保留连接信息和原始工作簿。')
