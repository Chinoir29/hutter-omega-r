#!/usr/bin/env python3
"""OMÉGA-R v0.32: native genuine longer-prefix proof with independent byte comparison.

The input to the codec is the TRUE enwik9 preprocessed stream from the complete
canonical 1GB file; the first N bytes are copied locally to a reference BEFORE
encoding. Archive9's output is compared byte by byte to the reference in a
fresh workdir initially containing only archive9.

This is NOT an original-enwik9 1GB decompression and NOT an eligible Hutter S.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v26"))
from one_core_resource_meter import run as monitor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v32"))
from prepare_extended_prefix import LIMIT_MIN,LIMIT_MAX

CORPUS_SHA = "159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc"
PRECODER_TOTAL = 501062281

def hashfile(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(4<<20),b""):h.update(part)
    return h.hexdigest()

def compare_bytes(source:Path,restored:Path,expected_len:int)->str:
    if not source.is_file() or not restored.is_file():
        raise ValueError("REFERENCE_OR_DECODED_OUTPUT_MISSING")
    if source.stat().st_size!=expected_len or restored.stat().st_size!=expected_len:
        raise ValueError("PREFIX_LENGTH_MISMATCH")
    h=hashlib.sha256()
    with source.open("rb") as a,restored.open("rb") as b:
        while block:=a.read(4<<20):
            other=b.read(len(block))
            if other!=block:
                raise ValueError("FIRST_DIFFERENT_CHUNK_DECODE_IS_NOT_LOSSLESS")
            h.update(block)
        if b.read(1):
            raise ValueError("TRAILING_UNEXPECTED_DECODED_BYTES")
    return h.hexdigest()

def run_experiment(comp9:Path,corpus:Path,work:Path,report:Path,cap:int)->dict:
    if not isinstance(cap,int) or cap<LIMIT_MIN or cap>LIMIT_MAX or cap%LIMIT_MIN:
        raise ValueError("INVALID_CAP")
    if work.exists() or report.resolve().is_relative_to(work.resolve()):
        raise ValueError("UNSAFE_OR_EXISTING_WORKDIR")
    if not comp9.is_file() or not os.access(comp9,os.X_OK):
        raise ValueError("MISSING_COMP9")
    if corpus.stat().st_size!=1000000000 or hashfile(corpus)!=CORPUS_SHA:
        raise ValueError("BAD_CANONICAL_WIKIPEDIA_SHA")
    work.mkdir(parents=True)
    rec={
       "status":"STARTED",
       "run_type":"authentic canonical enwik9 preprocessed prefix true native comp9/archive9",
       "upstream_commit":"35d1957a5074db802fc134126afc77b76d931761",
       "corpus_bytes":1000000000,
       "corpus_sha256":CORPUS_SHA,
       "full_precoder_stream_expected_bytes":PRECODER_TOTAL,
       "prefix_limit_bytes":cap,
       "comp9_bytes":comp9.stat().st_size,
       "comp9_sha256":hashfile(comp9),
       "official_Hutter_score_S":None,
       "entire_original_enwik9_restored":False,
       "official_validation":False,
    }
    try:
        enc=work/"encode";enc.mkdir()
        (enc/"enwik9").symlink_to(corpus.resolve())
        old=os.environ.get("OMR21_SHADOW_PREFIX_BYTES")
        os.environ["OMR21_SHADOW_PREFIX_BYTES"]=str(cap)
        try:
            encode=monitor([str(comp9.resolve())],enc,
                           Path("/tmp/omr32-encode-meter.json"),
                           timeout_s=12500,sample_s=0.4)
        finally:
            if old is None:os.environ.pop("OMR21_SHADOW_PREFIX_BYTES",None)
            else:os.environ["OMR21_SHADOW_PREFIX_BYTES"]=old
        rec["encode_resource_metrics"]=encode
        if encode["status"]!="FINISHED" or encode["exit_code"]!=0:
            raise ValueError("GENUINE_COMP9_FAILED")
        stderr=Path(encode["error_log"]).read_text(errors="replace")
        if stderr.count("OMR21_PREFIX_ACTUAL_CODED_STREAM_BYTES=501062281")!=1:
            raise ValueError("INCORRECT_PRECODER_INPUT_LENGTH")
        if not encode["memory_below_project_limit_observed"] or not encode["disk_below_project_limit_observed"]:
            raise ValueError("OBSERVED_RESOURCE_LIMIT_OVERRUN")
        ref=enc/"omr23-reference-prefix.bin"
        archive=enc/"archive9"
        if not archive.is_file() or not os.access(archive,os.X_OK):
            raise ValueError("NATIVE_ARCHIVE9_MISSING")
        if not ref.is_file() or ref.stat().st_size!=cap:
            raise ValueError("GENUINE_PRECODER_PREFIX_REFERENCE_MISSING")
        rec["reference_prefix_sha256"]=hashfile(ref)
        rec["native_archive_bytes"]=archive.stat().st_size
        rec["native_archive_sha256"]=hashfile(archive)
        rec["arithmetic_payload_bytes"]=None # parse counted native trailer below
        with archive.open("rb") as f:
            import struct
            assert f.read(4)==b"\x7fELF"
            f.seek(-8,2)
            coded,weights=struct.unpack("<ii",f.read(8))
        if coded<100 or weights!=3744629:
            raise ValueError("INVALID_NATIVE_ARCHIVE9_LAYOUT")
        rec["native_archive_components"]={
           "coded_prefix_bytes":coded,"weights_bytes":weights,
           "trailer_bytes":8,
           "decoder_stub_bytes":archive.stat().st_size-coded-weights-8}
        rec["arithmetic_payload_bytes"]=coded
        report.write_text(json.dumps(rec,indent=2)+"\n")
        dec=work/"independent-archive-only";dec.mkdir()
        shutil.copyfile(archive,dec/"archive9")
        (dec/"archive9").chmod(0o755)
        if sorted(x.name for x in dec.iterdir())!=["archive9"]:
            raise ValueError("INDEPENDENT_DIR_NOT_EMPTY")
        saved=dict(os.environ)
        os.environ.clear()
        os.environ.update({"PATH":"/usr/bin:/bin","HOME":str(dec),"LC_ALL":"C","TZ":"UTC"})
        try:
            decode=monitor(["./archive9"],dec,Path("/tmp/omr32-decode-meter.json"),
                           timeout_s=12500,sample_s=0.4)
        finally:
            os.environ.clear()
            os.environ.update(saved)
        rec["decode_resource_metrics"]=decode
        if decode["status"]!="FINISHED" or decode["exit_code"]!=0:
            raise ValueError("INDEPENDENT_ARCHIVE9_FAILED")
        output=dec/"omr24-decoded-prefix.bin"
        digest=compare_bytes(ref,output,cap)
        rec["decoded_sha256"]=digest
        rec["decoded_bytes"]=cap
        rec["initial_independent_workdir_files"]=["archive9"]
        rec["independent_archive_argv"]=[]
        rec["status"]="LONGER_NATIVE_PRECODER_PREFIX_BITWISE_VERIFIED"
        # Evidence kept, all raw source and restored bytes destroyed.
        shutil.rmtree(work)
    except BaseException as exc:
        rec["status"]="FAILED_NATIVE_LONG_PREFIX"
        rec["error_type"]=type(exc).__name__
        rec["error_message"]=str(exc)
        raise
    finally:
        report.write_text(json.dumps(rec,indent=2)+"\n")
    return rec

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary",type=Path,required=True)
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--work",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--prefix-bytes",type=int,required=True)
    args=ap.parse_args()
    r=run_experiment(args.binary,args.corpus,args.work,args.report,args.prefix_bytes)
    print(json.dumps({"status":r["status"],"prefix_bytes":r["decoded_bytes"],
                      "decoded_sha256":r["decoded_sha256"],
                      "archive9_bytes":r["native_archive_bytes"],
                      "official_Hutter_S":None},indent=2))
