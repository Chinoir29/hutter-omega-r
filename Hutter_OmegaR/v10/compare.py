#!/usr/bin/env python3
"""Reproducible A/B trials. These are NOT Hutter Prize scores.

Examples:
  bash build.sh
  python3 compare.py --out my_results.json
  python3 compare.py --file /path/to/corpus.xml --out my_results.json
"""
import argparse, hashlib, json, pathlib, random, subprocess, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent

def check(label, original, mode):
    comp=ROOT/f'comp9_variant{mode}'
    with tempfile.TemporaryDirectory(prefix='omr10_') as d:
        base=pathlib.Path(d)
        inp=base/'input';inp.write_bytes(original)
        archive=base/'archive9'
        t=time.monotonic()
        p=subprocess.run([str(comp),str(inp),str(archive)],cwd=base,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
        dt=time.monotonic()-t
        if p.returncode!=0:raise RuntimeError((label,mode,'encode',p.stderr[-1200:]))
        decoder=base/'decoded';decoder.mkdir()
        dec=subprocess.run([str(archive)],cwd=decoder,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
        if dec.returncode!=0:raise RuntimeError((label,mode,'decode',dec.stderr[-1200:]))
        result=(decoder/'data9').read_bytes()
        if result!=original:raise AssertionError((label,mode,'non-lossless'))
        return {'dataset':label,'source_bytes':len(original),'variant':mode,
             'compressor_bytes':comp.stat().st_size,'archive_bytes':archive.stat().st_size,
             'score_bytes':comp.stat().st_size+archive.stat().st_size,
             'roundtrip_sha256_verified':hashlib.sha256(result).digest()==hashlib.sha256(original).digest(),
             'duration_compress_s':round(dt,4),
             'sha256_input':hashlib.sha256(original).hexdigest()}

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--file',type=pathlib.Path,action='append',default=[])
    a.add_argument('--out',type=pathlib.Path,default=ROOT/'comparison_reproduced.json')
    args=a.parse_args()
    rng=random.Random(2601)
    samples=[('empty',b''),('random_256KiB',rng.randbytes(256*1024)),('repetitive',b'abracadabra\n'*10000)]
    for file in args.file:
        samples.append((file.name,file.read_bytes()))
    rows=[]
    for name,data in samples:
        group=[]
        for mode in (0,1):
            entry=check(name,data,mode);rows.append(entry);group.append(entry)
        print(name,'control',group[0]['score_bytes'],'extra contexts',group[1]['score_bytes'],'difference',group[1]['score_bytes']-group[0]['score_bytes'],flush=True)
    args.out.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    print('Checked',len(rows),'round trips. No Hutter Prize result claimed.')
if __name__=='__main__':main()
