#!/usr/bin/env python3
"""Sequential, single-runner SEMCACHE gate A/B with an unchanged source checkout.

NEVER produces a valid enwik9 Hutter Prize archive. Research only.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = "35d1957a5074db802fc134126afc77b76d931761"
THRESHOLDS = (990, 980, 970)


def run(args, cwd=None, log=None, timeout=600):
    if log is None:
        result = subprocess.run(args, cwd=cwd, timeout=timeout, check=True,
                                capture_output=True, text=True)
        return result.stdout.strip()
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("wb") as f:
        result = subprocess.run(args, cwd=cwd, stdout=f, stderr=subprocess.STDOUT,
                                timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Exit={result.returncode}, command={args!r}, log={log}")
    return None


def sweep(repo: Path, sample: Path, reports: Path, timeout: int):
    repo, sample, reports = repo.resolve(), sample.resolve(), reports.resolve()
    reports.mkdir(parents=True, exist_ok=True)
    if not sample.is_file() or sample.stat().st_size != 65536:
        raise RuntimeError("Input is not the 65,536-byte laboratory sample")
    if run(["git", "rev-parse", "HEAD"], cwd=repo) != UPSTREAM:
        raise RuntimeError("Unsafe upstream checkout")
    for q in THRESHOLDS:
        folder = reports / f"q{q}"
        folder.mkdir(parents=True, exist_ok=True)
        print(f"BEGIN SEMCACHE threshold {q}",flush=True)
        start = time.monotonic()
        try:
            run(["git","reset","--hard",UPSTREAM], cwd=repo, log=folder/"reset.log")
            run(["git","clean","-fdx"], cwd=repo, log=folder/"clean.log")
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v13/semantic_cache_gate_patch.py"),
                 "--checkout",str(repo),"--qpe3",str(q),
                 "--report",str(folder/"semcache_patch.json")],
                 log=folder/"patch_threshold.log", timeout=60)
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v14/enable_raw_lab.py"),
                 "--checkout",str(repo),"--report",str(folder/"lab_patch.json")],
                 log=folder/"patch_lab.log",timeout=60)
            run(["/usr/bin/time","-f","wall_s=%e rss_kib=%M",
                 "-o",str(folder/"build_resources.txt"),
                 "make","CC=clang++-18",
                 "CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000",
                 "prof_use","-j2"],cwd=repo,log=folder/"build.log",timeout=1200)
            exe=repo/"cmix"
            if not exe.is_file() or exe.stat().st_size==0:
                raise RuntimeError("Build created no executable")
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v14/run_raw_lab.py"),
                 "--sample",str(sample),"--binary",str(exe),
                 "--weights",str(repo/"weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5"),
                 "--reports",str(folder),"--timeout",str(timeout)],
                 log=folder/"runner_stdout.log",timeout=timeout*2+180)
        except Exception as err:
            (folder/"failure.json").write_text(json.dumps({
                "status":"failed",
                "threshold_qpe3":q,
                "reason":str(err)[:800],
                "hutter_score":None
            },indent=2)+"\n")
            raise
        print(f"END SEMCACHE threshold {q}, elapsed {time.monotonic()-start:.1f}s",flush=True)
    run([sys.executable,str(ROOT/"Hutter_OmegaR/v15/summarize_lab.py"),
         "--reports",str(reports)],
        log=reports/"summary_stdout.log",timeout=30)
    return json.loads((reports/"comparison.json").read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--sample",type=Path,required=True)
    p.add_argument("--reports",type=Path,required=True)
    p.add_argument("--phase-timeout",type=int,default=900)
    a=p.parse_args()
    result=sweep(a.upstream,a.sample,a.reports,a.phase_timeout)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
