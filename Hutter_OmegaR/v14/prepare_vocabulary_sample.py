#!/usr/bin/env python3
"""Create an explicit *lossily filtered* surrogate stream from authentic enwik9.

Only for the laboratory -c/-d coder on the frozen 208-byte vocabulary.
DO NOT label its resulting payload a Hutter Prize score or an enwik9 archive.
No corpus is exported from GitHub CI.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_LEN=1_000_000_000
EXPECTED_SHA='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'

def sha256(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
    return h.hexdigest()

def get_bitmap(header:Path):
    s=header.read_text(encoding='utf8')
    m=re.search(r'kBitmap\[32\]\s*=\s*\{([^}]*)\}',s,re.S)
    if not m:raise ValueError('Frozen 208-byte vocabulary missing')
    entries=[int(part.strip(),0) for part in m.group(1).split(',') if part.strip()]
    if len(entries)!=32 or sum(x.bit_count() for x in entries)!=208:
        raise ValueError('Unexpected vocabulary size')
    return entries

def project(data:bytes,bitmap,target:int):
    if not 1024<=target<=262144:raise ValueError('target outside bounded lab range')
    retained=bytes(v for v in data if (bitmap[v//8]>>(v%8))&1)
    if len(retained)<target:raise ValueError('Insufficient accepted source bytes')
    return retained[:target]

def selftest():
    bitmap=[255]*32
    bitmap[0]&=~1
    b=project(bytes(range(256))*100,bitmap,2048)
    assert len(b)==2048 and 0 not in b
    try:project(bytes([0])*100,bitmap,2048)
    except ValueError:pass
    else:raise AssertionError('Expected data rejection')
    print('SURROGATE_SELF_TEST_PASS')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--enwik9',type=Path)
    p.add_argument('--vocab-header',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--target',type=int,default=65536)
    args=p.parse_args()
    if args.self_test:selftest();return
    if not(args.enwik9 and args.vocab_header and args.out and args.report):
        p.error('--enwik9 --vocab-header --out --report required')
    if args.enwik9.stat().st_size!=EXPECTED_LEN or sha256(args.enwik9)!=EXPECTED_SHA:
        raise SystemExit('BLOCKED: source is not official enwik9')
    bitmap=get_bitmap(args.vocab_header)
    with args.enwik9.open('rb') as f:data=f.read(4*1024*1024)
    sample=project(data,bitmap,args.target)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(sample)
    summary={
      'scope':'LOSSY_VOCABULARY_PROJECTION_RESEARCH_ONLY',
      'hutter_prize_score':None,
      'source_bytes':EXPECTED_LEN,'source_sha256':EXPECTED_SHA,
      'raw_prefix_bytes_examined':len(data),
      'sample_bytes':len(sample),
      'sample_sha256':hashlib.sha256(sample).hexdigest(),
      'frozen_vocabulary_size':208,
      'excluded_bytes_from_raw_prefix':sum(1 for b in data if not ((bitmap[b//8]>>(b%8))&1)),
      'normalization_is_lossy':True,'official_score_eligible':False
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
