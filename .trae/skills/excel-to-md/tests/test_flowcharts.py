import hashlib,json,os,re,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
from flowchart_fixture import workbook
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/excel_to_md.py'

class FlowchartTest(unittest.TestCase):
    def convert(self,root,*args,env=None,**fixture):
        source=root/'流程图.xlsx';workbook(source,**fixture);before=source.read_bytes()
        run=subprocess.run([sys.executable,str(SCRIPT),str(source),'-o',str(root/'output'),*args],capture_output=True,text=True,env=env,timeout=150)
        self.assertEqual(source.read_bytes(),before)
        self.assertEqual(run.returncode,0,run.stderr)
        return json.loads((root/'output/conversion-report.json').read_text()),(root/'output/流程图.md').read_text()

    def test_grouped_branches_and_reverse_arrow_keep_exact_endpoints(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report,md=self.convert(root,'--diagram-render','never')
            d=report['drawings'][0]
            self.assertEqual([n['text'] for n in d['nodes']],['提交申请','审核通过？','通过：执行','不通过：退回'])
            self.assertEqual([(c['start_id'],c['end_id']) for c in d['connectors']],[('1','2'),('2','3'),('2','4'),('1','2')])
            self.assertEqual(d['connectors'][3]['direction'],'end_to_start')
            self.assertIn('审核通过？ → 提交申请',md)
            self.assertIn('审核通过？ → 不通过：退回',md)
            self.assertTrue((root/'output'/d['source_workbook']).is_file())

    def test_dangling_connections_not_invented_and_unknown_frames_reported(self):
        with tempfile.TemporaryDirectory() as td:
            report,md=self.convert(Path(td),'--diagram-render','never',dangling=True,smartart=True)
            d=report['drawings'][0]
            self.assertFalse(d['connectors'][2]['resolved'])
            self.assertIn('999',json.dumps(report['warnings']))
            self.assertIn('graphicFrame',json.dumps(report['warnings']))
            self.assertIn('未解析',md)

    def test_missing_renderer_preserves_source_and_warns(self):
        with tempfile.TemporaryDirectory() as td:
            env=dict(os.environ,PATH=td)
            report,md=self.convert(Path(td),env=env)
            self.assertEqual(report['drawings'][0]['render_status'],'unavailable')
            self.assertIn('LibreOffice',json.dumps(report['warnings']))
            self.assertNotIn('](assets/sheet01-drawing.png)',md)

    def test_bidirectional_and_undirected_edges_are_not_forced_one_way(self):
        import zipfile
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'arrows.xlsx';workbook(src)
            with zipfile.ZipFile(src) as z:data={n:z.read(n) for n in z.namelist()}
            xml=data['xl/drawings/drawing1.xml'].decode()
            xml=xml.replace('<a:tailEnd type="triangle"/>','<a:headEnd type="triangle"/><a:tailEnd type="triangle"/>',1)
            xml=xml.replace('<a:headEnd type="triangle"/>','<a:headEnd type="oval"/>',1)
            # First edge retains only a forward triangle; oval must not imply reverse direction.
            data['xl/drawings/drawing1.xml']=xml.encode()
            with zipfile.ZipFile(src,'w') as z:
                for n,v in data.items():z.writestr(n,v)
            sys.path.insert(0,str(SCRIPT.parent))
            from flowcharts import inspect_drawing
            with zipfile.ZipFile(src) as z:d=inspect_drawing(z,'xl/drawings/drawing1.xml','流程图')
            self.assertEqual(d['connectors'][0]['direction'],'start_to_end')
            xml=xml.replace('<a:headEnd type="oval"/>','<a:headEnd type="triangle"/>')
            data['xl/drawings/drawing1.xml']=xml.encode()
            with zipfile.ZipFile(src,'w') as z:
                for n,v in data.items():z.writestr(n,v)
            with zipfile.ZipFile(src) as z:d=inspect_drawing(z,'xl/drawings/drawing1.xml','流程图')
            self.assertEqual(d['connectors'][0]['direction'],'both')
            xml=xml.replace('<a:tailEnd type="triangle"/>','<a:tailEnd type="none"/>',2)
            # First edge is now reverse-only; second has no arrowhead.
            data['xl/drawings/drawing1.xml']=xml.encode()
            with zipfile.ZipFile(src,'w') as z:
                for n,v in data.items():z.writestr(n,v)
            with zipfile.ZipFile(src) as z:d=inspect_drawing(z,'xl/drawings/drawing1.xml','流程图')
            self.assertEqual(d['connectors'][0]['direction'],'end_to_start')
            self.assertEqual(d['connectors'][1]['direction'],'undirected')

    def test_required_missing_renderer_returns_error_but_keeps_report(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'required.xlsx';workbook(src)
            run=subprocess.run([sys.executable,str(SCRIPT),str(src),'-o',str(root/'out'),'--diagram-render','required'],env=dict(os.environ,PATH=td),capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            report=json.loads((root/'out/conversion-report.json').read_text())
            self.assertEqual(report['drawings'][0]['render_status'],'unavailable')
            self.assertTrue((root/'out'/report['drawings'][0]['source_workbook']).is_file())

    def test_renderer_failure_retains_connections_and_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fake=root/'soffice'
            fake.write_text('#!/bin/sh\necho deliberate-render-failure >&2\nexit 3\n');fake.chmod(0o755)
            report,md=self.convert(root,env=dict(os.environ,PATH=td))
            self.assertEqual(report['drawings'][0]['render_status'],'failed')
            self.assertIn('deliberate-render-failure',json.dumps(report['warnings']))
            self.assertIn('审核通过？ → 通过：执行',md)
            self.assertNotIn('![工作表绘图预览]',md)

    @unittest.skipUnless(shutil.which('soffice') or shutil.which('libreoffice'),'LibreOffice not installed')
    def test_real_render_with_hidden_sheet_keeps_preview_and_relative_links(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report,md=self.convert(root,'--diagram-render','required',hidden_drawing=True)
            d=report['drawings'][0];self.assertEqual(d['render_status'],'rendered')
            self.assertEqual(d['pdf_page'],1)
            hidden=report['drawings'][1]
            self.assertEqual(hidden['pdf_page'],2)
            self.assertEqual(hidden['render_status'],'rendered')
            import pymupdf
            with pymupdf.open(root/'output'/hidden['pdf']) as pdf:
                self.assertIn('HIDDEN_FLOW',''.join(pdf[1].get_text().split()))
                self.assertNotIn('HIDDEN_FLOW',''.join(pdf[0].get_text().split()))
            for link in re.findall(r'\]\((assets/[^)]+)\)',md):self.assertTrue((root/'output'/link).is_file(),link)
            with Image.open(root/'output'/d['preview']) as im:
                im.load();self.assertGreater(im.width,100);self.assertGreater(im.height,100)
            self.assertEqual(report['totals']['formula_cells'],0)

if __name__=='__main__':unittest.main(verbosity=2)
