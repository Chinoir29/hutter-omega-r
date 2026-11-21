#!/usr/bin/env python3
"""Offline audit of an OMÉGA-R enwik9 local benchmark report.

This checks the *internal consistency* of a report emitted by
Hutter_OmegaR/v6/verified_enwik9_run_v6.py. It cannot independently certify
that the remote run really happened, that the model is admissible, or that a
Hutter Prize committee has accepted it.

No network access or third-party dependencies are used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ENWIK9_SHA256 = "159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc"
AWARDED_SCORE_SNAPSHOT = 100_424_672
PENDING_SCORE_SNAPSHOT = 93_388_956
RAM_LIMIT_KIB = 10 * 1024 * 1024


def limit_for_one_percent(reference: int) -> int:
    """Integer ceiling for S <= 99% reference; exact integer arithmetic."""
    return reference * 99 // 100


def is_nonnegative_int(x: Any) -> bool:
    return type(x) is int and x >= 0


def classify(report: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    notes: list[str] = []
    good_input = report.get("verified_official_input") is True
    good_roundtrip = report.get("verified_full_roundtrip_sha256") is True

    if not good_input:
        issues.append("official_input_not_verified")
    if report.get("source_sha256") != ENWIK9_SHA256:
        issues.append("source_sha256_mismatch")
    if not good_roundtrip:
        issues.append("lossless_reconstruction_not_verified")
    if report.get("no_runtime_options_counted") is not True:
        issues.append("command_arguments_not_accounted_for")
    if report.get("organizer_verified") is True:
        issues.append("cannot_independently_confirm_organizer_verification")

    components = ("comp9_bytes", "archive9_bytes", "score_bytes_LOCAL_only")
    for k in components:
        if not is_nonnegative_int(report.get(k)):
            issues.append("missing_or_invalid_" + k)
    score = None
    if all(is_nonnegative_int(report.get(k)) for k in components):
        score = report["score_bytes_LOCAL_only"]
        if score != report["comp9_bytes"] + report["archive9_bytes"]:
            issues.append("score_does_not_equal_program_plus_archive")
        if report["comp9_bytes"] == 0 or report["archive9_bytes"] == 0:
            issues.append("empty_program_or_archive")

    resources: dict[str, dict[str, Any]] = {}
    cpus = []
    for phase in ("compression", "decompression"):
        entry = report.get(phase)
        if not isinstance(entry, dict):
            issues.append("missing_" + phase + "_measurements")
            continue
        rss = entry.get("max_rss_kib")
        wall = entry.get("reported_wall_seconds")
        core = entry.get("cpu_core")
        if not is_nonnegative_int(rss) or rss == 0:
            issues.append("invalid_" + phase + "_rss")
        if type(wall) not in (float, int) or wall <= 0:
            issues.append("invalid_" + phase + "_wall_time")
        if not is_nonnegative_int(core):
            issues.append("invalid_" + phase + "_cpu_core")
        else:
            cpus.append(core)
        resources[phase] = {"max_rss_kib": rss, "wall_seconds": wall, "cpu_core": core}
        if is_nonnegative_int(rss) and rss > RAM_LIMIT_KIB:
            issues.append(phase + "_rss_exceeds_10_gib")
    if len(cpus) == 2 and cpus[0] != cpus[1]:
        notes.append("different_affinity_cpu_id_between_phases")

    awarded_ceiling = limit_for_one_percent(AWARDED_SCORE_SNAPSHOT)
    pending_ceiling = limit_for_one_percent(PENDING_SCORE_SNAPSHOT)
    if score is not None and not issues:
        if score <= pending_ceiling:
            category = "MEETS_HISTORICAL_SCORE_THRESHOLDS_ONLY"
        elif score <= awarded_ceiling:
            category = "MEETS_AWARDED_THRESHOLD_ONLY"
        else:
            category = "NOT_COMPETITIVE_WITH_AWARDED_THRESHOLD"
    else:
        category = "INVALID_OR_UNVERIFIED_REPORT"

    notes.extend([
        "Committee rules, hardware-normalized time limit, exact disk usage, and standalone eligibility are NOT validated by this audit.",
        "Benchmarks and reference figures are dated 2026-11-21; verify up-to-date record before competition submission.",
        "This checks report claims only, not the corpus or archive bytes independently.",
    ])

    return {
        "audit_version": "OMÉGA-R report audit v0.9.1",
        "category": category,
        "report_internally_consistent": not issues,
        "issues": issues,
        "notes": notes,
        "historical_awarded_record_bytes": AWARDED_SCORE_SNAPSHOT,
        "historical_awarded_1pct_ceiling_bytes": awarded_ceiling,
        "historical_pending_candidate_bytes": PENDING_SCORE_SNAPSHOT,
        "historical_pending_1pct_ceiling_bytes": pending_ceiling,
        "local_score_bytes": score,
        "bytes_to_save_for_awarded_1pct_if_over": max(0,score-awarded_ceiling) if score is not None else None,
        "bytes_to_save_for_pending_1pct_if_over": max(0,score-pending_ceiling) if score is not None else None,
        "resources": resources,
        "committee_validated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="JSON from the official-input local benchmark, never an extract")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = json.loads(args.report.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        parser.error("expected a JSON object")
    audited = classify(data)
    output = json.dumps(audited, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if audited["report_internally_consistent"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
