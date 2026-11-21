#!/usr/bin/env python3
"""Sequential A/B of SEMCACHE 990/995/999 on three projected Wiki holdouts.

This is NOT an official Hutter score and does not use the release -e path.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UPSTREAM='35d1957a5074db802fc134126afc77b76d931761'
THRESHOLDS=(990,995,999)
OFFSETS_MIB=(32,96,192)


def run(args:list[str], *, cwd:Path|None=None, log:Path|None=None, timeout:int=1500)->str:
    if log:
        log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('wb') as f:
            p=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
        if p.returncode:
            tail=log.read_text(encoding='utf-8',errors='replace')[-1200:]
            raise RuntimeError(f'Exit {p.returncode}: {args!r}; tail={tail}')
        return ''
    p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout,check=True)
    return p.stdout.strip()


def sweep(repo:Path,samples:Path,manifest_file:Path,reports:Path,timeout:int):
    repo,samples,manifest_file,reports=[p.resolve() for p in (repo,samples,manifest_file,reports)]
    manifest=json.loads(manifest_file.read_text())
    if not (manifest.get('lossy_projection') is True
            and manifest.get('competitive_hutter_score') is None
            and [r['offset_mib'] for r in manifest['holdouts']]==list(OFFSETS_MIB)):
        raise RuntimeError('Unexpected or invalid holdout provenance')
    for rec in manifest['holdouts']:
        file=samples/rec['filename']
        if not file.is_file() or file.stat().st_size!=65536:
            raise RuntimeError('Missing 64 KiB sample '+str(file))
        if hashlib.sha256(file.read_bytes()).hexdigest()!=rec['sample_sha256']:
            raise RuntimeError('Holdout hash mismatch')
    if run(['git','rev-parse','HEAD'],cwd=repo)!=UPSTREAM:
        raise RuntimeError('Unexpected upstream commit')
    if not (repo/'LICENSE').is_file():raise RuntimeError('Missing upstream GPL license')
    for q in THRESHOLDS:
        print(f'BEGIN q={q}',flush=True)
        dest=reports/f'q{q}'
        dest.mkdir(parents=True,exist_ok=True)
        started=time.monotonic()
        try:
            run(['git','reset','--hard',UPSTREAM],cwd=repo,log=dest/'reset.log',timeout=60)
            run(['git','clean','-fdx'],cwd=repo,log=dest/'clean.log',timeout=60)
            run([sys.executable,str(ROOT/'Hutter_OmegaR/v16/patch_upper_gate.py'),
                 '--checkout',str(repo),'--qpe3',str(q),
                 '--report',str(dest/'semcache_patch.json')],
                log=dest/'patch.log',timeout=60)
            run([sys.executable,str(ROOT/'Hutter_OmegaR/v14/enable_raw_lab.py'),
                 '--checkout',str(repo),'--report',str(dest/'lab_patch.json')],
                log=dest/'patch_lab.log',timeout=60)
            run(['/usr/bin/time','-f','build_wall_s=%e build_rss_kib=%M',
                 '-o',str(dest/'build_resources.txt'),
                 'make','CC=clang++-18','CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000',
                 'prof_use','-j2'],cwd=repo,log=dest/'build.log',timeout=1200)
            binary=repo/'cmix'
            if not binary.is_file() or binary.stat().st_size==0:
                raise RuntimeError('Missing full-model laboratory executable')
            for off in OFFSETS_MIB:
                sample=samples/f'holdout_{off}MiB.dat'
                local=dest/f'h{off}'
                local.mkdir(parents=True,exist_ok=True)
                run([sys.executable,str(ROOT/'Hutter_OmegaR/v14/run_raw_lab.py'),
                     '--sample',str(sample),'--binary',str(binary),
                     '--weights',str(repo/'weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5'),
                     '--reports',str(local),'--timeout',str(timeout)],
                    log=local/'runner_stdout.log',timeout=2*timeout+120)
                row=json.loads((local/'coder_report.json').read_text())
                print(f' q={q} offset={off}MiB coder={row["lab_coder_bytes"]} lossless={row["lossless_roundtrip_verified"]}',flush=True)
        except Exception as e:
            (dest/'failure.json').write_text(json.dumps({
                'status':'error','threshold_qpe3':q,'message':str(e)[:1500],
                'official_hutter_score':None},indent=2)+'\n')
            raise
        print(f'END q={q} total_wall_s={time.monotonic()-started:.1f}',flush=True)
    run([sys.executable,str(ROOT/'Hutter_OmegaR/v16/summarize_holdouts.py'),
        '--manifest',str(manifest_file),'--reports',str(reports)],
        log=reports/'summary_stdout.log',timeout=60)
    result=json.loads((reports/'comparison.json').read_text())
    print('RESULT:',json.dumps(result['aggregates'],ensure_ascii=False),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream',type=Path,required=True)
    parser.add_argument('--samples-dir',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--reports',type=Path,required=True)
    parser.add_argument('--phase-timeout',type=int,default=600)
    args=parser.parse_args()
    sweep(args.upstream,args.samples_dir,args.manifest,args.reports,args.phase_timeout)

if __name__=='__main__':main()
