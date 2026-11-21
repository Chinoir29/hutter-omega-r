#!/usr/bin/env python3
"""Synthetic mock compressor tests only; no upstream compression result asserted."""
import json, tempfile, unittest
from pathlib import Path
import run_reversible_lab as runner
from reversible_sample import (codec, encode, sha, git_blob_sha)

B=(254,30,0,0,255,255,255,3,1,252,15,249,254,255,255,7,
   255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255)
FAKE='''#!/usr/bin/env python3
import sys, pathlib, zlib
cmd,src,dst=sys.argv[1:]
p=pathlib.Path(src).read_bytes()
if cmd=='-c':pathlib.Path(dst).write_bytes(zlib.compress(p,6))
elif cmd=='-d':pathlib.Path(dst).write_bytes(zlib.decompress(p))
else:sys.exit(2)
'''

class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        header=(b'constexpr unsigned char kBitmap[32] = {'+
                b','.join(str(b).encode() for b in B)+b'};\n')
        self.header=self.root/'vocab.h';self.header.write_bytes(header)
        self.orig=runner.VOCAB_GIT_BLOB
        runner.VOCAB_GIT_BLOB=git_blob_sha(header)
        self.raw=bytes(range(256))*256
        coded=encode(self.raw,B)
        self.sample=self.root/'escaped_256MiB.dat';self.sample.write_bytes(coded)
        self.record={'raw_bytes':65536,'raw_sha256':sha(self.raw),
                     'encoded_bytes':len(coded),'encoded_sha256':sha(coded),
                     'offset_mib':256,'lossless_codec_verified':True}
        self.binary=self.root/'cmix';self.binary.write_text(FAKE);self.binary.chmod(0o755)
        self.weights=self.root/'weights.c5';self.weights.write_bytes(b'test-only-dummy')
    def tearDown(self):
        runner.VOCAB_GIT_BLOB=self.orig
        self.tmp.cleanup()
    def test_both_stages(self):
        out=runner.experiment(self.sample,self.record,self.binary,self.weights,
            self.header,self.root/'reports',timeout=10)
        self.assertEqual(out['status'],'two_stage_verified')
        self.assertTrue(out['roundtrip_raw_excerpt_sha256'])
        self.assertIsNone(out['hutter_score'])
        self.assertFalse(out['self_extracting_archive'])
    def test_bad_manifest_hash(self):
        bad={**self.record,'raw_sha256':'0'*64}
        with self.assertRaises(RuntimeError):runner.experiment(self.sample,bad,self.binary,self.weights,
            self.header,self.root/'reports',timeout=10)
    def test_bad_sample_bytes(self):
        self.sample.write_bytes(self.sample.read_bytes()+b'!')
        with self.assertRaises(RuntimeError):runner.experiment(self.sample,self.record,self.binary,self.weights,
            self.header,self.root/'reports',timeout=10)

if __name__=='__main__':unittest.main(verbosity=2)
