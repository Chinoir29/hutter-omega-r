"""Adversarial v0.28 source gates and an independent math reference for Bayes mixing."""
from pathlib import Path
from unittest.mock import patch
import math
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_bayesian_pair as g

ORIGINAL_ENCODER = '''#include "encoder.h"
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
'''.encode()
ORIGINAL_DECODER = ORIGINAL_ENCODER.replace(b'encoder.h',b'decoder.h').replace(
    b'Encoder::Encode',b'Decoder::Decode').replace(b'void Encoder::Flush()',b'void extraneous()')


class InsertionTests(unittest.TestCase):
    def test_git_blob(self):
        self.assertEqual(g.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_unpinned_source_refused(self):
        with self.assertRaisesRegex(ValueError,'UPSTREAM_CODEC_DRIFT'):
            g.instrument(ORIGINAL_ENCODER,'encoder')
    def test_both_routes_mirror_probability_and_learning(self):
        with patch.dict(g.UPSTREAM_BLOBS, {'src/coder/encoder.cpp':g.git_blob(ORIGINAL_ENCODER),
                                          'src/coder/decoder.cpp':g.git_blob(ORIGINAL_DECODER)}):
            e=g.instrument(ORIGINAL_ENCODER,'encoder').decode()
            d=g.instrument(ORIGINAL_DECODER,'decoder').decode()
        for code in (e,d):
            self.assertEqual(code.count('omr28_bitmix::Before('),1)
            self.assertEqual(code.count('omr28_bitmix::After('),1)
            self.assertIn('const uint32_t omr28_original_p32',code)
        self.assertEqual(e.count('omr28_bitmix::Report();'),1)
        self.assertNotIn('omr28_bitmix::Report();',d)
    def test_ambiguous_probability_source_rejected(self):
        dup=ORIGINAL_ENCODER+g.ORIGINAL_OPEN.encode()
        with patch.dict(g.UPSTREAM_BLOBS,{'src/coder/encoder.cpp':g.git_blob(dup)}):
            with self.assertRaisesRegex(ValueError,'CODEC_ANCHOR_NOT_UNIQUE'):
                g.instrument(dup,'encoder')
    def test_wrong_mode_refused(self):
        with self.assertRaisesRegex(ValueError,'MODE_MUST'):
            g.instrument(ORIGINAL_ENCODER,'both')


class IndependentBayesianLemma(unittest.TestCase):
    def test_exact_mixture_regret_bound_on_all_small_binary_sequences(self):
        # Exact fractional Bayes posterior on a single fixed byte-prefix context.
        # The conditional main-predictor p is not fixed or constant across bits.
        probabilities=[0.65,0.03,0.87,0.7,0.1,0.99,0.39,0.53]
        for value in range(1<<len(probabilities)):
            odds_prior=0.5
            n0=n1=0
            lp0=lp_mix=0.0
            for i,p in enumerate(probabilities):
                bit=(value >> i) & 1
                kt=(n1+0.5)/(n0+n1+1)
                q=odds_prior*kt+(1-odds_prior)*p
                lp0-=math.log2(p if bit else 1-p)
                lp_mix-=math.log2(q if bit else 1-q)
                likelihood_kt=(kt if bit else 1-kt)
                likelihood_p=(p if bit else 1-p)
                odds_prior=(odds_prior*likelihood_kt)/(odds_prior*likelihood_kt+(1-odds_prior)*likelihood_p)
                if bit:n1+=1
                else:n0+=1
            self.assertLessEqual(lp_mix-lp0,1.0+1e-9)
    def test_zero_contexts_do_not_pay_a_prefix_prior(self):
        self.assertEqual(len(g.UPSTREAM_BLOBS),2)


if __name__=='__main__':unittest.main(verbosity=2)
