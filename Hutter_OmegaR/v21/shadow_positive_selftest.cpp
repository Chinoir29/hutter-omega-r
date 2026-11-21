// Additional synthetic test: prove the shadow can detect a beneficial correction.
#include "omr21_shadow.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
int main(){
  setenv("OMR21_SHADOW_PREFIX_BYTES","524288",1);
  for(unsigned j=0;j<350000;++j){
    const unsigned k=(j/8)&7u;
    const uint32_t p=0x73333333u; // predicted 45% probability of bit 1
    const int bit=(j%5)!=0;        // observed 80% probability of bit 1
    assert(omr21_shadow::Before(p,1u<<k)==p);
    omr21_shadow::After(bit);
  }
  auto &s=omr21_shadow::S();
  int best=0;
  for(int j=1;j<4;++j)if(s.train[j]<s.train[best])best=j;
  assert(best>0);
  assert(s.validation[best]<s.validation[0]);
  omr21_shadow::Report();
  std::puts("OMR21_SHADOW_POSITIVE_SYNTHETIC_TEST_OK");
}
