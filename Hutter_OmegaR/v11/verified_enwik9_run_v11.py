#!/usr/bin/env python3
"""Verify official enwik9 and run a local score test of OMÉGA-R v0.11.

Requires canonical enwik9 (1_000_000_000 bytes, SHA256 below), Linux x86-64,
/usr/bin/time, Python 3, CPU affinity support, and a built v6/comp9.

The test is LOCAL, not a Hutter Prize judgement. A pass does NOT confer eligibility
or award; the committee independently validates RAM, deadlines, source and score.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, shutil, subprocess, tempfile, time

OFFICIAL_SIZE=1_000_000_000
OFFICIAL_SHA256='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
AWARDED_REFERENCE_20261121=100_424_672
AWARDED_1PCT_CEILING=99_420_425
PENDING_CANDIDATE_20261121=93_388_956
PENDING_1PCT_CEILING=92_455_066
PROGRAM=pathlib.Path(__file__).resolve().parent/'comp9_mode2'

def sha256_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''): h.update(block)
 return h.hexdigest()

def run_checked(argv, cwd, max_hours, cpu):
 def preexec():
  os.sched_setaffinity(0,{cpu})
 start=time.monotonic()
 r=subprocess.run(['/usr/bin/time','-f','__OMR6_TIME__%e %M %U %S',*argv],
  cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
  timeout=int(max_hours*3600),preexec_fn=preexec)
 if r.returncode!=0:raise RuntimeError(f'Command failed: {argv}; exit={r.returncode}; tail={r.stderr[-3000:]!r}')
 out=r.stderr.decode('utf8','replace')
 records=[x.split('__OMR6_TIME__',1)[1].split() for x in out.splitlines() if x.startswith('__OMR6_TIME__')]
 if len(records)!=1:raise RuntimeError('No unambiguous memory/time measurements')
 wall,rss,user,system=map(float,records[0])
 return {'wall_seconds':round(time.monotonic()-start,3),'reported_wall_seconds':wall,
         'max_rss_kib':int(rss),'user_cpu_s':user,'system_cpu_s':system,
         'cpu_core':cpu,'command':argv,'stderr_tail':out[-1400:]}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('enwik9',type=pathlib.Path,help='Raw, extracted original file (not a .zip)')
 ap.add_argument('--out',type=pathlib.Path,default=pathlib.Path('hutter_v6_local_enwik9.json'))
 ap.add_argument('--limit-hours',type=float,default=50.0)
 args=ap.parse_args()
 src=args.enwik9.resolve()
 if not src.is_file():raise SystemExit('BLOCKED: official enwik9 file is missing')
 if src.stat().st_size!=OFFICIAL_SIZE:raise SystemExit('BLOCKED: file length differs from 1,000,000,000 bytes')
 actual=sha256_file(src)
 if actual!=OFFICIAL_SHA256:raise SystemExit('BLOCKED: enwik9 SHA-256 mismatch')
 if not PROGRAM.is_file():raise SystemExit('BLOCKED: compile OMÉGA-R v0.6 comp9 first')
 if os.name!='posix' or not hasattr(os,'sched_getaffinity'):raise SystemExit('BLOCKED: Linux CPU affinity required')
 if not pathlib.Path('/usr/bin/time').is_file():raise SystemExit('BLOCKED: /usr/bin/time required')
 cpu=min(os.sched_getaffinity(0))
 with tempfile.TemporaryDirectory(prefix='omr6_full_enwik9_') as d:
  root=pathlib.Path(d);enc=root/'encoder';dec=root/'decoder';enc.mkdir();dec.mkdir()
  shutil.copyfile(src,enc/'enwik9')
  shutil.copyfile(PROGRAM,enc/'comp9');(enc/'comp9').chmod(0o755)
  compress=run_checked(['./comp9'],enc,args.limit_hours,cpu)
  arc=enc/'archive9'
  if not arc.is_file():raise RuntimeError('Missing archive9')
  program_bytes=(enc/'comp9').stat().st_size
  archive_bytes=arc.stat().st_size
  shutil.copyfile(arc,dec/'archive9');(dec/'archive9').chmod(0o755)
  if (dec/'enwik9').exists():raise RuntimeError('No isolation of decoder')
  decompress=run_checked(['./archive9'],dec,args.limit_hours,cpu)
  decoded=dec/'data9'
  if not decoded.is_file() or decoded.stat().st_size!=OFFICIAL_SIZE or sha256_file(decoded)!=OFFICIAL_SHA256:
   raise RuntimeError('Full reconstruction is NOT byte-identical')
  score=program_bytes+archive_bytes
  result={'version':'OMÉGA-R v0.11','verified_official_input':True,
   'source_sha256':actual,'verified_full_roundtrip_sha256':True,
   'organizer_verified':False,'official_record_awarded':False,
   'score_bytes_LOCAL_only':score,'comp9_bytes':program_bytes,'archive9_bytes':archive_bytes,
   'comp9_sha256':sha256_file(enc/'comp9'),'archive9_sha256':sha256_file(arc),
   'baseline_v06_git_run_score_bytes':284637047,'delta_vs_v06_full_bytes':score-284637047,
   'no_runtime_options_counted':True,
   'award_ceiling_2026_11_21':AWARDED_1PCT_CEILING,
   'pending_candidate_2026_11_21':PENDING_CANDIDATE_20261121,
   'pending_candidate_1pct_ceiling_if_awarded':PENDING_1PCT_CEILING,
   'locally_below_awarded_1pct_ceiling':score<=AWARDED_1PCT_CEILING,
   'locally_below_pending_1pct_ceiling':score<=PENDING_1PCT_CEILING,
   'compression':compress,'decompression':decompress,
   'warning':'Local single-core benchmark only; hardware-normalized deadlines and compliance must be checked by Hutter Prize committee.'}
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
