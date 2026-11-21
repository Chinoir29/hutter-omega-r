#!/usr/bin/env python3
"""Source-level contradiction tests for the controlled -c laboratory opening."""
import unittest
from enable_raw_lab import (
    modify_source, OLD_PARSER, OLD_BRANCH, OLD_HELPER,
    NEW_PARSER, NEW_BRANCH, NEW_HELPER, LAB_HEAD
)

FIXTURE = (
    "int main(){\n  if (" + OLD_PARSER + " && true) return Help();\n}\n"
    + OLD_HELPER + " { return true; }\n"
    + OLD_BRANCH + "\nif (argv[1][1] == 'c'){}\n"
)

class TestRawLaboratoryPatch(unittest.TestCase):
    def test_expected_parser_branch_and_helper(self):
        result = modify_source(FIXTURE)
        self.assertIn(NEW_PARSER, result)
        self.assertIn(NEW_BRANCH, result)
        self.assertIn(NEW_HELPER, result)
        self.assertTrue(result.startswith(LAB_HEAD))
        self.assertEqual(result.count("OMR14_RAW_CODER"), 3)

    def test_only_the_three_intended_edits(self):
        expected = (LAB_HEAD + FIXTURE.replace(OLD_PARSER, NEW_PARSER)
                    .replace(OLD_BRANCH, NEW_BRANCH)
                    .replace(OLD_HELPER, NEW_HELPER))
        self.assertEqual(modify_source(FIXTURE), expected)

    def test_duplicate_parser_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE + OLD_PARSER)

    def test_duplicate_branch_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE + OLD_BRANCH)

    def test_duplicate_helper_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE + OLD_HELPER)

    def test_old_release_helper_missing_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE.replace(OLD_HELPER, "#if 0"))

    def test_old_release_switch_missing_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE.replace(OLD_BRANCH, "#if 0"))

    def test_repatch_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(modify_source(FIXTURE))

    def test_no_change_to_selfextract_branch(self):
        self.assertEqual(modify_source(FIXTURE).count("if (argv[1][1] == 'c')"),1)

if __name__=="__main__":
    unittest.main(verbosity=2)
