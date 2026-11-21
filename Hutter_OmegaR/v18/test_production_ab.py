#!/usr/bin/env python3
"""Adversarial tests of v0.18 source gates; synthetic fixtures are NOT upstream."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import production_ab as m


class ProductionGateTests(unittest.TestCase):
    def make_fixture(self, root: Path):
        runner = '''void f() {
Predictor p(vocab);
Compress(temp_bytes, temp_in, data_out, output_bytes, &p);
Decompress(*output_bytes, data_in, temp_out, &p);
Predictor p(vocab);
preprocessor::Encode(data_in, temp_out, *input_bytes, dictionary);
preprocessor::Decode(temp_in, data_out, dictionary);
dict_article::DateiAusSlot();
selfextract_decomp();
}
if (argc == 1) {
 selfextract_decomp();
}
// the package form has no -c
if (argv[1][1] == 'e') {
 dict_derive::BuildDictFromInput(input_path.c_str(), ".hints", ".dict");
}
'''
        for path, content in {
            'src/runner.cpp': runner,
            'src/semantic_cache.h': 'constexpr int kQpE3 = 990;\n',
            'src/readalike_prepr/self_extract.h': 'header.weights_size;\n',
        }.items():
            f = root / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)

    def test_source_contract_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t); self.make_fixture(r)
            result = m.source_contract(r)
            self.assertEqual(result['predictor_constructors'], 2)
            self.assertEqual(result['threshold_before'], 990)

    def test_reject_missing_dictionary_path(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t); self.make_fixture(r)
            f = r / 'src/runner.cpp'
            f.write_text(f.read_text().replace('dict_derive::BuildDictFromInput(', 'NO_DICTIONARY('))
            with self.assertRaisesRegex(ValueError, 'PRODUCTION_ROUTE_CHANGED'):
                m.source_contract(r)

    def test_reject_mismatched_predictor(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t); self.make_fixture(r)
            f = r / 'src/runner.cpp'
            f.write_text(f.read_text().replace('Predictor p(vocab);', 'Predictor p(vocab);\nPredictor p(vocab);', 1))
            with self.assertRaisesRegex(ValueError, 'ASYMMETRY'):
                m.source_contract(r)

    def test_reject_ambiguous_patch(self):
        with tempfile.TemporaryDirectory() as t:
            r = Path(t); self.make_fixture(r)
            f = r / 'src/semantic_cache.h'
            f.write_text(f.read_text() * 2)
            with self.assertRaisesRegex(ValueError, 'NOT_UNIQUE'):
                m.source_contract(r)

    def test_clone_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / 'src'; src.mkdir(); self.make_fixture(src)
            original = (src / 'src/semantic_cache.h').read_bytes()
            # The fixture is explicitly synthetic: do not bypass source checks in production.
            with patch.object(m, 'checked_checkout', return_value={'fixture_only': True}), \
                 patch.dict(m.PINS, {'src/semantic_cache.h': m.git_blob(original)}):
                result = m.create_pair(src, Path(t) / 'experiment')
            self.assertEqual((src / 'src/semantic_cache.h').read_bytes(), original)
            self.assertEqual((Path(t) / 'experiment/candidate/src/semantic_cache.h').read_text(),
                             'constexpr int kQpE3 = 999;\n')
            self.assertIsNone(result['experiment']['competition_score'])
            self.assertEqual(result['experiment']['status'], 'SOURCE_PREPARED_NOT_BENCHMARKED')
            with self.assertRaisesRegex(ValueError, 'WORKDIR_ALREADY_EXISTS'):
                m.create_pair(src, Path(t) / 'experiment')

    def test_reject_noncanonical_corpus_before_run(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / 'wrong'; f.write_bytes(b'<xml>no enwik9</xml>')
            with self.assertRaisesRegex(ValueError, 'CANONICAL_ENWIK9_REQUIRED'):
                m.full_compare(Path(t), f, 10, [])

    def test_git_blob_algorithm(self):
        self.assertEqual(m.git_blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')


if __name__ == '__main__':
    unittest.main(verbosity=2)
