#!/usr/bin/env python3
"""OMÉGA-R v0.26: one-core resource witness for future Hutter candidate runs.

Linux-only local measurement. A successful run is NOT official Hutter validation.
Invokes a program, pins the entire inherited process tree to one CPU, samples
the sum of per-process RSS, and tracks newly allocated disk blocks in cwd.
No network or third-party Python dependencies. GPL-3.0-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

DEFAULT_MEMORY_LIMIT = 10 * (1 << 30)  # conservative project interpretation: 10 GiB
DEFAULT_DISK_LIMIT = 100_000_000_000  # conservative 100 decimal GB


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def allocated_bytes(root: Path) -> int:
    """Disk blocks actually allocated; symlink target is never traversed."""
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            p = Path(base) / name
            try:
                total += p.lstat().st_blocks * 512
            except FileNotFoundError:
                pass
    return total


def proc_parent_and_rss(pid: int) -> tuple[int, int] | None:
    try:
        status = Path(f"/proc/{pid}/status").read_text(errors="replace")
        parent = 0
        rss = 0
        for line in status.splitlines():
            if line.startswith("PPid:"):
                parent = int(line.split()[1])
            elif line.startswith("VmRSS:"):
                rss = int(line.split()[1]) * 1024
        return parent, rss
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, IndexError):
        return None


def group_rss(group_id: int) -> tuple[int, int]:
    """RSS of all members of one isolated POSIX process group, even if parent exited.

    Unlike a PPID tree scan this retains descendants that have been orphaned
    and reparented after the main command terminates.
    """
    rss = 0
    alive = 0
    for name in os.listdir("/proc"):
        if not name.isdecimal():
            continue
        pid = int(name)
        try:
            if os.getpgid(pid) != group_id:
                continue
        except (ProcessLookupError, PermissionError):
            continue
        info = proc_parent_and_rss(pid)
        if info is not None:
            rss += info[1]
            alive += 1
    return rss, alive


def run(command: list[str], cwd: Path, report: Path, *, timeout_s: int = 120,
        sample_s: float = 0.20, cpu: int | None = None,
        stdout: Path | None = None, stderr: Path | None = None) -> dict:
    if not sys.platform.startswith("linux") or not hasattr(os, "sched_setaffinity"):
        raise RuntimeError("LINUX_CPU_AFFINITY_REQUIRED")
    if not command or not cwd.is_dir() or timeout_s < 1 or sample_s <= 0:
        raise ValueError("INVALID_MONITOR_ARGUMENTS")
    if report.resolve().is_relative_to(cwd.resolve()):
        raise ValueError("REPORT_MUST_NOT_CONTAMINATE_WORK_DIRECTORY")
    if stdout and stdout.resolve().is_relative_to(cwd.resolve()):
        raise ValueError("STDOUT_MUST_BE_OUTSIDE_WORK_DIRECTORY")
    if stderr and stderr.resolve().is_relative_to(cwd.resolve()):
        raise ValueError("STDERR_MUST_BE_OUTSIDE_WORK_DIRECTORY")
    allowed = sorted(os.sched_getaffinity(0))
    if not allowed:
        raise RuntimeError("NO_AVAILABLE_CPU")
    selected = cpu if cpu is not None else allowed[0]
    if selected not in allowed:
        raise ValueError("CPU_NOT_ALLOWED_BY_HOST")

    initial_disk = allocated_bytes(cwd)
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    peak_rss, peak_pids, peak_disk_delta = 0, 0, 0
    stopped_by_timeout = False
    output_path = stdout or report.with_suffix(".stdout.log")
    error_path = stderr or report.with_suffix(".stderr.log")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    error_path.parent.mkdir(parents=True, exist_ok=True)

    def pin():
        os.sched_setaffinity(0, {selected})

    with output_path.open("wb") as out, error_path.open("wb") as err:
        p = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                             stdout=out, stderr=err, start_new_session=True,
                             preexec_fn=pin)
        try:
            while True:
                rss, nproc = group_rss(p.pid)
                peak_rss = max(peak_rss, rss)
                peak_pids = max(peak_pids, nproc)
                peak_disk_delta = max(peak_disk_delta, max(0, allocated_bytes(cwd) - initial_disk))
                if p.poll() is not None and nproc == 0:
                    break
                if time.monotonic() - start >= timeout_s:
                    stopped_by_timeout = True
                    os.killpg(p.pid, signal.SIGKILL)
                    break
                time.sleep(sample_s)
            code = p.wait()
        finally:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
    seconds = time.monotonic() - start
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    rec = {
        "status": "TIMEOUT" if stopped_by_timeout else "FINISHED",
        "exit_code": code,
        "command_executable": command[0],
        "argv_length_bytes": sum(len(a.encode("utf-8")) for a in command[1:]),
        "cpu_affinity": [selected],
        "child_process_affinity_inherited": True,
        "process_group_tracked_after_leader_exit": True,
        "wall_seconds": round(seconds, 4),
        "child_user_cpu_seconds": round(ru1.ru_utime - ru0.ru_utime, 4),
        "child_system_cpu_seconds": round(ru1.ru_stime - ru0.ru_stime, 4),
        "rss_sum_observed_peak_bytes": peak_rss,
        "concurrent_descendants_observed_peak": peak_pids,
        "disk_allocated_delta_observed_peak_bytes": peak_disk_delta,
        "sampling_interval_seconds": sample_s,
        "memory_limit_project_assumption_bytes": DEFAULT_MEMORY_LIMIT,
        "disk_limit_project_assumption_bytes": DEFAULT_DISK_LIMIT,
        "memory_below_project_limit_observed": peak_rss <= DEFAULT_MEMORY_LIMIT,
        "disk_below_project_limit_observed": peak_disk_delta <= DEFAULT_DISK_LIMIT,
        "output_log": str(output_path),
        "error_log": str(error_path),
        "official_hutter_compliance": None,
        "note": "Sampling can miss short peaks; GB/GiB and normalized runtime require independent jury checks.",
    }
    report.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--sample-seconds", type=float, default=0.20)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    result = run(command, args.cwd, args.report,
                 timeout_s=args.timeout_seconds, sample_s=args.sample_seconds, cpu=args.cpu)
    print(json.dumps({k: v for k, v in result.items() if k not in ("output_log", "error_log")}, indent=2))
    if result["exit_code"] != 0 or result["status"] != "FINISHED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
