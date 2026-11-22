"""v0.28 adversarial tests of paired report parser and native-size accounting."""
from pathlib import Path
from unittest.mock import patch
import hashlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_real_bayesian_pair as m


class PairReportTests(unittest.TestCase):
    def report(self, *, gain="5.2500", contexts=42):
        return ("preprocessing ...\n"
            "OMR28_BAYES_REPORT coded_bits=4071047 active_contexts="
            f"{contexts} changed_probabilities=100 "
            f"baseline_ideal_bits=3400000.0000 candidate_ideal_bits=3399994.7500 ideal_gain_bits={gain}\n")
    def test_parse_valid_model_scores(self):
        result=m.report_from_encoder(self.report())
        self.assertEqual(result["coded_bits"],m.FREE_CODED_BITS)
        self.assertEqual(result["active_contexts"],42)
        self.assertEqual(result["ideal_gain_bits"],5.25)
    def test_refuse_unbounded_logloss_regret(self):
        with self.assertRaisesRegex(ValueError,"BAYES_REGRET_BOUND_VIOLATED"):
            m.report_from_encoder(self.report(gain="-99.5"))
    def test_refuse_missing_or_double_report(self):
        for s in ("",self.report()+self.report()):
            with self.assertRaisesRegex(ValueError,"MISSING_OR_MULTIPLE"):
                m.report_from_encoder(s)
    def test_refuse_truncated_report(self):
        with self.assertRaisesRegex(ValueError,"BAD_BAYES_REPORT_FIELDS"):
            m.report_from_encoder("OMR28_BAYES_REPORT coded_bits=4071047\n")
    def test_reject_unverified_corpus_before_creating_workdir(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'wrong';p.write_bytes(b'not enwik9')
            wd=Path(td)/'work'
            with self.assertRaisesRegex(ValueError,'CANONICAL_CORPUS'):
                m.run_pair(wd,p,Path(td)/'out.json')
            self.assertFalse(wd.exists())
    def test_native_container_count_and_endian(self):
        with tempfile.TemporaryDirectory() as td:
            from struct import pack
            p=Path(td)/'archive9'
            with p.open('wb') as out:
                out.write(b'\x7fELF'+b'Z'*176842)
                out.write(b'0'*m.WEIGHTS_BYTES)
                out.write(b'Q'*300)
                out.write(pack('<ii',300,m.WEIGHTS_BYTES))
            record=m.native_archive_layout(p)
            self.assertEqual(record['decoder_stub_bytes'],176846)
            self.assertEqual(record['arithmetic_payload_bytes'],300)
            self.assertEqual(record['archive_bytes'],176846+m.WEIGHTS_BYTES+300+8)
    def test_corrupted_trailer_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            from struct import pack
            p=Path(td)/'archive9'
            with p.open('wb') as out:
                out.write(b'\x7fELF'+b'A'*2_000_000)
                out.write(pack('<ii',400000,8))
            with self.assertRaisesRegex(ValueError,'BAD_NATIVE_ARCHIVE_LAYOUT'):
                m.native_archive_layout(p)

if __name__=='__main__':unittest.main(verbosity=2)
