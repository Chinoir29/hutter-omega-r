"""Adversarial tests for v0.19 on synthetic strings; source pin remotely tested."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import production_stream_probe as p

class TestProductionStreamProbe(unittest.TestCase):
    def fixture(self):
        return (b'prefix\n' + p.ORIGINAL.encode() + b'\nPredictor p(vocab);\n'
                b'Compress(temp_bytes, temp_in, data_out, output_bytes, &p);\n')

    def test_git_blob(self):
        self.assertEqual(p.git_blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')

    def test_reject_changed_upstream(self):
        with self.assertRaisesRegex(ValueError, 'DRIFT'):
            p.transform_runner(self.fixture())

    def test_instrument_before_arithmetic_coder(self):
        data = self.fixture()
        with patch.object(p, 'RUNNER_BLOB', p.git_blob(data)):
            out = p.transform_runner(data)
        self.assertIn(b'OMR19_REAL_CODER_INPUT=', out)
        self.assertLess(out.index(b'OMR19_REAL_CODER_INPUT='), out.index(b'Predictor p(vocab)'))
        self.assertEqual(out.count(b'OMR19_PROBE_PRODUCTION_STREAM'), 1)
        self.assertEqual(out.count(p.ORIGINAL.encode()), 1)

    def test_reject_double_instrumentation(self):
        data = self.fixture() + p.ORIGINAL.encode()
        with patch.object(p, 'RUNNER_BLOB', p.git_blob(data)):
            with self.assertRaisesRegex(ValueError, 'NOT_UNIQUE'):
                p.transform_runner(data)

    def test_reject_noncompetition_path(self):
        data = self.fixture()
        with patch.object(p, 'RUNNER_BLOB', p.git_blob(data)):
            out = p.transform_runner(data)
        self.assertIn(b'input_path != ".ready4cmix"', out)
        self.assertIn(b'output_path != "archive9"', out)
        self.assertIn(b'dictionary == NULL', out)
        self.assertIn(b'!enable_preprocess', out)
        self.assertIn(b'std::exit(182)', out)

    def test_pinned_commit_format(self):
        self.assertEqual(len(p.UPSTREAM_SHA), 40)
        self.assertTrue(set(p.UPSTREAM_SHA).issubset(set('0123456789abcdef')))

if __name__ == '__main__':
    unittest.main(verbosity=2)
