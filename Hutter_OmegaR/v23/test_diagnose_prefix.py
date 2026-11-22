import unittest,tempfile
from pathlib import Path
from diagnose_prefix import investigate
class Tests(unittest.TestCase):
    def test_identity(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b';a.write_bytes(b'abcdefghi');b.write_bytes(b'abcdefghi')
            r=investigate(a,b,3)
            self.assertTrue(r['identical']);self.assertIsNone(r['first_difference_offset'])
    def test_changed_byte(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b';a.write_bytes(b'abcdefghi');b.write_bytes(b'abXdefgXi')
            r=investigate(a,b,3)
            self.assertFalse(r['identical']);self.assertEqual(r['first_difference_offset'],2)
            self.assertEqual(r['total_different_or_missing_bytes'],2)
    def test_truncation(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b';a.write_bytes(b'abcdefghij');b.write_bytes(b'abcd')
            r=investigate(a,b,3)
            self.assertFalse(r['identical']);self.assertEqual(r['first_difference_offset'],4)
            self.assertEqual(r['total_different_or_missing_bytes'],6)
if __name__=='__main__':unittest.main(verbosity=2)
