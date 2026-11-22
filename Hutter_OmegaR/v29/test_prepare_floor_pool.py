from pathlib import Path
from unittest.mock import patch
import hashlib
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_floor_pool as p
import floor_pool_reference as ref

class SourceTests(unittest.TestCase):
    def fixture(self):
        return b'''#ifndef FLOOR_STAGE_H
#define FLOOR_STAGE_H
namespace floor_stage {
constexpr int kCLog = 12;
struct Cell { unsigned n,k; };
struct Stage {
  Cell c[kCtx];
  int cur = -1;
  void P32(){
    cur = -1;
    const Cell& e = c[idx];
    const uint64_t cw = (uint64_t)1 << c_log;
    uint64_t err = (((uint64_t)e.k << 32) + cw * ((uint64_t)f << 16)) / ((uint64_t)e.n + cw);
  }
  void Update(int bit) {
    Cell& e = c[cur];
    ++e.n;
  }
};
}
#endif
'''
    def test_blob_sha_matches_git(self):
        self.assertEqual(p.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')

    def test_reject_source_drift(self):
        with self.assertRaisesRegex(ValueError,'PINNED_FLOOR_STAGE_DRIFT'):
            p.make_patch(self.fixture())

    def test_preserve_original_submodel_and_add_parent(self):
        x=self.fixture()
        with patch.object(p,'ORIGINAL_GIT_BLOB',p.git_blob(x)):
            y=p.make_patch(x)
        self.assertIn(b'constexpr int kCLog = 12;',y)
        self.assertIn(b'Parent parent[16]',y)
        self.assertIn(b'par.expected_f += cur_f',y)
        self.assertIn(b'cw * (f_prior << 16)',y)
        self.assertNotIn(b'cw * ((uint64_t)f << 16)',y)
        self.assertNotIn(b'extern',y)
        self.assertIn(b'const unsigned __int128 num',y)

    def test_refuse_ambiguous_old_method(self):
        x=self.fixture().replace(b'  Cell c[kCtx];',b'  Cell c[kCtx];\n  Cell c[kCtx];')
        with patch.object(p,'ORIGINAL_GIT_BLOB',p.git_blob(x)):
            with self.assertRaisesRegex(ValueError,'AMBIGUOUS_FLOOR_STAGE_ANCHOR'):
                p.make_patch(x)

    def test_no_source_repatch(self):
        x=self.fixture()
        with patch.object(p,'ORIGINAL_GIT_BLOB',p.git_blob(x)):
            y=p.make_patch(x)
            with self.assertRaisesRegex(ValueError,'PINNED_FLOOR_STAGE_DRIFT'):
                p.make_patch(y)

    def test_only_16_parent_rows_and_no_side_data(self):
        self.assertIn('Parent parent[16] = {};',p.PARENT)
        self.assertIn('cur_parent = (side << 3) | (bp & 7);',p.PATCH_PRIOR)
        self.assertNotIn('fopen',p.PATCH_UPDATE+p.PATCH_PRIOR)

class ReferenceTests(unittest.TestCase):
    def test_reject_incomplete_reference(self):
        with self.assertRaisesRegex(ValueError,'MISSING_GROUNDED_CPP_METRICS'):
            ref.parse('OMR29_FLOOR_TEST loss_bits=100')

    def test_loss_report_parser(self):
        line='OMR29_FLOOR_TEST case=mismatch bits=400000 errors=7 loss_bits=20.125000000 input_checksum=0123456789abcdef prediction_checksum=9876543210abcdef'
        self.assertEqual(ref.parse(line)['prediction_checksum'],'9876543210abcdef')

if __name__=='__main__': unittest.main(verbosity=2)
