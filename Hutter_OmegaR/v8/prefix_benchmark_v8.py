#!/usr/bin/env python3
"""OMR v0.8: independent lossless prefix benchmark.

Authenticates the exact 100MB enwik8 before sampling it. Offline --self-test
is intentionally labeled NONOFFICIAL and cannot be reported as Wikipedia.
This benchmark NEVER claims a Hutter Prize score or eligibility.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ENWIK8_SIZE = 100_000_000
ENWIK8_MD5 = 'a1fa5ffddb56f4953e226637dabbb36a'
ENWIK8_SHA1 = '57b8363b814821dc9d47aa4d41f58733519076b2'
DEFAULT_COMP = Path(__file__).resolve().parents[1] / 'v6' / 'comp9'

def hashes(path: Path):
    md5=hashlib.md5(); sha1=hashlib.sha1(); sha256=hashlib.sha256(); size=0
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b''):
            size += len(chunk)
            md5.update(chunk);sha1.update(chunk);sha256.update(chunk)
    return dict(bytes=size, md5=md5.hexdigest(),sha1=sha1.hexdigest(),sha256=sha256.hexdigest())

def run_measured(argv:list[str], cwd:Path, timeout:int, cpu:int):
    def affinity(): os.sched_setaffinity(0,{cpu})
    start=time.monotonic()
    r=subprocess.run(['/usr/bin/time','-f','__OMRV8__%e %M %U %S',*argv],cwd=cwd,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,preexec_fn=affinity)
    stderr=r.stderr.decode('utf8',errors='replace')
    if r.returncode: raise RuntimeError(f'{argv} exited {r.returncode}: {stderr[-900:]}')
    lines=[l.split('__OMRV8__',1)[1].split() for l in stderr.splitlines() if l.startswith('__OMRV8__')]
    if len(lines)!=1:raise RuntimeError('Ambiguous /usr/bin/time output')
    wall,mem,user,system=map(float,lines[0])
    return dict(wall_seconds=round(time.monotonic()-start,4),time_wall_seconds=wall,
        max_rss_kib=int(mem),cpu_user_seconds=user,cpu_sys_seconds=system,cpu_affinity=cpu,
        stderr_tail=stderr[-500:])

def benchmark(src:Path,comp:Path,n:int,timeout:int,offset:int=0):
    cpu=min(os.sched_getaffinity(0))
    with tempfile.TemporaryDirectory(prefix='hutter_v8_') as tmp:
        root=Path(tmp); enc=root/'compress';dec=root/'decompress'; enc.mkdir();dec.mkdir()
        source_hash=hashlib.sha256()
        with src.open('rb') as f, (enc/'enwik9').open('wb') as o:
            f.seek(offset)
            remaining=n
            while remaining:
                block=f.read(min(4*1024*1024,remaining))
                if not block:raise RuntimeError('Source truncated during benchmark')
                o.write(block);source_hash.update(block);remaining-=len(block)
        shutil.copy2(comp,enc/'comp9');(enc/'comp9').chmod(0o755)
        encode=run_measured(['./comp9'],enc,timeout,cpu)
        archive=enc/'archive9'
        if not archive.is_file():raise RuntimeError('Missing archive9')
        comp_size=(enc/'comp9').stat().st_size;archive_size=archive.stat().st_size
        shutil.copy2(archive,dec/'archive9');(dec/'archive9').chmod(0o755)
        decode=run_measured(['./archive9'],dec,timeout,cpu)
        restored=dec/'data9'
        if not restored.is_file() or restored.stat().st_size!=n or hashes(restored)['sha256']!=source_hash.hexdigest():
            raise RuntimeError('Roundtrip SHA256 or length mismatch')
        zstd=None
        if shutil.which('zstd'):
            zr=subprocess.run(['zstd','-19','-T1','-q','-c',str(enc/'enwik9')],
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
            if zr.returncode==0: zstd=len(zr.stdout)
        return dict(input_bytes=n,input_offset_bytes=offset,input_sha256=source_hash.hexdigest(),
           compressor_bytes=comp_size, archive_bytes=archive_size,
           local_sum_comp_plus_archive=comp_size+archive_size,
           payload_estimated_bytes=archive_size-comp_size-32,
           zstd19_payload_bytes=zstd,
           baseline_zstd_is_not_self_extracting=True,
           lossless_roundtrip_verified=True,compress=encode,decompress=decode)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--enwik8',type=Path,help='Exact uncompressed canonical 100MB enwik8, authenticated using official hashes')
    g.add_argument('--self-test',type=Path,help='Offline NONOFFICIAL data to exercise pipeline; never claim official status')
    p.add_argument('--prefix-mib',type=int,default=8)
    p.add_argument('--offset-mib',type=int,default=0,help='Start of independent slice; model resets here')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--comp',type=Path,default=DEFAULT_COMP)
    p.add_argument('--max-phase-seconds',type=int,default=480)
    args=p.parse_args()
    if args.prefix_mib<1 or args.prefix_mib>64: p.error('--prefix-mib must be within 1..64')
    if args.offset_mib<0 or args.offset_mib>96:p.error('--offset-mib must be within 0..96')
    if os.name!='posix' or not hasattr(os,'sched_getaffinity'):p.error('Linux with CPU affinity required')
    if not Path('/usr/bin/time').is_file():p.error('Missing /usr/bin/time')
    src=(args.enwik8 or args.self_test).resolve()
    if not src.is_file():p.error(f'Source missing: {src}')
    comp=args.comp.resolve()
    if not comp.is_file():p.error(f'Compressor missing: {comp}')
    hs=hashes(src)
    official=args.enwik8 is not None
    if official:
        if hs['bytes']!=ENWIK8_SIZE or hs['md5']!=ENWIK8_MD5 or hs['sha1']!=ENWIK8_SHA1:
            raise SystemExit('BLOCKED: enwik8 size/MD5/SHA1 differs from official Matt Mahoney reference')
    offset=args.offset_mib*1024*1024
    n=min(args.prefix_mib*1024*1024,hs['bytes']-offset)
    if n<=0:raise SystemExit('BLOCKED: empty source')
    result=benchmark(src,comp,n,args.max_phase_seconds,offset)
    report=dict(version='0.8',test_type='AUTHENTIC_ENWIK8_PREFIX' if official else 'NONOFFICIAL_LOCAL_SMOKE',
        enwik8_whole_file_verified=official,source_file_hashes=hs,
        source_name=src.name,release_comp_sha256=hashes(comp)['sha256'],
        officially_judged=False,enwik9_used=False,
        hutter_prize_score=None,hutter_prize_submission_ready=False,measurement=result)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
