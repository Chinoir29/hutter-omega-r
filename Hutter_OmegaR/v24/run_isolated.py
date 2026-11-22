#!/usr/bin/env python3
"""Run ONLY one experimental prefix archive in a fresh directory with no corpus.

Proves (or refutes) independent extraction and decoding of a *preprocessed*
prefix, not enwik9 decompression. Does not send payloads to logs or to GitHub.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

EXPECTED_SHA256 = "1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf"
EXPECTED_BYTES = 524_288


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_isolated(archive: Path, work: Path, report_path: Path, *,
                    expected_sha: str = EXPECTED_SHA256, expected_size: int = EXPECTED_BYTES,
                    timeout: int = 900) -> dict:
    if not archive.is_file() or not os.access(archive, os.X_OK):
        raise ValueError("ARCHIVE_MISSING_OR_NOT_EXECUTABLE")
    if work.exists():
        raise ValueError("REFUSE_EXISTING_WORK_DIRECTORY")
    if expected_size < 1 or len(expected_sha) != 64:
        raise ValueError("BAD_EXPECTATION")
    if report_path.resolve().is_relative_to(work.resolve()):
        raise ValueError("REPORT_MUST_BE_OUTSIDE_ISOLATION")
    work.mkdir(parents=True)
    local_archive = work / "archive9"
    shutil.copyfile(archive, local_archive)
    local_archive.chmod(0o755)
    at_start = sorted(p.name for p in work.iterdir())
    if at_start != ["archive9"]:
        raise AssertionError("EXTERNAL_DATA_IN_DECODER_WORKDIR")
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(work),
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
    }
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(["./archive9"], cwd=work, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=timeout)
        code = proc.returncode
        error_excerpt = proc.stderr.decode("utf-8", errors="replace")[-1800:]
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        code = 124
        error_excerpt = (exc.stderr or b"").decode("utf-8", errors="replace")[-1800:]
    restored = work / "omr24-decoded-prefix.bin"
    result = {
        "status": "ISOLATED_PREFIX_ROUNDTRIP_FAILED",
        "experiment": "zero-argument executable alone in new working directory",
        "started_files": at_start,
        "command": "./archive9",
        "inherited_environment": "minimal PATH/HOME/locale only, no prefix env variable",
        "archive_sha256": sha256(local_archive),
        "archive_bytes": local_archive.stat().st_size,
        "returncode": code,
        "timed_out": timed_out,
        "wall_seconds": round(time.monotonic() - started, 3),
        "expected_decoded_bytes": expected_size,
        "expected_decoded_sha256": expected_sha,
        "actual_decoded_bytes": restored.stat().st_size if restored.is_file() else None,
        "actual_decoded_sha256": sha256(restored) if restored.is_file() else None,
        "error_excerpt": error_excerpt if code != 0 else None,
        "whole_enwik9_restored": False,
        "hutter_score_S": None,
        "official_validation": False,
    }
    if (code == 0 and restored.is_file()
            and restored.stat().st_size == expected_size and sha256(restored) == expected_sha):
        result["status"] = "INDEPENDENT_ZERO_ARG_PRECODER_PREFIX_RESTORED"
    report_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--expected-sha", default=EXPECTED_SHA256)
    ap.add_argument("--expected-size", type=int, default=EXPECTED_BYTES)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    result = verify_isolated(args.archive, args.work, args.report,
                             expected_sha=args.expected_sha, expected_size=args.expected_size,
                             timeout=args.timeout)
    # Compact output: never write binary content or raw Wikipedia bytes.
    print(json.dumps(result, indent=2))
    if result["status"] != "INDEPENDENT_ZERO_ARG_PRECODER_PREFIX_RESTORED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
