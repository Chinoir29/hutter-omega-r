#!/usr/bin/env python3
"""Generate OMÉGA-R v0.11 source by one auditable substitution in v0.6.
The transformation is intentionally checked before writing output.
"""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'v6'/'omr6_sfx.cpp'
TARGET=ROOT/'omr11_fold_word.cpp'
HEAD='''// OMEGA-R v0.11 experimental mutually exclusive word normalizations.
// Build modes: 0 original, 1 ASCII case-fold, 2 ASCII case-fold + digit fold,
// 3 digit fold only.  No new model tables or extra memory.
// All states are functions of already decoded bytes: exact round trips required.
// ABLATION ONLY: no verified enwik9 improvement or Hutter Prize score.
#ifndef OMR11_FOLD
#define OMR11_FOLD 0
#endif
static_assert(OMR11_FOLD>=0 && OMR11_FOLD<=3, "Invalid OMR11_FOLD");
'''
OLD='''      word=word*1315423911ull+uint64_t(c)+1;
'''
NEW='''      unsigned normalized=c;
#if OMR11_FOLD==1 || OMR11_FOLD==2
      if(normalized>='A' && normalized<='Z') normalized+=('a'-'A');
#endif
#if OMR11_FOLD==2 || OMR11_FOLD==3
      if(normalized>='0' && normalized<='9') normalized='#';
#endif
      word=word*1315423911ull+uint64_t(normalized)+1;
'''
base=SOURCE.read_text(encoding='utf-8')
if base.count(OLD)!=1 or base.count('namespace omr6 {')!=1:
    raise SystemExit('BLOCKED: baseline source mismatch')
result=base.replace(OLD, NEW).replace('namespace omr6 {',HEAD+'\nnamespace omr6 {')
TARGET.write_text(result,encoding='utf-8')
print(TARGET,hashlib.sha256(result.encode()).hexdigest())
