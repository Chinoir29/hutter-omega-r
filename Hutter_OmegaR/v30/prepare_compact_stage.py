#!/usr/bin/env python3
"""OMÉGA-R v0.30: structural replacement of the upstream confidence floor.

Pins the exact original upstream git blob and replaces the Stage data structure
with a 16-cell causal reliability-pool estimator. Uses the proven native
v0.25 comp9/archive9 path. Upstream GPL-3.0-only code remains scratch-only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v25"))
import prepare_native as v25

PIN_GIT_BLOB = "cfdedf819ddeae4aeebf1a91e9dbb6942c8be03c"
START = "struct Stage {"
END = "};\n\n// Interval split with a 32-bit probability"
REPLACEMENT = "// OMÉGA-R v0.30: replacement, not an additional probability model.\n// GNU GPL-3.0-only when compiled into cmix-neif-2.0.\n// Compress and decompress share this same in-memory state; no side data.\n//\n// Replaces thousands of high-confidence fine-bin cells with sixteen\n// (predicted side x bit position) reliability pools.  A pool learns\n// observed/expected mistakes ratio from PREVIOUS coded bits only. The\n// original p16 determines the local confidence and the multiplicative\n// ratio corrects only skipped high-confidence bits.\nstruct Stage {\n  struct PoolRow {\n    uint64_t expected_q16 = 0;\n    uint64_t mistakes = 0;\n  };\n  PoolRow pool[16] = {};\n  int current = -1;\n  unsigned int last_f = 0;\n  int predicted_side = 0;\n\n  __attribute__((noinline, minsize)) Stage() = default;\n\n  __attribute__((noinline)) uint32_t P32(\n      unsigned int p16, int override_active, int skip, int bitl,\n      float z, float m1raw, int meta, int bit_pos) {\n    (void)bitl; (void)z; (void)m1raw; (void)meta;\n    current = -1;\n    const uint32_t uncorrected = (uint32_t)p16 << 16;\n    if (override_active || !skip) return uncorrected;\n    if (!(p16 >= 1u && p16 <= 65535u)) __builtin_trap();\n\n    predicted_side = p16 >= 32768u ? 1 : 0;\n    const unsigned int f = p16 < 32768u ? p16 : 65536u - p16;\n    current = (predicted_side << 3) | (bit_pos & 7);\n    last_f = f;\n    const PoolRow& row = pool[current];\n    // Units: expected_q16 = SUM(f); mistakes in integer bits.\n    // The 16 effective prior examples preserve ratio 1 at startup.\n    const unsigned __int128 numerator =\n        (static_cast<unsigned __int128>(row.mistakes) + 16u) << 32;\n    const uint64_t denominator =\n        row.expected_q16 + (uint64_t(16) << 16);\n    uint64_t ratio_q16 = static_cast<uint64_t>(numerator / denominator);\n    if (ratio_q16 < (uint64_t(1) << 14)) ratio_q16 = uint64_t(1) << 14;\n    if (ratio_q16 > (uint64_t(4) << 16)) ratio_q16 = uint64_t(4) << 16;\n    uint64_t f_eff = (uint64_t(f) * ratio_q16 + (uint64_t(1) << 15)) >> 16;\n    if (f_eff < 1) f_eff = 1;\n    if (f_eff > 32768) f_eff = 32768;\n    const uint32_t err_q32 = static_cast<uint32_t>(f_eff << 16);\n    return predicted_side ? uint32_t((uint64_t(1) << 32) - err_q32) : err_q32;\n  }\n\n  __attribute__((noinline)) void Update(int bit) {\n    if (current < 0) return;\n    PoolRow& r = pool[current];\n    r.expected_q16 += last_f;\n    if (bit != predicted_side) ++r.mistakes;\n    current = -1;\n  }\n};\n"

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def replace_stage(source:bytes)->bytes:
    if git_blob(source)!=PIN_GIT_BLOB:
        raise ValueError("SOURCE_BLOB_DRIFT")
    text=source.decode("utf-8")
    if text.count(START)!=1 or text.count(END)!=1:
        raise ValueError("STAGE_ANCHOR_NONUNIQUE_OR_MISSING")
    a=text.index(START)
    b=text.index(END,a)+2
    if b<=a:raise AssertionError("SOURCE_STAGE_BOUNDARY")
    patched=text[:a]+REPLACEMENT+text[b:]
    if "Cell c[kCtx]" in patched:
        raise AssertionError("ORIGINAL_FINE_BINS_STILL_IN_STAGE")
    if patched.count("PoolRow pool[16]")!=1:
        raise AssertionError("WRONG_POOL_GEOMETRY")
    if patched.count("inline unsigned int Mid(")!=1:
        raise AssertionError("ORIGINAL_ARITHMETIC_SPLITTER_CHANGED")
    return patched.encode("utf-8")

def prepare(upstream:Path,output:Path)->dict:
    original=v25.prepare(upstream,output)
    dst=output/"src/floor_stage.h"
    raw=dst.read_bytes()
    patched=replace_stage(raw)
    dst.write_bytes(patched)
    for role in ("encoder","decoder"):
        txt=(output/"src/coder"/(role+".cpp")).read_text()
        if "floor_.P32(p," not in txt or "floor_.Update(bit)" not in txt:
            raise AssertionError("CODER_AND_DECODER_NOT_SHARED")
    evidence={
      "status":"STRUCTURAL_REPLACEMENT_SOURCE_PREPARED_NOT_BUILT",
      "upstream_commit":original["upstream_commit"],
      "original_stage_cell_count":11264,
      "original_stage_cell_bytes":90112,
      "new_reliability_pool_count":16,
      "new_pool_bytes":256,
      "replaced_file":"src/floor_stage.h",
      "original_blob_git":PIN_GIT_BLOB,
      "baseline_floor_sha256":hashlib.sha256(raw).hexdigest(),
      "candidate_floor_sha256":hashlib.sha256(patched).hexdigest(),
      "same_native_comp9_archive9_runner":True,
      "real_codec_motors_unchanged":True,
      "causal_one_step_update_only":True,
      "new_side_data_bytes":0,
      "official_hutter_score":None,
      "whole_enwik9_restored":False
    }
    (output.parent/"omr30-source-audit.json").write_text(json.dumps(evidence,indent=2)+"\n")
    return evidence

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    print(json.dumps(prepare(a.upstream,a.output),indent=2))
