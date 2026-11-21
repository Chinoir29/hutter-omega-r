#!/usr/bin/env python3
"""Profile real post-WRT/pre-coder stream, never assert a prize score.

Uses zlib(3) in fixed windows as a diagnostic proxy only. Does not produce or
publish raw corpus bytes, dictionary bytes, model weights or a competition archive.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import zlib

def profile(path:Path, chunk_bytes:int=8<<20)->dict:
    if chunk_bytes <= 0:
        raise ValueError('positive chunk size required')
    sha=hashlib.sha256()
    rows=[]
    count=0
    with path.open('rb') as f:
        while data:=f.read(chunk_bytes):
            sha.update(data)
            hist=Counter(data)
            n=len(data)
            h=-sum((v/n)*math.log2(v/n) for v in hist.values())
            proxy=len(zlib.compress(data,3))
            rows.append({'block_index':len(rows),'offset_bytes':count,'input_bytes':n,
                         'zlib3_proxy_bytes':proxy,'zlib3_proxy_bits_per_byte':round(8*proxy/n,6),
                         'empirical_byte_entropy_bits':round(h,6)})
            count+=n
    if not rows:
        raise ValueError('empty stream cannot be profiled')
    ranked=sorted(rows,key=lambda x:x['zlib3_proxy_bytes'],reverse=True)[:5]
    return {'status':'REAL_STREAM_PROFILED_NOT_CODED','stream_bytes':count,
        'stream_sha256':sha.hexdigest(),'chunk_bytes':chunk_bytes,
        'zlib3_proxy_total_bytes':sum(x['zlib3_proxy_bytes'] for x in rows),
        'zlib3_proxy_only_no_competition_score':True,
        'top5_proxy_cost_blocks':[x['block_index'] for x in ranked],
        'blocks':rows,'official_hutter_score':None,'archive9':None,
        'independently_reconstructs_enwik9':False}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stream',type=Path)
    ap.add_argument('--chunk',type=int,default=8<<20)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=profile(args.stream,args.chunk)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='blocks'},indent=2))

if __name__=='__main__':
    main()
