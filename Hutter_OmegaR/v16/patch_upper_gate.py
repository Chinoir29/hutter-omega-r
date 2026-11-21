#!/usr/bin/env python3
"""Pin exact upstream and modify only SEMCACHE lookup threshold (lab only).

This code applies a source patch to GPL-3.0 source already fetched from the
copyright holder. No copies of upstream code/weights are distributed here.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'v13'))
import semantic_cache_gate_patch as base

ALLOWED = (990, 995, 999)


def modify_source(source: str, threshold: int) -> str:
    if type(threshold) is not int or threshold not in ALLOWED:
        raise ValueError('Only 990, 995, 999 are permitted')
    if len(list(base.SOURCE_RX.finditer(source))) != 1:
        raise ValueError('Expected a unique upstream kQpE3=990 declaration')
    if source.count('constexpr int kSpE3 = 950;') != 1:
        raise ValueError('Unexpected storage confidence threshold')
    if source.count('constexpr int kCalqE3 = 900;') != 1:
        raise ValueError('Unexpected centering threshold')
    if threshold == 990:
        return source
    result = base.SOURCE_RX.sub(lambda m: m.group(1)+str(threshold)+m.group(2), source)
    if result == source or result.count('constexpr int kQpE3') != 1:
        raise RuntimeError('Unexpected rewrite')
    return result


def patch_checkout(checkout: Path, threshold: int, out: Path) -> dict:
    checkout=checkout.resolve()
    commit=base.git('rev-parse','HEAD',cwd=checkout)
    if commit != base.BASE_COMMIT:
        raise RuntimeError('Wrong upstream commit')
    file=checkout/base.RELATIVE_SOURCE
    sha=base.git('hash-object',str(file),cwd=checkout)
    if sha != base.BASE_BLOB:
        raise RuntimeError('Unexpected upstream blob')
    changed=modify_source(file.read_text(encoding='utf-8'),threshold)
    file.write_text(changed,encoding='utf-8')
    newsha=base.git('hash-object',str(file),cwd=checkout)
    if (newsha==sha) != (threshold==990):
        raise RuntimeError('Patch invariants not met')
    record={
        'experiment':'OMR16 controlled upper SEMCACHE lookup threshold',
        'source_repository':'https://github.com/marwoelk/cmix-neif-2.0',
        'license':'GPL-3.0',
        'upstream_commit':commit,
        'original_blob':sha,
        'modified_blob':newsha,
        'threshold_qpe3':threshold,
        'changed_source_files':([] if threshold==990 else [str(base.RELATIVE_SOURCE)]),
        'lab_only':True,
        'official_enwik9_score':None,
        'prize_submission':False,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkout',type=Path,required=True)
    p.add_argument('--qpe3',type=int,choices=ALLOWED,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(patch_checkout(a.checkout,a.qpe3,a.report),indent=2))

if __name__=='__main__':
    main()
