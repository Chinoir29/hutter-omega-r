"""Adversarial source gates for v0.30 replacement of the confidence floor."""
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_compact_stage as src
import compact_reference as ref

class SourceTests(unittest.TestCase):
    def fake(self):
        return b'''#ifndef FLOOR_STAGE_H_
#define FLOOR_STAGE_H_
#include <stdint.h>
namespace floor_stage {
struct Cell { uint32_t n,k; };
struct Stage {
  Cell c[kCtx];
  int cur=-1;
};
 
// Interval split with a 32-bit probability
inline unsigned int Mid(unsigned int x1, unsigned int x2, uint32_t p32) {
 return x1 + (unsigned int)(((uint64_t)(x2 - x1) * (uint64_t)p32) >> 32);
}
}
#endif
'''
    def test_pin_rejects_other_sources(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_DRIFT"):
            src.replace_stage(self.fake())

    def test_replacement_is_exactly_one_structure(self):
        fake=self.fake()
        with patch.object(src,'PIN_GIT_BLOB',src.git_blob(fake)):
            patched=src.replace_stage(fake)
        self.assertIn(b'PoolRow pool[16]',patched)
        self.assertNotIn(b'Cell c[kCtx]',patched)
        self.assertIn(b'inline unsigned int Mid(',patched)
        self.assertIn(b'uint64_t expected_q16 = 0;',patched)
        self.assertIn(b'curre',patched)
        self.assertIn(b'if (override_active || !skip) return uncorrected;',patched)
        self.assertEqual(patched.count(b'struct Stage {'),1)
    def test_refuse_unpinned_twice_patched(self):
        fake=self.fake()
        with patch.object(src,'PIN_GIT_BLOB',src.git_blob(fake)):
            result=src.replace_stage(fake)
            with self.assertRaisesRegex(ValueError,'SOURCE_BLOB_DRIFT'):
                src.replace_stage(result)
    def test_reject_ambiguous_stage_anchor(self):
        fake=self.fake()+src.START.encode()
        with patch.object(src,'PIN_GIT_BLOB',src.git_blob(fake)):
            with self.assertRaisesRegex(ValueError,'STAGE_ANCHOR'):
                src.replace_stage(fake)
    def test_no_new_side_data_or_external_seed(self):
        self.assertNotIn('fopen(',src.REPLACEMENT)
        self.assertNotIn('getenv(',src.REPLACEMENT)
        self.assertNotIn('rand(',src.REPLACEMENT)
        self.assertNotIn('extern ',src.REPLACEMENT)
    def test_exact_pool_geometry(self):
        self.assertEqual(src.REPLACEMENT.count('PoolRow pool[16]'),1)
        self.assertIn('(predicted_side << 3) | (bit_pos & 7)',src.REPLACEMENT)
    def test_git_blob_known(self):
        self.assertEqual(src.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_independent_reference_rejects_incomplete_cpp_log(self):
        with self.assertRaisesRegex(ValueError,"MISSING_GROUNDED_CPP_METRICS"):
            ref.baseline_ref.parse("status=ok")
    def test_counter_math_initial_prior_is_one(self):
        for obs in (0,1,500):
            expected=obs<<16
            numerator=(obs+16)<<32
            denominator=expected+(16<<16)
            self.assertEqual(numerator//denominator,1<<16)

if __name__=="__main__":unittest.main(verbosity=2)
