// Standalone synthetic unit test; no Wikipedia source required.
#include "omr21_shadow.h"
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <cstdio>
int main() {
  setenv("OMR21_SHADOW_PREFIX_BYTES","131072",1);
  assert(omr21_shadow::Corrected(1,0,0)==1);
  assert(omr21_shadow::Corrected(4294967295u,65536,3)==4294967295u);
  assert(omr21_shadow::Corrected(1,-65536,3)==1);
  assert(omr21_shadow::Bucket(0x80000000u,1u)==0);
  assert(omr21_shadow::Bucket(0x80000000u,128u)==28);
  for(int j=0;j<350000;++j){
    const unsigned int ctx=1u<<((j>>4)&7);
    const uint32_t p=(j&1)?0x33333333u:0xCCCCCCCCu;
    assert(omr21_shadow::Before(p,ctx)==p);
    omr21_shadow::After((j>>3)&1);
  }
  auto &s=omr21_shadow::S();
  assert(s.bits==350000u);
  assert(s.train_n==omr21_shadow::kTrainBits);
  assert(s.validation_n==350000u-omr21_shadow::kTrainBits);
  for(int k=0;k<4;++k) {
    assert(std::isfinite(s.train[k]));assert(std::isfinite(s.validation[k]));
    assert(s.train[k]>0 && s.validation[k]>0);
  }
  omr21_shadow::Report();
  std::puts("OMR21_SHADOW_SYNTHETIC_SELFTEST_OK");
}
