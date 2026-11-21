#!/usr/bin/env python3
"""Portable paired compression/decompression ablation, NOT a Hutter Prize score.
Run only after make_candidate.py and build.sh. Use --file path(s) to pass real data.
"""
import argparse, hashlib, json, pathlib, random, subprocess, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent

def evaluate(name, data, binary, mode, timeout):
  with tempfile.TemporaryDirectory(prefix='omr11_') as directory:
    d=pathlib.Path(directory);(d/'input').write_bytes(data)
    started=time.monotonic()
    enc=subprocess.run([str(binary),str(d/'input'),str(d/'archive9')],cwd=d,capture_output=True,timeout=timeout)
    seconds=time.monotonic()-started
    if enc.returncode:raise RuntimeError((name,mode,'encoder',enc.stderr[-1000:]))
    (d/'decoded').mkdir()
    dec=subprocess.run([str(d/'archive9')],cwd=d/'decoded',capture_output=True,timeout=timeout)
    if dec.returncode:raise RuntimeError((name,mode,'decoder',dec.stderr[-1000:]))
    restored=(d/'decoded'/'data9').read_bytes()
    if restored!=data:raise AssertionError('lossless reconstruction failure')
    return {'dataset':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
      'mode':mode,'comp9_bytes':binary.stat().st_size,'archive9_bytes':(d/'archive9').stat().st_size,
      'total_bytes':binary.stat().st_size+(d/'archive9').stat().st_size,
      'roundtrip':True,'compress_wall_s':round(seconds,3)}

def main():
  p=argparse.ArgumentParser(description=__doc__)
  p.add_argument('--file',type=pathlib.Path,action='append',default=[])
  p.add_argument('--out',type=pathlib.Path,default=ROOT/'portable_ablation.json')
  p.add_argument('--timeout',type=int,default=180)
  a=p.parse_args()
  rng=random.Random(2109)
  files=[('random_128k',rng.randbytes(128*1024)),('repetitive',b'abracadabra\n'*2500)]
  for path in a.file:
    files.append((str(path),path.read_bytes()))
  rows=[]
  for name,data in files:
    for mode in range(4):
      binary=ROOT/f'comp9_mode{mode}'
      if not binary.is_file():p.error('Build all four variants first: bash build.sh')
      row=evaluate(name,data,binary,mode,a.timeout)
      rows.append(row)
      print(name,'mode',mode,'total',row['total_bytes'],flush=True)
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
  print('Successful lossless reconstructions:',len(rows),'NOT a Hutter Prize score')
if __name__=='__main__':main()
