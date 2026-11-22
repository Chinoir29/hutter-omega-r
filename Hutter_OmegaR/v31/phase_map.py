#!/usr/bin/env python3
"""OMÉGA-R v0.31: locate page-phase boundaries on TRUE production pre-coder bytes.

Corpus source: pinned public enwik9. Uses the exact kAnker byte pattern from
the pinned upstream GPL header src/text_start_pack.h. Emits ONLY counts,
offsets, checksums and budget proposals, never text/data snippets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mmap
from pathlib import Path

STREAM_BYTES = 501_062_281
STREAM_SHA256 = "c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718"
ANCHOR = bytes([0x20,0x20,0x4c,0x2f,0xdf,0x98,0x4e,0x0a])
CHUNK_BYTES = 8 * 1024 * 1024
UPSTREAM_COMMIT = "35d1957a5074db802fc134126afc77b76d931761"


def sha256file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()


def scan_file(path: Path, *, expected_size: int | None = STREAM_BYTES,
              expected_sha256: str | None = STREAM_SHA256,
              chunk_bytes: int = CHUNK_BYTES) -> dict:
    if chunk_bytes <= len(ANCHOR):
        raise ValueError("CHUNK_MUST_EXCEED_ANCHOR")
    if not path.is_file():
        raise ValueError("NO_PRECODER_STREAM")
    n = path.stat().st_size
    if n == 0 or (expected_size is not None and n != expected_size):
        raise ValueError("PRECODER_STREAM_WRONG_SIZE")
    sha = sha256file(path)
    if expected_sha256 is not None and sha != expected_sha256:
        raise ValueError("PRECODER_STREAM_SHA256_MISMATCH")

    k = (n + chunk_bytes - 1)//chunk_bytes
    count = [0] * k
    first = []
    last = []
    total = 0
    last_offset = -1
    with path.open('rb') as stream:
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            p = 0
            while True:
                match = data.find(ANCHOR, p)
                if match == -1:
                    break
                total += 1
                count[match // chunk_bytes] += 1
                if len(first) < 10:
                    first.append(match)
                if len(last) == 10:
                    last.pop(0)
                last.append(match)
                last_offset = match
                p = match + len(ANCHOR)
    first_offset = first[0] if first else None
    # All region distinctions are grounded in the measured *page marker*,
    # not speculation that the marker itself exactly ends the meta block.
    chunks = [
        {
            "index": i,
            "start_byte": i * chunk_bytes,
            "end_byte_exclusive": min(n, (i + 1) * chunk_bytes),
            "page_anchors": cnt,
        } for i,cnt in enumerate(count)
    ]
    first_page_region = first_offset // chunk_bytes if first_offset is not None else None
    dense = sorted(range(k), key=lambda i: (-count[i],i))[:5]
    proposals = {
        "original_start": {"start":0,"length":min(n, 524288),
                           "warning":"historical v0.25-v0.30 tested this only"},
        "first_page_context": {
            "start":max(0,(first_offset or 0)-1024) if first_offset is not None else None,
            "length": min(8*1024*1024,n-(first_offset or 0)) if first_offset is not None else None,
            "requires_carrying_all_prior_predictor_history":True,
        },
        "central": {"start":(n//2)//chunk_bytes*chunk_bytes,
                    "length":min(chunk_bytes,n-((n//2)//chunk_bytes*chunk_bytes)),
                    "requires_carrying_all_prior_predictor_history":True},
        "high_anchor_density_8MiB_windows":dense,
    }
    result = {
        "status":"ACTUAL_PRECODER_PHASE_MAP_NOT_CMIX_COMPRESSED",
        "source_git_commit":UPSTREAM_COMMIT,
        "marker_from_upstream":"src/text_start_pack.h kAnker (8 source-code bytes)",
        "stream_bytes":n,
        "stream_sha256":sha,
        "chunk_bytes":chunk_bytes,
        "total_exact_page_markers":total,
        "first_ten_marker_offsets":first,
        "last_ten_marker_offsets":last,
        "first_marker_offset":first_offset,
        "last_marker_offset":last_offset if total else None,
        "first_marker_chunk":first_page_region,
        "chunks":chunks,
        "study_proposals":proposals,
        "producer_creates_archive9":False,
        "official_Hutter_S":None,
        "whole_enwik9_reconstructed":False,
        "caution":"Marker is a frozen-byte page pattern, not a substitute for a fully parsed zone automaton."
    }
    assert sum(count) == total
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("--report",required=True,type=Path)
    args=parser.parse_args()
    out=scan_file(args.input)
    args.report.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="chunks"},indent=2))


if __name__=="__main__":
    main()
