"""Adversarial tests for v0.32 long native prefix byte-identity witness."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_native_extended as r

class NativeLongValidationTests(unittest.TestCase):
    def test_exact_byte_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'ref';b=Path(d)/'restored'
            data=bytes(range(256))*32
            a.write_bytes(data);b.write_bytes(data)
            self.assertEqual(r.compare_bytes(a,b,len(data)),r.hashfile(a))
    def test_reject_corruption_even_if_size_equal(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'ref';b=Path(d)/'restored'
            a.write_bytes(b'A'*20000)
            b.write_bytes(b'A'*19999+b'B')
            with self.assertRaisesRegex(ValueError,"FIRST_DIFFERENT_CHUNK"):
                r.compare_bytes(a,b,20000)
    def test_reject_extra_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'ref';b=Path(d)/'restored'
            a.write_bytes(b'abc');b.write_bytes(b'abcd')
            with self.assertRaisesRegex(ValueError,"PREFIX_LENGTH_MISMATCH"):
                r.compare_bytes(a,b,3)
    def test_reject_missing_corpus_cap_before_access(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"INVALID_CAP"):
                r.run_experiment(Path('/bin/true'),Path('/no-corpus'),
                                 Path(d)/'new',Path(d)/'report.json',7)
    def test_reject_missing_files(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'reference';a.write_bytes(b'ok')
            with self.assertRaisesRegex(ValueError,"REFERENCE_OR_DECODED_OUTPUT_MISSING"):
                r.compare_bytes(a,Path(d)/'missing',2)
    def test_known_sha256(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'x';a.write_bytes(b'hello')
            self.assertEqual(r.hashfile(a),'2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824')
    def test_must_reject_workdir_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaisesRegex(ValueError,'UNSAFE_OR_EXISTING_WORKDIR'):
                r.run_experiment(Path('/bin/true'),Path('/no-corpus'),
                                 root,root.parent/'report.json',8388608)

if __name__=='__main__':unittest.main(verbosity=2)
