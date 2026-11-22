#include "omr22_temperature.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
int main(){
 setenv("OMR21_SHADOW_PREFIX_BYTES","524288",1);
 for(unsigned j=0;j<400000;++j){
   const uint32_t p=0xc0000000u; // p(one) = exactly 3/4
   const int bit=(j%4)!=0;       // exactly 3/4 observed ones
   const uint32_t ctx=1u<<((j>>5)&7u);
   assert(omr21_shadow::Before(p,ctx)==p);
   omr21_shadow::After(bit);
 }
 auto& s=omr21_shadow::S();
 assert(s.global_select==0);
 for(int k=0;k<8;++k) assert(s.pos_select[k]==0);
 assert(s.coded_bits==400000 && s.train_bits==262144);
 for(uint32_t p: {1u,17u,0x55555555u,0x80000000u,0xaaaaaaaau,0xffffffffu})
   for(int k=0;k<omr21_shadow::kModes;++k)
     assert(omr21_shadow::Temperature(p,k)>=1);
 omr21_shadow::Report();
 std::puts("OMR22_CALIBRATED_NULL_TEST_OK");
}