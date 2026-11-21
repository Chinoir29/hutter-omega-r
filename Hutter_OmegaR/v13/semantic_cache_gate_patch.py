#!/usr/bin/env python3
"""Controlled one-parameter A/B patch for cmix-neif-2.0 (upstream GPL-3.0).

Requires a checkout at the exact published baseline commit, and refuses all
unknown source variants. Generates a traceable report. It does not claim a
compression gain or run a Hutter Prize benchmark.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE_COMMIT = '35d1957a5074db802fc134126afc77b76d931761'
BASE_BLOB = '20614538d3ff90906163a6bd9150894cbb7020f1'
RELATIVE_SOURCE = Path('src/semantic_cache.h')
SOURCE_RX = re.compile(r'(?m)^(constexpr int kQpE3\s*=\s*)990(\s*;\s*// look up below\s*)$')
ALLOWED = (970, 980, 990)


def modify_source(original: str, new_threshold: int) -> str:
    """Returns replacement with exactly one threshold edited; fails closed."""
    if type(new_threshold) is not int or new_threshold not in ALLOWED:
        raise ValueError('threshold must be precisely one of 970, 980, 990')
    matches = list(SOURCE_RX.finditer(original))
    if len(matches) != 1:
        raise ValueError(f'unexpected source: expected 1 kQpE3=990, found {len(matches)}')
    if not re.search(r'(?m)^constexpr int kSpE3\s*=\s*950\s*;', original):
        raise ValueError('source missing expected storage threshold kSpE3=950')
    if not re.search(r'(?m)^constexpr int kCalqE3\s*=\s*900\s*;', original):
        raise ValueError('source missing expected calibration threshold kCalqE3=900')
    if not (new_threshold >= 950 and new_threshold >= 900):
        raise ValueError('cannot break source invariant kSpE3/kCalqE3 <= kQpE3')
    if new_threshold == 990:
        return original
    result = SOURCE_RX.sub(lambda m: m.group(1) + str(new_threshold) + m.group(2), original)
    if result == original:
        raise RuntimeError('patch produced no change')
    if result.count('constexpr int kQpE3') != 1:
        raise RuntimeError('unexpected number of threshold declarations')
    return result


def git(*args: str, cwd: Path) -> str:
    r = subprocess.run(['git', *args], cwd=cwd, text=True,
                       capture_output=True, check=True)
    return r.stdout.strip()


def patch_checkout(checkout: Path, threshold: int, report: Path) -> dict:
    checkout = checkout.resolve()
    actual = git('rev-parse', 'HEAD', cwd=checkout)
    if actual != BASE_COMMIT:
        raise RuntimeError(f'revision mismatch: {actual} != {BASE_COMMIT}')
    path = checkout / RELATIVE_SOURCE
    actual_blob = git('hash-object', str(path), cwd=checkout)
    if actual_blob != BASE_BLOB:
        raise RuntimeError(f'blob mismatch: {actual_blob} != {BASE_BLOB}')
    original = path.read_text(encoding='utf-8')
    edited = modify_source(original, threshold)
    path.write_text(edited, encoding='utf-8')
    after_blob = git('hash-object', str(path), cwd=checkout)
    changed = threshold != 990
    if changed and after_blob == BASE_BLOB:
        raise RuntimeError('changed threshold but blob is identical')
    if not changed and after_blob != BASE_BLOB:
        raise RuntimeError('control unexpectedly changed source')
    result = {
        'project': 'OMÉGA-R v0.13 semantic cache gate ablation',
        'baseline_repo': 'https://github.com/marwoelk/cmix-neif-2.0',
        'upstream_license': 'GPL-3.0',
        'baseline_revision': BASE_COMMIT,
        'baseline_blob': BASE_BLOB,
        'result_blob': after_blob,
        'threshold_qpe3': threshold,
        'changed_source_files': [str(RELATIVE_SOURCE)] if changed else [],
        'comparison_required': True,
        'performance_measured': False,
        'lossless_roundtrip_verified': False,
        'hutter_prize_score': None,
        'claim': 'source patch only, not a compression improvement',
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--checkout', type=Path, required=True)
    ap.add_argument('--qpe3', type=int, choices=ALLOWED, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(patch_checkout(args.checkout, args.qpe3, args.report), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
