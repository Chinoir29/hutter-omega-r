"""Cross-source provenance adversaries for OMÉGA-R phase-to-real-cost join."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import join_phase_cost as p

class PhaseJoinTests(unittest.TestCase):
    def fixtures(self):
        phase={
            "status":"ACTUAL_PRECODER_PHASE_MAP_NOT_CMIX_COMPRESSED",
            "source_git_commit":p.UPSTREAM,
            "stream_sha256":p.STREAM_SHA,
            "total_exact_page_markers":7,
            "first_marker_offset":100,
            "first_marker_chunk":0,
            "chunks":[
              {"index":0,"start_byte":0,"end_byte_exclusive":16,"page_anchors":1},
              {"index":1,"start_byte":16,"end_byte_exclusive":32,"page_anchors":2},
              {"index":2,"start_byte":32,"end_byte_exclusive":48,"page_anchors":4},
            ]}
        model={
            "classification":"REPROCESSED_PUBLISHED_CMIX_CODER_COST_MAP_NOT_LOCAL_REEXECUTION",
            "source_commit":p.UPSTREAM,
            "omr19_stream_sha256":p.STREAM_SHA,
            "source_file":"doc/stream_rate.tsv",
            "source_blob_sha":"2a042eb0b69a31b9033721485e364de13ee0f093",
            "source_rows":1000,
            "source_total_model_coded_bytes":85417870,
            "alignment":"interpolated, not exact at the 8MiB boundaries",
            "windows":[
              {"index":0,"from_bytes":0,"input_bytes":16,"model_output_bytes_approx":8,"model_bits_per_byte_approx":4.0},
              {"index":1,"from_bytes":16,"input_bytes":16,"model_output_bytes_approx":6,"model_bits_per_byte_approx":3.0},
              {"index":2,"from_bytes":32,"input_bytes":16,"model_output_bytes_approx":7,"model_bits_per_byte_approx":3.5},
            ]}
        return phase,model

    def test_grounded_ranking_excludes_first_mixed_window(self):
        phase,cost=self.fixtures()
        out=p.combine(phase,cost)
        self.assertEqual(out["status"],"ACTUAL_PAGE_PHASE_PUBLISHED_CODER_COST_MAP_JOINED")
        self.assertEqual([x["window_index"] for x in out["research_windows_after_first_page"]],[2,1])
        self.assertTrue(out["must_preserve_complete_prior_coder_state_in_window_tests"])
        self.assertIsNone(out["unverified_gain_bytes"])
    def test_refuse_wrong_sha(self):
        phase,cost=self.fixtures()
        cost["omr19_stream_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"NOT_SAME"):
            p.combine(phase,cost)
    def test_refuse_mixed_upstream(self):
        phase,cost=self.fixtures()
        cost["source_commit"]="0000000"
        with self.assertRaisesRegex(ValueError,"DIFFERENT_UPSTREAM"):
            p.combine(phase,cost)
    def test_refuse_off_by_one_window_boundary(self):
        phase,cost=self.fixtures()
        cost["windows"][2]["from_bytes"]=33
        with self.assertRaisesRegex(ValueError,"DIFFERENT_BYTE_WINDOWS"):
            p.combine(phase,cost)
    def test_refuse_missing_window(self):
        phase,cost=self.fixtures()
        cost["windows"].pop()
        with self.assertRaisesRegex(ValueError,"WINDOW_COUNT"):
            p.combine(phase,cost)
    def test_refuse_fake_provenance(self):
        phase,cost=self.fixtures()
        cost["classification"]="COLLECTED_OWN_RUN_NOT_PUBLISHED"
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_PROVENANCE"):
            p.combine(phase,cost)
    def test_correlation_constant_returns_unknown(self):
        self.assertIsNone(p.correlation([1.,1.,1.],[2.,3.,4.]))
    def test_no_page_marker_does_not_select_windows(self):
        phase,cost=self.fixtures()
        phase["first_marker_chunk"]=None
        phase["first_marker_offset"]=None
        phase["total_exact_page_markers"]=0
        for ch in phase["chunks"]:ch["page_anchors"]=0
        self.assertEqual(p.combine(phase,cost)["research_windows_after_first_page"],[])
    def test_reject_negative_measurements(self):
        phase,cost=self.fixtures()
        phase["chunks"][1]["page_anchors"]=-4
        with self.assertRaisesRegex(ValueError,"NEGATIVE_MEASUREMENTS"):
            p.combine(phase,cost)
if __name__=="__main__":
    unittest.main(verbosity=2)
