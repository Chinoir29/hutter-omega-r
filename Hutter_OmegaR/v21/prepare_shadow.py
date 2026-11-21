#!/usr/bin/env python3
"""Prepare two source-pinned ephemeral research builds, no upstream redistribution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

COMMIT = '35d1957a5074db802fc134126afc77b76d931761'
PINS = {
    'src/runner.cpp': '4f9ee4adfeef37069eecf95bf8efb4c0d03cf09b',
    'src/coder/encoder.cpp': 'c7299664111582c04c5d1fee4a545505e46f10d0',
    'src/coder/decoder.cpp': '58f5d01bb4520378968fc43f226486ea56ea9bc7',
}


def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def patch_sources(files:dict[str,bytes],header:bytes, shadow:bool=True)->dict[str,bytes]:
    for p,expected in PINS.items():
        if blob(files[p])!=expected:
            raise ValueError('PINNED_SOURCE_BLOB_MISMATCH '+p)
    code = files['src/coder/encoder.cpp'].decode()
    if code.count('#include "encoder.h"')!=1:
        raise ValueError('ENCODER_INCLUDE_ANCHOR_DRIFT')
    code=code.replace('#include "encoder.h"','#include "encoder.h"\n#include "../omr21_shadow.h"')
    left='  const unsigned int xmid = floor_stage::Mid(x1_, x2_, p_->SemCorrect(floor_.P32(p,'
    right='      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7)));'
    if code.count(left)!=1 or code.count(right)!=1:
        raise ValueError('ARITHMETIC_PROBABILITY_ANCHOR_DRIFT')
    code=code.replace(left,'  const unsigned int omr21_p32 = p_->SemCorrect(floor_.P32(p,',1)
    code=code.replace(right,'      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7));\n  const unsigned int xmid = floor_stage::Mid(x1_, x2_, omr21_shadow::Before(omr21_p32, p_->BbBitCtx()));',1)
    if code.count('  p_->SemLearn(bit);')!=1: raise ValueError('SEM_LEARN_ANCHOR_DRIFT')
    code=code.replace('  p_->SemLearn(bit);','  p_->SemLearn(bit);\n  omr21_shadow::After(bit);',1)
    tail='  total_out_ += out_n_;\n  out_n_ = 0;\n}'
    if code.count(tail)!=1: raise ValueError('FLUSH_ANCHOR_DRIFT')
    code=code.replace(tail,'  total_out_ += out_n_;\n  out_n_ = 0;\n  omr21_shadow::Report();\n}',1)
    runner=files['src/runner.cpp'].decode()
    anchor='  while (pos < input_bytes) {'
    if runner.count(anchor)!=1:raise ValueError('CODED_STREAM_PREFIX_ANCHOR_DRIFT')
    runner=runner.replace(anchor,'''  unsigned long long omr21_cap = input_bytes;
  if (const char* limit = std::getenv("OMR21_SHADOW_PREFIX_BYTES")) {
    char* end = nullptr;
    const unsigned long long n = std::strtoull(limit, &end, 10);
    if (!*limit || *end || n < 65536ull || n > 1048576ull || n > input_bytes) {
      std::fprintf(stderr, "OMR21_INVALID_PREFIX\\n"); std::exit(183);
    }
    omr21_cap = n;
  }
  while (pos < omr21_cap) {''',1)
    flush='  e.Flush();\n  run_mode::gram.Report("compress");'
    if runner.count(flush)!=1: raise ValueError('COMPRESS_FLUSH_ANCHOR_DRIFT')
    runner=runner.replace(flush,'  e.Flush();\n  if (std::getenv("OMR21_SHADOW_PREFIX_BYTES")) { *output_bytes=ftell(os); return; }\n  run_mode::gram.Report("compress");',1)
    anchor2='  Compress(temp_bytes, temp_in, data_out, output_bytes, &p);'
    if runner.count(anchor2)!=1:raise ValueError('RUN_COMPRESSION_ANCHOR_DRIFT')
    runner=runner.replace(anchor2,anchor2+'''
  if (std::getenv("OMR21_SHADOW_PREFIX_BYTES")) {
    std::fprintf(stderr,"OMR21_PREFIX_ACTUAL_CODED_STREAM_BYTES=%llu\\n",(unsigned long long)temp_bytes);
    fclose(temp_in); fclose(data_out);
    // Keep only until the two SHA-256 hashes are compared; not a prize archive.
    if (std::rename(output_path.c_str(), "omr21-coded-prefix.bin") != 0) std::exit(184);
    remove(temp_path.c_str());
    std::exit(0);
  }
''',1)
    edits={'src/runner.cpp':runner.encode()}
    if shadow: edits.update({'src/coder/encoder.cpp':code.encode(),'src/omr21_shadow.h':header})
    return edits


def prepare(src:Path,dest:Path,header:Path,shadow:bool=True)->dict:
    git=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
    if git!=COMMIT:raise ValueError('UNPINNED_UPSTREAM '+git)
    if subprocess.check_output(['git','-C',str(src),'status','--porcelain'],text=True).strip():
        raise ValueError('DIRTY_UPSTREAM')
    if dest.exists() or dest.resolve().is_relative_to(src.resolve()):
        raise ValueError('DEST_EXISTS_OR_NESTED')
    if not (src/'LICENSE').is_file():raise ValueError('GPL3_MISSING')
    original={p:(src/p).read_bytes() for p in PINS}
    edits=patch_sources(original,header.read_bytes(),shadow=shadow)
    shutil.copytree(src,dest,ignore=shutil.ignore_patterns('.git','.build','run','comp9','__pycache__'))
    for p,body in edits.items():(dest/p).write_bytes(body)
    record={'status':'SOURCE_PREPARED_NOT_CODED','arm':'shadow' if shadow else 'control','upstream_commit':git,
            'patches':{p:hashlib.sha256(b).hexdigest() for p,b in edits.items()},
            'untouched_decoder_blob':blob((dest/'src/coder/decoder.cpp').read_bytes()),
            'insertion':'read-only probability observer after SemCorrect, before Mid',
            'coded_stream_limit':'65536..1048576 bytes on true -e path',
            'expected_actual_arithmetic_change':False,'competition_score':None,
            'licence':'GPL-3.0-only upstream notices remain in ephemeral checkout'}
    (dest.parent/('omr21-source-audit-'+('shadow' if shadow else 'control')+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--header',type=Path,default=Path(__file__).with_name('omr21_shadow.h'))
    ap.add_argument('--control-output',type=Path)
    a=ap.parse_args()
    reports=[prepare(a.upstream,a.output,a.header,shadow=True)]
    if a.control_output: reports.append(prepare(a.upstream,a.control_output,a.header,shadow=False))
    print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
