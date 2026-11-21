#!/usr/bin/env python3
"""A/B laboratory codec roundtrip for the modified full-model -c/-d interface.

The archive is NOT self-extracting and the source has been transformed to
satisfy the upstream hard-coded byte alphabet. No Hutter Prize score.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

def sha(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for p in iter(lambda:f.read(1<<20),b''):h.update(p)
    return h.hexdigest()

def timed(argv,cwd:Path,dest:Path,limit:int,cpu:int):
    with dest.open('wb') as output:
        def affinity():os.sched_setaffinity(0,{cpu})
        p=subprocess.run(['/usr/bin/time','-f','__OMR14__%e %M %U %S',*argv],
            cwd=cwd,stdout=output,stderr=subprocess.STDOUT,
            timeout=limit,preexec_fn=affinity)
    txt=dest.read_text(encoding='utf8',errors='replace')
    records=[line.split('__OMR14__',1)[1].split() for line in txt.splitlines()
             if line.startswith('__OMR14__')]
    if p.returncode!=0:
        raise RuntimeError(f'{argv[0]} exited {p.returncode}: {txt[-1300:]}')
    if len(records)!=1:
        raise RuntimeError('Missing unambiguous elapsed-time and RSS values')
    wall,rss,user,system=map(float,records[0])
    return dict(wall_s=wall,max_rss_kib=int(rss),user_cpu_s=user,system_cpu_s=system,
                affinity_cpu=cpu)

def run(sample,raw_bin,weights,report_dir,timeout):
    report_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='omr14_encode_') as en, tempfile.TemporaryDirectory(prefix='omr14_decode_') as de:
        enc=Path(en);dec=Path(de)
        for folder in (enc,dec):
            shutil.copyfile(raw_bin,folder/'cmix')
            (folder/'cmix').chmod(0o755)
            shutil.copyfile(weights,folder/weights.name)
        shutil.copyfile(sample,enc/'input')
        cp=min(os.sched_getaffinity(0))
        c=timed(['./cmix','-c','input','coder.bin'],enc,report_dir/'encode.log',timeout,cp)
        compressed=enc/'coder.bin'
        if not compressed.is_file() or compressed.stat().st_size==0:
            raise RuntimeError('Missing or empty coder.bin')
        shutil.copyfile(compressed,dec/'coder.bin')
        d=timed(['./cmix','-d','coder.bin','restored'],dec,report_dir/'decode.log',timeout,cp)
        restored=dec/'restored'
        if not restored.is_file() or restored.stat().st_size!=sample.stat().st_size or sha(restored)!=sha(sample):
            raise RuntimeError('Lossless decoded bytes are missing or mismatched')
        return dict(
            status='verified_roundtrip',research_only=True,
            hutter_score_bytes=None,full_enwik9=False,upstream_release_unmodified=False,
            model_build='full-model original source plus OMR14 laboratory -c parser patch',
            source_bytes=sample.stat().st_size,source_sha256=sha(sample),
            lab_coder_bytes=compressed.stat().st_size,lab_coder_sha256=sha(compressed),
            unpacked_program_bytes=raw_bin.stat().st_size,unpacked_program_sha256=sha(raw_bin),
            self_extracting_archive=False,
            lossless_roundtrip_verified=True,
            compression=c,decompression=d)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sample',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--weights',type=Path,required=True)
    p.add_argument('--reports',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=900)
    a=p.parse_args()
    try:
        d=run(a.sample.resolve(),a.binary.resolve(),a.weights.resolve(),a.reports.resolve(),a.timeout)
    except Exception as e:
        a.reports.mkdir(parents=True,exist_ok=True)
        (a.reports/'failure.json').write_text(json.dumps({'status':'error','reason':str(e),
           'prize_score':None},indent=2)+'\n')
        raise
    (a.reports/'coder_report.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(d,indent=2))
if __name__=='__main__':main()
