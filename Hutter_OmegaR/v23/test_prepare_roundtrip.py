"""Four adversarial source-contract tests; real upstream blob pins checked by CI."""
from unittest.mock import patch
import unittest
import prepare_roundtrip as m
import prepare_shadow as v21
ENC='''#include "encoder.h"
void Encoder::Encode(int bit){
  const unsigned int xmid = floor_stage::Mid(x1_, x2_, p_->SemCorrect(floor_.P32(p,
      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7)));
  p_->SemLearn(bit);
}
void Encoder::Flush() {
  total_out_ += out_n_;
  out_n_ = 0;
}
'''
RUN='''void Compress(){
  while (pos < input_bytes) { }
  e.Flush();
  run_mode::gram.Report("compress");
}
void Decompress() {
  for(int pos=0;pos<output_length;++pos){ }
  run_mode::gram.Report("decompress");
}
bool RunCompression(){
  dict_article::strom = temp_bytes;
  Compress(temp_bytes, temp_in, data_out, output_bytes, &p);
}
bool RunDecompression(){
    Decompress(*output_bytes, data_in, temp_out, &p);
  malloc_trim(0);
  if (!text_start::Unpack(temp_path, !MetablockInert())) { }
}
int main(){
  mallopt(M_MMAP_THRESHOLD, 1 << 20);
    if (!RunDecompression(input_path, temp_path, output_path, dictionary,
        &input_bytes, &output_bytes)) { }
}
'''
class SourceTests(unittest.TestCase):
    def fixture(self):
        return {'src/runner.cpp':RUN.encode(),'src/coder/encoder.cpp':ENC.encode(),
                'src/coder/decoder.cpp':b'// true decoder source unchanged'}
    def test_unpinned_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'PINNED_SOURCE_BLOB_MISMATCH'):
            m.transform(self.fixture())
    def test_only_runner_changes(self):
        files=self.fixture()
        with patch.dict(v21.PINS,{p:m.blob(b) for p,b in files.items()}):
            patchset=m.transform(files)
        self.assertEqual(list(patchset),['src/runner.cpp'])
        result=patchset['src/runner.cpp'].decode()
        for token in ('omr23-reference-prefix.bin','omr23-decoded-prefix.bin',
                      'omr21-coded-prefix.bin','OMR21_SHADOW_PREFIX_BYTES'):
            self.assertIn(token,result)
        self.assertEqual(result.count('OMR23_PREFIX_DECODE'),6)
        self.assertIn('Decompress(decode_bytes, data_in, temp_out, &p);',result)
    def test_decoder_loop_anchor_drift_rejected(self):
        f=self.fixture()
        f['src/runner.cpp']=f['src/runner.cpp'].replace(b'run_mode::gram.Report("decompress");',b'none();')
        with patch.dict(v21.PINS,{p:m.blob(b) for p,b in f.items()}):
            with self.assertRaisesRegex(ValueError,'ANCHOR_DECODE_REPORT_NOT_UNIQUE'):
                m.transform(f)
    def test_main_flags_anchor_drift_rejected(self):
        f=self.fixture()
        f['src/runner.cpp']=f['src/runner.cpp'].replace(b'mallopt(M_MMAP_THRESHOLD, 1 << 20);',b'noop();')
        with patch.dict(v21.PINS,{p:m.blob(b) for p,b in f.items()}):
            with self.assertRaisesRegex(ValueError,'ANCHOR_DECODE_PPMD_MODE_NOT_UNIQUE'):
                m.transform(f)
if __name__=='__main__':unittest.main(verbosity=2)
