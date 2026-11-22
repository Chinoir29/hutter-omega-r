#!/usr/bin/env python3
"""Independent big-integer reference for OMR29 high-confidence parent calibration.

Reproduces the fixed-point computations of *floor_stage::P32* and *Update*
without importing any C++ or copied upstream source. This is not a Hutter
score or proof that the modification helps on enwik9.
"""
from __future__ import annotations
import math
import re
import sys

P = 1099511628211
MASK = (1 << 64) - 1
Q32 = (1 << 32)


def trial(mismatched:bool,pooled:bool) -> dict:
    counts={}  # fine context (side, bp, z-bin) -> (n, mistakes)
    parents={} # coarse context (side,bp) -> (sum_q16_expected, mistakes)
    state=0x40caf3e1
    input_sig=1469598103934665603
    pred_sig=1469598103934665603
    errors=0
    loss=0.0
    for i in range(400000):
        state=(state*1664525+1013904223)&0xffffffff
        bp=(i>>1)&7
        side=i&1
        b=(i//32)%48
        z=7.0+0.25*b
        f=max(1,int(math.floor(65536.0/(1.0+math.exp(z))+0.5)))
        p16=65536-f if side else f
        draw=(state>>9)%1000000
        expected_error=int(math.floor((float(f)/65536.0)*1000000.0))
        error=draw<(3500 if mismatched else expected_error)
        bit=side^int(error)
        idx=(side,bp,b)
        n,k=counts.get(idx,(0,0))
        pp=(side,bp)
        expected_f,mistakes=parents.get(pp,(0,0))
        prior_f=f
        if pooled:
            ratio=((mistakes+16)<<32)//(expected_f+(16<<16))
            ratio=max(1<<14,min(4<<16,ratio))
            prior_f=(f*ratio+(1<<15))>>16
            prior_f=max(1,min(32768,prior_f))
        cw=1<<12
        er=((k<<32)+cw*(prior_f<<16))//(n+cw)
        er=max(1,min(1<<31,er))
        out=(Q32-er) if side else er
        q=float(out)/Q32
        loss-=math.log2(q if bit else 1-q)
        counts[idx]=(n+1,k+int(error))
        parents[pp]=(expected_f+f,mistakes+int(error))
        errors+=int(error)
        input_sig=((input_sig^((bit<<32)|p16))*P)&MASK
        pred_sig=((pred_sig^out)*P)&MASK
    return {"bits":400000,"errors":errors,"loss_bits":loss,
            "input_checksum":f"{input_sig:016x}",
            "prediction_checksum":f"{pred_sig:016x}"}


def parse(line:str)->dict:
    m=re.search(r"OMR29_FLOOR_TEST case=(\w+) bits=(\d+) errors=(\d+) loss_bits=([\d.]+) input_checksum=([0-9a-f]{16}) prediction_checksum=([0-9a-f]{16})",line)
    if not m:
        raise ValueError("MISSING_GROUNDED_CPP_METRICS")
    c,n,e,loss,inp,pred=m.groups()
    return dict(case=c,bits=int(n),errors=int(e),loss_bits=float(loss),input_checksum=inp,prediction_checksum=pred)


def check(candidate_mismatch:str,baseline_mismatch:str,candidate_control:str,baseline_control:str)->dict:
    inputs={
      ("mismatch",True):parse(candidate_mismatch),
      ("mismatch",False):parse(baseline_mismatch),
      ("baseline",True):parse(candidate_control),
      ("baseline",False):parse(baseline_control),
    }
    for (name,pooled),actual in inputs.items():
        expected=trial(name=="mismatch",pooled)
        for k in ("bits","errors","input_checksum","prediction_checksum"):
            if actual[k]!=expected[k]:
                raise ValueError("PY_CPP_Q32_DIVERGENCE "+str((name,pooled,k,actual[k],expected[k])))
        if abs(actual["loss_bits"]-expected["loss_bits"])>0.01:
            raise ValueError("LOSS_COMPUTATION_MISMATCH "+str((name,pooled)))
    bm=inputs[("mismatch",False)]["loss_bits"]
    cm=inputs[("mismatch",True)]["loss_bits"]
    return {"status":"INDEPENDENT_CPP_PYTHON_Q32_EXACT",
            "mismatch_synthetic_baseline_loss_bits":bm,
            "mismatch_synthetic_candidate_loss_bits":cm,
            "mismatch_synthetic_candidate_saving_bits":bm-cm,
            "calibrated_synthetic_baseline_loss_bits":inputs[("baseline",False)]["loss_bits"],
            "calibrated_synthetic_candidate_loss_bits":inputs[("baseline",True)]["loss_bits"],
            "warning":"synthetic only; real compression unknown"}


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: floor_pool_reference.py <candidate-mismatch-log> <baseline-mismatch-log> <candidate-control-log> <baseline-control-log>")
    from pathlib import Path
    result=check(*(Path(p).read_text() for p in sys.argv[1:]))
    import json
    print(json.dumps(result,indent=2))
