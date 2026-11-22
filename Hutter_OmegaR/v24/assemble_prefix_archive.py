#!/usr/bin/env python3
"""OMÉGA-R v0.24: assemble the EXACT upstream prefix-archive container layout.

For a research prefix ONLY: [decoder stub][TF weights][coded prefix][2 x int32].
The resulting executable is ephemeral and cannot restore all enwik9.
GPL-3.0-only upstream binary/weights are not copied to the GitHub repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

TRAILER = struct.Struct("<ii")  # upstream ArchivKopf on Ubuntu x86-64
WEIGHTS = "weights-poc8m_w2048_tf2t3_pruned_v5k_np2.c5"
PREFIX_CODED_BYTES = 158_153
PREFIX_CODED_SHA256 = "836a7f6eb3b439f3f682fe8c16252d5a10d44fcbabfdc053f0053ec217baa0d3"
WEIGHTS_UPSTREAM_SIZE = 3_744_629


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def append_file(out, path: Path) -> int:
    total = 0
    with path.open("rb") as source:
        while part := source.read(1 << 20):
            out.write(part)
            total += len(part)
    return total


def assemble(stub: Path, weights: Path, coded: Path, dest: Path,
             *, verify_coded_reference: bool = True) -> dict:
    inputs = [stub, weights, coded]
    for p in inputs:
        if not p.is_file() or not p.stat().st_size:
            raise ValueError("MISSING_ARCHIVE_COMPONENT_" + str(p.name))
    if len({p.resolve() for p in inputs}) != 3 or dest.exists():
        raise ValueError("DUPLICATE_COMPONENT_OR_OUTPUT_EXISTS")
    with stub.open("rb") as f:
        if f.read(4) != b"\x7fELF":
            raise ValueError("NOT_AN_ELF_DECODER_STUB")
    if weights.stat().st_size != WEIGHTS_UPSTREAM_SIZE:
        raise ValueError("WEIGHTS_SIZE_NOT_UPSTREAM")
    if verify_coded_reference and (
        coded.stat().st_size != PREFIX_CODED_BYTES or
        sha256(coded) != PREFIX_CODED_SHA256
    ):
        raise ValueError("PREPROCESSED_PREFIX_CODER_REFERENCE_MISMATCH")
    if dest.resolve() in {p.resolve() for p in inputs}:
        raise ValueError("OUTPUT_ALIASES_INPUT")
    if not all(p.stat().st_size < 2**31 for p in (weights, coded)):
        raise ValueError("TRAILER_INT32_OVERFLOW")
    try:
        with dest.open("xb") as out:
            sizes = [append_file(out, p) for p in inputs]
            out.write(TRAILER.pack(sizes[2], sizes[1]))
    except BaseException:
        dest.unlink(missing_ok=True)
        raise
    dest.chmod(0o755)
    total = dest.stat().st_size
    expected = sum(sizes) + TRAILER.size
    if total != expected:
        raise AssertionError("ARCHIVE_SIZE_ACCOUNTING_FAILURE")
    with dest.open("rb") as f:
        f.seek(-TRAILER.size, 2)
        if TRAILER.unpack(f.read(TRAILER.size)) != (sizes[2], sizes[1]):
            raise AssertionError("INVALID_ARCHIVE_TRAILER")
    record = {
        "status": "EXPERIMENTAL_PREFIX_ARCHIVE_BUILT_NOT_YET_EXECUTED",
        "archive_bytes": total,
        "archive_sha256": sha256(dest),
        "decoder_stub_bytes": sizes[0],
        "embedded_weights_bytes": sizes[1],
        "arithmetic_prefix_bytes": sizes[2],
        "trailer_bytes": TRAILER.size,
        "arithmetic_prefix_sha256": sha256(coded),
        "embedded_weights_sha256": sha256(weights),
        "decoder_stub_sha256": sha256(stub),
        "no_external_sidecars_required_by_container_format": True,
        "whole_enwik9_restored": False,
        "official_score_S": None,
        "license": "Experiment uses upstream GPL-3.0-only decoder/weights; neither artifact nor bytes redistributed",
    }
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", type=Path, required=True, help="the original encoder working directory")
    ap.add_argument("--out", type=Path, required=True, help="isolated target path; must not exist")
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    r = assemble(args.dir / ".decomp_bin", args.dir / WEIGHTS,
                 args.dir / "omr21-coded-prefix.bin", args.out)
    args.report.write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
