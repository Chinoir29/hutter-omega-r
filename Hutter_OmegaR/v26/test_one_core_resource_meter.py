"""Tests de sécurité et de mesure de ressources v0.26 (aucun corpus requis)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from one_core_resource_meter import run, allocated_bytes, proc_parent_and_rss


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux /proc required")
class MonitorTests(unittest.TestCase):
    def test_real_process_child_affinity_and_disk(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_dir = root / "work"
            run_dir.mkdir()
            code = (
                "import os,pathlib,time;"
                "pathlib.Path('result').write_bytes(b'A'*65536);"
                "pathlib.Path('cpu_count').write_text(str(len(os.sched_getaffinity(0))));"
                "time.sleep(0.35)"
            )
            result = run([sys.executable, "-c", code], run_dir, root / "audit.json",
                         timeout_s=4, sample_s=0.03)
            self.assertEqual(result["status"], "FINISHED")
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual((run_dir / "cpu_count").read_text(), "1")
            self.assertGreater(result["rss_sum_observed_peak_bytes"], 1_000_000)
            self.assertGreater(result["disk_allocated_delta_observed_peak_bytes"], 0)
            self.assertEqual(result["official_hutter_compliance"], None)
            self.assertTrue((root / "audit.json").exists())
            self.assertEqual(result, json.loads((root / "audit.json").read_text()))

    def test_timeout_is_reported_not_silently_successful(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cwd = root / "work"
            cwd.mkdir()
            result = run([sys.executable, "-c", "import time; time.sleep(10)"], cwd,
                         root / "audit.json", timeout_s=1, sample_s=0.05)
            self.assertEqual(result["status"], "TIMEOUT")
            self.assertNotEqual(result["exit_code"], 0)

    def test_refuse_artifacts_inside_target_workdir(self):
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            with self.assertRaisesRegex(ValueError, "REPORT_MUST_NOT"):
                run([sys.executable], cwd, cwd / "audit.json")
            with self.assertRaisesRegex(ValueError, "STDOUT_MUST_BE"):
                run([sys.executable], cwd, cwd.parent / "audit.json", stdout=cwd / "bad.log")

    def test_refuse_unavailable_cpu(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cwd = root / "cwd"
            cwd.mkdir()
            available = set(os.sched_getaffinity(0))
            unavailable = next(c for c in range(max(available) + 2) if c not in available)
            with self.assertRaisesRegex(ValueError, "CPU_NOT_ALLOWED"):
                run([sys.executable], cwd, root / "audit.json", cpu=unavailable)

    def test_reject_bad_parameters(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "INVALID_MONITOR_ARGUMENTS"):
                run([], root, root.parent / "audit.json")
            with self.assertRaisesRegex(ValueError, "INVALID_MONITOR_ARGUMENTS"):
                run([sys.executable], root, root.parent / "audit.json", sample_s=0)

    def test_stat_followlinks_false(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "wrk"
            d.mkdir()
            external = root / "external"
            external.write_bytes(b'x' * 500_000)
            (d / "linked").symlink_to(external)
            self.assertLess(allocated_bytes(d), external.stat().st_size)

    def test_proc_status(self):
        current = proc_parent_and_rss(os.getpid())
        self.assertIsNotNone(current)
        self.assertGreater(current[1], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
