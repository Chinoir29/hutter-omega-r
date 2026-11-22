#!/usr/bin/env python3
"""OMÉGA-R v0.29: real one-core A/B of original floor stage vs pooled calibration.

True comp9 and archive9, independent zero-argument decode of authentic 524288
byte PREPROCESSED prefix, not 1GB Hutter Prize enwik9. All intermediate
Wikipedia bytes, model weights and GPL-derived binaries stay ephemeral.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v28"))
from run_real_bayesian_pair import (sha256,native_archive_layout,write_report,
    CORPUS_SHA,PREFIX_SHA,PREFIX_BYTES,PRECODER_STREAM_BYTES,ORIGINAL_ARCHIVE_BYTES)

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v26"))
from one_core_resource_meter import run as monitor


def measured_pair(root:Path,corpus:Path,report:Path)->dict:
    if root.exists():
        raise ValueError("ALREADY_EXISTING_WORKROOT_REJECTED")
    if report.resolve().is_relative_to(root.resolve()):
        raise ValueError("REPORT_INSIDE_WORKROOT")
    if corpus.stat().st_size!=1000000000 or sha256(corpus)!=CORPUS_SHA:
        raise ValueError("CANONICAL_ENWIK9_WRONG_SIZE_OR_SHA")
    record={
      "version":"OMÉGA-R v0.29",
      "status":"STARTED",
      "experiment":"strict native comp9/archive9 on preprocessed enwik9 first 524288 bytes; hierarchical floor-stage calibration",
      "upstream_commit":"35d1957a5074db802fc134126afc77b76d931761",
      "source_corpus_sha256":CORPUS_SHA,
      "target_reference_sha256":PREFIX_SHA,
      "original_precoder_full_stream_bytes":PRECODER_STREAM_BYTES,
      "decoded_target_bytes":PREFIX_BYTES,
      "historical_native_baseline_archive9_bytes":ORIGINAL_ARCHIVE_BYTES,
      "contest_S":None,"entire_enwik9_reconstructed":False,"official_validation":False,
      "arms":{}}
    root.mkdir(parents=True)
    try:
      for arm in ("baseline","candidate"):
        comp9=Path("/tmp/omr29-"+arm)/"comp9"
        if not comp9.is_file() or not os.access(comp9,os.X_OK):
            raise ValueError("MISSING_BUILT_COMP9_"+arm)
        build={"comp9_bytes":comp9.stat().st_size,"comp9_sha256":sha256(comp9)}
        work=root/arm
        work.mkdir()
        (work/"enwik9").symlink_to(corpus.resolve())
        old=os.environ.get("OMR21_SHADOW_PREFIX_BYTES")
        os.environ["OMR21_SHADOW_PREFIX_BYTES"]=str(PREFIX_BYTES)
        try:
            encode=monitor([str(comp9)],work,
                Path("/tmp/omr29-"+arm+"-encode.json"),
                timeout_s=2200,sample_s=.30)
        finally:
            if old is None: os.environ.pop("OMR21_SHADOW_PREFIX_BYTES",None)
            else:os.environ["OMR21_SHADOW_PREFIX_BYTES"]=old
        if encode["status"]!="FINISHED" or encode["exit_code"]!=0:
            raise RuntimeError("NATIVE_COMP9_FAILED_"+arm)
        stderr=Path(encode["error_log"]).read_text(errors="replace")
        if stderr.count("OMR21_PREFIX_ACTUAL_CODED_STREAM_BYTES=501062281")!=1:
            raise RuntimeError("COMPRESSOR_REAL_PREPROCESS_LENGTH_MISMATCH_"+arm)
        if not encode["memory_below_project_limit_observed"] or not encode["disk_below_project_limit_observed"]:
            raise RuntimeError("OBSERVED_RESOURCE_LIMIT_EXCEEDED_"+arm)
        build["compress"]=encode
        build.update(native_archive_layout(work/"archive9"))
        record["arms"][arm]=build
        write_report(report,record)
        independent=root/("decoded-"+arm)
        independent.mkdir()
        shutil.copyfile(work/"archive9",independent/"archive9")
        (independent/"archive9").chmod(0o755)
        if sorted(p.name for p in independent.iterdir())!=["archive9"]:
            raise AssertionError("DECODER_DIRECTORY_NOT_EMPTY_AT_START")
        # No special experiment environment in the independent decoder.
        env_saved=dict(os.environ)
        os.environ.clear()
        os.environ.update({"PATH":"/usr/bin:/bin","HOME":str(independent),"LC_ALL":"C","TZ":"UTC"})
        try:
            dec=monitor(["./archive9"],independent,
                 Path("/tmp/omr29-"+arm+"-decode.json"),
                 timeout_s=1300,sample_s=.30)
        finally:
            os.environ.clear();os.environ.update(env_saved)
        restored=independent/"omr24-decoded-prefix.bin"
        if dec["status"]!="FINISHED" or dec["exit_code"]!=0:
            raise RuntimeError("INDEPENDENT_DECODER_FAILED_"+arm)
        if not restored.is_file() or restored.stat().st_size!=PREFIX_BYTES or sha256(restored)!=PREFIX_SHA:
            raise RuntimeError("BITWISE_DECODE_SHA_FAILED_"+arm)
        build["decode"]=dec
        build["recovered_bytes"]=PREFIX_BYTES
        build["recovered_sha256"]=PREFIX_SHA
        build["isolation_initial_files"]=["archive9"]
        build["isolated_zero_arguments"]=True
        write_report(report,record)
        shutil.rmtree(work)
        shutil.rmtree(independent)
      b=record["arms"]["baseline"]
      c=record["arms"]["candidate"]
      if b["arithmetic_payload_bytes"]!=158153 or b["archive_bytes"]!=ORIGINAL_ARCHIVE_BYTES:
          raise RuntimeError("NATIVE_BASELINE_NOT_REPRODUCED")
      record["comparison"]={
        "arithmetic_delta_candidate_minus_baseline_bytes":c["arithmetic_payload_bytes"]-b["arithmetic_payload_bytes"],
        "archive_delta_candidate_minus_baseline_bytes":c["archive_bytes"]-b["archive_bytes"],
        "comp9_delta_candidate_minus_baseline_bytes":c["comp9_bytes"]-b["comp9_bytes"],
        "experimental_comp9_plus_archive9_baseline_bytes":b["comp9_bytes"]+b["archive_bytes"],
        "experimental_comp9_plus_archive9_candidate_bytes":c["comp9_bytes"]+c["archive_bytes"],
        "experimental_combined_delta_candidate_minus_baseline_bytes":
            c["comp9_bytes"]+c["archive_bytes"]-b["comp9_bytes"]-b["archive_bytes"],
        "full_Hutter_S_measured":False,
        "note":"valid only for 524288 preprocessed stream bytes and the upstream fixed weights; not all original enwik9",
      }
      record["status"]="TWO_INDEPENDENT_REAL_NATIVE_PREFIX_ROUNDTRIPS_VERIFIED"
    except BaseException as exc:
      record["status"]="FAILED_REAL_INTEGRATION"
      record["error"]=str(exc)
      record["error_type"]=type(exc).__name__
      raise
    finally:
      write_report(report,record)
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--corpus",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    r=measured_pair(a.root,a.corpus,a.report)
    print(json.dumps({"status":r["status"],"comparison":r["comparison"],
                      "official_Hutter_S":None},indent=2))


if __name__=="__main__": main()
