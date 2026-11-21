#!/usr/bin/env python3
"""Run a lossless canary on a *small* reconstructed XML subset.

The output is NEVER a prize score: it is not enwik9, and program overhead and
execution constraints are not eligible for extrapolation. No remote work here.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, shutil, subprocess, tempfile


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as file:
        for chunk in iter(lambda:file.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def measured(command,cwd,phase,reports,timeout,cpu):
    output=reports/f'{phase}.log'
    time_log=reports/f'{phase}.resource.txt'
    with output.open('wb') as f:
        run=subprocess.run(['/usr/bin/time','-f','wall_s=%e\nmax_rss_kib=%M\nuser_cpu_s=%U\nsystem_cpu_s=%S',
            '-o',str(time_log),'taskset','-c',str(cpu),*command],cwd=cwd,
            stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    if run.returncode:
        raise RuntimeError(f'{phase} exited {run.returncode}; consult {output}')
    values=dict(line.strip().split('=',1) for line in time_log.read_text().splitlines())
    return {k:float(v) for k,v in values.items()}


def run(sample,compressor,reports,timeout=1500):
    reports.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='omr12_cmix_enc_') as tmp, tempfile.TemporaryDirectory(prefix='omr12_cmix_dec_') as dt:
        root=pathlib.Path(tmp);enc=root/'enc';dec=pathlib.Path(dt)/'dec';enc.mkdir();dec.mkdir()
        original=enc/'canary.xml'
        shutil.copyfile(sample,original)
        shutil.copyfile(compressor,enc/'comp9')
        (enc/'comp9').chmod(0o755)
        cpu=min(os.sched_getaffinity(0))
        comp=measured(['./comp9','-e',str(original),'archive9'],enc,'compress',reports,timeout,cpu)
        archive=enc/'archive9'
        if not archive.is_file() or archive.stat().st_size==0:
            raise RuntimeError('cmix-neif did not produce archive9')
        shutil.copyfile(archive,dec/'archive9');(dec/'archive9').chmod(0o755)
        decomp=measured(['./archive9'],dec,'decompress',reports,timeout,cpu)
        output=dec/'enwik9_uncompressed'
        if not output.is_file() or output.stat().st_size!=original.stat().st_size or sha(output)!=sha(original):
            raise RuntimeError('Decoder output is absent or SHA-256 differs')
        return {'status':'pass','source':'subset of authentic enwik9',
                'official_hutter_score':None,'enwik9_full_tested':False,
                'sample_bytes':original.stat().st_size,'sample_sha256':sha(original),
                'compressor_bytes':(enc/'comp9').stat().st_size,
                'compressor_sha256':sha(enc/'comp9'),
                'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),
                'standalone_decoder':True,'roundtrip_sha256_verified':True,
                'single_cpu_affinity':cpu,'compression':comp,'decompression':decomp}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample',type=pathlib.Path,required=True)
    parser.add_argument('--comp9',type=pathlib.Path,required=True)
    parser.add_argument('--reports',type=pathlib.Path,required=True)
    parser.add_argument('--timeout',type=int,default=1500)
    a=parser.parse_args()
    if not a.sample.is_file() or not a.comp9.is_file():parser.error('Missing sample or executable')
    try:
        out=run(a.sample.resolve(),a.comp9.resolve(),a.reports.resolve(),a.timeout)
    except Exception as err:
        a.reports.mkdir(parents=True,exist_ok=True)
        (a.reports/'failure.json').write_text(json.dumps({'status':'error','error':str(err),
             'official_hutter_score':None},indent=2)+'\n')
        raise
    (a.reports/'result.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
