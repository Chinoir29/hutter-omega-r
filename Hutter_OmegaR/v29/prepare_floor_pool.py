#!/usr/bin/env python3
"""OMÉGA-R v0.29: pooled high-confidence error calibration of cmix floor_stage.

This is a new causal hierarchical estimator, not a threshold sweep.
It shares a learned error-rate *ratio* across fine confidence bins of the same
bit position and predicted side. Baseline compiler and decoder code unchanged,
except the shared floor_stage.h used on BOTH encoder and decoder.

Sources pinned to cmix-neif-2.0 GPL-3.0-only commit; scratch checkout retains
upstream notices. Never publish third-party code, weights, corpus, or binaries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v25"))
import prepare_native as v25

ORIGINAL_GIT_BLOB = "cfdedf819ddeae4aeebf1a91e9dbb6942c8be03c"
ORIGINAL_C = "  Cell c[kCtx];"
ORIGINAL_CUR = "  int cur = -1;"
ORIGINAL_RESET = "    cur = -1;"
ORIGINAL_CELL = "    const Cell& e = c[idx];"
ORIGINAL_NUM = "cw * ((uint64_t)f << 16)"
ORIGINAL_UP = "    Cell& e = c[cur];"

# The parent class excludes the confidence bin but keeps predicted side
# and the bit position of the byte. The baseline fine-bin counts remain intact.
PARENT = """  struct Parent {
    uint64_t expected_f = 0;  // cumulative baseline predicted mistakes, Q16
    uint64_t mistakes = 0;    // actual surprising bits
  };
  Parent parent[16] = {};
  int cur_parent = -1;
  uint32_t cur_f = 0;
"""
PATCH_PRIOR = """    uint64_t f_prior = f;
    if (skip) {
      cur_parent = (side << 3) | (bp & 7);
      cur_f = f;
      const Parent& par = parent[cur_parent];
      // Ratio = (observed errors + 16)/(sum of baseline error probabilities + 16).
      // Numerator units: Q32. Denominator: Q16. Result: Q16.
      const unsigned __int128 num =
          (static_cast<unsigned __int128>(par.mistakes) + 16u) << 32;
      const uint64_t den = par.expected_f + (uint64_t(16) << 16);
      uint64_t ratio_q16 = static_cast<uint64_t>(num / den);
      if (ratio_q16 < (uint64_t(1) << 14)) ratio_q16 = uint64_t(1) << 14;
      if (ratio_q16 > (uint64_t(4) << 16)) ratio_q16 = uint64_t(4) << 16;
      f_prior = (uint64_t(f) * ratio_q16 + (uint64_t(1) << 15)) >> 16;
      if (f_prior < 1u) f_prior = 1u;
      if (f_prior > 32768u) f_prior = 32768u;
    }
"""
PATCH_UPDATE = """    if (cur_parent >= 0) {
      Parent& par = parent[cur_parent];
      par.expected_f += cur_f;
      if (bit != side) ++par.mistakes;
    }
"""


def git_blob(src:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(src)).encode()+b"\0"+src).hexdigest()


def make_patch(orig:bytes)->bytes:
    if git_blob(orig)!=ORIGINAL_GIT_BLOB:
        raise ValueError("PINNED_FLOOR_STAGE_DRIFT")
    text=orig.decode("utf-8")
    for needle in (ORIGINAL_C,ORIGINAL_CUR,ORIGINAL_RESET,ORIGINAL_CELL,ORIGINAL_NUM,ORIGINAL_UP):
        if text.count(needle)!=1:
            raise ValueError("AMBIGUOUS_FLOOR_STAGE_ANCHOR "+needle)
    text=text.replace(ORIGINAL_C,ORIGINAL_C+"\n"+PARENT,1)
    text=text.replace(ORIGINAL_RESET,ORIGINAL_RESET+"\n    cur_parent = -1;",1)
    text=text.replace(ORIGINAL_CELL,ORIGINAL_CELL+"\n"+PATCH_PRIOR,1)
    text=text.replace(ORIGINAL_NUM,"cw * (f_prior << 16)",1)
    text=text.replace(ORIGINAL_UP,ORIGINAL_UP+"\n"+PATCH_UPDATE,1)
    for marker in ("cur_parent = -1;","par.expected_f += cur_f","num / den","cw * (f_prior << 16)"):
        if text.count(marker)!=1 and marker!="cur_parent = -1;":
            raise AssertionError("NOT_ONE_HIERARCHICAL_UPDATE "+marker)
    return text.encode()


def prepare(upstream:Path, output:Path)->dict:
    prereq=v25.prepare(upstream,output)
    target=output/"src/floor_stage.h"
    raw=target.read_bytes()
    revised=make_patch(raw)
    target.write_bytes(revised)
    # This same shared header is included by original Encoder and Decoder.
    for role in ("encoder","decoder"):
        cpp=(output/f"src/coder/{role}.cpp").read_bytes()
        if b'floor_.P32(p,' not in cpp:
            raise ValueError("UNSHARED_FLOOR_STAGE_"+role)
    result={
      "status":"POOLED_CALIBRATOR_SOURCE_PREPARED_NOT_YET_BUILT",
      "upstream_commit":prereq["upstream_commit"],
      "base_native_comp9_from_v25":True,
      "source_file":"src/floor_stage.h",
      "original_floor_git_blob":ORIGINAL_GIT_BLOB,
      "baseline_floor_sha256":hashlib.sha256(raw).hexdigest(),
      "candidate_floor_sha256":hashlib.sha256(revised).hexdigest(),
      "change":"parent calibration of error ratio per (predicted side, byte bit position) only for skipped high-confidence bits; all fine-bin counts preserved",
      "parent_bins":16, "ratio_clip_q16":[1<<14,4<<16],
      "causal_integer_arithmetic_only":True,
      "symmetric_shared_header":True,
      "no_new_decoder_side_data":True,
      "full_enwik9_restored":False,
      "contest_score_S":None
    }
    (output.parent/"omr29-source-audit.json").write_text(json.dumps(result,indent=2)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(a.upstream,a.output),indent=2))


if __name__=="__main__":main()
