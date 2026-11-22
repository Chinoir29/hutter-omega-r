#!/usr/bin/env python3
"""Byte-for-byte comparison without publishing any original or decoded bytes."""
from pathlib import Path
import hashlib,json,argparse
def investigate(a:Path,b:Path,chunk:int=1<<20)->dict:
    if not a.is_file() or not b.is_file():raise ValueError('MISSING_PREFIX_STREAM')
    if chunk<=0:raise ValueError('INVALID_CHUNK_SIZE')
    ha,hb=hashlib.sha256(),hashlib.sha256()
    offset=0;first=None;bad=0
    with a.open('rb') as f,b.open('rb') as g:
        while True:
            x=f.read(chunk);y=g.read(chunk)
            if not x and not y:break
            ha.update(x);hb.update(y)
            overlap=min(len(x),len(y))
            for i in range(overlap):
                if x[i]!=y[i]:
                    if first is None:first=offset+i
                    bad+=1
            if len(x)!=len(y):
                bad+=abs(len(x)-len(y))
                if first is None:first=offset+overlap
            offset+=max(len(x),len(y))
    sa,sb=a.stat().st_size,b.stat().st_size
    da,db=ha.hexdigest(),hb.hexdigest()
    return {'source_size':sa,'decoded_size':sb,'source_sha256':da,'decoded_sha256':db,
            'identical':first is None and sa==sb and da==db,
            'first_difference_offset':first,'total_different_or_missing_bytes':bad,
            'contains_raw_content':False,'hutter_score':None}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('decoded',type=Path)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    result=investigate(a.source,a.decoded)
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
