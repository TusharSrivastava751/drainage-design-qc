import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

COMMAND = ['drainage_qc.py', 'examples/pipes.csv']

class CliTests(unittest.TestCase):
    def test_report_and_exit_modes(self):
        with tempfile.TemporaryDirectory() as d:
            command=[sys.executable]+COMMAND+['--out',d]
            p=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            report=json.loads((Path(d)/'report.json').read_text())
            self.assertTrue(report['demo'])
            self.assertTrue(report['inputs'])
            self.assertTrue((Path(d)/'report.md').read_text().startswith('#'))
            p=subprocess.run(command+['--fail-on-findings'],capture_output=True,text=True)
            self.assertEqual(p.returncode,1,p.stderr)

    def test_missing_input_returns_two(self):
        with tempfile.TemporaryDirectory() as d:
            command=[sys.executable]+[COMMAND[0],'missing-demo-input.file']+COMMAND[2:]+['--out',d]
            p=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(p.returncode,2,p.stderr)
            self.assertNotIn('Traceback',p.stderr)
            self.assertFalse((Path(d)/'report.json').exists())
