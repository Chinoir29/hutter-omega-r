#!/usr/bin/env python3
"""Two-mode A/B on three *losslessly escaped* unseen Wiki excerpts.

This invokes a patched raw laboratory path, NOT the submitted archive -e path.
Both configurations use the same fixed source/weights/compiler and same samples.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UPSTREAM='35d1957a5074db802fc134126afc77b76d931761'
THRESHOLDS=(990,999)
OFFSETS=(256,384,640)


def call(argv, cwd=None, logfile=None, timeout=1500) -> str:
    if logfile is not None:
        logfile.parent.mkdir(parents=True,exist_ok=True)
        with logfile.open('wb') as out:
            p=subprocess.run(argv,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
        if p.returncode:
            raise RuntimeError(f'Command exited {p.returncode}: {argv!r}, log tail={logfile.read_text(errors="replace")[-900:]}')
        return ''
    r=subprocess.run(argv,cwd=cwd,check=True,capture_output=True,text=True,timeout=timeout)
    return r.stdout.strip()


def sweep(repo:Path,samples:Path,manifest_path:Path,reports:Path,timeout:int) -> dict:
    repo,samples,manifest_path,reports=(p.resolve() for p in (repo,samples,manifest_path,reports))
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if (manifest.get('upstream_commit')!=UPSTREAM
            or manifest.get('lossy_projection') is not False
            or manifest.get('contest_coding_path') is not False
            or manifest.get('hutter_score') is not None
            or manifest.get('offsets_mib')!=list(OFFSETS)):
        raise RuntimeError('Unpinned/incorrect manifest')
    for entry in manifest['samples']:
        source=samples/entry['file']
        if (entry['offset_mib'] not in OFFSETS or not source.is_file()
                or hashlib.sha256(source.read_bytes()).hexdigest()!=entry['encoded_sha256']):
            raise RuntimeError('Sample mismatch')
    if call(['git','rev-parse','HEAD'],cwd=repo)!=UPSTREAM:
        raise RuntimeError('Unsafe upstream checkout')
    if not (repo/'LICENSE').is_file():raise RuntimeError('Upstream GPL license missing')
    reports.mkdir(parents=True,exist_ok=True)
    for threshold in THRESHOLDS:
        d=reports/f'q{threshold}';d.mkdir(parents=True,exist_ok=True)
        print('BEGIN q=',threshold,flush=True)
        try:
            call(['git','reset','--hard',UPSTREAM],cwd=repo,logfile=d/'gitreset.log',timeout=60)
            call(['git','clean','-fdx'],cwd=repo,logfile=d/'gitclean.log',timeout=60)
            call([sys.executable,str(ROOT/'Hutter_OmegaR/v16/patch_upper_gate.py'),
                  '--checkout',str(repo),'--qpe3',str(threshold),
                  '--report',str(d/'threshold_patch.json')],logfile=d/'threshold_stdout.log',timeout=60)
            call([sys.executable,str(ROOT/'Hutter_OmegaR/v14/enable_raw_lab.py'),
                  '--checkout',str(repo),'--report',str(d/'lab_patch.json')],logfile=d/'lab_patch_stdout.log',timeout=60)
            call(['/usr/bin/time','-f','build_wall_s=%e build_rss_kib=%M',
                  '-o',str(d/'build_resources.txt'),'make','CC=clang++-18',
                  'CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000','prof_use','-j2'],
                 cwd=repo,logfile=d/'build.log',timeout=1200)
            exe=repo/'cmix'
            if not exe.is_file() or not exe.stat().st_size:
                raise RuntimeError('No laboratory binary compiled')
            for off in OFFSETS:
                folder=d/f'h{off}'
                folder.mkdir(parents=True,exist_ok=True)
                call([sys.executable,str(ROOT/'Hutter_OmegaR/v17/run_reversible_lab.py'),
                    '--sample',str(samples/f'escaped_{off}MiB.dat'),
                    '--manifest',str(manifest_path), '--offset-mib',str(off),
                    '--binary',str(exe),
                    '--weights',str(repo/'weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5'),
                    '--vocab-header',str(repo/'src/vocab_frozen.h'),
                    '--out',str(folder),'--timeout',str(timeout)],
                    logfile=folder/'runner_stdout.log',timeout=2*timeout+90)
                measure=json.loads((folder/'result.json').read_text())
                print('q',threshold,'offset',off,'bytes',measure['lab_coder_bytes'],
                      'raw_reproduced',measure['roundtrip_raw_excerpt_sha256'],flush=True)
        except Exception as e:
            (d/'failure.json').write_text(json.dumps({'threshold':threshold,'error':str(e)[:1600],
                  'hutter_score':None},indent=2)+'\n')
            raise
    call([sys.executable,str(ROOT/'Hutter_OmegaR/v17/summarize_reversible.py'),
          '--manifest',str(manifest_path),'--reports',str(reports)],
          logfile=reports/'summary_stdout.log',timeout=60)
    return json.loads((reports/'comparison.json').read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('upstream','samples-dir','manifest','reports'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--phase-timeout',type=int,default=600)
    args=p.parse_args()
    result=sweep(args.upstream,args.samples_dir,args.manifest,args.reports,args.phase_timeout)
    print(json.dumps(result['aggregates'],indent=2),flush=True)

if __name__=='__main__':main()
