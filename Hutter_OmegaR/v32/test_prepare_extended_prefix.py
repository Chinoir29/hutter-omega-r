"""Fail-closed tests for long-prefix genuine native comp9/archive9 research path."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_extended_prefix as p

class SourceExtensionTests(unittest.TestCase):
    def fixture(self):
        return b'''bool f() {
  if (n>1048576ull) return;
  if (n>1048576ull) return;
  if (count>1048576ull) return;
  setenv("OMR23_PREFIX_DECODE", "524288", 1);
  FILE* dst = fopen("omr23-reference-prefix.bin", "wb");
  if(rename(temp_path.c_str(),"omr23-decoded-prefix.bin")!=0) return false;
  rename(temp_path.c_str(), "archive9");
  return true;
}
'''
    def test_exact_three_constraints_and_archive_preserved(self):
        data=p.extend(self.fixture(),16*1024*1024).decode()
        self.assertEqual(data.count("67108864ull"),3)
        self.assertEqual(data.count('setenv("OMR23_PREFIX_DECODE", "16777216", 1)'),1)
        self.assertEqual(data.count("1048576ull"),0)
        self.assertIn('rename(temp_path.c_str(), "archive9")',data)
        self.assertIn('omr23-reference-prefix.bin',data)
        self.assertIn('omr23-decoded-prefix.bin',data)
    def test_accept_8_16_32_64m(self):
        for size in (8,16,32,64):
            out=p.extend(self.fixture(),size*1024*1024).decode()
            self.assertIn('"'+str(size*1024*1024)+'"',out)
    def test_refuse_non_aligned_and_outside_limits(self):
        for n in (0,1024,524287,524289,65*1024*1024,-1,True):
            with self.assertRaisesRegex(ValueError,'INVALID_PREFIX_CAP'):
                p.extend(self.fixture(),n)
    def test_missing_one_cap_rejected(self):
        data=self.fixture().replace(b'count>1048576ull',b'count>wrong')
        with self.assertRaisesRegex(ValueError,"PREFIX_CAP_ANCHORS"):
            p.extend(data,8*1024*1024)
    def test_duplicate_decoder_internal_cap_rejected(self):
        data=self.fixture()+b'setenv("OMR23_PREFIX_DECODE", "524288", 1);'
        with self.assertRaisesRegex(ValueError,"INTERNAL_DECODE_CAP_ANCHOR"):
            p.extend(data,8*1024*1024)
    def test_missing_native_packager_rejected(self):
        data=self.fixture().replace(b'rename(temp_path.c_str(), "archive9")',b'do_not_pack()')
        with self.assertRaisesRegex(ValueError,"NATIVE_ARCHIVE9_PACKER"):
            p.extend(data,8*1024*1024)
    def test_missing_reference_or_inverse_rejected(self):
        data=self.fixture().replace(b'omr23-reference-prefix.bin',b'other')
        with self.assertRaisesRegex(ValueError,"REAL_REFERENCE_OR_DECODE_PROBE_MISSING"):
            p.extend(data,8*1024*1024)
    def test_non_native_older_packager_rejected(self):
        data=self.fixture()+b'// old omr21-coded-prefix.bin\n'
        with self.assertRaisesRegex(ValueError,"NON_NATIVE_OLDER_PREFIX_PACKER"):
            p.extend(data,8*1024*1024)

if __name__=="__main__":unittest.main(verbosity=2)
