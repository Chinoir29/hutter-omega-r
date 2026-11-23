#!/usr/bin/env python3
"""OMÉGA-R v0.35: two matched full-model SEMCACHE lab configurations.
Prospectively fixed 5 windows; 10 double roundtrips. No contest score.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from fresh_samples import OFFSETS_MIB

ROOT=Path(__file__).resolve().parents[2]
UPSTREAM="35d1957a5074db802fc134126afc77b76d931761"
SP=(950,980)
Q=999

def run(argv, cwd=None, log=None, timeout=1400):
    if log is None:
        return subprocess.run(argv,cwd=cwd,capture_output=True,text=True,
                              timeout=timeout,check=True).stdout.strip()
    log.parent.mkdir(parents=True,exist_ok=True)
    with log.open("wb") as f:
        proc=subprocess.run(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    if proc.returncode:
        raise RuntimeError(f"Command exit {proc.returncode}: {argv!r}\n"+
                           log.read_text(errors="replace")[-1300:])
    return ""

def sweep(checkout: Path, samples: Path, manifest_path: Path, reports: Path,
          phase_timeout: int):
    checkout,samples,manifest_path,reports=(
        v.resolve() for v in (checkout,samples,manifest_path,reports))
    manifest=json.loads(manifest_path.read_text())
    if (manifest.get("upstream_commit")!=UPSTREAM or
        manifest.get("offsets_mib")!=list(OFFSETS_MIB) or
        manifest.get("hutter_prize_score") is not None or
        manifest.get("lossy_projection") is not False or
        manifest.get("contest_coding_path") is not False):
        raise ValueError("Unpinned or invalid v0.35 manifest")
    if len(manifest["samples"])!=5:
        raise ValueError("Unexpected window count")
    for rec in manifest["samples"]:
        p=samples/rec["file"]
        if (rec["offset_mib"] not in OFFSETS_MIB or not p.is_file()
            or hashlib.sha256(p.read_bytes()).hexdigest()!=rec["encoded_sha256"]
            or rec["raw_bytes"]!=65536 or rec["lossless_codec_verified"] is not True):
            raise ValueError("Corrupt transformed sample")
    if run(["git","rev-parse","HEAD"],cwd=checkout)!=UPSTREAM:
        raise ValueError("Unpinned upstream")
    if not (checkout/"LICENSE").is_file():raise ValueError("GPL source license missing")
    reports.mkdir(parents=True,exist_ok=True)
    measurements=[]
    for sp in SP:
        target=reports/("sp"+str(sp))
        target.mkdir(exist_ok=True)
        print("BEGIN_SP",sp,flush=True)
        try:
            run(["git","reset","--hard",UPSTREAM],cwd=checkout,
                log=target/"reset.log",timeout=60)
            run(["git","clean","-fdx"],cwd=checkout,
                log=target/"clean.log",timeout=60)
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v35/patch_storage.py"),
                 "--checkout",str(checkout),"--sp-e3",str(sp),
                 "--report",str(target/"patch.json")],
                log=target/"patch.log",timeout=60)
            p=json.loads((target/"patch.json").read_text())
            if p["query_threshold_qpe3"]!=Q or p["store_threshold_spe3"]!=sp:
                raise ValueError("Patch parameter mismatch")
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v14/enable_raw_lab.py"),
                 "--checkout",str(checkout),"--report",str(target/"raw_lab_patch.json")],
                 log=target/"raw_lab_patch.log",timeout=60)
            run(["/usr/bin/time","-f","build_wall_s=%e build_max_rss_kib=%M",
                 "-o",str(target/"build_resources.txt"),
                 "make","CC=clang++-18",
                 "CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000",
                 "prof_use","-j2"],cwd=checkout,log=target/"build.log",timeout=1200)
            program=checkout/"cmix"
            if not program.is_file() or program.stat().st_size<100000:
                raise ValueError("No compiled full model lab program")
            for off in OFFSETS_MIB:
                folder=target/("h"+str(off))
                folder.mkdir(exist_ok=True)
                run([sys.executable,str(ROOT/"Hutter_OmegaR/v17/run_reversible_lab.py"),
                     "--sample",str(samples/f"escaped_{off}MiB.dat"),
                     "--manifest",str(manifest_path),"--offset-mib",str(off),
                     "--binary",str(program),
                     "--weights",str(checkout/"weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5"),
                     "--vocab-header",str(checkout/"src/vocab_frozen.h"),
                     "--out",str(folder),"--timeout",str(phase_timeout)],
                    log=folder/"runner_stdout.log",timeout=2*phase_timeout+90)
                r=json.loads((folder/"result.json").read_text())
                if (r["status"]!="two_stage_verified" or
                    r["offset_mib"]!=off or r["hutter_score"] is not None or
                    r["full_enwik9"] is not False or
                    r["roundtrip_escaped_sha256"] is not True or
                    r["roundtrip_raw_excerpt_sha256"] is not True):
                    raise ValueError("Incomplete double roundtrip")
                rec=next(x for x in manifest["samples"] if x["offset_mib"]==off)
                if (r["original_raw_sha256"]!=rec["raw_sha256"] or
                    r["escaped_sha256"]!=rec["encoded_sha256"] or
                    r["original_raw_bytes"]!=65536):
                    raise ValueError("Mismatched source")
                measurements.append({
                    "sp_e3":sp,"q_e3":Q,"offset_mib":off,
                    "raw_sha256":r["original_raw_sha256"],
                    "escaped_sha256":r["escaped_sha256"],
                    "lab_coder_bytes":r["lab_coder_bytes"],
                    "unpacked_lab_binary_bytes":r["unpacked_program_bytes"],
                    "compression_wall_s":r["compression"]["wall_s"],
                    "decompression_wall_s":r["decompression"]["wall_s"],
                    "compression_max_rss_kib":r["compression"]["max_rss_kib"],
                    "decompression_max_rss_kib":r["decompression"]["max_rss_kib"],
                    "double_roundtrip_verified":True
                })
                print("MEASURE",sp,off,r["lab_coder_bytes"],flush=True)
        except Exception as exc:
            (target/"failure.json").write_text(json.dumps({
                "status":"failed","message":str(exc)[:1600],
                "hutter_prize_score":None},indent=2)+"\n")
            raise

    pairs=[]
    for off in OFFSETS_MIB:
        a=next(x for x in measurements if x["sp_e3"]==950 and x["offset_mib"]==off)
        b=next(x for x in measurements if x["sp_e3"]==980 and x["offset_mib"]==off)
        if a["raw_sha256"]!=b["raw_sha256"] or a["escaped_sha256"]!=b["escaped_sha256"]:
            raise ValueError("Not matched samples")
        pairs.append({"offset_mib":off,"control_sp950_bytes":a["lab_coder_bytes"],
                      "candidate_sp980_bytes":b["lab_coder_bytes"],
                      "candidate_minus_control":b["lab_coder_bytes"]-a["lab_coder_bytes"]})
    delta=sum(x["candidate_minus_control"] for x in pairs)
    wins=sum(x["candidate_minus_control"]<0 for x in pairs)
    losses=sum(x["candidate_minus_control"]>0 for x in pairs)
    result={
        "project":"OMEGA-R v0.35 prospective SEMCACHE storage retention",
        "status":"all_ten_double_roundtrips_verified",
        "input_is_authentic_enwik9":True,
        "enwik9_sha256":manifest["source_sha256"],
        "upstream_commit":UPSTREAM,
        "query_threshold_qpe3_fixed":Q,
        "baseline_storage_threshold_spe3":950,
        "candidate_storage_threshold_spe3":980,
        "held_out_windows_mib":list(OFFSETS_MIB),
        "raw_bytes_per_sample":65536,
        "raw_wikipedia_roundtrip_verified":True,
        "research_only":True,
        "contest_path":False,
        "self_extracting_archive":False,
        "hutter_prize_score":None,
        "competition_submission_sent":False,
        "measurements":measurements,
        "paired_results":pairs,
        "delta_candidate_minus_control_lab_bytes":delta,
        "wins_candidate":wins,"losses_candidate":losses,
        "ties":5-wins-losses,
        "success_criterion_predeclared":(
            "all 10 double roundtrips; total delta negative; "
            "candidate wins at least 4 of 5")
    }
    result["provisionally_supported"]=delta<0 and wins>=4
    assert len(measurements)==10 and len(pairs)==5
    assert all(x["double_roundtrip_verified"] for x in measurements)
    dest=reports/"V35_SEMCACHE_STORAGE_AB.json"
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("V035_VERDICT",json.dumps({"delta":delta,"wins":wins,
          "losses":losses,"provisional":result["provisionally_supported"],
          "hutter_score":None}),flush=True)
    return result

def main():
    ap=argparse.ArgumentParser()
    for name in ("upstream","samples-dir","manifest","reports"):
        ap.add_argument("--"+name,required=True,type=Path)
    ap.add_argument("--phase-timeout",default=600,type=int)
    args=ap.parse_args()
    sweep(args.upstream,args.samples_dir,args.manifest,args.reports,args.phase_timeout)

if __name__=="__main__":main()
