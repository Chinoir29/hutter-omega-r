#!/usr/bin/env python3
"""Synthetic-only tests for the SEMCACHE three-way laboratory A/B aggregator."""
import copy
import unittest
from summarize_lab import summarize, SAMPLE_SHA, UPSTREAM, BASELINE_STREAM_SHA

def make_fixture():
    out = {}
    for q in (990, 980, 970):
        out[q] = {
            "coder_report": {
                "status":"verified_roundtrip",
                "lossless_roundtrip_verified":True,
                "source_bytes":65536,
                "source_sha256":SAMPLE_SHA,
                "lab_coder_bytes":20533+(990-q),
                "lab_coder_sha256":BASELINE_STREAM_SHA if q==990 else str(q)*16,
                "unpacked_program_bytes":621432,
                "unpacked_program_sha256":"aa"*32,
                "self_extracting_archive":False,
                "hutter_score_bytes":None,
                "compression":{"wall_s":40.0,"max_rss_kib":7100000},
                "decompression":{"wall_s":39.0,"max_rss_kib":5500000}
            },
            "patch":{"baseline_revision":UPSTREAM,"threshold_qpe3":q,"result_blob":"bb"*20},
            "lab_patch":{
                "head_commit":UPSTREAM,
                "changed_files":["src/runner.cpp","src/tf1/tf1_gate.cpp"],
                "runner_patched_git_blob":"cc"*20,
                "gate_patched_git_blob":"dd"*20
            }
        }
    return out


class TestSummarizer(unittest.TestCase):
    def test_three_way_roundtrip(self):
        x=summarize(make_fixture())
        self.assertEqual(x["status"],"all_three_lossless_roundtrips_verified")
        self.assertEqual(len(x["results"]),3)
        self.assertTrue(x["baseline_reproduces_v0143_stream"])
        self.assertTrue(x["observed_threshold_effect"])
        self.assertIsNone(x["hutter_prize_score"])

    def test_missing_mode(self):
        f=make_fixture()
        del f[970]
        with self.assertRaises(ValueError):summarize(f)

    def test_wrong_source_sha(self):
        f=make_fixture()
        f[980]["coder_report"]["source_sha256"]="invalid"
        with self.assertRaises(ValueError):summarize(f)

    def test_wrong_upstream_revision(self):
        f=make_fixture()
        f[970]["lab_patch"]["head_commit"]="0"*40
        with self.assertRaises(ValueError):summarize(f)

    def test_not_lossless(self):
        f=make_fixture()
        f[990]["coder_report"]["lossless_roundtrip_verified"]=False
        with self.assertRaises(ValueError):summarize(f)

    def test_invalid_score_claim(self):
        f=make_fixture()
        f[980]["coder_report"]["hutter_score_bytes"]=50
        with self.assertRaises(ValueError):summarize(f)

    def test_wrong_code_patched(self):
        f=make_fixture()
        f[970]["lab_patch"]["changed_files"]=["src/runner.cpp"]
        with self.assertRaises(ValueError):summarize(f)

    def test_same_stream_is_no_effect(self):
        f=make_fixture()
        for q in (980,970):
            f[q]["coder_report"]["lab_coder_sha256"]=BASELINE_STREAM_SHA
            f[q]["coder_report"]["lab_coder_bytes"]=20533
        x=summarize(f)
        self.assertFalse(x["observed_threshold_effect"])
        self.assertEqual(x["results"][-1]["delta_stream_bytes_vs_control"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
