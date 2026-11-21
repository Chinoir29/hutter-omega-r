#!/usr/bin/env python3
"""Create three *lossy* holdout byte streams from authenticated enwik9.

The raw source is never retained in results. The three windows do not overlap
with each other or with the first 4 MiB used by v0.15. Not a Hutter score.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

OFFSETS_MIB=(32,96,192)
WINDOW_BYTES=2*1024*1024
SAMPLE_BYTES=65536
EXPECTED_SIZE=1_000_000_000
EXPECTED_SHA='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def read_bitmap(path:Path):
    source=path.read_text(encoding='utf-8')
    m=re.search(r'kBitmap\[32\]\s*=\s*\{([^}]*)\}',source,re.S)
    if m is None:
        raise ValueError('Frozen vocabulary bitmap not found')
    nums=[int(i.strip(),0) for i in m.group(1).split(',') if i.strip()]
    if len(nums)!=32 or any(n<0 or n>255 for n in nums) or sum(x.bit_count() for x in nums)!=208:
        raise ValueError('Frozen vocabulary does not contain exactly 208 bytes')
    return nums

def project_bytes(data:bytes, bitmap:list[int], target:int=SAMPLE_BYTES)->bytes:
    projected=bytes(ch for ch in data if (bitmap[ch//8]>>(ch%8))&1)
    if len(projected)<target:
        raise ValueError('Window lacks enough permitted bytes')
    return projected[:target]

def make_holdouts(source:Path, header:Path, output:Path):
    if source.stat().st_size != EXPECTED_SIZE or sha256_file(source)!=EXPECTED_SHA:
        raise ValueError('Not canonical enwik9: length or SHA-256 mismatch')
    bitmap=read_bitmap(header)
    output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for start_mib in OFFSETS_MIB:
        with source.open('rb') as f:
            f.seek(start_mib*1024*1024)
            window=f.read(WINDOW_BYTES)
        if len(window)!=WINDOW_BYTES:raise ValueError('Truncated holdout window')
        sample=project_bytes(window,bitmap)
        path=output/f'holdout_{start_mib}MiB.dat'
        path.write_bytes(sample)
        rows.append({
            'offset_mib':start_mib,
            'raw_window_bytes':WINDOW_BYTES,
            'raw_window_sha256':hashlib.sha256(window).hexdigest(),
            'sample_bytes':len(sample),
            'sample_sha256':hashlib.sha256(sample).hexdigest(),
            'removed_bytes_in_raw_window':sum(not ((bitmap[c//8]>>(c%8))&1) for c in window),
            'filename':path.name,
            'lossy':True,
        })
    if len({r['sample_sha256'] for r in rows})!=len(rows):
        raise ValueError('Samples are not independent: duplicate byte streams')
    return {
        'project':'OMÉGA-R v0.16 nonofficial holdout',
        'input_verified_sha256':EXPECTED_SHA,
        'input_bytes':EXPECTED_SIZE,
        'holdouts':rows,
        'reference_source':'https://mattmahoney.net/dc/enwik9.zip',
        'transform':'filter source bytes according to upstream frozen 208-byte vocabulary, retain first 64KiB',
        'lossy_projection':True,
        'competitive_hutter_score':None,
        'no_raw_data_uploaded':True,
    }

def self_test():
    bitmap=[0xff]*32
    for i in range(48):bitmap[i//8]&=~(1<<(i%8))
    assert sum(x.bit_count() for x in bitmap)==208
    assert project_bytes(bytes(range(256))*800,bitmap,65536)==(bytes(range(48,256))*316)[:65536]
    try:project_bytes(bytes([0])*90000,bitmap)
    except ValueError:pass
    else:raise AssertionError('Expected forbidden-byte sample rejection')
    with tempfile.TemporaryDirectory() as d:
        header=Path(d)/'vocab.h'
        header.write_text('constexpr unsigned char kBitmap[32] = {'+','.join(hex(x) for x in bitmap)+'};')
        assert read_bitmap(header)==bitmap
        header.write_text('constexpr unsigned char kBitmap[32] = {0};')
        try:read_bitmap(header)
        except ValueError:pass
        else:raise AssertionError('Bad vocabulary accepted')
    print('HOLDOUT_UNIT_TEST_PASS')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--enwik9',type=Path)
    p.add_argument('--vocab-header',type=Path)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--report',type=Path)
    a=p.parse_args()
    if a.self_test:return self_test()
    if not all((a.enwik9,a.vocab_header,a.out_dir,a.report)):
        p.error('--enwik9 --vocab-header --out-dir --report are required')
    report=make_holdouts(a.enwik9,a.vocab_header,a.out_dir)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
