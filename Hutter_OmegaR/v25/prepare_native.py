#!/usr/bin/env python3
"""OMÉGA-R v0.25: let the REAL comp9 -e path assemble its own partial archive9.

The upstream compressor's own native [decoder][weights][payload][trailer]
packaging logic is used; no Python-built archive enters this experiment.
Research-only 524288-byte PREPROCESSED prefix, NOT all 1GB enwik9.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v24"))
import prepare_selfextract as v24

TAG = '  if (std::getenv("OMR21_SHADOW_PREFIX_BYTES")) {\n    std::fprintf(stderr,"OMR21_PREFIX_ACTUAL_CODED_STREAM_BYTES='
REMOVE = '    if (std::rename(output_path.c_str(), "omr21-coded-prefix.bin") != 0) std::exit(184);'
EXIT = '    std::exit(0);'
PACKER = 'rename(temp_path.c_str(), "archive9")'


def promote_runner(v24_runner: bytes) -> bytes:
    txt = v24_runner.decode("utf-8")
    if txt.count(TAG) != 1 or txt.count(PACKER) != 1:
        raise ValueError("NATIVE_PRODUCTION_PACKER_OR_PROBE_NOT_UNIQUE")
    start = txt.index(TAG)
    if not txt.index("bool RunCompression(") < start < txt.index("bool RunDecompression("):
        raise ValueError("PROBE_NOT_IN_COMPRESSION_FUNCTION")
    end = txt.find("\n  }\n", start)
    if end < 0:
        raise ValueError("INCOMPLETE_PROBE_BLOCK")
    end += len("\n  }\n")
    block = txt[start:end]
    if block.count(REMOVE) != 1 or block.count(EXIT) != 1:
        raise ValueError("UNEXPECTED_PREFIX_EXIT_SHAPE")
    new_block = block.replace(REMOVE + "\n", "", 1).replace(EXIT, "    return true;", 1)
    if "fclose(temp_in); fclose(data_out);" not in new_block:
        raise ValueError("PREFIX_OUTPUT_NOT_FLUSHED")
    if 'setenv("OMR23_PREFIX_DECODE", "524288", 1)' not in txt:
        raise ValueError("ZERO_ARG_DECODE_REQUIRES_V24")
    result = txt[:start] + new_block + txt[end:]
    if REMOVE in result:
        raise AssertionError("OLD_EARLY_EXIT_STILL_PRESENT")
    if result.count(PACKER) != 1:
        raise AssertionError("NATIVE_PACKER_REMOVED")
    return result.encode("utf-8")


def prepare(upstream: Path, dest: Path) -> dict:
    audit = v24.prepare(upstream, dest)
    runner = dest / "src/runner.cpp"
    raw = runner.read_bytes()
    patched = promote_runner(raw)
    runner.write_bytes(patched)
    result = {
        "status": "NATIVE_PARTIAL_ARCHIVE_PRODUCTION_PATH_PREPARED_NOT_EXECUTED",
        "parent_v24_runner_sha256": hashlib.sha256(raw).hexdigest(),
        "v25_runner_sha256": hashlib.sha256(patched).hexdigest(),
        "upstream_commit": audit["upstream_commit"],
        "coded_input_limit_bytes": 524288,
        "native_comp9_assembles_archive9": True,
        "decoder_prefix_selfcontained_test": "requires real execution in new directory",
        "whole_enwik9_restored": False,
        "official_score_S": None,
        "upstream_GPL3_source_remains_ephemeral": True,
    }
    (dest.parent / "omr25-source-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(prepare(args.upstream, args.output), indent=2))
