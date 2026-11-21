#!/usr/bin/env python3
"""Falsifiable holdout gate for SEMCACHE, NOT an enwik9 Hutter score."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

THRESHOLDS=(990,995,999)
OFFSETS_MIB=(32,96,192)
UPSTREAM='35d1957a5074db802fc134126afc77b76d931761'


def summarize(manifest:dict, runs:dict[tuple[int,int],dict]):
    samples=manifest.get('holdouts',[])
    if not (manifest.get('lossy_projection') is True and
            manifest.get('competitive_hutter_score') is None and
            manifest.get('input_bytes')==1_000_000_000 and
            len(samples)==len(OFFSETS_MIB)):
        raise ValueError('Cannot treat this manifest as official enwik9 holdouts')
    if [x['offset_mib'] for x in samples]!=list(OFFSETS_MIB):
        raise ValueError('Unexpected holdout offsets')
    if len(set(x['sample_sha256'] for x in samples))!=len(samples):
        raise ValueError('Duplicate samples')
    if sorted(runs)!=sorted((q,offset) for q in THRESHOLDS for offset in OFFSETS_MIB):
        raise ValueError('Nine paired reports required')

    rows=[]
    size_by_q={}
    for q in THRESHOLDS:
        binary_sizes=set()
        for sample in samples:
            off=sample['offset_mib']
            d=runs[(q,off)]
            b,p,g=d['coder_report'],d['patch'],d['lab_patch']
            if not (p.get('upstream_commit')==UPSTREAM and p.get('threshold_qpe3')==q
                    and p.get('original_blob')=='20614538d3ff90906163a6bd9150894cbb7020f1'
                    and g.get('head_commit')==UPSTREAM
                    and sorted(g.get('changed_files',[]))==['src/runner.cpp','src/tf1/tf1_gate.cpp']):
                raise ValueError(f'Unpinned source or unexpected patch at {q}/{off}')
            if p.get('changed_source_files')!=([] if q==990 else ['src/semantic_cache.h']):
                raise ValueError(f'Unexpected patch scope at {q}/{off}')
            if not (b.get('status')=='verified_roundtrip'
                    and b.get('lossless_roundtrip_verified') is True
                    and b.get('research_only') is True
                    and b.get('self_extracting_archive') is False
                    and b.get('hutter_score_bytes') is None
                    and b.get('source_sha256')==sample['sample_sha256']
                    and b.get('source_bytes')==sample['sample_bytes']):
                raise ValueError(f'Noncomparable data or failed roundtrip {q}/{off}')
            if type(b.get('lab_coder_bytes')) is not int or b['lab_coder_bytes']<=0:
                raise ValueError('Invalid stream size')
            if type(b.get('unpacked_program_bytes')) is not int or b['unpacked_program_bytes']<=0:
                raise ValueError('Invalid program size')
            for phase in ('compression','decompression'):
                m=b.get(phase,{})
                if not (isinstance(m.get('wall_s'),(int,float)) and m['wall_s']>0
                        and type(m.get('max_rss_kib')) is int and m['max_rss_kib']>0
                        and m['max_rss_kib'] <= 10*1024*1024):
                    raise ValueError(f'Invalid resources in {q}/{off}/{phase}')
            binary_sizes.add(b['unpacked_program_bytes'])
            rows.append(dict(threshold_qpe3=q,offset_mib=off,
                source_sha256=b['source_sha256'],lab_stream_bytes=b['lab_coder_bytes'],
                lab_stream_sha256=b['lab_coder_sha256'],
                unpacked_program_bytes=b['unpacked_program_bytes'],
                unpacked_program_sha256=b['unpacked_program_sha256'],
                compression=b['compression'],decompression=b['decompression'],
                roundtrip_verified=True))
        if len(binary_sizes)!=1:
            raise ValueError('Same variant has inconsistent executable size across inputs')
        size_by_q[q]=next(iter(binary_sizes))

    reference={r['offset_mib']:r for r in rows if r['threshold_qpe3']==990}
    for r in rows:
        r['delta_stream_bytes_from_q990']=(r['lab_stream_bytes']-
            reference[r['offset_mib']]['lab_stream_bytes'])
    aggregates=[]
    for q in THRESHOLDS:
        rs=[r for r in rows if r['threshold_qpe3']==q]
        d=sum(r['delta_stream_bytes_from_q990'] for r in rs)
        wins=sum(r['delta_stream_bytes_from_q990']<0 for r in rs)
        ref_total=sum(reference[o]['lab_stream_bytes'] for o in OFFSETS_MIB)
        aggregates.append(dict(threshold_qpe3=q,
            total_lab_stream_bytes=sum(r['lab_stream_bytes'] for r in rs),
            delta_total_stream_bytes_from_q990=d,
            relative_stream_delta_percent=round(100*d/ref_total,4),
            win_count=wins,loss_count=sum(r['delta_stream_bytes_from_q990']>0 for r in rs),
            program_bytes=size_by_q[q],
            delta_unpacked_program_bytes=size_by_q[q]-size_by_q[990],
            provisional_support=(q!=990 and d<0 and wins>=2)))
    return {
        'project':'OMÉGA-R v0.16 SEMCACHE high-threshold holdout A/B',
        'status':'all_nine_lab_roundtrips_verified',
        'input_is_lossy_projection':True,
        'samples_from_authentic_enwik9':True,
        'holdout_offsets_mib':list(OFFSETS_MIB),
        'reference_qpe3':990,
        'hypothesis':'More SEMCACHE lookups via upper thresholds 995 or 999',
        'results':rows,
        'aggregates':aggregates,
        'any_provisionally_supported':any(a['provisional_support'] for a in aggregates),
        'conclusion_scope':'Only nonofficial lab coder streams on 3 disjoint projected holdouts, not enwik9 or an archive score',
        'official_hutter_score':None,
        'full_enwik9_compared':False,
        'self_extracting_archive_compared':False,
        'jury_approved':False,
        'submission_sent':False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--reports',type=Path,required=True)
    a=p.parse_args()
    manifest=json.loads(a.manifest.read_text())
    d={}
    for q in THRESHOLDS:
        for off in OFFSETS_MIB:
            folder=a.reports / f'q{q}' / f'h{off}'
            d[q,off]={
                'coder_report':json.loads((folder/'coder_report.json').read_text()),
                'patch':json.loads((a.reports/f'q{q}'/'semcache_patch.json').read_text()),
                'lab_patch':json.loads((a.reports/f'q{q}'/'lab_patch.json').read_text()),
            }
    data=summarize(manifest,d)
    (a.reports/'comparison.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
