#!/usr/bin/env python3
"""Run the modified cmix-neif research -c/-d path on a reversible Wiki sample.

Verifies TWO roundtrips: arithmetic coder -> escaped stream -> original RAW
Wikimedia excerpt. Not an official archive: contest preprocessor is bypassed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path
from reversible_sample import (VOCAB_GIT_BLOB, codec, decode, file_sha,
                               git_blob_sha, parse_bitmap, sha)


def timed(cmd, cwd: Path, log: Path, timeout: int, cpu: int) -> dict:
    with log.open('wb') as stream:
        def pin(): os.sched_setaffinity(0,{cpu})
        result=subprocess.run(['/usr/bin/time','-f','__OMR17__%e %M %U %S',*cmd],
                              cwd=cwd,stdout=stream,stderr=subprocess.STDOUT,
                              timeout=timeout,preexec_fn=pin)
    tail=log.read_text(encoding='utf-8',errors='replace')
    if result.returncode:
        raise RuntimeError(f'Command {cmd!r} exited {result.returncode}: {tail[-1000:]}')
    lines=[line.split('__OMR17__',1)[1].split() for line in tail.splitlines()
           if line.startswith('__OMR17__')]
    if len(lines)!=1:
        raise RuntimeError('No unambiguous /usr/bin/time result')
    wall,rss,user,system=map(float,lines[0])
    if rss>10*1024*1024:
        raise RuntimeError('Experiment exceeds nominal 10 GiB RSS')
    return {'wall_s':wall,'max_rss_kib':int(rss),'cpu_user_s':user,
            'cpu_sys_s':system,'affinity_cpu':cpu}


def experiment(sample: Path, record: dict, binary: Path, weights: Path,
               header: Path, output: Path, timeout: int) -> dict:
    source=sample.read_bytes()
    if (len(source)!=record['encoded_bytes'] or sha(source)!=record['encoded_sha256']
            or record['raw_bytes']!=65536 or record['lossless_codec_verified'] is not True):
        raise RuntimeError('Nonmatching encoded input or manifest')
    head=header.read_bytes()
    if git_blob_sha(head)!=VOCAB_GIT_BLOB:
        raise RuntimeError('Incorrect source version of upstream vocabulary')
    bitmap=parse_bitmap(head)
    raw=decode(source,bitmap)
    if len(raw)!=record['raw_bytes'] or sha(raw)!=record['raw_sha256']:
        raise RuntimeError('Reversibility test failed before compression')
    del raw
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='omr17_enc_') as a, tempfile.TemporaryDirectory(prefix='omr17_dec_') as b:
        enc=Path(a);dec=Path(b)
        for folder in (enc,dec):
            shutil.copyfile(binary,folder/'cmix')
            (folder/'cmix').chmod(0o755)
            shutil.copyfile(weights,folder/weights.name)
        shutil.copyfile(sample,enc/'input')
        cpu=min(os.sched_getaffinity(0))
        compression=timed(['./cmix','-c','input','coder.bin'],enc,output/'encode.log',timeout,cpu)
        coder=enc/'coder.bin'
        if not coder.is_file() or coder.stat().st_size<=0:
            raise RuntimeError('Missing or empty lab arithmetic coder stream')
        shutil.copyfile(coder,dec/'coder.bin')
        decompression=timed(['./cmix','-d','coder.bin','recovered'],dec,output/'decode.log',timeout,cpu)
        restored=(dec/'recovered').read_bytes()
        if restored!=source:
            raise RuntimeError('Lab arithmetic coder did not reconstruct escaped stream exactly')
        recovered_raw=decode(restored,bitmap)
        if len(recovered_raw)!=record['raw_bytes'] or sha(recovered_raw)!=record['raw_sha256']:
            raise RuntimeError('Original raw enwik9 excerpt NOT restored exactly')
        return {
            'status':'two_stage_verified', 'research_only':True, 'contest_eligible':False,
            'full_enwik9':False, 'self_extracting_archive':False, 'hutter_score':None,
            'lossless_escape':True, 'roundtrip_escaped_sha256':True,
            'roundtrip_raw_excerpt_sha256':True,
            'offset_mib':record['offset_mib'], 'original_raw_bytes':record['raw_bytes'],
            'original_raw_sha256':record['raw_sha256'],
            'escaped_bytes':record['encoded_bytes'], 'escaped_sha256':record['encoded_sha256'],
            'lab_coder_bytes':coder.stat().st_size,'lab_coder_sha256':file_sha(coder),
            'unpacked_program_bytes':binary.stat().st_size,
            'unpacked_program_sha256':file_sha(binary),
            'compression':compression,'decompression':decompression,
        }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('sample','manifest','binary','weights','vocab-header','out'):
        p.add_argument('--'+x,required=True,type=Path)
    p.add_argument('--offset-mib',type=int,required=True)
    p.add_argument('--timeout',type=int,default=600)
    a=p.parse_args()
    report=json.loads(a.manifest.read_text())
    if (report.get('lossy_projection') is not False or report.get('hutter_score') is not None
          or report.get('contest_coding_path') is not False):
        p.error('Manifest incorrectly claims a competition-eligible transformation')
    item=next((s for s in report['samples'] if s['offset_mib']==a.offset_mib),None)
    if not item or a.sample.name!=item['file']:
        p.error('Sample does not belong to pinned manifest')
    try:
        r=experiment(a.sample.resolve(),item,a.binary.resolve(),a.weights.resolve(),
                     a.vocab_header.resolve(),a.out.resolve(),a.timeout)
    except Exception as exc:
        a.out.mkdir(parents=True,exist_ok=True)
        (a.out/'failure.json').write_text(json.dumps({'status':'failed','error':str(exc)[:1200],
             'hutter_score':None},indent=2)+'\n')
        raise
    (a.out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))

if __name__=='__main__': main()
