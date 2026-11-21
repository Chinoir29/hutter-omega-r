#!/usr/bin/env python3
"""OMÉGA-R v0.20: honest AB of *reversible* stream reshapes on the REAL -e pre-coder stream.

Diagnostic only; the independent zlib archive is NOT a Hutter entry. Distinguishes
train-mode selection from an independent heldout comparison and charges identical
container overhead to both sides. Writes no input bytes or compressed payloads to
results.json. All input/output payloads are scratch-only and must not be published.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

MAGIC = b'OMR20\x00\x01\x00'
HEADER = struct.Struct('<8sIQI')
PART = struct.Struct('<BI')
DEFAULT_CHUNK = 8 << 20
MODES = ('identity','split2','split4','reverse','swap_pairs')
CANONICAL_PRECODER_SHA = 'c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718'
CANONICAL_PRECODER_BYTES = 501_062_281


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()


def transform(source: bytes, mode: int) -> bytes:
    if mode == 0: return source
    if mode == 1: return source[::2] + source[1::2]
    if mode == 2: return b''.join(source[i::4] for i in range(4))
    if mode == 3: return source[::-1]
    if mode == 4:
        out = bytearray(source)
        last = len(source) & ~1
        out[:last:2] = source[1:last:2]
        out[1:last:2] = source[:last:2]
        return bytes(out)
    raise ValueError('UNSUPPORTED_MODE')


def inverse(coded: bytes, mode: int) -> bytes:
    if mode in (0,3,4): return transform(coded,mode)
    if mode in (1,2):
        stride = 2 if mode==1 else 4
        n=len(coded)
        sizes=[len(range(i,n,stride)) for i in range(stride)]
        out=bytearray(n)
        pos=0
        for i,count in enumerate(sizes):
            out[i::stride] = coded[pos:pos+count]
            pos+=count
        assert pos == n
        return bytes(out)
    raise ValueError('UNSUPPORTED_MODE')


def compressed_size(data:bytes)->int:
    return len(zlib.compress(data,3))


def choose_mode(input_path: Path, chunk_bytes: int) -> dict:
    """Pre-register train indices i%5==0; remaining 4/5 indices are held out."""
    total=input_path.stat().st_size
    n=math.ceil(total/chunk_bytes)
    summary={name:0 for name in MODES}
    examples=[]
    with input_path.open('rb') as f:
        for i in range(0,n,5):
            f.seek(i*chunk_bytes)
            data=f.read(min(chunk_bytes,total-i*chunk_bytes))
            base=compressed_size(data)
            examples.append({'index':i,'original_bytes':len(data),'baseline_zlib3_bytes':base})
            for k,name in enumerate(MODES):
                other=transform(data,k)
                if inverse(other,k)!=data:
                    raise AssertionError('LOSSY_TRANSFORM_TRAIN '+name)
                summary[name]+=compressed_size(other)
    # Selection on training *alone*. Identity wins ties; no post-hoc winner on heldout.
    chosen=min(range(len(MODES)),key=lambda i:(summary[MODES[i]],i))
    return {'selection_rule':'min sum zlib3 training costs, ties identity',
            'train_indices':[e['index'] for e in examples],
            'training_zlib_bytes_by_mode':summary,
            'chosen_mode':MODES[chosen],'chosen_mode_id':chosen,
            'training_examples':examples,
            'train_delta_bytes':summary['identity']-summary[MODES[chosen]]}


def archive(input_path:Path, dest:Path, chunk_bytes:int, mode:int)->dict:
    nbytes=input_path.stat().st_size
    nchunks=math.ceil(nbytes/chunk_bytes)
    if chunk_bytes < 1 or chunk_bytes > 16 << 20 or not 0 < nchunks < 1<<32:
        raise ValueError('INVALID_BOUNDS')
    if dest.exists(): raise ValueError('REFUSE_OVERWRITE')
    total_deflated=0
    rows=[]
    with input_path.open('rb') as fi, dest.open('xb') as out:
        out.write(HEADER.pack(MAGIC,chunk_bytes,nbytes,nchunks))
        for i in range(nchunks):
            raw=fi.read(chunk_bytes)
            tx=transform(raw,mode)
            if inverse(tx,mode)!=raw: raise AssertionError('LOSSY_TRANSFORM_ARCHIVE')
            coded=zlib.compress(tx,3)
            out.write(PART.pack(mode,len(coded)));out.write(coded)
            total_deflated+=len(coded)
            rows.append({'block':i,'original_bytes':len(raw),'coded_bytes':len(coded),
                         'sha256_prefix':hashlib.sha256(raw).hexdigest()[:16]})
        if fi.read(1): raise AssertionError('UNCONSUMED_DATA')
    expected=HEADER.size+nchunks*PART.size+total_deflated
    if dest.stat().st_size!=expected:raise AssertionError('HEADER_ACCOUNTING_FAILURE')
    return {'path':str(dest),'archive_bytes':expected,'zlib3_payload_bytes':total_deflated,
            'container_overhead_bytes':HEADER.size+nchunks*PART.size,
            'archive_sha256':sha256(dest),'rows':rows}


def restore(path:Path,dest:Path,max_bytes:int=1_000_000_000)->dict:
    if dest.exists():raise ValueError('REFUSE_OVERWRITE')
    with path.open('rb') as src:
        prefix=src.read(HEADER.size)
        if len(prefix)!=HEADER.size:raise ValueError('HEADER_TRUNCATED')
        magic,chunk,total,num=HEADER.unpack(prefix)
        if magic!=MAGIC:raise ValueError('BAD_MAGIC')
        if not 1<=chunk <= (16<<20) or not 1<=total<=max_bytes or num!=math.ceil(total/chunk):
            raise ValueError('UNSAFE_HEADER')
        sha=hashlib.sha256()
        with dest.open('xb') as target:
            got=0
            for i in range(num):
                block_head=src.read(PART.size)
                if len(block_head)!=PART.size:raise ValueError('TRUNCATED_PART_HEADER')
                mode,compressed_bytes=PART.unpack(block_head)
                if mode>=len(MODES) or compressed_bytes<1 or compressed_bytes>chunk*2+1024:
                    raise ValueError('INVALID_PART')
                payload=src.read(compressed_bytes)
                if len(payload)!=compressed_bytes:raise ValueError('TRUNCATED_PART_DATA')
                expected=min(chunk,total-got)
                inflator=zlib.decompressobj()
                tx=inflator.decompress(payload,expected+1)
                if len(tx)!=expected or not inflator.eof or inflator.unused_data or inflator.unconsumed_tail:
                    raise ValueError('INVALID_INFLATE_LENGTH_OR_TRAILING')
                raw=inverse(tx,mode)
                if len(raw)!=expected:raise ValueError('INVALID_INVERSE_LENGTH')
                target.write(raw);sha.update(raw);got+=len(raw)
            if src.read(1):raise ValueError('TRAILING_ARCHIVE_BYTES')
    if got!=total:raise AssertionError('LENGTH_MISMATCH')
    return {'bytes':got,'sha256':sha.hexdigest(),'blocks':num}


def evaluate(input_path:Path, work:Path, out:Path, chunk:int=DEFAULT_CHUNK,
             expected_sha:str=CANONICAL_PRECODER_SHA, expected_size:int=CANONICAL_PRECODER_BYTES)->dict:
    if not input_path.is_file():raise ValueError('MISSING_REAL_STREAM')
    if input_path.stat().st_size!=expected_size or sha256(input_path)!=expected_sha:
        raise ValueError('REAL_STREAM_SHA_OR_SIZE_MISMATCH')
    if not 1 <=chunk<=16<<20:raise ValueError('CHUNK_BOUNDS')
    if work.exists():raise ValueError('WORKDIR_ALREADY_EXISTS')
    work.mkdir(parents=True)
    select=choose_mode(input_path,chunk)
    candidate=select['chosen_mode_id']
    baseline=archive(input_path,work/'baseline.omr20',chunk,0)
    variant=archive(input_path,work/'candidate.omr20',chunk,candidate)
    roundtrips={}
    for label,data in [('baseline',baseline),('candidate',variant)]:
        rest=restore(Path(data['path']),work/(label+'.restored'),max_bytes=expected_size)
        if rest['sha256']!=expected_sha or rest['bytes']!=expected_size:
            raise AssertionError('STREAM_ROUNDTRIP_FAILED '+label)
        roundtrips[label]=rest
    hold_idx=[i for i in range(len(baseline['rows'])) if i%5!=0]
    hold_base=sum(baseline['rows'][i]['coded_bytes'] for i in hold_idx)
    hold_cand=sum(variant['rows'][i]['coded_bytes'] for i in hold_idx)
    decision='KEEP_PROXY_AND_INTEGRATION_RESEARCH' if candidate!=0 and hold_cand<hold_base else 'REJECT_UNIFORM_RESHAPE_PROXY'
    result={'status':'REAL_PRECODER_STREAM_DOUBLE_ROUNDTRIP',
            'source_sha256':expected_sha,'source_bytes':expected_size,
            'chunk_bytes':chunk,'num_chunks':len(baseline['rows']),
            'pre_registered_split':'train i mod 5 = 0; holdout otherwise',
            'training':select,'holdout_blocks':len(hold_idx),
            'holdout_zlib3_baseline_bytes':hold_base,'holdout_zlib3_candidate_bytes':hold_cand,
            'holdout_improvement_bytes':hold_base-hold_cand,
            'baseline_archive_bytes':baseline['archive_bytes'],
            'candidate_archive_bytes':variant['archive_bytes'],
            'container_overhead_bytes_each':baseline['container_overhead_bytes'],
            'full_proxy_improvement_bytes':baseline['archive_bytes']-variant['archive_bytes'],
            'baseline_archive_sha256':baseline['archive_sha256'],
            'candidate_archive_sha256':variant['archive_sha256'],
            'two_exact_stream_sha_roundtrips':roundtrips,
            'per_block_baseline_bytes':[r['coded_bytes'] for r in baseline['rows']],
            'per_block_candidate_bytes':[r['coded_bytes'] for r in variant['rows']],
            'decision':decision,
            'competition_score':None,'independent_enwik9_restoration':False,
            'no_claim_of_hutter_admissibility':True}
    out.write_text(json.dumps(result,indent=2)+'\n')
    # Discard 500MB+ scratch transformed files; release all real stream-derived bytes.
    for f in work.iterdir():f.unlink()
    work.rmdir()
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stream',type=Path)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--chunk',type=int,default=DEFAULT_CHUNK)
    p.add_argument('--expected-sha',default=CANONICAL_PRECODER_SHA)
    p.add_argument('--expected-size',type=int,default=CANONICAL_PRECODER_BYTES)
    a=p.parse_args()
    r=evaluate(a.stream,a.work,a.result,a.chunk,a.expected_sha,a.expected_size)
    print(json.dumps({k:v for k,v in r.items() if k not in ('per_block_baseline_bytes','per_block_candidate_bytes','two_exact_stream_sha_roundtrips')},indent=2))

if __name__=='__main__':main()
