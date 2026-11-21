#!/usr/bin/env python3
"""Synthetic-only falsification tests, NOT compression experiment results."""
import copy, unittest
from summarize_reversible import summarize, UPSTREAM, EXPECTED_SHA, OFFSETS, THRESHOLDS


def fixture():
    items=[{'offset_mib':off,'raw_bytes':65536,'raw_sha256':f'{off:064x}',
            'encoded_bytes':69000+off,'encoded_sha256':f'{off+1:064x}',
            'lossless_codec_verified':True,'file':f'escaped_{off}MiB.dat'}
           for off in OFFSETS]
    manifest={'source_bytes':1000000000,'source_sha256':EXPECTED_SHA,
              'upstream_commit':UPSTREAM,'lossy_projection':False,
              'contest_coding_path':False,'hutter_score':None,
              'offsets_mib':list(OFFSETS),'samples':items}
    trials={}
    for q in THRESHOLDS:
        for rec in items:
            off=rec['offset_mib']
            trials[q,off]={
                'lab':{'status':'two_stage_verified','research_only':True,
                       'contest_eligible':False,'self_extracting_archive':False,
                       'hutter_score':None,'lossless_escape':True,
                       'roundtrip_escaped_sha256':True,
                       'roundtrip_raw_excerpt_sha256':True,'offset_mib':off,
                       'original_raw_bytes':rec['raw_bytes'],
                       'original_raw_sha256':rec['raw_sha256'],
                       'escaped_bytes':rec['encoded_bytes'],
                       'escaped_sha256':rec['encoded_sha256'],
                       'lab_coder_bytes':20000+off-(10 if q==999 else 0),
                       'lab_coder_sha256':str(q)*16,
                       'unpacked_program_bytes':620000,
                       'unpacked_program_sha256':'aa'*32 if q==990 else 'bb'*32,
                       'compression':{'wall_s':20,'max_rss_kib':6900000},
                       'decompression':{'wall_s':22,'max_rss_kib':6200000}},
                'threshold_patch':{'upstream_commit':UPSTREAM,
                    'threshold_qpe3':q,
                    'original_blob':'20614538d3ff90906163a6bd9150894cbb7020f1',
                    'changed_source_files':[] if q==990 else ['src/semantic_cache.h']},
                'lab_patch':{'head_commit':UPSTREAM,
                    'changed_files':['src/runner.cpp','src/tf1/tf1_gate.cpp']}}
    return manifest,trials

class TestSummary(unittest.TestCase):
    def test_credible_complete(self):
        a,b=fixture();r=summarize(a,b)
        self.assertEqual(r['status'],'all_six_full_raw_excerpt_roundtrips_verified')
        self.assertTrue(r['raw_wikipedia_bytes_preserved'])
        self.assertIsNone(r['hutter_prize_score'])
        self.assertEqual(r['aggregates'][1]['delta_bytes_vs_990'],-30)
    def test_missing_mode(self):
        a,b=fixture();del b[999,256]
        with self.assertRaises(ValueError):summarize(a,b)
    def test_lossy_flag_denied(self):
        a,b=fixture();a['lossy_projection']=True
        with self.assertRaises(ValueError):summarize(a,b)
    def test_forged_official_prize_score_denied(self):
        a,b=fixture();b[999,384]['lab']['hutter_score']=42
        with self.assertRaises(ValueError):summarize(a,b)
    def test_bad_raw_hash_denied(self):
        a,b=fixture();b[990,256]['lab']['original_raw_sha256']='f'*64
        with self.assertRaises(ValueError):summarize(a,b)
    def test_failed_decoding_denied(self):
        a,b=fixture();b[999,640]['lab']['roundtrip_raw_excerpt_sha256']=False
        with self.assertRaises(ValueError):summarize(a,b)
    def test_bad_source_commit_denied(self):
        a,b=fixture();b[990,256]['lab_patch']['head_commit']='0'*40
        with self.assertRaises(ValueError):summarize(a,b)
    def test_bad_unlisted_file_denied(self):
        a,b=fixture();b[999,640]['lab_patch']['changed_files'].append('secret.cpp')
        with self.assertRaises(ValueError):summarize(a,b)
    def test_wrong_sample_sha_denied(self):
        a,b=fixture();b[999,640]['lab']['escaped_sha256']='0'*64
        with self.assertRaises(ValueError):summarize(a,b)
    def test_exceeds_memory_denied(self):
        a,b=fixture();b[999,384]['lab']['compression']['max_rss_kib']=10*1024*1024+1
        with self.assertRaises(ValueError):summarize(a,b)
    def test_program_varies_across_samples_denied(self):
        a,b=fixture();b[999,384]['lab']['unpacked_program_bytes']+=12
        with self.assertRaises(ValueError):summarize(a,b)
    def test_worse_variant_rejected(self):
        a,b=fixture();
        for o in OFFSETS:b[999,o]['lab']['lab_coder_bytes']+=50
        r=summarize(a,b)
        self.assertFalse(r['aggregates'][1]['provisionally_better_in_lab'])
    def test_source_whole_file_sha_denied(self):
        a,b=fixture();a['source_sha256']='0'*64
        with self.assertRaises(ValueError):summarize(a,b)

if __name__=='__main__':unittest.main(verbosity=2)
