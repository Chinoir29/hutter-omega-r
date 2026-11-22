// Independent fixed-vector fingerprint of Q32 Bayesian predictor, GPL-3.0-only.
#include "omr28_bayes_bitmix.h"
#include <cstdint>
#include <cstdio>
int main(){
  uint64_t check=UINT64_C(1469598103934665603);
  uint32_t state=0x9e3779b9u;
  for(unsigned i=0;i<8192;++i){
    state=state*1664525u+1013904223u;
    uint32_t ctx=1u+(state>>16)%255u;
    uint32_t base=1u+(state%4294967294u);
    int bit=(state>>31)&1u;
    uint32_t got=omr28_bitmix::Before(base,ctx);
    check=(check^got)*UINT64_C(1099511628211);
    omr28_bitmix::After(bit);
  }
  std::printf("OMR28_Q32_CROSS_IMPL %016llx\n",(unsigned long long)check);
}
