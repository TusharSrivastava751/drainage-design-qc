import tempfile
import unittest
from pathlib import Path
from auditlib import read_csv, number

class InputTests(unittest.TestCase):
    def test_invalid_numeric_values(self):
        for value in ['NaN', 'inf', '-inf', '', True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value, 'value')

    def test_csv_structure(self):
        for content in ['x,x\n1,2\n', 'y\n1\n', 'x\n', 'x\n1,2\n', 'x,y\n1\n', 'x\n""\n']:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as d:
                p = Path(d) / 'input.csv'
                p.write_text(content)
                with self.assertRaises(ValueError):
                    read_csv(p, ['x'])
