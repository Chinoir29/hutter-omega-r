"""Synthetic-only adversarial unit tests; these are NOT compression tests."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from patch_upper_gate import modify_source, ALLOWED

SRC='''namespace semantic_cache {
constexpr int kQpE3 = 990;             // look up below
constexpr int kSpE3 = 950;             // store below
constexpr int kCalqE3 = 900;           // calibration
}'''

class TestPatch(unittest.TestCase):
    def test_control_byte_identical(self):
        self.assertEqual(modify_source(SRC,990),SRC)
    def test_995_only_one_change(self):
        self.assertEqual(modify_source(SRC,995),SRC.replace('kQpE3 = 990','kQpE3 = 995'))
    def test_999_only_one_change(self):
        self.assertEqual(modify_source(SRC,999),SRC.replace('kQpE3 = 990','kQpE3 = 999'))
    def test_range(self):
        for n in (900,950,970,980,1000,1001,-1,True):
            with self.subTest(n=n), self.assertRaises(ValueError):modify_source(SRC,n)
    def test_absent_declaration(self):
        with self.assertRaises(ValueError):modify_source(SRC.replace('kQpE3','other'),995)
    def test_duplicate_declaration(self):
        with self.assertRaises(ValueError):modify_source(SRC+SRC,995)
    def test_absent_storage(self):
        with self.assertRaises(ValueError):modify_source(SRC.replace('kSpE3','other'),995)
    def test_absent_calibration(self):
        with self.assertRaises(ValueError):modify_source(SRC.replace('kCalqE3','other'),995)
    def test_explicit_values(self):
        self.assertEqual(ALLOWED,(990,995,999))

if __name__=='__main__':unittest.main(verbosity=2)
