#!/usr/bin/env python3
"""OMÉGA-R v0.34 — prospective paired SEMCACHE 990 vs 999 on novel
lossless original enwik9 excerpts; NOT an official Hutter score.
Original GPL-3.0 model fetched/pinned separately, not redistributed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from fresh_samples import OFFSETS_MIB

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = "35d1957a5074db802fc134126afc77b76d931761"
THRESHOLDS = (990,999)

def run(argv, cwd=None, log=None, timeout=1200):
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("wb") as dest:
            p = subprocess.run(argv, cwd=cwd, stdout=dest, stderr=subprocess.STDOUT, timeout=timeout)
        if p.returncode:
            raise RuntimeError("Command exit " + str(p.returncode) + ": " +
                               str(argv) + ", tail " +
                               log.read_text(errors="replace")[-1200:])
        return ""
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                            timeout=timeout, check=True)
    return result.stdout.strip()

def sweep(upstream, samples, manifest_file, reports, phase_timeout):
    upstream, samples, manifest_file, reports = (
        p.resolve() for p in (upstream, samples, manifest_file, reports)
    )
    manifest=json.loads(manifest_file.read_text(encoding="utf8"))
    if (manifest.get("upstream_commit") != UPSTREAM or
        manifest.get("lossy_projection") is not False or
        manifest.get("contest_coding_path") is not False or
        manifest.get("hutter_score") is not None or
        manifest.get("offsets_mib") != list(OFFSETS_MIB)):
        raise ValueError("Wrong sample manifest or data provenance")
    if [x["offset_mib"] for x in manifest["samples"]] != list(OFFSETS_MIB):
        raise ValueError("Mismatch in held-out ordering")
    for record in manifest["samples"]:
        f = samples/record["file"]
        if (not f.is_file() or f.stat().st_size!=record["encoded_bytes"]
            or hashlib.sha256(f.read_bytes()).hexdigest()!=record["encoded_sha256"]
            or record["lossless_codec_verified"] is not True
            or record["raw_bytes"]!=65536):
            raise ValueError("Invalid sample " + str(f))
    if run(["git","rev-parse","HEAD"],cwd=upstream)!=UPSTREAM:
        raise ValueError("Unpinned upstream code")
    if not (upstream/"LICENSE").is_file():
        raise ValueError("GPL license missing")
    reports.mkdir(parents=True,exist_ok=True)
    rows=[]
    for q in THRESHOLDS:
        dest=reports/("q"+str(q))
        dest.mkdir(exist_ok=True)
        print("BEGIN q",q,flush=True)
        try:
            run(["git","reset","--hard",UPSTREAM],cwd=upstream,log=dest/"reset.log",timeout=60)
            run(["git","clean","-fdx"],cwd=upstream,log=dest/"clean.log",timeout=60)
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v16/patch_upper_gate.py"),
                 "--checkout",str(upstream),"--qpe3",str(q),
                 "--report",str(dest/"patch_semcache.json")],log=dest/"patch.log",timeout=60)
            run([sys.executable,str(ROOT/"Hutter_OmegaR/v14/enable_raw_lab.py"),
                 "--checkout",str(upstream),"--report",str(dest/"patch_lab.json")],
                log=dest/"patch_raw.log",timeout=60)
            run(["/usr/bin/time","-f","build_s=%e max_rss_kib=%M",
                 "-o",str(dest/"build_resources.txt"),
                 "make","CC=clang++-18",
                 "CFLAGS_DEFINES=-DSEED=923 -DUPDATE_LIMIT=3000",
                 "prof_use","-j2"],cwd=upstream,log=dest/"build.log",timeout=1200)
            binary=upstream/"cmix"
            if not binary.is_file() or binary.stat().st_size<100000:
                raise ValueError("Missing compiled full-model lab binary")
            for off in OFFSETS_MIB:
                folder=dest/("h"+str(off))
                folder.mkdir(exist_ok=True)
                run([sys.executable,str(ROOT/"Hutter_OmegaR/v17/run_reversible_lab.py"),
                     "--sample",str(samples/f"escaped_{off}MiB.dat"),
                     "--manifest",str(manifest_file),
                     "--offset-mib",str(off),
                     "--binary",str(binary),
                     "--weights",str(upstream/"weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5"),
                     "--vocab-header",str(upstream/"src/vocab_frozen.h"),
                     "--out",str(folder),
                     "--timeout",str(phase_timeout)],
                    log=folder/"stdout.log",timeout=2*phase_timeout+100)
                data=json.loads((folder/"result.json").read_text())
                if (data.get("offset_mib")!=off
                    or data.get("roundtrip_escaped_sha256") is not True
                    or data.get("roundtrip_raw_excerpt_sha256") is not True
                    or data.get("hutter_score") is not None
                    or data.get("full_enwik9") is not False):
                    raise ValueError("Unverified lab result")
                rows.append({
                    "qpe3":q, "offset_mib":off,
                    "raw_sha256":data["original_raw_sha256"],
                    "coded_stream_bytes":data["lab_coder_bytes"],
                    "binary_bytes_unpacked_lab":data["unpacked_program_bytes"],
                    "max_compression_rss_kib":data["compression"]["max_rss_kib"],
                    "max_decompression_rss_kib":data["decompression"]["max_rss_kib"],
                    "double_roundtrip_verified":True
                })
                print("LAB_ROW",q,off,data["lab_coder_bytes"],flush=True)
        except Exception as e:
            (dest/"failure.json").write_text(json.dumps({
                "status":"failed","reason":str(e)[:1400],"official_hutter_score":None
            },indent=2)+"\n")
            raise

    pairs=[]
    for off in OFFSETS_MIB:
        a=next(x for x in rows if x["qpe3"]==990 and x["offset_mib"]==off)
        b=next(x for x in rows if x["qpe3"]==999 and x["offset_mib"]==off)
        if a["raw_sha256"]!=b["raw_sha256"]:
            raise ValueError("Paired source differs")
        pairs.append({"offset_mib":off, "q990":a["coded_stream_bytes"],
                      "q999":b["coded_stream_bytes"],
                      "q999_minus_q990":b["coded_stream_bytes"]-a["coded_stream_bytes"]})
    aggregate = sum(p["q999_minus_q990"] for p in pairs)
    verdict = {
        "project":"OMÉGA-R v0.34 prospective SEMCACHE replication",
        "status":"all_ten_double_roundtrips_verified",
        "authentic_enwik9_source_sha256":manifest["source_sha256"],
        "source_commit":UPSTREAM,
        "GPL_3_0_upstream_not_redistributed":True,
        "held_out_windows_mib":list(OFFSETS_MIB),
        "raw_bytes_per_window":65536,
        "laboratory_only":True,
        "reversible_raw_source":True,
        "contest_coding_path":False,
        "self_extracting_archive":False,
        "hutter_score":None,
        "competition_submission_sent":False,
        "rows":rows,
        "pairs":pairs,
        "sum_q990_lab_bytes":sum(p["q990"] for p in pairs),
        "sum_q999_lab_bytes":sum(p["q999"] for p in pairs),
        "delta_q999_minus_q990":aggregate,
        "wins_q999":sum(p["q999_minus_q990"]<0 for p in pairs),
        "losses_q999":sum(p["q999_minus_q990"]>0 for p in pairs),
        "ties":sum(p["q999_minus_q990"]==0 for p in pairs),
        "provisional_replication_supported":
            aggregate<0 and sum(p["q999_minus_q990"]<0 for p in pairs)>=4
    }
    if len(rows)!=10 or not all(r["double_roundtrip_verified"] for r in rows):
        raise ValueError("Incomplete verification")
    outfile=reports/"V34_FRESH_SEMCACHE_RESULT.json"
    outfile.write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n")
    print("V34_RESULT",json.dumps({
        "delta":aggregate,"wins":verdict["wins_q999"],
        "losses":verdict["losses_q999"],
        "provisional":verdict["provisional_replication_supported"],
        "score":None
    }),flush=True)
    return verdict

def main():
    p=argparse.ArgumentParser()
    for key in ("upstream","samples-dir","manifest","reports"):
        p.add_argument("--"+key,required=True,type=Path)
    p.add_argument("--phase-timeout",type=int,default=600)
    a=p.parse_args()
    sweep(a.upstream,a.samples_dir,a.manifest,a.reports,a.phase_timeout)

if __name__=="__main__":main()
