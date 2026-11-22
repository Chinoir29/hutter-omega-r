#!/usr/bin/env python3
"""Independent arbitrary-precision Q32 oracle for the 16-pool replacement stage.

Identical fixed synthetic input as the verified v0.29 C++ fixture, but this
implementation does not import or execute the C++ target algorithm.
"""
from __future__ import annotations
from pathlib import Path
import math
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v29"))
import floor_pool_reference as baseline_ref

Q32=1<<32
MASK=(1<<64)-1
FNV=1099511628211

def compact_trial(mismatch:bool)->dict:
    rows=[[0,0] for _ in range(16)] # expected summed Q16, observed mistakes
    state=0x40caf3e1
    input_sig=1469598103934665603
    p_sig=1469598103934665603
    bits=400000
    err_count=0
    loss=0.0
    for i in range(bits):
        state=(state*1664525+1013904223)&0xffffffff
        bp=(i>>1)&7
        side=i&1
        z_bin=(i//32)%48
        z=7.0+0.25*z_bin
        f=max(1,int(math.floor(65536.0/(1.0+math.exp(z))+0.5)))
        p16=65536-f if side else f
        draw=(state>>9)%1000000
        expected_err=int(math.floor((float(f)/65536.0)*1000000))
        err=draw<(3500 if mismatch else expected_err)
        bit=side^int(err)
        idx=(side<<3)|bp
        expected,errors=rows[idx]
        denominator=expected+(16<<16)
        ratio=((errors+16)<<32)//denominator
        ratio=max(1<<14,min(4<<16,ratio))
        adjusted_f=max(1,min(32768,(f*ratio+(1<<15))>>16))
        predicted=Q32-(adjusted_f<<16) if side else (adjusted_f<<16)
        q=predicted/Q32
        loss-=math.log2(q if bit else 1-q)
        rows[idx][0]+=f
        rows[idx][1]+=int(err)
        err_count+=int(err)
        input_sig=((input_sig^((bit<<32)|p16))*FNV)&MASK
        p_sig=((p_sig^predicted)*FNV)&MASK
    return dict(bits=bits,errors=err_count,loss_bits=loss,
                input_checksum=f"{input_sig:016x}",prediction_checksum=f"{p_sig:016x}")

def check(baseline_mismatch:Path,candidate_mismatch:Path,
          baseline_control:Path,candidate_control:Path)->dict:
    inp={
      ("mismatch",False):baseline_ref.parse(baseline_mismatch.read_text()),
      ("mismatch",True):baseline_ref.parse(candidate_mismatch.read_text()),
      ("baseline",False):baseline_ref.parse(baseline_control.read_text()),
      ("baseline",True):baseline_ref.parse(candidate_control.read_text())
    }
    for (label,candidate),actual in inp.items():
        ref=(compact_trial(label=="mismatch") if candidate
             else baseline_ref.trial(label=="mismatch",False))
        for key in ("bits","errors","input_checksum","prediction_checksum"):
            if actual[key]!=ref[key]:
                raise AssertionError("Q32_CROSS_LANGUAGE_MISMATCH "+str((label,candidate,key,actual[key],ref[key])))
        if abs(ref["loss_bits"]-actual["loss_bits"])>0.01:
            raise AssertionError("LOG_LOSS_MISMATCH "+str((label,candidate)))
    result={"status":"INDEPENDENT_NUMERIC_ALL_1P6M_BITS_MATCHED",
            "mismatch_ideal_saving_bits":inp[("mismatch",False)]["loss_bits"]-inp[("mismatch",True)]["loss_bits"],
            "calibrated_ideal_saving_bits":inp[("baseline",False)]["loss_bits"]-inp[("baseline",True)]["loss_bits"],
            "baseline_mismatch_loss_bits":inp[("mismatch",False)]["loss_bits"],
            "candidate_mismatch_loss_bits":inp[("mismatch",True)]["loss_bits"],
            "baseline_calibrated_loss_bits":inp[("baseline",False)]["loss_bits"],
            "candidate_calibrated_loss_bits":inp[("baseline",True)]["loss_bits"],
            "source":"artificial synthetic, not real enwik9",
            "official_Hutter_score":None}
    return result

if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: compact_reference.py original_mismatch candidate_mismatch original_control candidate_control")
    import json
    result=check(*(Path(v) for v in sys.argv[1:]))
    print(json.dumps(result,indent=2))
