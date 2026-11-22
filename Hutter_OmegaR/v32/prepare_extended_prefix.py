#!/usr/bin/env python3
"""OMÉGA-R v0.32 — extend the *proved native comp9/archive9 path* up to 64 MiB.

The upstream -e transforms the canonical COMPLETE 1 GB enwik9 file first.
Only its PREPROCESSED arithmetic input is capped. The modified native archive9
reverses precisely that prefix, not the complete enwik9 corpus.

Source and GPL license preserved in scratch; no third-party binary distributed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v25"))
import prepare_native as v25

OLD_LIMIT = "1048576ull"
NEW_LIMIT = "67108864ull"
OLD_INTERNAL = 'setenv("OMR23_PREFIX_DECODE", "524288", 1)'
LIMIT_MIN = 524_288
LIMIT_MAX = 64 * 1024 * 1024


def extend(original:bytes, cap:int)->bytes:
    if not isinstance(cap,int) or cap<LIMIT_MIN or cap>LIMIT_MAX or cap % LIMIT_MIN:
        raise ValueError("INVALID_PREFIX_CAP_MUST_BE_512K_ALIGNED_AND_AT_MOST_64M")
    code=original.decode("utf-8")
    if code.count(OLD_LIMIT)!=3:
        raise ValueError("PREFIX_CAP_ANCHORS_NOT_EXACTLY_THREE")
    if code.count(OLD_INTERNAL)!=1:
        raise ValueError("INTERNAL_DECODE_CAP_ANCHOR_DRIFT")
    if code.count("omr23-reference-prefix.bin")!=1 or code.count('rename(temp_path.c_str(),"omr23-decoded-prefix.bin")')!=1:
        raise ValueError("REAL_REFERENCE_OR_DECODE_PROBE_MISSING")
    if code.count('rename(temp_path.c_str(), "archive9")')!=1:
        raise ValueError("NATIVE_ARCHIVE9_PACKER_MISSING")
    code=code.replace(OLD_LIMIT,NEW_LIMIT)
    code=code.replace(OLD_INTERNAL,f'setenv("OMR23_PREFIX_DECODE", "{cap}", 1)',1)
    if "omr21-coded-prefix.bin" in code:
        raise ValueError("NON_NATIVE_OLDER_PREFIX_PACKER")
    if code.count(NEW_LIMIT)!=3:
        raise AssertionError("NOT_ALL_THREE_LIMITS_REPLACED")
    return code.encode()


def prepare(upstream:Path,output:Path,cap:int)->dict:
    parent=v25.prepare(upstream,output)
    runner=output/"src/runner.cpp"
    base=runner.read_bytes()
    out=extend(base,cap)
    runner.write_bytes(out)
    # Fresh same binary from this source is needed for the given cap; not a
    # post-hoc alteration of the competitor's submitted decompressor.
    metadata={
        "status":"VARIABLE_NATIVE_PREFIX_SOURCE_PREPARED_NOT_EXECUTED",
        "upstream_commit":parent["upstream_commit"],
        "source_original_v25_sha256":hashlib.sha256(base).hexdigest(),
        "source_extended_sha256":hashlib.sha256(out).hexdigest(),
        "fixed_internal_decoder_cap_bytes":cap,
        "same_encoder_and_decoder_preprocessor":True,
        "native_comp9_archive9_packaging_preserved":True,
        "canonical_enwik9_processing_before_capping":True,
        "reference_file_captured_before_arithmetic":"omr23-reference-prefix.bin",
        "output_file_written_by_only_native_archive9":"omr24-decoded-prefix.bin",
        "source_cap_limit_max_bytes":LIMIT_MAX,
        "side_files_needed_by_archive9_at_start":0,
        "whole_enwik9_restored":False,
        "eligible_Hutter_score_S":None,
        "licence":"upstream GPL-3.0-only scratch checkout; do not redistribute"
    }
    (output.parent/"omr32-source-audit.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return metadata


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--prefix-bytes",type=int,required=True)
    args=ap.parse_args()
    print(json.dumps(prepare(args.upstream,args.output,args.prefix_bytes),indent=2))
