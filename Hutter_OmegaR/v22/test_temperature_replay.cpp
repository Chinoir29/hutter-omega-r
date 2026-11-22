#include "omr22_temperature.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
static void Replay(){
  for(unsigned j=0;j<400000;++j){
    const uint32_t p=1u+((uint64_t)(j+17u)*2654435761ull % 4294967294ull);
    const uint32_t ctx=1u<<((j/101)&7u);
    const int bit=(j%17)<8;
    assert(omr21_shadow::Before(p,ctx)==p);
    omr21_shadow::After(bit);
  }
}
int main(){
  setenv("OMR21_SHADOW_PREFIX_BYTES","524288",1);
  Replay();
  const auto original=omr21_shadow::S();
  omr21_shadow::S()=omr21_shadow::State{};
  Replay();
  const auto again=omr21_shadow::S();
  assert(original.train_bits==262144 && original.holdout_bits==137856);
  assert(again.train_bits==original.train_bits && again.holdout_bits==original.holdout_bits);
  assert(original.selection_frozen && again.selection_frozen);
  for(int k=0;k<8;++k)assert(original.pos_select[k]==again.pos_select[k]);
  for(int i=0;i<7;++i){
    assert(original.train[i]==again.train[i]);
    assert(original.holdout[i]==again.holdout[i]);
  }
  omr21_shadow::Report();
  std::puts("OMR22_DETERMINISTIC_REPLAY_TEST_OK");
}
