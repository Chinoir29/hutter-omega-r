#!/usr/bin/env python3
"""Strict A/B aggregation, original raw Wiki excerpt SHA-256 verified in each trial.

A successful score here concerns only a modified research coder, not Hutter.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

UPSTREAM='35d1957a5074db802fc134126afc77b76d931761'
THRESHOLDS=(990,999)
OFFSETS=(256,384,640)
EXPECTED_SHA='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'


def summarize(manifest:dict, trials:dict[tuple[int,int],dict]) -> dict:
    examples=manifest.get('samples',[])
    if not (manifest.get('source_bytes')==1_000_000_000
            and manifest.get('source_sha256')==EXPECTED_SHA
            and manifest.get('upstream_commit')==UPSTREAM
            and manifest.get('lossy_projection') is False
            and manifest.get('contest_coding_path') is False
            and manifest.get('hutter_score') is None
            and manifest.get('offsets_mib')==list(OFFSETS)
            and len(examples)==len(OFFSETS)
            and [r.get('offset_mib') for r in examples]==list(OFFSETS)
            and len({r.get('raw_sha256') for r in examples})==3):
        raise ValueError('Unverifiable original-source manifest')
    if set(trials)!={(q,off) for q in THRESHOLDS for off in OFFSETS}:
        raise ValueError('Six A/B trials required')
    rows=[]
    programs={}
    for threshold in THRESHOLDS:
        binary_sizes=set()
        binary_hashes=set()
        for item in examples:
            off=item['offset_mib'];case=trials[threshold,off]
            b,p,g=case['lab'],case['threshold_patch'],case['lab_patch']
            if not (p.get('upstream_commit')==UPSTREAM
                    and p.get('threshold_qpe3')==threshold
                    and p.get('original_blob')=='20614538d3ff90906163a6bd9150894cbb7020f1'
                    and p.get('changed_source_files')==([] if threshold==990 else ['src/semantic_cache.h'])
                    and g.get('head_commit')==UPSTREAM
                    and sorted(g.get('changed_files',[]))==['src/runner.cpp','src/tf1/tf1_gate.cpp']):
                raise ValueError(f'Unsafe source patch at {threshold}/{off}')
            if not (b.get('status')=='two_stage_verified'
                    and b.get('research_only') is True
                    and b.get('contest_eligible') is False
                    and b.get('self_extracting_archive') is False
                    and b.get('hutter_score') is None
                    and b.get('lossless_escape') is True
                    and b.get('roundtrip_escaped_sha256') is True
                    and b.get('roundtrip_raw_excerpt_sha256') is True
                    and b.get('offset_mib')==off
                    and b.get('original_raw_bytes')==item['raw_bytes']
                    and b.get('original_raw_sha256')==item['raw_sha256']
                    and b.get('escaped_bytes')==item['encoded_bytes']
                    and b.get('escaped_sha256')==item['encoded_sha256']):
                raise ValueError(f'Cannot verify raw original from run {threshold}/{off}')
            if type(b.get('lab_coder_bytes')) is not int or b['lab_coder_bytes']<=0:
                raise ValueError('Bad stream size')
            if type(b.get('unpacked_program_bytes')) is not int or b['unpacked_program_bytes']<=0:
                raise ValueError('Bad program size')
            for phase in ('compression','decompression'):
                res=b.get(phase,{})
                if not (type(res.get('wall_s')) in (int,float) and res['wall_s']>0
                        and type(res.get('max_rss_kib')) is int
                        and 0<res['max_rss_kib']<=10*1024*1024):
                    raise ValueError('Resource time/RSS missing or invalid')
            binary_sizes.add(b['unpacked_program_bytes'])
            binary_hashes.add(b['unpacked_program_sha256'])
            rows.append({'threshold_qpe3':threshold,'offset_mib':off,
                'original_raw_bytes':b['original_raw_bytes'],
                'original_raw_sha256':b['original_raw_sha256'],
                'escaped_bytes':b['escaped_bytes'],
                'lab_stream_bytes':b['lab_coder_bytes'],
                'lab_stream_sha256':b['lab_coder_sha256'],
                'unpacked_program_bytes':b['unpacked_program_bytes'],
                'compression':b['compression'],'decompression':b['decompression'],
                'both_sha256_roundtrips_pass':True})
        if len(binary_sizes)!=1 or len(binary_hashes)!=1:
            raise ValueError('Inconsistent binary for same threshold')
        programs[threshold]=next(iter(binary_sizes))
    base={x['offset_mib']:x['lab_stream_bytes'] for x in rows if x['threshold_qpe3']==990}
    agg=[]
    for threshold in THRESHOLDS:
        cases=[r for r in rows if r['threshold_qpe3']==threshold]
        deltas=[r['lab_stream_bytes']-base[r['offset_mib']] for r in cases]
        agg.append({'threshold_qpe3':threshold,
                    'total_coder_bytes':sum(r['lab_stream_bytes'] for r in cases),
                    'delta_bytes_vs_990':sum(deltas),
                    'change_percent_vs_990':round(100*sum(deltas)/sum(base.values()),4),
                    'wins':sum(d<0 for d in deltas),'losses':sum(d>0 for d in deltas),
                    'unchanged':sum(d==0 for d in deltas),
                    'unpacked_program_bytes':programs[threshold],
                    'binary_delta_bytes':programs[threshold]-programs[990],
                    'provisionally_better_in_lab':threshold!=990 and sum(deltas)<0 and sum(d<0 for d in deltas)>=2})
    return {'project':'OMÉGA-R v0.17 reversible-source SEMCACHE A/B',
            'status':'all_six_full_raw_excerpt_roundtrips_verified',
            'raw_wikipedia_bytes_preserved':True,'raw_samples_not_uploaded':True,
            'transform_is_reversible':True,'laboratory_only':True,
            'original_enwik9_not_compressed_in_full':True,
            'upstream_release_path_modified':True,'self_extracting_archive':False,
            'hutter_prize_score':None,'contest_submission_sent':False,
            'offsets_mib':list(OFFSETS), 'raw_bytes_per_sample':65536,
            'reference_threshold_qpe3':990,
            'compared_threshold_qpe3':999,
            'source_pinned':UPSTREAM,
            'samples':examples,'results':rows,'aggregates':agg,
            'interpretation':'Lab coder bitstreams on losslessly escaped original excerpts; NOT a prize score or a validated archive.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--reports',type=Path,required=True)
    a=p.parse_args()
    manifest=json.loads(a.manifest.read_text())
    cases={}
    for threshold in THRESHOLDS:
        folder=a.reports/f'q{threshold}'
        for off in OFFSETS:
            cases[threshold,off]={
                'lab':json.loads((folder/f'h{off}'/'result.json').read_text()),
                'threshold_patch':json.loads((folder/'threshold_patch.json').read_text()),
                'lab_patch':json.loads((folder/'lab_patch.json').read_text())}
    summary=summarize(manifest,cases)
    (a.reports/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary['aggregates'],indent=2),flush=True)

if __name__=='__main__':main()
