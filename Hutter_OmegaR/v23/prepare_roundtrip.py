#!/usr/bin/env python3
"""OMÉGA-R v0.23: source-pinned genuine cmix bitstream prefix roundtrip harness.

Integration experiment only. Does not create an autonomous Hutter archive.
Upstream sources are GPL-3.0-only; preserve notices, never redistribute raw
enwik9 / preprocessed bytes / model weights or modified upstream binaries.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'v21'))
from prepare_shadow import COMMIT,PINS,blob,patch_sources

ENC_PREFIX_AT='  dict_article::strom = temp_bytes;'
ENC_PREFIX_SOURCE='''  // OMR23: retain a raw prefix reference to verify the genuine inverse coder.
  if (const char* raw_limit = std::getenv("OMR21_SHADOW_PREFIX_BYTES")) {
    const unsigned long long n = std::strtoull(raw_limit,nullptr,10);
    if(n<65536ull || n>1048576ull || n>temp_bytes) std::exit(181);
    FILE* src = fopen(temp_path.c_str(), "rb");
    FILE* dst = fopen("omr23-reference-prefix.bin", "wb");
    if(!src || !dst)std::exit(182);
    unsigned long long pending=n;
    char b[65536];
    while(pending){
      const size_t count=(size_t)(pending<sizeof(b)?pending:sizeof(b));
      const size_t got=fread(b,1,count,src);
      if(got!=count || fwrite(b,1,got,dst)!=got)std::exit(183);
      pending-=got;
    }
    fclose(src);fclose(dst);
  }
'''
DECODE_LOOP_END='  run_mode::gram.Report("decompress");'
DEC_RUN='    Decompress(*output_bytes, data_in, temp_out, &p);'
DECODE_START='  malloc_trim(0);\n  if (!text_start::Unpack(temp_path, !MetablockInert())) {'
MAIN_MALLOPT='  mallopt(M_MMAP_THRESHOLD, 1 << 20);'
MAIN_DEC='    if (!RunDecompression(input_path, temp_path, output_path, dictionary,\n        &input_bytes, &output_bytes)) {'


def transform(files:dict[str,bytes])->dict[str,bytes]:
    # Original encoder AND decoder untouched; reuse the pinned v0.21 runner cap.
    patches=patch_sources(files,b'',shadow=False)
    code=patches['src/runner.cpp'].decode()
    def unique(anchor:str,replacement:str,label:str):
        nonlocal code
        if code.count(anchor)!=1:raise ValueError('ANCHOR_'+label+'_NOT_UNIQUE')
        code=code.replace(anchor,replacement,1)
    unique(ENC_PREFIX_AT,ENC_PREFIX_SOURCE+ENC_PREFIX_AT,'ENCODER_PRECODER_INPUT')
    unique(DECODE_LOOP_END,
           '  if (std::getenv("OMR23_PREFIX_DECODE")) return;\n'+DECODE_LOOP_END,
           'DECODE_REPORT')
    unique(DEC_RUN,'''    const char* prefix_req=std::getenv("OMR23_PREFIX_DECODE");
    unsigned long long decode_bytes=*output_bytes;
    if(prefix_req){
      char* end=nullptr;
      const unsigned long long count=std::strtoull(prefix_req,&end,10);
      if(!*prefix_req || *end || count<65536ull || count>1048576ull || count>*output_bytes)std::exit(185);
      decode_bytes=count;
    }
    Decompress(decode_bytes, data_in, temp_out, &p);''','DECOMPRESS_SIZE')
    unique(DECODE_START,'''  if (std::getenv("OMR23_PREFIX_DECODE")) {
    const unsigned long long n=std::strtoull(std::getenv("OMR23_PREFIX_DECODE"),nullptr,10);
    if(rename(temp_path.c_str(),"omr23-decoded-prefix.bin")!=0) return false;
    *output_bytes=n;
    return true;
  }
'''+DECODE_START,'DECOMPRESS_INVERSION_SKIP')
    unique(MAIN_MALLOPT,MAIN_MALLOPT+'''
  if (std::getenv("OMR23_PREFIX_DECODE")) ppmd_page::hilfs=0;''',
           'DECODE_PPMD_MODE')
    unique(MAIN_DEC,'''    if (std::getenv("OMR23_PREFIX_DECODE")) {
      census_block_active=true;
      isbn_check::after_at.an=true;
    }
'''+MAIN_DEC,'DECODE_PRODUCTION_FLAGS')
    if code.count('OMR23_PREFIX_DECODE')!=6:
        raise AssertionError('UNEXPECTED_NUMBER_OF_DECODE_HOOKS')
    return {'src/runner.cpp':code.encode()}


def prepare(src:Path,dst:Path)->dict:
    head=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
    if head!=COMMIT:raise ValueError('UPSTREAM_COMMIT_DRIFT')
    if subprocess.check_output(['git','-C',str(src),'status','--porcelain'],text=True).strip():
        raise ValueError('DIRTY_UPSTREAM')
    if dst.exists() or dst.resolve().is_relative_to(src.resolve()):raise ValueError('UNSAFE_OUTPUT')
    files={p:(src/p).read_bytes() for p in PINS}
    patch=transform(files)
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.git','.build','run','comp9','__pycache__'))
    for p,b in patch.items():(dst/p).write_bytes(b)
    if not (dst/'LICENSE').is_file():raise ValueError('UPSTREAM_GPL_LICENSE_NOT_PRESERVED')
    record={'status':'ROUNDTRIP_PRODUCTION_PREFIX_INSTRUMENTED_NOT_CODED',
            'upstream_commit':head,'patched_runner_sha256':hashlib.sha256(patch['src/runner.cpp']).hexdigest(),
            'unmodified_encoder_git_blob':blob((dst/'src/coder/encoder.cpp').read_bytes()),
            'unmodified_decoder_git_blob':blob((dst/'src/coder/decoder.cpp').read_bytes()),
            'stream_cap_bytes':524288,'reference_file':'omr23-reference-prefix.bin',
            'decoded_file':'omr23-decoded-prefix.bin','arithmetic_prefix_file':'omr21-coded-prefix.bin',
            'official_score':None,'archive9':False,'whole_enwik9_decoded':False}
    (dst.parent/'omr23-preflight.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    print(json.dumps(prepare(a.upstream,a.output),indent=2))
