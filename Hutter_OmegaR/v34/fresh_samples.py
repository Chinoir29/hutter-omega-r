#!/usr/bin/env python3
"""OMÉGA-R v0.34: five independent, reversible raw enwik9 holdouts.
The samples are *not* the competition archive and have no official score.
Copyright 2026 OMÉGA-R. SPDX-License-Identifier: MIT.
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

OFFSETS_MIB = (64, 160, 448, 704, 896)
RAW_BYTES = 65536


def prepare(enwik9: Path, header: Path, out: Path, report: Path):
    head = header.read_bytes()
    if git_blob_sha(head) != VOCAB_GIT_BLOB:
        raise ValueError("Frozen 208-symbol vocabulary mismatch")
    bitmap = parse_bitmap(head)
    if enwik9.stat().st_size != ENWIK9_BYTES or file_sha(enwik9) != ENWIK9_SHA:
        raise ValueError("Official enwik9 SHA256/byte count mismatch")
    out.mkdir(parents=True, exist_ok=True)
    samples = []
    for offset in OFFSETS_MIB:
        with enwik9.open("rb") as stream:
            stream.seek(offset * 1048576)
            raw = stream.read(RAW_BYTES)
        if len(raw) != RAW_BYTES:
            raise AssertionError("Short holdout")
        coded = encode(raw, bitmap)
        if decode(coded, bitmap) != raw:
            raise AssertionError("Nonreversible input transform")
        file = out / f"escaped_{offset}MiB.dat"
        file.write_bytes(coded)
        samples.append({
            "offset_mib": offset,
            "raw_bytes": len(raw),
            "raw_sha256": sha(raw),
            "encoded_bytes": len(coded),
            "encoded_sha256": sha(coded),
            "escape_pairs": len(coded) - len(raw),
            "file": file.name,
            "lossless_codec_verified": True
        })
    manifest = {
        "project": "OMEGA-R v0.34 prospective held-out windows",
        "source_bytes": ENWIK9_BYTES,
        "source_sha256": ENWIK9_SHA,
        "upstream_commit": UPSTREAM_SHA,
        "upstream_vocab_git_blob": VOCAB_GIT_BLOB,
        "offsets_mib": list(OFFSETS_MIB),
        "lossy_projection": False,
        "contest_coding_path": False,
        "original_enwik9_not_compressed_in_full": True,
        "hutter_score": None,
        "samples": samples
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser()
    for x in ("enwik9", "vocab-header", "out-dir", "report"):
        p.add_argument("--" + x, type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        assert len(OFFSETS_MIB) == len(set(OFFSETS_MIB)) == 5
        assert max(OFFSETS_MIB) * 1048576 + RAW_BYTES < ENWIK9_BYTES
        assert set(OFFSETS_MIB).isdisjoint({32,96,192,256,384,640})
        print("V34_HOLDOUT_METADATA_SELF_TEST_PASS")
        return
    if not all((args.enwik9, args.vocab_header, args.out_dir, args.report)):
        p.error("Required: --enwik9 --vocab-header --out-dir --report")
    result = prepare(args.enwik9, args.vocab_header, args.out_dir, args.report)
    print(json.dumps({"sample_count":len(result["samples"]),
                       "official_score":result["hutter_score"],
                       "offsets_mib":result["offsets_mib"]},indent=2))


if __name__ == "__main__": main()
