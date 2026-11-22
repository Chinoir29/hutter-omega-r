#include "omr22_temperature.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
int main(){
 setenv("OMR21_SHADOW_PREFIX_BYTES","524288",1);
 for(unsigned j=0;j<400000;++j){
   unsigned pos=(j/100)&7u;
   const int bit=(j%100)<((pos&1u)?50:90);
   const uint32_t p=0xc0000000u;
   assert(omr21_shadow::Before(p,1u<<pos)==p);
   omr21_shadow::After(bit);
 }
 auto& s=omr21_shadow::S();
 assert(s.selection_frozen);
 for(int pos=0;pos<8;++pos){
   if(pos&1)assert(s.pos_select[pos]==5);
   else assert(s.pos_select[pos]==6);
 }
 const double specialist=s.holdout[0]-omr21_shadow::SpecialistHoldout(s);
 const double global=s.holdout[0]-s.holdout[s.global_select];
 assert(specialist>global && specialist>0);
 omr21_shadow::Report();
 std::puts("OMR22_HETEROGENEOUS_POSITION_TEST_OK");
}
