#!/usr/bin/env python3
"""OMÉGA-R v0.35: prospectively fixed, fresh, losslessly-escaped enwik9 windows.

This is not the contest preprocessor or a Hutter score. Original corpus is not
redistributed. MIT license applies to this glue only; cmix-neif is GPL-3.0.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v17"))
from reversible_sample import (
    UPSTREAM_SHA, VOCAB_GIT_BLOB, ENWIK9_SHA, ENWIK9_BYTES,
    encode, decode, file_sha, git_blob_sha, parse_bitmap, sha,
)

OFFSETS_MIB = (48, 224, 512, 752, 928)
BYTES = 65536
PREVIOUS_OFFSETS = {0,32,64,96,128,160,192,256,320,384,448,640,704,872,896}


def prepare(corpus: Path, vocab: Path, output: Path, manifest: Path):
    head=vocab.read_bytes()
    if git_blob_sha(head)!=VOCAB_GIT_BLOB:
        raise ValueError("Wrong pinned vocabulary")
    bitmap=parse_bitmap(head)
    if corpus.stat().st_size!=ENWIK9_BYTES or file_sha(corpus)!=ENWIK9_SHA:
        raise ValueError("Not verified original enwik9")
    output.mkdir(parents=True,exist_ok=True)
    samples=[]
    for offset in OFFSETS_MIB:
        with corpus.open("rb") as f:
            f.seek(offset*1048576)
            raw=f.read(BYTES)
        if len(raw)!=BYTES:raise ValueError("Truncated window")
        coded=encode(raw,bitmap)
        if decode(coded,bitmap)!=raw:
            raise AssertionError("Lossless transform failed")
        path=output/f"escaped_{offset}MiB.dat"
        path.write_bytes(coded)
        samples.append({
            "offset_mib":offset,
            "raw_bytes":BYTES,
            "raw_sha256":sha(raw),
            "encoded_bytes":len(coded),
            "encoded_sha256":sha(coded),
            "file":path.name,
            "lossless_codec_verified":True
        })
    r={
        "project":"OMEGA-R v0.35 store-retention A/B",
        "source_sha256":ENWIK9_SHA,
        "source_bytes":ENWIK9_BYTES,
        "upstream_commit":UPSTREAM_SHA,
        "upstream_vocab_git_blob":VOCAB_GIT_BLOB,
        "offsets_mib":list(OFFSETS_MIB),
        "raw_bytes_per_sample":BYTES,
        "lossy_projection":False,
        "contest_coding_path":False,
        "hutter_prize_score":None,
        "samples":samples
    }
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    return r


def self_test():
    assert len(set(OFFSETS_MIB))==5
    assert not (set(OFFSETS_MIB)&PREVIOUS_OFFSETS)
    assert max(OFFSETS_MIB)*1048576+BYTES<ENWIK9_BYTES
    print("V035_PROSPECTIVE_OFFSETS_OK",OFFSETS_MIB)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    for x in ("enwik9","vocab-header","out-dir","report"):
        p.add_argument("--"+x,type=Path)
    a=p.parse_args()
    if a.self_test:
        self_test();return
    if not all((a.enwik9,a.vocab_header,a.out_dir,a.report)):
        p.error("Provide --enwik9 --vocab-header --out-dir --report")
    r=prepare(a.enwik9,a.vocab_header,a.out_dir,a.report)
    print("V035_AUTHENTIC_SAMPLES_READY",len(r["samples"]))


if __name__=="__main__":main()
