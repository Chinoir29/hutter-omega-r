#!/usr/bin/env python3
"""Contradictory unit tests of the five strictly scoped v0.14.2 lab changes.

Source-only: does NOT test compression, GPU inference, the original enwik9, or
Hutter Prize eligibility. This is code-construction quality assurance.
"""
import unittest
from enable_raw_lab import (
    modify_source, OLD_PARSER, OLD_BRANCH, OLD_HELPER,
    NEW_PARSER, NEW_BRANCH, NEW_HELPER, LAB_HEAD,
    INERT_ANCHOR, INERT_OLD, INERT_NEW, LAB_GLOBAL,
    MAIN_ANCHOR, MAIN_REPLACE
)

FIXTURE = (
    "int fake(){\n  if (" + OLD_PARSER + " && true) return Help();\n}\n"
    + OLD_HELPER + " { return true; }\n"
    + OLD_BRANCH + "\nif (argv[1][1] == 'c'){}\n"
    + LAB_GLOBAL.replace("g_omr14_lab_raw_mode = false;", "placeholder_ignore = false;")
      .replace("static bool placeholder_ignore = false;\n\n", "")
      .replace("// Independent from transformer::Active() and SEMCACHE.\n", "")
      .replace("// Lab-only: disable metadata transformations for raw byte streams.\n", "")
    + "".join(
        "static inline bool " + func + "() {\n" + INERT_OLD + "\n}\n"
        for func in ("AuthorBlockInert", "MetablockInert", "TimestampProgressInert")
    )
    + MAIN_ANCHOR + "\n  return 0;\n}\n"
)

class TestRawLaboratoryPatch(unittest.TestCase):
    def test_modify_source_is_scoped(self):
        s=modify_source(FIXTURE)
        self.assertIn(NEW_PARSER,s)
        self.assertIn(NEW_BRANCH,s)
        self.assertIn(NEW_HELPER,s)
        self.assertIn(MAIN_REPLACE,s)
        self.assertEqual(s.count(INERT_NEW),3)
        self.assertEqual(s.count(LAB_GLOBAL),1)
        self.assertTrue(s.startswith(LAB_HEAD))
        self.assertEqual(s.count("OMR14_RAW_CODER"),3)

    def test_equal_to_exact_expected_replacements(self):
        expected=(LAB_HEAD+FIXTURE.replace(OLD_PARSER,NEW_PARSER,1)
                  .replace(OLD_BRANCH,NEW_BRANCH,1)
                  .replace(OLD_HELPER,NEW_HELPER,1)
                  .replace(INERT_ANCHOR,LAB_GLOBAL+INERT_ANCHOR,1)
                  .replace(INERT_OLD,INERT_NEW,3)
                  .replace(MAIN_ANCHOR,MAIN_REPLACE,1))
        self.assertEqual(modify_source(FIXTURE),expected)

    def test_duplicate_parser_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+OLD_PARSER)

    def test_duplicate_branch_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+OLD_BRANCH)

    def test_duplicate_helper_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+OLD_HELPER)

    def test_missing_helper_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE.replace(OLD_HELPER,"#if 0"))

    def test_missing_branch_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE.replace(OLD_BRANCH,"#if 0"))

    def test_duplicate_inert_body_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE+INERT_OLD)

    def test_missing_metablock_inert_rejected(self):
        with self.assertRaises(ValueError):
            modify_source(FIXTURE.replace("static inline bool MetablockInert", "static inline bool Different"))

    def test_missing_main_entry_rejected(self):
        with self.assertRaises(ValueError):modify_source(FIXTURE.replace(MAIN_ANCHOR,"int main() {"))

    def test_repatch_rejected(self):
        with self.assertRaises(ValueError):modify_source(modify_source(FIXTURE))

    def test_coder_and_decoder_both_select_lab_mode(self):
        out=modify_source(FIXTURE)
        self.assertIn("argv[1][1] == 'c' || argv[1][1] == 'd'",out)
        self.assertTrue("MetablockInert" in out)
        self.assertTrue("AuthorBlockInert" in out)
        self.assertTrue("TimestampProgressInert" in out)

if __name__=="__main__":
    unittest.main(verbosity=2)
