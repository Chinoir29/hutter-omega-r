"""Synthetic fixtures for quality gate; not actual compression measurements."""
import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summarize_holdouts import summarize, THRESHOLDS, OFFSETS_MIB, UPSTREAM

def fixture():
    manifest={
        'input_bytes':1_000_000_000,'lossy_projection':True,'competitive_hutter_score':None,
        'holdouts':[{'offset_mib':off,'sample_bytes':65536,'sample_sha256':str(off)*16} for off in OFFSETS_MIB]
    }
    rows={}
    for q in THRESHOLDS:
        for off in OFFSETS_MIB:
            rows[q,off]={
                'patch':{'upstream_commit':UPSTREAM,'threshold_qpe3':q,
                   'original_blob':'20614538d3ff90906163a6bd9150894cbb7020f1',
                   'changed_source_files':[] if q==990 else ['src/semantic_cache.h']},
                'lab_patch':{'head_commit':UPSTREAM,'changed_files':['src/runner.cpp','src/tf1/tf1_gate.cpp']},
                'coder_report':{
                    'status':'verified_roundtrip','research_only':True,'self_extracting_archive':False,
                    'lossless_roundtrip_verified':True,'source_bytes':65536,'source_sha256':str(off)*16,
                    'lab_coder_bytes':20000+(q-990)+(off//32),
                    'lab_coder_sha256':'f'*64,'unpacked_program_bytes':621432,
                    'unpacked_program_sha256':'a'*64,
                    'hutter_score_bytes':None,
                    'compression':{'wall_s':15.0,'max_rss_kib':7000000},
                    'decompression':{'wall_s':16.0,'max_rss_kib':6000000},
                }
            }
    return manifest,rows

class TestSummarizer(unittest.TestCase):
    def test_nine_reports_pass(self):
        m,r=fixture();x=summarize(m,r)
        self.assertEqual(x['status'],'all_nine_lab_roundtrips_verified')
        self.assertEqual(len(x['results']),9)
        self.assertIsNone(x['official_hutter_score'])
        self.assertFalse(x['any_provisionally_supported'])
    def test_aggregate_positive_delta(self):
        m,r=fixture();x=summarize(m,r)
        self.assertEqual(x['aggregates'][1]['delta_total_stream_bytes_from_q990'],15)
    def test_provisionally_supported_if_two_win_and_sum_improves(self):
        m,r=fixture()
        for off in OFFSETS_MIB[:2]:r[995,off]['coder_report']['lab_coder_bytes']-=20
        x=summarize(m,r)
        self.assertTrue(x['aggregates'][1]['provisional_support'])
    def test_mismatched_source_rejected(self):
        m,r=fixture();r[999,32]['coder_report']['source_sha256']='BAD'
        with self.assertRaises(ValueError):summarize(m,r)
    def test_wrong_upstream_rejected(self):
        m,r=fixture();r[995,96]['patch']['upstream_commit']='BAD'
        with self.assertRaises(ValueError):summarize(m,r)
    def test_wrong_patch_scope_rejected(self):
        m,r=fixture();r[999,96]['patch']['changed_source_files']=['README.md']
        with self.assertRaises(ValueError):summarize(m,r)
    def test_missing_run_rejected(self):
        m,r=fixture();del r[995,96]
        with self.assertRaises(ValueError):summarize(m,r)
    def test_duplicate_sample_rejected(self):
        m,r=fixture();m['holdouts'][1]['sample_sha256']=m['holdouts'][0]['sample_sha256']
        with self.assertRaises(ValueError):summarize(m,r)
    def test_missing_roundtrip_rejected(self):
        m,r=fixture();r[990,192]['coder_report']['lossless_roundtrip_verified']=False
        with self.assertRaises(ValueError):summarize(m,r)
    def test_wrong_resource_rejected(self):
        m,r=fixture();r[990,192]['coder_report']['compression']['max_rss_kib']=10*1024*1024+1
        with self.assertRaises(ValueError):summarize(m,r)
    def test_wrong_manifest_rejected(self):
        m,r=fixture();m['lossy_projection']=False
        with self.assertRaises(ValueError):summarize(m,r)

if __name__=='__main__':unittest.main(verbosity=2)
