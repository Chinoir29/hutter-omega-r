#!/usr/bin/env python3
"""Tests for the pure, side-effect-free source replacement; no upstream fetch."""
import unittest
from semantic_cache_gate_patch import modify_source, BASE_COMMIT, BASE_BLOB

ORIGINAL = '''namespace semantic_cache {
constexpr int kQpE3 = 990;             // look up below
constexpr int kSpE3 = 950;             // store below
constexpr int kCalqE3 = 900;           // mean
}'''


class TestThresholdPatching(unittest.TestCase):
    def test_control_identical(self):
        self.assertEqual(modify_source(ORIGINAL, 990), ORIGINAL)

    def test_variant_980_only_one_change(self):
        self.assertEqual(modify_source(ORIGINAL, 980), ORIGINAL.replace('kQpE3 = 990;', 'kQpE3 = 980;'))

    def test_variant_970_only_one_change(self):
        self.assertEqual(modify_source(ORIGINAL, 970), ORIGINAL.replace('kQpE3 = 990;', 'kQpE3 = 970;'))

    def test_reject_invalid_threshold(self):
        for threshold in (0, 900, 949, 951, 975, 999, True, 980.0, '980'):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    modify_source(ORIGINAL, threshold)

    def test_reject_wrong_original_threshold(self):
        with self.assertRaises(ValueError):
            modify_source(ORIGINAL.replace('kQpE3 = 990;', 'kQpE3 = 980;'), 970)

    def test_reject_duplicate_threshold(self):
        with self.assertRaises(ValueError):
            modify_source(ORIGINAL + '\nconstexpr int kQpE3 = 990; // look up below', 970)

    def test_reject_source_without_storage_gate(self):
        with self.assertRaises(ValueError):
            modify_source(ORIGINAL.replace('kSpE3 = 950', 'kSpE3 = 999'), 970)

    def test_reject_source_without_calibration_gate(self):
        with self.assertRaises(ValueError):
            modify_source(ORIGINAL.replace('kCalqE3 = 900', 'kCalqE3 = 999'), 980)

    def test_pinned_revision(self):
        self.assertEqual(len(BASE_COMMIT), 40)
        self.assertEqual(len(BASE_BLOB), 40)


if __name__ == '__main__':
    unittest.main(verbosity=2)
