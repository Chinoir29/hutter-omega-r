#!/usr/bin/env python3
"""OMÉGA-R v0.18: fail-closed experiment on the *upstream competition route*.

No embedded corpus, weights, or third-party source. Requires a separately
obtained, pristine GPL-3.0 cmix-neif-2.0 checkout at the pinned commit.
Preparations are safe and cheap; --run-full explicitly invokes two full
competition-path runs and must only be used on sufficiently provisioned hardware.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

COMMIT = '35d1957a5074db802fc134126afc77b76d931761'
ENWIK9 = '159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
PINS = {
    'src/runner.cpp': '4f9ee4adfeef37069eecf95bf8efb4c0d03cf09b',
    'src/preprocess/dict_derive.cpp': 'd534e62caa6cf78245221b06d68e6a1ee31fd6fe',
    'src/preprocess/preprocessor.cpp': '13d886987d9057eb280a8a3f8fa5a535807c2ed6',
    'src/readalike_prepr/self_extract.h': 'beb208a5f8dd8abfe0b5411dba14136106e87f01',
    'src/semantic_cache.h': '20614538d3ff90906163a6bd9150894cbb7020f1',
    'src/vocab_frozen.h': 'da5ffe84fb7e3d9a5061b43da5970f7c9f728e19',
    'build.sh': '990e275c57c8e336f6fd950040d287fbaa8e3e71',
}
SEARCH = {
    'encoder_dict_derive': ('src/runner.cpp', 'dict_derive::BuildDictFromInput('),
    'encoder_preprocess': ('src/runner.cpp', 'preprocessor::Encode(data_in, temp_out, *input_bytes, dictionary);'),
    'encoder_arithmetic': ('src/runner.cpp', 'Compress(temp_bytes, temp_in, data_out, output_bytes, &p);'),
    'decoder_arithmetic': ('src/runner.cpp', 'Decompress(*output_bytes, data_in, temp_out, &p);'),
    'decoder_preprocess': ('src/runner.cpp', 'preprocessor::Decode(temp_in, data_out, dictionary);'),
    'decoder_dictionary_from_stream': ('src/runner.cpp', 'dict_article::DateiAusSlot()'),
    'decoder_self_extract': ('src/runner.cpp', 'selfextract_decomp()'),
    'source_weights_embedded': ('src/readalike_prepr/self_extract.h', 'header.weights_size'),
    'release_excludes_lab_c': ('src/runner.cpp', '// the package form has no -c'),
    'same_predictor_encode': ('src/runner.cpp', 'Predictor p(vocab);'),
}
THRESHOLD = 'constexpr int kQpE3 = 990;'


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def checked_checkout(src: Path) -> dict:
    """Reject drift and local edits. Do not trust a filename or branch name."""
    git = subprocess.run(['git', '-C', str(src), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    if git != COMMIT:
        raise ValueError('UPSTREAM_COMMIT_MISMATCH ' + git)
    status = subprocess.run(['git', '-C', str(src), 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout
    if status.strip():
        raise ValueError('UPSTREAM_DIRTY: refuse benchmark against modified input')
    for name, pin in PINS.items():
        actual = git_blob((src / name).read_bytes())
        if actual != pin:
            raise ValueError('BLOB_MISMATCH ' + name + ' ' + actual)
    if not (src / 'LICENSE').is_file() or 'GNU GENERAL PUBLIC LICENSE' not in (src / 'LICENSE').read_text(errors='replace'):
        raise ValueError('GPL_LICENSE_NOT_FOUND')
    if not list(src.glob('weights-*.c5')):
        raise ValueError('UPSTREAM_WEIGHTS_ABSENT: do not claim production build')
    checks = source_contract(src)
    return {'pinned_commit': git, 'blobs': PINS, 'source_contract': checks,
            'licence': 'upstream GPL-3.0; preserve upstream notices; no upstream files redistributed'}


def source_contract(src: Path) -> dict:
    for key, (path, needle) in SEARCH.items():
        text = (src / path).read_text(encoding='utf-8')
        if needle not in text:
            raise ValueError('PRODUCTION_ROUTE_CHANGED ' + key)
    header = (src / 'src/semantic_cache.h').read_text(encoding='utf-8')
    if header.count(THRESHOLD) != 1:
        raise ValueError('SEMCACHE_BASELINE_NOT_UNIQUE')
    runner = (src / 'src/runner.cpp').read_text(encoding='utf-8')
    if runner.count('Predictor p(vocab);') != 2:
        raise ValueError('ENCODE_DECODE_PREDICTOR_ASYMMETRY')
    e = runner.index("if (argv[1][1] == 'e') {")
    d = runner.index('if (argc == 1) {')
    if not d < e or 'dict_derive::BuildDictFromInput(' not in runner[e:]:
        raise ValueError('UPSTREAM_E_ROUTE_NOT_RECOGNIZED')
    return {key: True for key in SEARCH} | {'predictor_constructors': 2,
        'threshold_before': 990, 'competition_path_is_not_lab_c': True,
        'dictionary_derived_from_full_input': True,
        'archive_decode_output_name': 'enwik9_uncompressed'}


def create_pair(src: Path, work: Path) -> dict:
    if work.exists():
        raise ValueError('WORKDIR_ALREADY_EXISTS (never overwrite prior results)')
    record = checked_checkout(src)
    if work.resolve().is_relative_to(src.resolve()) or src.resolve().is_relative_to(work.resolve()):
        raise ValueError('WORKDIR_MUST_BE_SEPARATE')
    work.mkdir(parents=True)
    for mode in ('baseline', 'candidate'):
        shutil.copytree(src, work / mode, ignore=shutil.ignore_patterns('.git', '.build', 'comp9', 'run', '__pycache__'))
    original = (work / 'baseline/src/semantic_cache.h').read_bytes()
    patched = original.replace(THRESHOLD.encode(), b'constexpr int kQpE3 = 999;')
    if patched == original or patched.count(b'constexpr int kQpE3 = 999;') != 1:
        raise AssertionError('NOT_A_UNIQUE_SOURCE_PATCH')
    dest = work / 'candidate/src/semantic_cache.h'
    dest.write_bytes(patched)
    for mode in ('baseline', 'candidate'):
        if mode == 'baseline' and git_blob((work / mode / 'src/semantic_cache.h').read_bytes()) != PINS['src/semantic_cache.h']:
            raise AssertionError('BASELINE_CHANGED')
        if mode == 'candidate' and len(patched) != len(original):
            raise AssertionError('UNEXPECTED_BINARY_LENGTH_CHANGE_IN_SOURCE')
    record['experiment'] = {'baseline': 990, 'candidate': 999, 'changed_file': 'src/semantic_cache.h',
                            'candidate_source_sha256': hashlib.sha256(patched).hexdigest(),
                            'baseline_source_sha256': hashlib.sha256(original).hexdigest(),
                            'patch_scope': 'prediction; upstream -e/-d competition code unchanged',
                            'data_comparison': None, 'competition_score': None,
                            'status': 'SOURCE_PREPARED_NOT_BENCHMARKED'}
    (work / 'preflight.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def execute(binary: Path, cwd: Path, label: str, timeout: int, cpu: int | None) -> dict:
    """Serial one-core execution, logs stay local; no official calibration claim."""
    def one_core():
        if cpu is not None and hasattr(os, 'sched_setaffinity'):
            os.sched_setaffinity(0, {cpu})
    started = time.monotonic()
    with (cwd / f'{label}.stdout').open('wb') as out, (cwd / f'{label}.stderr').open('wb') as err:
        proc = subprocess.run([str(binary)], cwd=cwd, stdout=out, stderr=err,
                              timeout=timeout, preexec_fn=one_core if cpu is not None else None)
    if proc.returncode:
        raise RuntimeError(f'{label} failed returncode={proc.returncode}; see log in {cwd}')
    return {'wall_seconds': round(time.monotonic() - started, 3),
            'cpu_affinity': cpu, 'returncode': proc.returncode}


def build_pair(work: Path, seconds: int) -> list[dict]:
    rows = []
    for mode in ('baseline', 'candidate'):
        folder = work / mode
        started = time.monotonic()
        with (work / f'build_{mode}.stdout').open('wb') as out, (work / f'build_{mode}.stderr').open('wb') as err:
            proc = subprocess.run(['bash', 'build.sh'], cwd=folder, stdout=out, stderr=err, timeout=seconds)
        if proc.returncode:
            raise RuntimeError(f'PRODUCTION_BUILD_FAILED {mode}: {proc.returncode}')
        comp = (folder / 'comp9').resolve()
        if not comp.is_file() or not os.access(comp, os.X_OK):
            raise RuntimeError('FULL_COMP9_MISSING ' + mode)
        rows.append({'mode': mode, 'comp9_bytes': comp.stat().st_size,
                     'comp9_sha256': digest(comp),
                     'build_wall_seconds': round(time.monotonic() - started, 3)})
    return rows


def full_compare(work: Path, corpus: Path, seconds: int, builds: list[dict]) -> dict:
    if not corpus.is_file() or corpus.stat().st_size != 1_000_000_000 or digest(corpus) != ENWIK9:
        raise ValueError('CANONICAL_ENWIK9_REQUIRED')
    results = []
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else []
    cpu = affinity[0] if affinity else None
    for mode in ('baseline', 'candidate'):
        folder = work / mode
        # Use exclusively the two already-built, source-pinned production binaries.
        comp = (folder / 'comp9').resolve()
        run = (work / ('run_' + mode))
        run.mkdir()
        (run / 'enwik9').symlink_to(corpus.resolve())
        encode = execute(comp, run, 'encode', seconds, cpu)
        archive = run / 'archive9'
        if not archive.is_file() or archive.stat().st_size == 0:
            raise RuntimeError('NO_ARCHIVE9 ' + mode)
        decoded = (work / ('decode_' + mode)); decoded.mkdir()
        archive_copy = decoded / 'archive9'; shutil.copy2(archive, archive_copy); archive_copy.chmod(0o755)
        # Decoder only sees its *own* archive9, no Wikipedia, model files or side information.
        decode = execute(archive_copy.resolve(), decoded, 'decode', seconds, cpu)
        restored = decoded / 'enwik9_uncompressed'
        if not restored.is_file() or restored.stat().st_size != 1_000_000_000 or digest(restored) != ENWIK9:
            raise RuntimeError('LOSSLESS_ROUNDTRIP_FAILED ' + mode)
        results.append({'mode': mode, 'comp9_bytes': comp.stat().st_size,
                        'archive9_bytes': archive.stat().st_size,
                        'option_bytes': 0, 'S_bytes': comp.stat().st_size + archive.stat().st_size,
                        'build_wall_seconds': next(b['build_wall_seconds'] for b in builds if b['mode']==mode),
                        'encode': encode, 'decode': decode,
                        'restored_sha256': ENWIK9, 'lossless': True})
    return {'status': 'FULL_LOCAL_AB_VERIFIED', 'hutter_prize_score': None,
            'official_validation': False, 'local_competition_formula_S': True,
            'results': results, 'delta_S_bytes': results[0]['S_bytes']-results[1]['S_bytes']}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--run-full', action='store_true')
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--enwik9', type=Path)
    parser.add_argument('--seconds-per-phase', type=int, default=210000)
    args = parser.parse_args()
    if args.run_full and args.build_only:
        parser.error('--run-full and --build-only are mutually exclusive')
    if args.run_full and not args.enwik9:
        parser.error('--run-full requires --enwik9')
    record = create_pair(args.upstream, args.work)
    if args.run_full or args.build_only:
        builds = build_pair(args.work, args.seconds_per_phase)
        record['experiment']['builds'] = builds
        record['experiment']['status'] = 'BOTH_PRODUCTION_BINARIES_BUILT_NO_DATA'
        if args.run_full:
            result = full_compare(args.work, args.enwik9, args.seconds_per_phase, builds)
            record['experiment'].update(result)
            record['experiment']['status'] = result['status']
        (args.work / ('full_ab.json' if args.run_full else 'build_ab.json')).write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'status': record['experiment']['status'], 'work': str(args.work),
                      'note': 'SOURCE_ONLY; no full result without --run-full'}))


if __name__ == '__main__':
    main()
