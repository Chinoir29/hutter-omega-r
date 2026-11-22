"""Adversarial synthetic tests for the v0.24 source, archive and isolation gates."""
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_selfextract as p
import assemble_prefix_archive as a
import run_isolated as iso


class SourceAugmentation(unittest.TestCase):
    def fixture(self):
        return b'''// OMR23_PREFIX_DECODE
// omr23-decoded-prefix.bin
void f() {
    // run compression
    input_path = ".ready4cmix_decomp";
    split4Decomp();
}
'''
    def test_single_patch_and_structure(self):
        out = p.augment_runner(self.fixture())
        self.assertIn(b'setenv("OMR23_PREFIX_DECODE", "524288", 1)', out)
        self.assertIn(b'goto print_end_message;', out)
        self.assertLess(out.index(b'setenv('), out.index(b'input_path = ".ready4cmix_decomp";'))
        self.assertLess(out.index(b'goto print_end_message;'), out.index(b'split4Decomp();'))
    def test_decoder_never_calls_encoder_only_size_helper(self):
        out = p.augment_runner(self.fixture())
        self.assertNotIn(b"getFileSize(", out)
        self.assertIn(b'rename("omr23-decoded-prefix.bin", "omr24-decoded-prefix.bin")', out)

    def test_no_v23_hooks_rejected(self):
        with self.assertRaisesRegex(ValueError, 'V23_DECODE'):
            p.augment_runner(b'    split4Decomp();\n')
    def test_ambiguous_anchor_rejected(self):
        with self.assertRaisesRegex(ValueError, 'NON_UNIQUE'):
            p.augment_runner(self.fixture() + b'    split4Decomp();\n')


class ArchiveLayout(unittest.TestCase):
    def test_real_layout_and_counted_overhead(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stub=root/'stub';stub.write_bytes(b'\x7fELF' + b'STUB0')
            weights=root/'weights';weights.write_bytes(b'1234')
            coded=root/'coded';coded.write_bytes(b'good compressed payload')
            result=root/'archive9'
            with patch.object(a,'WEIGHTS_UPSTREAM_SIZE',4):
                r=a.assemble(stub,weights,coded,result,verify_coded_reference=False)
            self.assertEqual(r['archive_bytes'],9+4+len(coded.read_bytes())+8)
            self.assertEqual(r['trailer_bytes'],8)
            self.assertEqual(a.TRAILER.unpack(result.read_bytes()[-8:]),(len(coded.read_bytes()),4))
            self.assertEqual(result.read_bytes()[0:4],b'\x7fELF')
            with self.assertRaisesRegex(ValueError, 'OUTPUT_EXISTS'):
                a.assemble(stub,weights,coded,result,verify_coded_reference=False)
    def test_invalid_coded_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            s=root/'stub';s.write_bytes(b'\x7fELFx')
            w=root/'weight';w.write_bytes(b'1234')
            c=root/'coded';c.write_bytes(b'bad')
            with patch.object(a,'WEIGHTS_UPSTREAM_SIZE',4):
                with self.assertRaisesRegex(ValueError,'REFERENCE_MISMATCH'):
                    a.assemble(s,w,c,root/'out')


class IndependentTest(unittest.TestCase):
    def synthetic_archive(self, root:Path, command:str) -> Path:
        f=root/'fakearchive';f.write_text('#!/bin/sh\n'+command+'\n');f.chmod(0o755)
        return f
    def test_zero_argument_clean_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            fake=self.synthetic_archive(root,"printf 'hello' > omr24-decoded-prefix.bin")
            expected=hashlib.sha256(b'hello').hexdigest()
            result=iso.verify_isolated(fake,root/'fresh',root/'report.json',
                                       expected_sha=expected,expected_size=5,timeout=5)
            self.assertEqual(result['status'],'INDEPENDENT_ZERO_ARG_PRECODER_PREFIX_RESTORED')
            self.assertEqual(result['started_files'],['archive9'])
            self.assertEqual(result['returncode'],0)
    def test_nonzero_return_fails_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fake=self.synthetic_archive(root,"echo failed >&2; exit 7")
            result=iso.verify_isolated(fake,root/'fresh',root/'report.json',
                                       expected_sha=hashlib.sha256(b'abc').hexdigest(),expected_size=3,timeout=5)
            self.assertEqual(result['status'],'ISOLATED_PREFIX_ROUNDTRIP_FAILED')
            self.assertEqual(result['returncode'],7)
            self.assertTrue((root/'report.json').exists())
            self.assertIsNone(result['actual_decoded_sha256'])
    def test_refuse_existing_clean_dir(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); fake=self.synthetic_archive(root,'exit 0')
            (root/'existing').mkdir()
            with self.assertRaisesRegex(ValueError,'REFUSE_EXISTING'):
                iso.verify_isolated(fake,root/'existing',root/'report.json')


if __name__ == "__main__":
    unittest.main(verbosity=2)
