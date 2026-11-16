import hashlib,json,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[1]
class DistributionTest(unittest.TestCase):
    def test_three_standalone_packages_have_correct_defaults_and_dependencies(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            build=subprocess.run([sys.executable,str(ROOT/'scripts/build_excel_variants.py'),'--output-root',td],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            source=root/'sample.xlsx';w=openpyxl.Workbook();w.active['A1']='测试';w.save(source)
            before=source.read_bytes();hashes=[]
            for backend in ['openpyxl','officecli','libreoffice']:
                skill=root/'.trae/skills'/('excel-to-md-'+backend)
                self.assertEqual(json.loads((skill/'variant.json').read_text())['backend'],backend)
                req=(skill/'requirements.txt').read_text()
                self.assertEqual('PyMuPDF' in req,backend=='libreoffice')
                package=root/'releases/excel-to-md'/('excel-to-md-'+backend+'.zip')
                with zipfile.ZipFile(package) as z:
                    self.assertIsNone(z.testzip());self.assertFalse(any('.venv/' in n or '__pycache__' in n for n in z.namelist()))
                    z.extractall(root/'unpacked'/backend)
                entry=root/'unpacked'/backend/skill.name/'scripts/excel_to_md.py'
                p=subprocess.run([sys.executable,str(entry),str(source),'-o',str(root/'out'/backend)],capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                report=json.loads((root/'out'/backend/'conversion-report.json').read_text());self.assertEqual(report['backend'],backend)
                hashes.append(hashlib.sha256(package.read_bytes()).hexdigest())
            self.assertEqual(source.read_bytes(),before)
            subprocess.run([sys.executable,str(ROOT/'scripts/build_excel_variants.py'),'--output-root',td],check=True,capture_output=True)
            self.assertEqual(hashes,[hashlib.sha256((root/'releases/excel-to-md'/('excel-to-md-'+b+'.zip')).read_bytes()).hexdigest() for b in ['openpyxl','officecli','libreoffice']])
if __name__=='__main__':unittest.main(verbosity=2)
