#!/usr/bin/env python3
"""Unit tests for audit logic with synthetic reports ONLY (not Hutter scores)."""
import sys
from copy import deepcopy
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assess_hutter_report import classify, limit_for_one_percent, ENWIK9_SHA256


def fixture(score=250_000_000):
    return dict(
        verified_official_input=True,
        source_sha256=ENWIK9_SHA256,
        verified_full_roundtrip_sha256=True,
        organizer_verified=False,
        no_runtime_options_counted=True,
        comp9_bytes=35_000,
        archive9_bytes=score-35_000,
        score_bytes_LOCAL_only=score,
        compression=dict(max_rss_kib=59_000, reported_wall_seconds=1000.0, cpu_core=1),
        decompression=dict(max_rss_kib=58_000, reported_wall_seconds=1000.0, cpu_core=1),
    )


class TestGate(unittest.TestCase):
    def test_exact_threshold_floor(self):
        self.assertEqual(limit_for_one_percent(100_424_672), 99_420_425)
        self.assertEqual(limit_for_one_percent(93_388_956), 92_455_066)

    def test_structurally_consistent_but_not_competitive(self):
        r = classify(fixture())
        self.assertTrue(r['report_internally_consistent'])
        self.assertEqual(r['category'], 'NOT_COMPETITIVE_WITH_AWARDED_THRESHOLD')
        self.assertFalse(r['committee_validated'])

    def test_theoretical_competitive_does_not_equal_award(self):
        r=classify(fixture(92_000_000))
        self.assertEqual(r['category'], 'MEETS_HISTORICAL_SCORE_THRESHOLDS_ONLY')
        self.assertFalse(r['committee_validated'])

    def test_inconsistent_score_rejected(self):
        f=fixture();f['score_bytes_LOCAL_only']+=1
        self.assertIn('score_does_not_equal_program_plus_archive', classify(f)['issues'])

    def test_wrong_source_rejected(self):
        f=fixture();f['source_sha256']='0'*64
        self.assertIn('source_sha256_mismatch', classify(f)['issues'])

    def test_roundtrip_false_rejected(self):
        f=fixture();f['verified_full_roundtrip_sha256']=False
        self.assertIn('lossless_reconstruction_not_verified', classify(f)['issues'])

    def test_ram_over_limit_rejected(self):
        f=fixture();f['compression']['max_rss_kib']=10*1024*1024+1
        self.assertIn('compression_rss_exceeds_10_gib', classify(f)['issues'])

    def test_external_args_not_counted_rejected(self):
        f=fixture();f['no_runtime_options_counted']=False
        self.assertIn('command_arguments_not_accounted_for', classify(f)['issues'])

    def test_bool_is_not_integer(self):
        f=fixture();f['comp9_bytes']=True
        self.assertIn('missing_or_invalid_comp9_bytes', classify(f)['issues'])

    def test_missing_cpu_phase_rejected(self):
        f=fixture();del f['decompression']
        self.assertIn('missing_decompression_measurements', classify(f)['issues'])

if __name__ == '__main__':unittest.main(verbosity=2)
