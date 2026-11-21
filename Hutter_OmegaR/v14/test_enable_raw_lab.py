#!/usr/bin/env python3
"""Source-level contradiction tests for the controlled -c laboratory opening."""
import unittest
from enable_raw_lab import modify_source, OLD_PARSER, OLD_BRANCH, LAB_HEAD, NEW_BRANCH, NEW_PARSER

FIXTURE="int main(){\n  if ((argc != 1) && (argv[1][1] != 'd' && argv[1][1] != 'e' && 1)) return Help();\n}\n"+OLD_BRANCH+"\nif (argv[1][1] == 'c'){}\n"

class TestRawLaboratoryPatch(unittest.TestCase):
    def test_expected_parser_and_branch(self):
        s=modify_source(FIXTURE)
        self.assertIn(NEW_PARSER,s)
        self.assertIn(NEW_BRANCH,s)
        self.assertTrue(s.startswith(LAB_HEAD))
    def test_no_unexpected_change(self):
        s=modify_source(FIXTURE)
        expected=LAB_HEAD+FIXTURE.replace(OLD_PARSER,NEW_PARSER).replace(OLD_BRANCH,NEW_BRANCH)
        self.assertEqual(s,expected)
    def test_duplicate_parser_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+OLD_PARSER)
    def test_duplicate_branch_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+OLD_BRANCH)
    def test_old_release_switch_missing_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE.replace(OLD_BRANCH,"#if 0"))
    def test_repatch_rejected(self):
        with self.assertRaises(ValueError):modify_source(modify_source(FIXTURE))
    def test_no_change_to_selfextract_branch(self):
        s=modify_source(FIXTURE)
        self.assertEqual(s.count("if (argv[1][1] == 'c')"),1)

if __name__=="__main__":unittest.main(verbosity=2)
