#!/usr/bin/env python3
"""Reversible encoding of *raw* enwik9 excerpts into cmix-neif's 208-byte alphabet.

Lab instrumentation only: a lossless byte-to-byte transducer, not the upstream
preprocessor or a Hutter Prize archive. No codebook depends on input statistics.
"""
from __future__ import annotations
import argparse, hashlib, json, re, tempfile
from pathlib import Path

UPSTREAM_SHA = '35d1957a5074db802fc134126afc77b76d931761'
VOCAB_GIT_BLOB = 'da5ffe84fb7e3d9a5061b43da5970f7c9f728e19'
ENWIK9_SHA = '159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
ENWIK9_BYTES = 1_000_000_000
OFFSETS_MIB = (256, 384, 640)  # untouched in v0.15/v0.16
RAW_BYTES = 65_536
ESC = ord('^')  # permitted by the frozen vocabulary; rare in normal Wiki text
# Exactly 49 distinct, printable, permitted symbols (48 rejected byte values + ESC itself).
CODES = b'abcdefghijklmnopqrstuvwxyz0123456789JKLMNOPQRSX_+'
assert len(CODES) == 49 and len(set(CODES)) == len(CODES)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bitmap(header: bytes) -> tuple[int, ...]:
    match = re.search(rb'kBitmap\[32\]\s*=\s*\{([^}]*)\}', header, re.S)
    if not match:
        raise ValueError('Missing frozen 208-byte vocabulary')
    entries = tuple(int(s.strip(), 0) for s in match.group(1).decode('ascii').split(',') if s.strip())
    if len(entries) != 32 or any(x < 0 or x > 255 for x in entries) or sum(x.bit_count() for x in entries) != 208:
        raise ValueError('Wrong frozen vocabulary geometry')
    return entries


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def codec(bitmap: tuple[int, ...]):
    allowed = {b for b in range(256) if bitmap[b >> 3] & (1 << (b & 7))}
    if len(allowed) != 208 or ESC not in allowed or not set(CODES).issubset(allowed) or ESC in CODES:
        raise ValueError('Codebook not allowed by upstream frozen vocabulary')
    exceptional = tuple(sorted((set(range(256)) - allowed) | {ESC}))
    if len(exceptional) != len(CODES):
        raise ValueError('Unexpected exception alphabet size')
    return allowed, dict(zip(exceptional, CODES)), dict(zip(CODES, exceptional))


def encode(raw: bytes, bitmap: tuple[int, ...]) -> bytes:
    allowed, escapes, _ = codec(bitmap)
    out = bytearray()
    for b in raw:
        if b in allowed and b != ESC:
            out.append(b)
        else:
            out.extend((ESC, escapes[b]))
    return bytes(out)


def decode(stream: bytes, bitmap: tuple[int, ...]) -> bytes:
    allowed, _, exceptions = codec(bitmap)
    out = bytearray()
    pos = 0
    while pos < len(stream):
        b = stream[pos]
        if b not in allowed:
            raise ValueError(f'Unrecognized byte at offset {pos}')
        if b == ESC:
            pos += 1
            if pos == len(stream) or stream[pos] not in exceptions:
                raise ValueError(f'Truncated/invalid escaped byte at {pos}')
            out.append(exceptions[stream[pos]])
        else:
            out.append(b)
        pos += 1
    return bytes(out)


def make_samples(enwik9: Path, header: Path, out: Path) -> dict:
    blob = header.read_bytes()
    if git_blob_sha(blob) != VOCAB_GIT_BLOB:
        raise ValueError('Upstream frozen vocabulary Git blob differs')
    bitmap = parse_bitmap(blob)
    if enwik9.stat().st_size != ENWIK9_BYTES or file_sha(enwik9) != ENWIK9_SHA:
        raise ValueError('Input is not authenticated official enwik9')
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for off in OFFSETS_MIB:
        with enwik9.open('rb') as f:
            f.seek(off * 1024 * 1024)
            raw = f.read(RAW_BYTES)
        if len(raw) != RAW_BYTES:
            raise ValueError('Truncated excerpt')
        coded = encode(raw, bitmap)
        if decode(coded, bitmap) != raw:
            raise AssertionError('Local encoding not exactly reversible')
        path = out / f'escaped_{off}MiB.dat'
        path.write_bytes(coded)
        results.append({
            'offset_mib': off, 'raw_bytes': len(raw), 'raw_sha256': sha(raw),
            'encoded_bytes': len(coded), 'encoded_sha256': sha(coded),
            'escape_pairs': len(coded) - len(raw), 'file': path.name,
            'lossless_codec_verified': True,
        })
    return {
        'version': 'OMEGA-R v0.17', 'source': 'authenticated enwik9',
        'source_sha256': ENWIK9_SHA, 'source_bytes': ENWIK9_BYTES,
        'upstream_commit': UPSTREAM_SHA, 'upstream_vocab_git_blob': VOCAB_GIT_BLOB,
        'transform': 'fixed two-byte escape coding, fully reversible',
        'lossy_projection': False, 'contest_coding_path': False,
        'hutter_score': None, 'offsets_mib': list(OFFSETS_MIB),
        'escape_byte': ESC, 'escape_codes': CODES.decode('ascii'), 'samples': results,
    }


def self_test() -> None:
    # Exact frozen vocabulary published by cmix-neif-2.0 at the pinned commit.
    b = (254,30,0,0,255,255,255,3,1,252,15,249,254,255,255,7,
         255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255)
    assert sum(x.bit_count() for x in b) == 208
    source = bytes(range(256)) * 5 + b'^Hello, World!\n' * 20
    coded = encode(source, b)
    assert decode(coded, b) == source
    assert set(coded).issubset({x for x in range(256) if b[x >> 3] & (1 << (x & 7))})
    accepted, _, _ = codec(b)
    assert len(coded) == len(source) + sum(x not in accepted or x == ESC for x in source)
    for sample in (b'', bytes([ESC]) * 100, bytes(range(256)), b'hello\x00world\r\n'):
        assert decode(encode(sample, b), b) == sample
    for bad in (bytes([ESC]), bytes([ESC, 1]), bytes([0])):
        try: decode(bad, b)
        except ValueError: pass
        else: raise AssertionError(f'Invalid encoded bytes accepted: {bad!r}')
    try:codec(tuple([255] * 32))
    except ValueError:pass
    else:raise AssertionError('Invalid 256-byte vocabulary accepted')
    print('REVERSIBLE_SAMPLE_SELF_TEST_PASS', len(source), len(coded))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--enwik9', type=Path)
    p.add_argument('--vocab-header', type=Path)
    p.add_argument('--out-dir', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    if args.self_test:
        self_test();return
    if not all((args.enwik9, args.vocab_header, args.out_dir, args.report)):
        p.error('--enwik9 --vocab-header --out-dir --report required')
    result = make_samples(args.enwik9, args.vocab_header, args.out_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':main()
