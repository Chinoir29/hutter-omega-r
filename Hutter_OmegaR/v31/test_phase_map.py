"""Adversarial tests of genuine pre-coder byte-phase mapper."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_map as p

class PhaseMapTests(unittest.TestCase):
    def work(self,body:bytes,chunk=16):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"test.bin"
            f.write_bytes(body)
            return p.scan_file(f,expected_size=len(body),expected_sha256=hashlib.sha256(body).hexdigest(),chunk_bytes=chunk)
    def test_two_exact_page_markers(self):
        b=b'hello world!!'+p.ANCHOR+b'-'*13+p.ANCHOR+b'extra'
        out=self.work(b)
        self.assertEqual(out["total_exact_page_markers"],2)
        self.assertEqual(out["first_marker_offset"],13)
        self.assertEqual(out["last_marker_offset"],13+8+13)
        self.assertEqual(out["chunks"][0]["page_anchors"],1)
        self.assertEqual(out["chunks"][2]["page_anchors"],1)
        self.assertIsNone(out["official_Hutter_S"])
    def test_marker_crosses_window_boundary(self):
        out=self.work(b'x'*15+p.ANCHOR+b'y'*8,chunk=16)
        self.assertEqual(out["first_marker_offset"],15)
        self.assertEqual(out["chunks"][0]["page_anchors"],1)
        self.assertEqual(out["chunks"][1]["page_anchors"],0)
    def test_no_fake_page_marker(self):
        out=self.work(b'a'*85)
        self.assertEqual(out["total_exact_page_markers"],0)
        self.assertIsNone(out["first_marker_offset"])
        self.assertIsNone(out["study_proposals"]["first_page_context"]["start"])
    def test_reject_wrong_canonical_hash(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"x"
            f.write_bytes(b"some bytes")
            with self.assertRaisesRegex(ValueError,"SHA256_MISMATCH"):
                p.scan_file(f,expected_size=10,expected_sha256="0"*64,chunk_bytes=16)
    def test_reject_wrong_size(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"x";f.write_bytes(b"abc")
            with self.assertRaisesRegex(ValueError,"WRONG_SIZE"):
                p.scan_file(f,expected_size=10,expected_sha256=None,chunk_bytes=16)
    def test_reject_empty(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"x";f.write_bytes(b"")
            with self.assertRaisesRegex(ValueError,"WRONG_SIZE"):
                p.scan_file(f,expected_size=None,expected_sha256=None,chunk_bytes=16)
    def test_reject_unvalid_chunk_size(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"x";f.write_bytes(p.ANCHOR)
            with self.assertRaisesRegex(ValueError,"CHUNK_MUST_EXCEED_ANCHOR"):
                p.scan_file(f,expected_size=None,expected_sha256=None,chunk_bytes=8)
    def test_anchor_bytes_exact_upstream(self):
        self.assertEqual(p.ANCHOR.hex(),"20204c2fdf984e0a")
        self.assertEqual(p.CHUNK_BYTES,8*1024*1024)
    def test_stable_stream_source_sha256(self):
        self.assertEqual(p.STREAM_SHA256,"c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718")
if __name__=="__main__":
    unittest.main(verbosity=2)
