#!/usr/bin/env python3
"""OMÉGA-R v0.24: instrument the pinned real coder for a zero-argument prefix archive.

Research-only proof of self-containment for 524288 PREPROCESSED bytes, NOT
restoration of enwik9 or an eligible Hutter Prize entry. Never republishes
third-party source; retains GPL-3.0-only notices in its temporary copy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v23"))
import prepare_roundtrip as v23

COMMIT = "35d1957a5074db802fc134126afc77b76d931761"
PREFIX = 524_288
# This is an exact, release-specific insertion point inside main(argc==1).
MAIN_ANCHOR = '    // run compression\n    input_path = ".ready4cmix_decomp";'
STOP_ANCHOR = '    split4Decomp();'
INTERNAL_LIMIT = '''    // OMR24 research: zero-argument archive9 uses a fixed pre-coder prefix cap.
    // Not an enwik9 decompressor. No externally supplied option or environment.
    if (setenv("OMR23_PREFIX_DECODE", "524288", 1) != 0) return Help();
'''
STOP_EARLY = '''    // OMR24: an independent archive9 run has decoded the genuine prefix.
    // Deliberately skip all whole-corpus postprocessing (unavailable on a prefix).
    if (rename("omr23-decoded-prefix.bin", "omr24-decoded-prefix.bin") != 0)
      return Help();
    if (getFileSize("omr24-decoded-prefix.bin") != 524288ULL) return Help();
    goto print_end_message;
'''


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def augment_runner(v23_runner: bytes) -> bytes:
    if b"OMR23_PREFIX_DECODE" not in v23_runner or b"omr23-decoded-prefix.bin" not in v23_runner:
        raise ValueError("V23_DECODE_INSTRUMENTATION_MISSING")
    text = v23_runner.decode("utf-8")
    for anchor, name in [(MAIN_ANCHOR, "SELF_EXTRACT_PREFIX"), (STOP_ANCHOR, "WHOLE_CORPUS_STOP")]:
        if text.count(anchor) != 1:
            raise ValueError(f"NON_UNIQUE_{name}_ANCHOR")
    text = text.replace(MAIN_ANCHOR, INTERNAL_LIMIT + MAIN_ANCHOR, 1)
    text = text.replace(STOP_ANCHOR, STOP_EARLY + STOP_ANCHOR, 1)
    if text.count('setenv("OMR23_PREFIX_DECODE", "524288", 1)') != 1:
        raise AssertionError("NOT_FIXED_INTERNAL_LENGTH")
    return text.encode("utf-8")


def prepare(upstream: Path, dest: Path) -> dict:
    head = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if head != COMMIT:
        raise ValueError(f"UPSTREAM_DRIFT_{head}")
    if subprocess.check_output(["git", "-C", str(upstream), "status", "--porcelain"], text=True).strip():
        raise ValueError("DIRTY_UPSTREAM_REFUSED")
    if dest.exists() or dest.resolve().is_relative_to(upstream.resolve()):
        raise ValueError("UNSAFE_DESTINATION")
    files = {p: (upstream / p).read_bytes() for p in v23.PINS}
    v23_changes = v23.transform(files)
    patched = augment_runner(v23_changes["src/runner.cpp"])
    shutil.copytree(upstream, dest, ignore=shutil.ignore_patterns(".git", ".build", "comp9", "run", "__pycache__"))
    (dest / "src/runner.cpp").write_bytes(patched)
    license_file = dest / "LICENSE"
    if b"GNU GENERAL PUBLIC LICENSE" not in license_file.read_bytes():
        raise ValueError("UPSTREAM_GPL_3_LICENSE_NOT_COPIED")
    for path in ("src/coder/encoder.cpp", "src/coder/decoder.cpp"):
        if git_blob((dest / path).read_bytes()) != v23.PINS[path]:
            raise AssertionError(f"CODEC_UPSTREAM_CHANGED_{path}")
    result = {
        "status": "V24_SOURCE_PREPARED_NOT_BUILT",
        "upstream_commit": head,
        "v23_runner_sha256": sha256(v23_changes["src/runner.cpp"]),
        "v24_runner_sha256": sha256(patched),
        "encoder_decoder_unmodified": True,
        "prefix_preprocessed_bytes": PREFIX,
        "decode_mode": "argc==1, internal prefix cap, no options, no corpus",
        "extraction_format": "[decoder prefix][weights][coded prefix][ArchivKopf]",
        "whole_enwik9_restored": False,
        "official_score_S": None,
        "license": "Modified executable derived from GPL-3.0-only, no binary distributed",
    }
    (dest.parent / "omr24-source-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(prepare(args.upstream, args.output), indent=2))


if __name__ == "__main__":
    main()
