#!/usr/bin/env python3
"""OMÉGA-R v0.28: paired genuine native comp9 → archive9 experiment on one core.

Uses the original experimental v0.25 native preprocessed-prefix route as the
control, and the fixed-point Bayesian coder+decoder as the candidate. Both run
in identical fresh workdirs against the same authenticated 1GB corpus.

Never publishes weights, any portion of Wikipedia, compressed payloads or
derived GPL-3.0-only executables. Reports are experimental, not Hutter S.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v26"))
from one_core_resource_meter import run as monitor

CORPUS_SHA = "159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc"
PREFIX_SHA = "1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf"
ORIGINAL_CODER_BYTES = 158153
ORIGINAL_ARCHIVE_BYTES = 4079636
PRECODER_STREAM_BYTES = 501062281
PREFIX_BYTES = 524288
WEIGHTS_BYTES = 3744629
FREE_CODED_BITS = 4071047


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def native_archive_layout(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size <= 1_000_000:
        raise ValueError("MISSING_OR_INVALID_EXPERIMENTAL_ARCHIVE")
    with path.open("rb") as f:
        if f.read(4) != b"\x7fELF":
            raise ValueError("NOT_AN_ELF")
        f.seek(-8, 2)
        coded, weights = struct.unpack("<ii", f.read(8))
    stub = path.stat().st_size - coded - weights - 8
    if coded < 100 or weights != WEIGHTS_BYTES or stub < 10000:
        raise ValueError("BAD_NATIVE_ARCHIVE_LAYOUT")
    return {"archive_bytes":path.stat().st_size, "archive_sha256":sha256(path),
            "decoder_stub_bytes":stub,"weights_bytes":weights,
            "arithmetic_payload_bytes":coded,"trailer_bytes":8}


def report_from_encoder(stderr: str) -> dict:
    marker="OMR28_BAYES_REPORT "
    lines=[line for line in stderr.splitlines() if marker in line]
    if len(lines)!=1:
        raise ValueError("MISSING_OR_MULTIPLE_BAYES_REPORTS")
    raw=lines[0].split(marker,1)[1]
    items=dict(re.findall(r"(\w+)=([-\d.]+)",raw))
    expected={"coded_bits","active_contexts","changed_probabilities",
              "baseline_ideal_bits","candidate_ideal_bits","ideal_gain_bits"}
    if set(items)!=expected:
        raise ValueError("BAD_BAYES_REPORT_FIELDS")
    out={k:(float(v) if "bits" in k and k not in ("coded_bits",) else int(v))
         for k,v in items.items()}
    out["coded_bits"]=int(items["coded_bits"])
    out["active_contexts"]=int(items["active_contexts"])
    out["changed_probabilities"]=int(items["changed_probabilities"])
    if out["coded_bits"]!=FREE_CODED_BITS or not 1<=out["active_contexts"]<=255:
        raise ValueError("BAD_CODED_BIT_COUNT_OR_CONTEXTS")
    # True real-number regret <= active-contexts; 1.0-bit rounding slack.
    if out["ideal_gain_bits"] < -out["active_contexts"]-1.0:
        raise ValueError("BAYES_REGRET_BOUND_VIOLATED")
    return out


def write_report(p: Path, rec: dict) -> None:
    p.write_text(json.dumps(rec, indent=2, ensure_ascii=False)+"\n")


def run_pair(root: Path, corpus: Path, results: Path) -> dict:
    if results.resolve().is_relative_to(root.resolve()):
        raise ValueError("REPORT_MUST_LIVE_OUTSIDE_WORK_ROOT")
    if root.exists():
        raise ValueError("NEW_EXPERIMENT_ROOT_REQUIRED")
    if not corpus.is_file() or corpus.stat().st_size != 1_000_000_000 or sha256(corpus)!=CORPUS_SHA:
        raise ValueError("CANONICAL_CORPUS_AUTHENTICATION_FAILED")
    rec={"status":"STARTED",
         "experiment":"paired authentic cmix arithmetic coder and isolated native prefix archive",
         "upstream_commit":"35d1957a5074db802fc134126afc77b76d931761",
         "input_corpus_sha256":CORPUS_SHA,
         "preprocessed_prefix_bytes":PREFIX_BYTES,
         "reference_prefix_sha256":PREFIX_SHA,
         "baseline_historical_archive_bytes":ORIGINAL_ARCHIVE_BYTES,
         "arithmetic_baseline_historical_bytes":ORIGINAL_CODER_BYTES,
         "real_full_enwik9_restored":False,
         "competition_score_S":None,
         "official_validation":False,
         "arms":{}}
    root.mkdir(parents=True)
    try:
        for arm in ("baseline","candidate"):
            binary=Path("/tmp/omr28-"+arm)/"comp9"
            if not binary.is_file() or not os.access(binary,os.X_OK):
                raise ValueError("MISSING_PRODUCTION_BINARY_"+arm)
            cwd=root/arm
            cwd.mkdir()
            (cwd/"enwik9").symlink_to(corpus.resolve())
            binary_meta={"comp9_bytes":binary.stat().st_size,"comp9_sha256":sha256(binary)}
            old_env=os.environ.get("OMR21_SHADOW_PREFIX_BYTES")
            os.environ["OMR21_SHADOW_PREFIX_BYTES"]=str(PREFIX_BYTES)
            try:
                monitor_result=monitor([str(binary)],cwd,
                    Path("/tmp/omr28-"+arm+"-encode-meter.json"),
                    timeout_s=2400,sample_s=0.3)
            finally:
                if old_env is None:os.environ.pop("OMR21_SHADOW_PREFIX_BYTES",None)
                else:os.environ["OMR21_SHADOW_PREFIX_BYTES"]=old_env
            binary_meta["encode_resources"]=monitor_result
            stderr_path=Path(monitor_result["error_log"])
            err=stderr_path.read_text(errors="replace")
            found=re.findall(r"OMR21_PREFIX_ACTUAL_CODED_STREAM_BYTES=(\d+)",err)
            if len(found)!=1 or int(found[0])!=PRECODER_STREAM_BYTES:
                raise ValueError("UNEXPECTED_REAL_PRECODER_LENGTH_"+arm)
            if monitor_result["status"]!="FINISHED" or monitor_result["exit_code"]!=0:
                raise ValueError("PRODUCTION_COMPRESSOR_FAILED_"+arm)
            if not (monitor_result["memory_below_project_limit_observed"]
                    and monitor_result["disk_below_project_limit_observed"]):
                raise ValueError("OBSERVED_RESOURCE_LIMIT_EXCEEDED_"+arm)
            archive=cwd/"archive9"
            binary_meta.update(native_archive_layout(archive))
            if arm=="candidate":
                binary_meta["bayes_online_bits"]=report_from_encoder(err)
            rec["arms"][arm]=binary_meta
            write_report(results,rec)
            # The decoder receives only archive9 in a brand-new directory.
            isolated=root/("independent-"+arm)
            isolated.mkdir()
            shutil.copyfile(archive,isolated/"archive9")
            (isolated/"archive9").chmod(0o755)
            if sorted(p.name for p in isolated.iterdir())!=["archive9"]:
                raise AssertionError("HIDDEN_DECODING_SIDE_FILES")
            saved=dict(os.environ)
            os.environ.clear()
            os.environ.update({"PATH":"/usr/bin:/bin","HOME":str(isolated),"LC_ALL":"C","TZ":"UTC"})
            try:
                decode_record=monitor(["./archive9"],isolated,
                    Path("/tmp/omr28-"+arm+"-decode-meter.json"),
                    timeout_s=1200,sample_s=0.3)
            finally:
                os.environ.clear()
                os.environ.update(saved)
            decoded=isolated/"omr24-decoded-prefix.bin"
            if decode_record["status"]!="FINISHED" or decode_record["exit_code"]!=0:
                raise ValueError("INDEPENDENT_DECODER_FAILED_"+arm)
            if not decoded.is_file() or decoded.stat().st_size != PREFIX_BYTES or sha256(decoded)!=PREFIX_SHA:
                raise ValueError("NON_IDENTITY_ON_GENUINE_PREPROCESSED_PREFIX_"+arm)
            binary_meta["isolated_decode_resources"]=decode_record
            binary_meta["decoded_prefix_sha256"]=sha256(decoded)
            binary_meta["decoded_bytes"]=decoded.stat().st_size
            binary_meta["initial_isolated_files"]=["archive9"]
            binary_meta["decode_argv"]=[]
            write_report(results,rec)
            # Erase protected temporary content, archive and extracted weights.
            shutil.rmtree(cwd)
            shutil.rmtree(isolated)
        b=rec["arms"]["baseline"]
        c=rec["arms"]["candidate"]
        rec["comparison"]={
            "arithmetic_payload_delta_candidate_minus_baseline":c["arithmetic_payload_bytes"]-b["arithmetic_payload_bytes"],
            "archive_delta_candidate_minus_baseline":c["archive_bytes"]-b["archive_bytes"],
            "comp9_delta_candidate_minus_baseline":c["comp9_bytes"]-b["comp9_bytes"],
            "combined_experimental_bytes_baseline":b["archive_bytes"]+b["comp9_bytes"],
            "combined_experimental_bytes_candidate":c["archive_bytes"]+c["comp9_bytes"],
            "combined_experimental_delta_candidate_minus_baseline":
                c["archive_bytes"]+c["comp9_bytes"]-b["archive_bytes"]-b["comp9_bytes"],
            "caveat":"524288 preprocessed bytes, not 1GB enwik9; no contest S",
        }
        rec["status"]="BOTH_REAL_NATIVE_PREFIX_ROUNDTRIPS_VERIFIED"
    except Exception as e:
        rec["status"]="FAILED_INTEGRATION_OR_RESOURCES"
        rec["error_type"]=type(e).__name__
        rec["error_message"]=str(e)
        raise
    finally:
        write_report(results,rec)
    return rec


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,required=True)
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    d=run_pair(a.root,a.corpus,a.report)
    print(json.dumps({"status":d["status"],
        "comparison":d.get("comparison"),
        "candidate_bayes_online_bits":d["arms"].get("candidate",{}).get("bayes_online_bits"),
        "official_hutter_score_S":None},indent=2))
