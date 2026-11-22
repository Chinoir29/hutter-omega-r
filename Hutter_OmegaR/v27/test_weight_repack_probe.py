"""Adversarial tests for OMÉGA-R v0.27; no third-party weights loaded."""
from pathlib import Path
import hashlib
import os
import random
import unittest
from unittest.mock import patch

from weight_repack_probe import audit, encode, decode, execute, CODECS, TRANSFORMS


class WeightRepackTests(unittest.TestCase):
    def test_five_odd_lengths_all_modes(self):
        for length in (0, 1, 2, 3, 5, 15, 16, 127, 256, 257, 1025):
            data = bytes(i % 256 for i in range(length))
            for m in TRANSFORMS:
                self.assertEqual(len(encode(data, m)), length)
                self.assertEqual(decode(encode(data, m), m), data)

    def test_random_binary_roundtrip(self):
        rnd = random.Random(12345)
        for n in (11, 1001, 65537):
            data = rnd.randbytes(n)
            for m in TRANSFORMS:
                self.assertEqual(decode(encode(data, m), m), data)

    def test_unknown_transform_fails(self):
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_TRANSFORM'):
            encode(b'abc', 'bogus')
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_TRANSFORM'):
            decode(b'abc', 'bogus')

    def test_refuse_noncanonical_weights(self):
        with self.assertRaisesRegex(ValueError, 'NOT_AUTHENTIC'):
            audit(b'this is not the production weight blob')

    def test_gzip_trial_on_synthetic_data(self):
        data = b'abracadabra' * 200
        r = audit(data, pin=False, codecs={'gzip9': CODECS['gzip9']})
        self.assertEqual(r['num_lossless_experiments'], len(TRANSFORMS))
        self.assertIsNone(r['official_hutter_S'])
        self.assertTrue(all(x['roundtrip_sha256_exact'] for x in r['results']))
        self.assertTrue(all(x['packed_bytes'] > 0 for x in r['results']))
        self.assertEqual(r['source_sha256'], hashlib.sha256(data).hexdigest())

    def test_missing_codec_detected(self):
        with self.assertRaisesRegex(ValueError, 'MISSING_CODEC_PROGRAM'):
            execute(['nonexistent-codec-omega-r-27'], b'data')

    def test_no_silent_inverse_mismatch(self):
        data = b'abc' * 111
        fake_codec = {'bad': (['gzip', '-9', '-n', '-c'], ['gzip', '-d', '-c'])}
        with patch('weight_repack_probe.decode', return_value=b'incorrect'):
            with self.assertRaisesRegex(AssertionError, 'NOT_LOSSLESS'):
                audit(data, pin=False, codecs=fake_codec)


if __name__ == '__main__':
    unittest.main(verbosity=2)
