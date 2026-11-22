#include "omr22_temperature.h"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
int main(){
 setenv("OMR21_SHADOW_PREFIX_BYTES","524288",1);
 for(uint64_t j=0;j<400000;++j){
   uint32_t p=(j&1)?0x55555555u:0xaaaaaaaau;
   uint32_t ctx=1u<<((j/32)&7u);
   assert(omr21_shadow::Before(p,ctx)==p);
   omr21_shadow::After((j%20)<12);
 }
 auto& s=omr21_shadow::S();
 assert(s.coded_bits==400000 && s.train_bits==262144 && s.holdout_bits==137856);
 assert(s.selection_frozen);
 assert(s.global_select==5); // deliberately overconfident model benefits from softening
 assert(s.holdout[s.global_select]<s.holdout[0]);
 assert(std::isfinite(omr21_shadow::SpecialistHoldout(s)));
 omr21_shadow::Report();
 std::puts("OMR22_BIASED_SPECIALIST_TEST_OK");
}