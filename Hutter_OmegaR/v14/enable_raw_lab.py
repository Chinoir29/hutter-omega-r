#!/usr/bin/env python3
"""Experimental laboratory switch for the uncompacted, full-model upstream coder.

- Exact Git commit/blob are mandatory.
- The release -e, archive9 and jury paths are NOT modified.
- Only enables -c for a laboratory build; never substitutes for Hutter testing.
- Upstream code is GNU GPL-3.0, remains cloned from its original author.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

UPSTREAM_COMMIT = "35d1957a5074db802fc134126afc77b76d931761"
RUNNER_BLOB = "4f9ee4adfeef37069eecf95bf8efb4c0d03cf09b"
RUNNER = Path("src/runner.cpp")
OLD_PARSER = "(argv[1][1] != 'd' && argv[1][1] != 'e'"
NEW_PARSER = "(argv[1][1] != 'c' && argv[1][1] != 'd' && argv[1][1] != 'e'"
OLD_HELPER = "#if !(1 && !AUX_BUILD)\\nstatic bool provide_dict_file"
NEW_HELPER = "#if OMR14_RAW_CODER || !(1 && !AUX_BUILD)\\nstatic bool provide_dict_file"
OLD_BRANCH = "#if !(1 && !AUX_BUILD)   // the package form has no -c"
NEW_BRANCH = "#if OMR14_RAW_CODER || !(1 && !AUX_BUILD) // LAB ONLY: allow -c in full-model build"
LAB_HEAD = ("// OMÉGA-R research-only build: allow raw -c coding with the unchanged full model.\n"
            "// This laboratory path and its scores are NOT Hutter Prize submissions.\n"
            "#define OMR14_RAW_CODER 1\n")

def modify_source(source: str) -> str:
    if source.count(OLD_PARSER) != 1:
        raise ValueError("Unexpected release argument parser")
    if source.count(OLD_BRANCH) != 1:
        raise ValueError("Unexpected release -c switch")
    if source.count(OLD_HELPER) != 1:
        raise ValueError("Missing auxiliary dictionary file helper")
    if "OMR14_RAW_CODER" in source:
        raise ValueError("This source was previously patched")
    changed=(LAB_HEAD+source.replace(OLD_PARSER,NEW_PARSER,1)
             .replace(OLD_BRANCH,NEW_BRANCH,1).replace(OLD_HELPER,NEW_HELPER,1))
    if changed.count("OMR14_RAW_CODER")!=3:
        raise RuntimeError("Unexpected patch output")
    return changed

def git(checkout:Path,*args:str)->str:
    return subprocess.check_output(["git",*args],cwd=checkout,text=True).strip()

def patch_checkout(checkout:Path,out:Path):
    checkout=checkout.resolve()
    found=git(checkout,"rev-parse","HEAD")
    if found!=UPSTREAM_COMMIT:
        raise RuntimeError(f"Unsafe revision {found}")
    source=checkout/RUNNER
    before_blob=git(checkout,"hash-object",str(source))
    if before_blob!=RUNNER_BLOB:
        raise RuntimeError(f"Unsafe upstream runner blob {before_blob}")
    source.write_text(modify_source(source.read_text(encoding="utf8")),encoding="utf8")
    after_blob=git(checkout,"hash-object",str(source))
    record={
       "project":"OMÉGA-R v0.14 experimental raw core coder",
       "upstream":"https://github.com/marwoelk/cmix-neif-2.0",
       "license":"GPL-3.0",
       "head_commit":found,
       "runner_original_git_blob":before_blob,
       "runner_patched_git_blob":after_blob,
       "changed_files":[str(RUNNER)],
       "change_scope":"enable -c for full-model laboratory coding; no claim of score",
       "hutter_score":None,
       "upstream_modified":True,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkout",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(patch_checkout(a.checkout,a.report),indent=2,ensure_ascii=False))
if __name__=="__main__":main()
