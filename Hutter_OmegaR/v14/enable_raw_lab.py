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
GATE = Path("src/tf1/tf1_gate.cpp")
GATE_BLOB = "17eae4b1f5eca43598fa1b28c46a10b191793fe1"
GATE_ANCHOR = "  r_anker_.Init(kAnker, 8);\n}"
GATE_REPLACEMENT = ("  r_anker_.Init(kAnker, 8);\n"
                    "  // OMR14_LAB_GATE: a raw research stream contains no enwik9 metadata.\n"
                    "  // Both laboratory encoder and decoder start in plain text-body mode.\n"
                    "  // The original release code stays unchanged in the upstream repository.\n"
                    "  mf_raus_ = true;\n"
                    "  st_state_ = kBody;\n"
                    "  arm_[kZoneHdrblock] = false;\n"
                    "}")
OLD_PARSER = "(argv[1][1] != 'd' && argv[1][1] != 'e'"
NEW_PARSER = "(argv[1][1] != 'c' && argv[1][1] != 'd' && argv[1][1] != 'e'"
OLD_HELPER = "#if !(1 && !AUX_BUILD)\nstatic bool provide_dict_file"
NEW_HELPER = "#if OMR14_RAW_CODER || !(1 && !AUX_BUILD)\nstatic bool provide_dict_file"
OLD_BRANCH = "#if !(1 && !AUX_BUILD)   // the package form has no -c"
NEW_BRANCH = "#if OMR14_RAW_CODER || !(1 && !AUX_BUILD) // LAB ONLY: allow -c in full-model build"
INERT_ANCHOR = "static inline bool AuthorBlockInert() {"
INERT_OLD = ("  if (transformer::BlobForm()) return true;\n"
             "  if (vocab_frozen::g_aux) return true;\n"
             "  return false;")
INERT_NEW = ("  if (g_omr14_lab_raw_mode) return true;\n"
             + INERT_OLD)
LAB_GLOBAL = ("// Independent from transformer::Active() and SEMCACHE.\n"
              "// Lab-only: disable metadata transformations for raw byte streams.\n"
              "static bool g_omr14_lab_raw_mode = false;\n\n")
MAIN_ANCHOR = "int main(int argc, char** argv) {\n  console_progress::Begin();"
MAIN_REPLACE = ("int main(int argc, char** argv) {\n"
                "  g_omr14_lab_raw_mode = (argc > 1 && argv[1][0] == '-' &&\n"
                "      (argv[1][1] == 'c' || argv[1][1] == 'd'));\n"
                "  console_progress::Begin();")

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
    if source.count(INERT_ANCHOR) != 1 or source.count(INERT_OLD) != 3:
        raise ValueError("Unexpected metadata-inert function bodies")
    for func in ("AuthorBlockInert", "MetablockInert", "TimestampProgressInert"):
        body_anchor = "static inline bool " + func + "() {\n" + INERT_OLD
        if source.count(body_anchor) != 1:
            raise ValueError("Unexpected metadata-inert function: " + func)
    if source.count(MAIN_ANCHOR) != 1:
        raise ValueError("Unexpected main entry")
    if "OMR14_RAW_CODER" in source:
        raise ValueError("This source was previously patched")
    changed=(LAB_HEAD+source.replace(OLD_PARSER,NEW_PARSER,1)
             .replace(OLD_BRANCH,NEW_BRANCH,1)
             .replace(OLD_HELPER,NEW_HELPER,1)
             .replace(INERT_ANCHOR,LAB_GLOBAL+INERT_ANCHOR,1)
             .replace(INERT_OLD,INERT_NEW,3)
             .replace(MAIN_ANCHOR,MAIN_REPLACE,1))
    if changed.count("OMR14_RAW_CODER")!=3 or changed.count(INERT_NEW)!=3:
        raise RuntimeError("Unexpected patch output")
    return changed

def modify_gate_source(source: str) -> str:
    if "OMR14_LAB_GATE" in source or source.count(GATE_ANCHOR) != 1:
        raise ValueError("Unsafe upstream gate source or repeated patch")
    return source.replace(GATE_ANCHOR, GATE_REPLACEMENT, 1)

def git(checkout:Path,*args:str)->str:
    return subprocess.check_output(["git",*args],cwd=checkout,text=True).strip()

def patch_checkout(checkout:Path,out:Path):
    checkout=checkout.resolve()
    found=git(checkout,"rev-parse","HEAD")
    if found!=UPSTREAM_COMMIT:
        raise RuntimeError(f"Unsafe revision {found}")
    source=checkout/RUNNER
    gate=checkout/GATE
    before_blob=git(checkout,"hash-object",str(source))
    gate_before_blob=git(checkout,"hash-object",str(gate))
    if before_blob!=RUNNER_BLOB:
        raise RuntimeError(f"Unsafe upstream runner blob {before_blob}")
    if gate_before_blob!=GATE_BLOB:
        raise RuntimeError(f"Unsafe upstream transformer gate blob {gate_before_blob}")
    new_runner=modify_source(source.read_text(encoding="utf8"))
    new_gate=modify_gate_source(gate.read_text(encoding="utf8"))
    source.write_text(new_runner,encoding="utf8")
    gate.write_text(new_gate,encoding="utf8")
    after_blob=git(checkout,"hash-object",str(source))
    gate_after_blob=git(checkout,"hash-object",str(gate))
    record={
       "project":"OMÉGA-R v0.14 experimental raw core coder",
       "upstream":"https://github.com/marwoelk/cmix-neif-2.0",
       "license":"GPL-3.0",
       "head_commit":found,
       "runner_original_git_blob":before_blob,
       "runner_patched_git_blob":after_blob,
       "gate_original_git_blob":gate_before_blob,
       "gate_patched_git_blob":gate_after_blob,
       "changed_files":[str(RUNNER),str(GATE)],
       "change_scope":"lab-only -c/-d, skip enwik9-specific metadata and gate initialization; keep Transformer+SEMCACHE, no score claimed",
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
