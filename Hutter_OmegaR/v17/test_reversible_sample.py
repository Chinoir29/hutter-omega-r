#!/usr/bin/env python3
"""Adversarial tests of the lossless fixed-alphabet transducer, not a Hutter score."""
from __future__ import annotations
import random, unittest
from pathlib import Path
from reversible_sample import (ESC, CODES, ENWIK9_SHA, OFFSETS_MIB, RAW_BYTES,
    codec, decode, encode, git_blob_sha, parse_bitmap, sha)

B = (254,30,0,0,255,255,255,3,1,252,15,249,254,255,255,7,
     255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255)

class Tests(unittest.TestCase):
    def test_all_bytes_roundtrip(self):
        data = bytes(range(256)) * 200
        self.assertEqual(decode(encode(data,B),B),data)
    def test_allowed_only_output(self):
        rng = random.Random(1731)
        raw = rng.randbytes(40_000)
        encoded = encode(raw,B)
        accepted=codec(B)[0]
        self.assertTrue(all(x in accepted for x in encoded))
        self.assertEqual(decode(encoded,B),raw)
    def test_empty(self):
        self.assertEqual(encode(b'',B),b'')
        self.assertEqual(decode(b'',B),b'')
    def test_escape_byte(self):
        self.assertEqual(encode(bytes([ESC]),B),bytes([ESC, CODES[-1]]) if codec(B)[1][ESC]==CODES[-1] else bytes([ESC,codec(B)[1][ESC]]))
        self.assertEqual(decode(encode(bytes([ESC])*300,B),B),bytes([ESC])*300)
    def test_non_allowed_values(self):
        disallowed=[i for i in range(256) if i not in codec(B)[0]]
        self.assertEqual(len(disallowed),48)
        for b in disallowed:
            self.assertEqual(decode(encode(bytes([b]),B),B),bytes([b]))
    def test_escape_overhead_exact(self):
        raw=bytes(range(256))*30
        out=encode(raw,B)
        valid=codec(B)[0]
        self.assertEqual(len(out)-len(raw),sum(b not in valid or b==ESC for b in raw))
    def test_incomplete_escape_rejected(self):
        with self.assertRaises(ValueError):decode(bytes([ESC]),B)
    def test_bad_escape_code_rejected(self):
        with self.assertRaises(ValueError):decode(bytes([ESC,1]),B)
    def test_bad_input_byte_rejected(self):
        with self.assertRaises(ValueError):decode(b'\0',B)
    def test_wrong_alphabet_rejected(self):
        with self.assertRaises(ValueError):codec((255,)*32)
    def test_bitmap_parser(self):
        literal=b'constexpr unsigned char kBitmap[32] = {'+b','.join(str(x).encode() for x in B)+b'};'
        self.assertEqual(parse_bitmap(literal),B)
    def test_bad_bitmap_rejected(self):
        with self.assertRaises(ValueError):parse_bitmap(b'kBitmap[32] = {0};')
    def test_git_blob_hash(self):
        self.assertEqual(git_blob_sha(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_nonoverlap_predeclared(self):
        self.assertEqual(OFFSETS_MIB,(256,384,640))
        self.assertEqual(RAW_BYTES,65536)
        self.assertGreater(min((y-x)*1048576 for x,y in zip(OFFSETS_MIB,OFFSETS_MIB[1:])),RAW_BYTES)
    def test_binary_payload_with_binary_controls(self):
        raw=b'\x00\xff\x04\r\n^' * 6000
        self.assertEqual(decode(encode(raw,B),B),raw)
    def test_source_hash_pinned(self):
        self.assertEqual(len(ENWIK9_SHA),64)
    def test_repeated_escape_codes(self):
        self.assertEqual(len(set(CODES)),49)
        self.assertNotIn(ESC,CODES)
        self.assertEqual(len(codec(B)[2]),49)

if __name__=='__main__':unittest.main(verbosity=2)
