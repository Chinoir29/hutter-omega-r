"""Synthetic adversarial contract tests for native comp9 archive production."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_native as m

class NativePackagingTests(unittest.TestCase):
    def fixture(self):
        return ('''bool RunCompression(const char* output_path) {
'''
            + m.TAG + '''501062281);
    fclose(temp_in); fclose(data_out);
    // prefix only
''' + m.REMOVE + '''
    remove(temp_path.c_str());
''' + m.EXIT + '''
  }
  return true;
}
bool RunDecompression() {}
void mainpath() {
    setenv("OMR23_PREFIX_DECODE", "524288", 1);
    rename(temp_path.c_str(), "archive9");
}
''').encode()

    def test_native_release_packer_preserved(self):
        out=m.promote_runner(self.fixture()).decode()
        self.assertEqual(out.count(m.PACKER),1)
        self.assertEqual(out.count("    return true;"),2)
        self.assertNotIn(m.REMOVE,out)
        self.assertEqual(out.count("fclose(temp_in); fclose(data_out);"),1)

    def test_refuse_no_v24_decoder_cap(self):
        data=self.fixture().replace(b'setenv("OMR23_PREFIX_DECODE", "524288", 1);',b'')
        with self.assertRaisesRegex(ValueError, 'ZERO_ARG_DECODE_REQUIRES_V24'):
            m.promote_runner(data)

    def test_reject_absent_release_packer(self):
        data=self.fixture().replace(m.PACKER.encode(),b'no_packer')
        with self.assertRaisesRegex(ValueError,'NATIVE_PRODUCTION_PACKER'):
            m.promote_runner(data)

    def test_reject_nonunique_probe(self):
        data=self.fixture() + m.TAG.encode()
        with self.assertRaisesRegex(ValueError,'NOT_UNIQUE'):
            m.promote_runner(data)

    def test_reject_early_exit_changed(self):
        data=self.fixture().replace(m.REMOVE.encode(),b'not_reached;')
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_PREFIX_EXIT_SHAPE'):
            m.promote_runner(data)

if __name__=='__main__':
    unittest.main(verbosity=2)
