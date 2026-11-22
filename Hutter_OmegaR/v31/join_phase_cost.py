#!/usr/bin/env python3
"""OMÉGA-R v0.31: join measured page-phase density to published cmix cost bins.

This is a *research targeting construction*, NOT a prediction that a chosen
change will improve compression. Published model-cost 8 MiB values are
overlap-interpolated from 1000 rows in doc/stream_rate.tsv, not own re-encoding.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

UPSTREAM = "35d1957a5074db802fc134126afc77b76d931761"
STREAM_SHA = "c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718"


def correlation(a:list[float], b:list[float])->float|None:
    if len(a)!=len(b) or not a:
        raise ValueError("UNEQUAL_COST_WINDOW_LENGTHS")
    ax=sum(a)/len(a);bx=sum(b)/len(b)
    x=[v-ax for v in a];y=[v-bx for v in b]
    numer=sum(p*q for p,q in zip(x,y))
    denom=math.sqrt(sum(p*p for p in x)*sum(q*q for q in y))
    return numer/denom if denom else None


def combine(phase:dict, cost:dict)->dict:
    if (phase.get("status")!="ACTUAL_PRECODER_PHASE_MAP_NOT_CMIX_COMPRESSED" or
        cost.get("classification")!="REPROCESSED_PUBLISHED_CMIX_CODER_COST_MAP_NOT_LOCAL_REEXECUTION"):
        raise ValueError("UNSUPPORTED_PROVENANCE_CLASS")
    if (phase.get("source_git_commit")!=UPSTREAM or cost.get("source_commit")!=UPSTREAM):
        raise ValueError("DIFFERENT_UPSTREAM_COMMITS")
    if (phase.get("stream_sha256")!=STREAM_SHA or cost.get("omr19_stream_sha256")!=STREAM_SHA):
        raise ValueError("NOT_SAME_GENUINE_PRECODER_BYTES")
    windows=phase.get("chunks")
    models=cost.get("windows")
    if not isinstance(windows,list) or not isinstance(models,list) or len(windows)!=len(models) or not windows:
        raise ValueError("WINDOW_COUNT_MISMATCH")
    out=[]
    for q,m in zip(windows,models):
        if (q.get("index")!=m.get("index") or
            q.get("start_byte")!=m.get("from_bytes") or
            q.get("end_byte_exclusive")-q.get("start_byte")!=m.get("input_bytes")):
            raise ValueError("DIFFERENT_BYTE_WINDOWS")
        pages=q["page_anchors"]
        if pages<0 or m["model_output_bytes_approx"]<0:
            raise ValueError("NEGATIVE_MEASUREMENTS")
        out.append({
           "window_index":q["index"],
           "start_byte":q["start_byte"],
           "input_bytes":m["input_bytes"],
           "page_anchors_measured_exactly":pages,
           "published_model_coded_bytes_approx":m["model_output_bytes_approx"],
           "published_model_bits_per_input_byte_approx":m["model_bits_per_byte_approx"],
        })
    marker_counts=[float(r["page_anchors_measured_exactly"]) for r in out]
    cost_bits=[float(r["published_model_bits_per_input_byte_approx"]) for r in out]
    first=phase.get("first_marker_chunk")
    if first is not None and (not isinstance(first,int) or first<0 or first>=len(out)):
        raise ValueError("BAD_FIRST_PAGE_WINDOW")
    # Retain only windows definitely AFTER the first observed page anchor.
    body=[r for r in out
          if first is not None and r["window_index"]>first
          and r["page_anchors_measured_exactly"]>0]
    # Rank purely by the published measured coder cost; no statistical
    # fitting to page density and no invented "improvement" from the join.
    top=sorted(body,key=lambda r:(-r["published_model_bits_per_input_byte_approx"],
                                  r["window_index"]))[:8]
    return {
        "status":"ACTUAL_PAGE_PHASE_PUBLISHED_CODER_COST_MAP_JOINED",
        "upstream_commit":UPSTREAM,
        "source_phase":{"stream_sha256":STREAM_SHA,
                        "exact_page_markers":phase["total_exact_page_markers"],
                        "first_page_marker_offset":phase.get("first_marker_offset"),
                        "first_marker_window":first},
        "published_model_cost":{
            "source_file":cost["source_file"],
            "source_blob_sha":cost["source_blob_sha"],
            "source_rows":cost["source_rows"],
            "source_total_coded_bytes_as_published":cost["source_total_model_coded_bytes"],
            "interpolation_warning":cost["alignment"]},
        "correlation_page_density_vs_published_model_bits_per_byte":correlation(marker_counts,cost_bits),
        "research_windows_after_first_page":top,
        "all_windows":out,
        "decision":"TARGET_PAGE_BEARING_HIGH_CODER_COST_WINDOWS; MAINTAIN_EXACT_PREVIOUS_PREDICTOR_STATE",
        "must_preserve_complete_prior_coder_state_in_window_tests":True,
        "unverified_gain_bytes":None,
        "official_hutter_score_S":None,
        "whole_enwik9_restored":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase",type=Path,required=True)
    ap.add_argument("--published-cost",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    result=combine(json.loads(a.phase.read_text()),json.loads(a.published_cost.read_text()))
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="all_windows"},indent=2))


if __name__=="__main__":
    main()
