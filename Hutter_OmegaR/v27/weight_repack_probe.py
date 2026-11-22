#!/usr/bin/env python3
"""OMÉGA-R v0.27: lossless repacking audit of the pinned cmix weight container.

This does NOT modify a competition binary. All original/transformed/packed bytes
stay in memory or ephemeral runner storage; publish only sizes, hashes and timing.
Unmodified upstream data and GPL-3.0-only license stay in the source checkout.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

SOURCE_SHA = '729694cba4969b7d833686ed3f597ff04d3b226da849d5f8004ec020a0ed9563'
SOURCE_BYTES = 3_744_629
CODECS = {
    'gzip9': (['gzip', '-9', '-n', '-c'], ['gzip', '-d', '-c']),
    'bzip2_9': (['bzip2', '-9', '-c'], ['bzip2', '-d', '-c']),
    'xz9e': (['xz', '-9e', '--threads=1', '-c'], ['xz', '-d', '-c']),
    'zstd19': (['zstd', '-19', '-T1', '-q', '-c'], ['zstd', '-d', '-q', '-c']),
    'brotli11': (['brotli', '-q', '11', '-c'], ['brotli', '-d', '-c']),
}
TRANSFORMS = ('identity', 'xor_prev', 'lanes4')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(raw: bytes, how: str) -> bytes:
    if how == 'identity':
        return raw
    if how == 'xor_prev':
        if not raw:
            return raw
        return bytes([raw[0]]) + bytes(a ^ b for a, b in zip(raw[1:], raw[:-1]))
    if how == 'lanes4':
        return b''.join(raw[i::4] for i in range(4))
    raise ValueError('UNKNOWN_TRANSFORM')


def decode(data: bytes, how: str) -> bytes:
    if how == 'identity':
        return data
    if how == 'xor_prev':
        out = bytearray(len(data))
        p = 0
        for i, c in enumerate(data):
            p ^= c
            out[i] = p
        return bytes(out)
    if how == 'lanes4':
        out = bytearray(len(data))
        off = 0
        for lane in range(4):
            n = len(range(lane, len(data), 4))
            out[lane::4] = data[off:off+n]
            off += n
        if off != len(data):
            raise AssertionError('BAD_LANES')
        return bytes(out)
    raise ValueError('UNKNOWN_TRANSFORM')


def execute(args: list[str], input_data: bytes, max_seconds: int = 300) -> tuple[bytes, float]:
    if not shutil.which(args[0]):
        raise ValueError('MISSING_CODEC_PROGRAM_'+args[0])
    t = time.monotonic()
    done = subprocess.run(args, input=input_data, capture_output=True, check=True, timeout=max_seconds)
    if done.stderr:
        # Codec stderr is diagnostic only, never embedded in a public result.
        raise RuntimeError('CODEC_REPORTED_UNEXPECTED_STDERR_'+args[0])
    return done.stdout, round(time.monotonic() - t, 4)


def audit(payload: bytes, *, pin: bool = True, codecs: dict = CODECS) -> dict:
    if pin and (len(payload) != SOURCE_BYTES or sha(payload) != SOURCE_SHA):
        raise ValueError('UPSTREAM_WEIGHT_CONTAINER_NOT_AUTHENTIC')
    original = len(payload)
    freq = Counter(payload)
    entropy = -sum((n/original) * math.log2(n/original) for n in freq.values()) if original else 0.0
    outcomes = []
    for transform in TRANSFORMS:
        transformed = encode(payload, transform)
        if len(transformed) != original or decode(transformed, transform) != payload:
            raise AssertionError('NOT_LOSSLESS_'+transform)
        for codec, (enc, dec) in codecs.items():
            packed, enc_s = execute(enc, transformed)
            reconstructed_transform, dec_s = execute(dec, packed)
            reconstructed = decode(reconstructed_transform, transform)
            if reconstructed != payload or sha(reconstructed) != sha(payload):
                raise AssertionError('WRAPPER_NOT_LOSSLESS_'+transform+'_'+codec)
            outcomes.append({
                'transform': transform,
                'codec': codec,
                'packed_bytes': len(packed),
                'packed_sha256': sha(packed),
                'saving_per_executable_bytes': original - len(packed),
                'optimistic_two_copy_saving_bytes': 2 * (original - len(packed)),
                'encode_wall_seconds': enc_s,
                'decode_wall_seconds': dec_s,
                'roundtrip_sha256_exact': True,
            })
    outcomes.sort(key=lambda x: (x['packed_bytes'], x['transform'], x['codec']))
    best = outcomes[0] if outcomes else None
    return {
        'status': 'SOURCE_WEIGHTS_REPACK_CROSSCHECKED',
        'upstream_commit': '35d1957a5074db802fc134126afc77b76d931761',
        'source_bytes': original,
        'source_sha256': sha(payload),
        'empirical_entropy_bits_per_byte': round(entropy, 6),
        'num_lossless_experiments': len(outcomes),
        'results': outcomes,
        'best': best,
        'required_saving_per_copy_to_beat_933890_two_copy_budget': 466945,
        'additional_decoder_binary_cost': None,
        'all_scores_are_pre_binary_overhead_proxies': True,
        'official_hutter_S': None,
        'enwik9_restoration_tested': False,
        'third_party_data_published': False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--weights', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    data = args.weights.read_bytes()
    results = audit(data, pin=True)
    args.report.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({k:v for k,v in results.items() if k != 'results'}, indent=2))


if __name__ == '__main__':
    main()
