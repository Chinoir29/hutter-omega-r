from unittest.mock import patch
import unittest
import prepare_shadow as p

class SourceGateTests(unittest.TestCase):
    def fixture(self):
        enc='''#include "encoder.h"
void Encoder::Encode(int bit) {
  const unsigned int xmid = floor_stage::Mid(x1_, x2_, p_->SemCorrect(floor_.P32(p,
      p_->bitl_override_,
      p_->AdepthSkipped() ? 1 : 0,
      bb_bitl, p_->bb_z_, p_->bitl_m1raw_, bit_head::MetaOff() ? 1 : 0,
      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7)));
  p_->SemLearn(bit);
}
void Encoder::Flush() {
  total_out_ += out_n_;
  out_n_ = 0;
}
'''
        run='''void Compress(unsigned long long input_bytes, FILE* is) {
  while (pos < input_bytes) {
    // coded bit loop
  }
}
bool RunCompression() {
  Compress(temp_bytes, temp_in, data_out, output_bytes, &p);
  return true;
}
'''
        return {'src/coder/encoder.cpp':enc.encode(),'src/runner.cpp':run.encode(),
                'src/coder/decoder.cpp':b'/*decoder pin*/'}

    def test_git_blob(self):
        self.assertEqual(p.blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_refuse_unpinned_source(self):
        with self.assertRaisesRegex(ValueError,'PINNED_SOURCE_BLOB_MISMATCH'):
            p.patch_sources(self.fixture(),b'// irrelevant\n')
    def test_read_only_shadow(self):
        data=self.fixture()
        with patch.dict(p.PINS,{k:p.blob(v) for k,v in data.items()}):
            patched=p.patch_sources(data,b'// test header\n')
        e=patched['src/coder/encoder.cpp'].decode()
        self.assertIn('omr21_shadow::Before(omr21_p32, p_->BbBitCtx())',e)
        self.assertIn('omr21_shadow::After(bit)',e)
        self.assertIn('omr21_shadow::Report()',e)
        self.assertIn('while (pos < omr21_cap)',patched['src/runner.cpp'].decode())
        self.assertNotIn('src/coder/decoder.cpp',patched)
        with patch.dict(p.PINS,{k:p.blob(v) for k,v in data.items()}):
            ctrl=p.patch_sources(data,b'// test header\n',shadow=False)
        self.assertEqual(list(ctrl),['src/runner.cpp'])
        self.assertEqual(ctrl['src/runner.cpp'],patched['src/runner.cpp'])
    def test_reject_double_probability_anchor(self):
        data=self.fixture()
        data['src/coder/encoder.cpp']+=b'\n  const unsigned int xmid = floor_stage::Mid(x1_, x2_, p_->SemCorrect(floor_.P32(p,'
        with patch.dict(p.PINS,{k:p.blob(v) for k,v in data.items()}):
            with self.assertRaisesRegex(ValueError,'ANCHOR_DRIFT'):
                p.patch_sources(data,b'header')
    def test_reject_wrong_coder_loop(self):
        data=self.fixture()
        data['src/runner.cpp']=data['src/runner.cpp'].replace(b'while (pos < input_bytes)',b'while (pos < wrong)')
        with patch.dict(p.PINS,{k:p.blob(v) for k,v in data.items()}):
            with self.assertRaisesRegex(ValueError,'PREFIX_ANCHOR_DRIFT'):
                p.patch_sources(data,b'header')

if __name__ == '__main__':unittest.main(verbosity=2)
