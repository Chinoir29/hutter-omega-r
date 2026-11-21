#!/usr/bin/env python3
"""Summarise STRICTLY the paired, lossless, nonofficial SEMCACHE lab streams."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

THRESHOLDS = (990, 980, 970)
SAMPLE_SHA = "c7fdfc7a3f1249269ec25541155b50a88ce8fcb06643198074cb06fd61daa604"
BASELINE_STREAM_SHA = "837f350ac4a4a4f046e1b9eac35956f34548d61db3d8f489fdd17d702e2bc3fe"
BASELINE_BYTES = 20533
UPSTREAM = "35d1957a5074db802fc134126afc77b76d931761"


def summarize(data: dict[int, dict]) -> dict:
    if sorted(data) != sorted(THRESHOLDS):
        raise ValueError("All three thresholds must be present")
    results = []
    for q in THRESHOLDS:
        d = data[q]
        b = d["coder_report"]
        p = d["patch"]
        g = d["lab_patch"]
        if p.get("baseline_revision") != UPSTREAM or g.get("head_commit") != UPSTREAM:
            raise ValueError(f"source revision mismatch at {q}")
        if p.get("threshold_qpe3") != q:
            raise ValueError(f"source threshold mismatch at {q}")
        if sorted(g.get("changed_files", [])) != ["src/runner.cpp", "src/tf1/tf1_gate.cpp"]:
            raise ValueError(f"laboratory patch mismatch at {q}")
        if not (b.get("status") == "verified_roundtrip"
                and b.get("lossless_roundtrip_verified") is True
                and b.get("source_sha256") == SAMPLE_SHA
                and b.get("source_bytes") == 65536
                and b.get("self_extracting_archive") is False
                and b.get("hutter_score_bytes") is None):
            raise ValueError(f"noncomparable or nonlossless laboratory data at {q}")
        result = {
            "threshold_qpe3": q,
            "source_sha256": b["source_sha256"],
            "lab_coder_bytes": b["lab_coder_bytes"],
            "lab_coder_sha256": b["lab_coder_sha256"],
            "unpacked_program_bytes": b["unpacked_program_bytes"],
            "unpacked_program_sha256": b["unpacked_program_sha256"],
            "compression": b["compression"],
            "decompression": b["decompression"],
            "roundtrip_sha256_verified": True,
            "source_patch_blob": p["result_blob"],
            "runner_patch_blob": g["runner_patched_git_blob"],
            "gate_patch_blob": g["gate_patched_git_blob"]
        }
        if type(result["lab_coder_bytes"]) is not int or result["lab_coder_bytes"] <= 0:
            raise ValueError("invalid raw stream bytes")
        results.append(result)

    baseline = results[0]
    for r in results:
        r["delta_stream_bytes_vs_control"] = r["lab_coder_bytes"] - baseline["lab_coder_bytes"]
        r["delta_unpacked_program_bytes_vs_control"] = (
            r["unpacked_program_bytes"] - baseline["unpacked_program_bytes"]
        )
        r["stream_differs_from_control"] = (
            r["lab_coder_sha256"] != baseline["lab_coder_sha256"]
        )
    return {
        "project": "OMÉGA-R v0.15 laboratory SEMCACHE gate A/B",
        "status": "all_three_lossless_roundtrips_verified",
        "source": "lossily projected 65,536 bytes of canonical enwik9 prefix",
        "source_is_lossy_projection": True,
        "source_sha256": SAMPLE_SHA,
        "sample_bytes": 65536,
        "upstream_commit": UPSTREAM,
        "baseline_reproduces_v0143_stream": (
            baseline["lab_coder_sha256"] == BASELINE_STREAM_SHA
            and baseline["lab_coder_bytes"] == BASELINE_BYTES
        ),
        "results": results,
        "observed_threshold_effect": any(r["stream_differs_from_control"] for r in results[1:]),
        "hutter_prize_score": None,
        "full_enwik9_tested": False,
        "self_extracting_archive_tested": False,
        "committee_verified": False,
        "competition_submission_sent": False,
        "interpretation": "Only the arithmetic-coded *research stream* may be compared; no full enwik9 or Hutter Prize claims."
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reports", type=Path, required=True)
    args = p.parse_args()
    d = {}
    for q in THRESHOLDS:
        folder = args.reports / f"q{q}"
        d[q] = {
            "coder_report": json.loads((folder/"coder_report.json").read_text()),
            "patch": json.loads((folder/"semcache_patch.json").read_text()),
            "lab_patch": json.loads((folder/"lab_patch.json").read_text())
        }
    result = summarize(d)
    path = args.reports / "comparison.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
