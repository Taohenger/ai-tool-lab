"""Backends must actually select different dependencies and execution paths."""
import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from flowchart_fixture import workbook
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/excel_to_md.py'
class BackendTest(unittest.TestCase):
    def run_backend(self,root,backend,*args,env=None):
        src=root/'diagram.xlsx';workbook(src);before=src.read_bytes()
        p=subprocess.run([sys.executable,str(SCRIPT),str(src),'-o',str(root/'output'),'--backend',backend,*args],env=env,capture_output=True,text=True,timeout=150)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(src.read_bytes(),before)
        return json.loads((root/'output/conversion-report.json').read_text()),(root/'output/diagram.md').read_text()
    def test_openpyxl_does_not_run_external_tools(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);marker=root/'called'
            for name in ['soffice','libreoffice','officecli']:
                p=root/name;p.write_text('#!/bin/sh\nprintf called > "'+str(marker)+'"\nexit 9\n');p.chmod(0o755)
            report,md=self.run_backend(root,'openpyxl',env=dict(os.environ,PATH=td))
            self.assertFalse(marker.exists());self.assertEqual(report['backend'],'openpyxl')
            self.assertEqual(report['drawings'][0]['render_status'],'disabled')
            self.assertIn('审核通过？ → 通过：执行',md)
    def test_legacy_xls_cannot_sneak_libreoffice_into_base_profiles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);marker=root/'called';src=root/'legacy.xls';src.write_bytes(b'legacy-input')
            for name in ['soffice','libreoffice']:
                p=root/name;p.write_text('#!/bin/sh\nprintf called > "'+str(marker)+'"\nexit 9\n');p.chmod(0o755)
            for backend in ['openpyxl','officecli']:
                run=subprocess.run([sys.executable,str(SCRIPT),str(src),'--backend',backend],env=dict(os.environ,PATH=td),capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0)
                self.assertFalse(marker.exists(),'Legacy .xls unexpectedly invoked LibreOffice')
                self.assertIn('.xlsx',run.stderr)
                self.assertEqual(src.read_bytes(),b'legacy-input')

    def test_officecli_missing_is_reported_without_trying_libreoffice(self):
        with tempfile.TemporaryDirectory() as td:
            report,md=self.run_backend(Path(td),'officecli',env=dict(os.environ,PATH=td))
            self.assertEqual(report['drawings'][0]['render_status'],'unavailable')
            self.assertIn('OfficeCLI',json.dumps(report['warnings']))
    def test_officecli_failure_does_not_claim_preview_success(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/'officecli';p.write_text('#!/bin/sh\necho test-officecli-error >&2\nexit 2\n');p.chmod(0o755)
            report,md=self.run_backend(root,'officecli','--officecli',str(p))
            self.assertEqual(report['drawings'][0]['render_status'],'failed')
            self.assertIn('test-officecli-error',json.dumps(report['warnings']))
            self.assertNotIn('[OfficeCLI 辅助预览]',md)
    @unittest.skipUnless(os.environ.get('OFFICECLI_TEST'),'Set OFFICECLI_TEST to test real OfficeCLI')
    def test_real_officecli_exports_html_but_does_not_certify_arrows(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);report,md=self.run_backend(root,'officecli','--officecli',os.environ['OFFICECLI_TEST'])
            d=report['drawings'][0];self.assertEqual(d['render_status'],'auxiliary')
            self.assertTrue((root/'output'/d['officecli_html']).is_file())
            self.assertIn('[OfficeCLI 辅助预览]',md)
            self.assertIn('箭头',''.join(report['warnings']))
            self.assertIn('审核通过？ → 通过：执行',md)
if __name__=='__main__':unittest.main(verbosity=2)
