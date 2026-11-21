#!/usr/bin/env python3
"""OMÉGA-R v0.19: source-pinned instrumentation of the *real* pre-coder stream.

This is a measurement instrument, not a modified Hutter Prize submission.
It stops after all -e preprocessing and before arithmetic coding and does
not create archive9. It never publishes the corpus or the upstream GPL source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

UPSTREAM_SHA = "35d1957a5074db802fc134126afc77b76d931761"
RUNNER_BLOB = "4f9ee4adfeef37069eecf95bf8efb4c0d03cf09b"
ORIGINAL = '''  if (!text_start::Pack(temp_path, !MetablockInert(), !enable_preprocess)) {
    msg_note(536);
    return false;
  }
'''
INSTRUMENT = '''
  // OMEGA-R research probe. Only in separate scratch copy of upstream.
  // Exits before Predictor and Compress: no official archive is produced.
  if (std::getenv("OMR19_PROBE_PRODUCTION_STREAM") != nullptr) {
    if (input_path != ".ready4cmix" || output_path != "archive9" ||
        !enable_preprocess || dictionary == NULL) {
      std::fprintf(stderr, "OMR19_BAD_ROUTE: requires canonical -e path\\n");
      std::exit(182);
    }
    std::fprintf(stderr, "OMR19_REAL_CODER_INPUT=%s\\n", temp_path.c_str());
    std::fflush(stderr);
    std::exit(0);
  }
'''


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(4 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def transform_runner(original: bytes) -> bytes:
    if git_blob(original) != RUNNER_BLOB:
        raise ValueError("UPSTREAM_RUNNER_BLOB_DRIFT")
    needle = ORIGINAL.encode('utf-8')
    if original.count(needle) != 1:
        raise ValueError("PREPROCESS_BOUNDARY_NOT_UNIQUE")
    if original.count(b'if (!text_start::Pack(') != 1:
        raise ValueError("PREPROCESS_PACK_NOT_UNIQUE")
    return original.replace(needle, needle + INSTRUMENT.encode('utf-8'), 1)


def prepare(root: Path, output: Path) -> dict:
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != UPSTREAM_SHA:
        raise ValueError('UNPINNED_UPSTREAM_COMMIT ' + head)
    if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip():
        raise ValueError('UNSAFE_DIRTY_UPSTREAM')
    code = (root / 'src/runner.cpp').read_bytes()
    changed = transform_runner(code)
    if output.exists():
        raise ValueError('OUTPUT_EXISTS_NEVER_OVERWRITE')
    if root.resolve() == output.resolve() or output.resolve().is_relative_to(root.resolve()):
        raise ValueError('DO_NOT_NEST_OUTPUT_WITHIN_UPSTREAM')
    shutil.copytree(root, output, ignore=shutil.ignore_patterns('.git', '.build', 'comp9', 'run', '__pycache__'))
    (output / 'src/runner.cpp').write_bytes(changed)
    if (output / 'src/runner.cpp').read_bytes() != changed:
        raise AssertionError('PATCH_NOT_WRITTEN')
    license_ = output / 'LICENSE'
    if not license_.is_file() or b'GNU GENERAL PUBLIC LICENSE' not in license_.read_bytes():
        raise ValueError('UPSTREAM_GPL3_NOT_PRESERVED')
    evidence = {
        'status': 'PRODUCTION_STREAM_INSTRUMENTED_NOT_YET_EXECUTED',
        'upstream_commit': head,
        'upstream_runner_git_blob': git_blob(code),
        'instrumented_runner_sha256': hashlib.sha256(changed).hexdigest(),
        'code_inserted_after': 'text_start::Pack',
        'code_inserted_before': 'Predictor p(vocab); Compress(...)',
        'requires_canonical_minus_e_path': True,
        'no_admissible_archive_created': True,
        'licence': 'Upstream GPL-3.0 notices preserved only in ephemeral checkout',
    }
    (output.parent / 'omr19_probe_preflight.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return evidence


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(prepare(args.upstream, args.output), indent=2))


if __name__ == '__main__':
    main()
