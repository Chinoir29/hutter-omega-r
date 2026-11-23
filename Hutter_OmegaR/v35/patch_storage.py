#!/usr/bin/env python3
"""v0.35 controlled 2-constant SEMCACHE patch on pinned GPL-3.0 upstream.
Always kQpE3=999. Compare store gate kSpE3=950 (control) and 980.
The rest of the upstream code/weights/toolchain remains unchanged.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"v13"))
sys.path.insert(0,str(HERE/"v16"))
import semantic_cache_gate_patch as base
import patch_upper_gate as upper

Q=999
STORE=(950,980)
STORE_RX=re.compile(r"(?m)^(constexpr int kSpE3\s*=\s*)950(\s*;\s*// store below\s*)$")

def rewrite(text: str, store: int) -> str:
    if type(store) is not int or store not in STORE:
        raise ValueError("unregistered store threshold")
    if len(STORE_RX.findall(text))!=1:
        raise ValueError("expected pinned unique store declaration")
    if len(base.SOURCE_RX.findall(text))!=1:
        raise ValueError("expected pinned unique query declaration")
    out=upper.modify_source(text,Q)
    if store!=950:
        out,n=STORE_RX.subn(lambda x: x.group(1)+str(store)+x.group(2),out)
        if n!=1:raise ValueError("store patch did not change one declaration")
    assert out.count("constexpr int kQpE3 = 999;")==1
    assert out.count("constexpr int kSpE3 = "+str(store)+";")==1
    assert out.count("constexpr int kCalqE3 = 900;")==1
    if store>Q:raise ValueError("store gate exceeds query gate")
    return out

def patch(checkout: Path, store: int, report: Path):
    checkout=checkout.resolve()
    commit=base.git("rev-parse","HEAD",cwd=checkout)
    if commit!=base.BASE_COMMIT:
        raise RuntimeError("Unpinned upstream source")
    source=checkout/base.RELATIVE_SOURCE
    oldsha=base.git("hash-object",str(source),cwd=checkout)
    if oldsha!=base.BASE_BLOB:
        raise RuntimeError("Upstream source hash mismatch")
    original=source.read_text(encoding="utf8")
    updated=rewrite(original,store)
    source.write_text(updated,encoding="utf8")
    newsha=base.git("hash-object",str(source),cwd=checkout)
    if newsha==oldsha:raise RuntimeError("Expected modifications missing")
    changed=subprocess.run(["git","diff","--name-only"],cwd=checkout,
                            capture_output=True,text=True,check=True).stdout.splitlines()
    if changed!=[str(base.RELATIVE_SOURCE)]:
        raise RuntimeError("Unexpected changes to source "+repr(changed))
    record={
        "project":"OMEGA-R v0.35 SEMCACHE store threshold paired experiment",
        "upstream_commit":base.BASE_COMMIT,
        "source_original_git_blob":oldsha,
        "source_modified_git_blob":newsha,
        "query_threshold_qpe3":Q,
        "store_threshold_spe3":store,
        "changed_files":changed,
        "upstream_license":"GPL-3.0",
        "laboratory_mode_only":True,
        "official_hutter_score":None
    }
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    return record

def self_test():
    source=(
        "constexpr int kQpE3 = 990;             // look up below\n"
        "constexpr int kSpE3 = 950;             // store below\n"
        "constexpr int kCalqE3 = 900;           // running\n"
    )
    a=rewrite(source,950)
    b=rewrite(source,980)
    assert "kQpE3 = 999;" in a and "kSpE3 = 950;" in a
    assert "kQpE3 = 999;" in b and "kSpE3 = 980;" in b
    for invalid in (1,970,990,1000,False):
        try:rewrite(source,invalid)
        except ValueError:pass
        else:raise AssertionError("invalid accepted")
    for malformed in ("",source.replace("kSpE3 = 950","kSpE3 = 951"),source+source):
        try:rewrite(malformed,980)
        except ValueError:pass
        else:raise AssertionError("invalid upstream accepted")
    print("V035_PATCH_SELFTEST_OK")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--checkout",type=Path)
    p.add_argument("--sp-e3",type=int,choices=STORE)
    p.add_argument("--report",type=Path)
    a=p.parse_args()
    if a.self_test:self_test();return
    if not all((a.checkout,a.sp_e3,a.report)):p.error("Need checkout, sp-e3, report")
    print(json.dumps(patch(a.checkout,a.sp_e3,a.report),indent=2))

if __name__=="__main__":main()
