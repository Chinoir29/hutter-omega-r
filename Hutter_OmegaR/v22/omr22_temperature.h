// OMÉGA-R v0.22: shadow logistic temperature specialists, GPL-3.0-only.
// Diagnostic of actual cmix coded bits, without changing arithmetic probability.
#ifndef OMR22_TEMPERATURE_H_
#define OMR22_TEMPERATURE_H_
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
namespace omr21_shadow {
// Reuse proven v0.21 source-pinner API; no modification of its decoder or stream.
constexpr int kModes=7, kPositions=8;
constexpr uint64_t kTrainBits=262144;
constexpr double kScale[kModes]={1.0,0.93,0.97,1.03,1.07,0.85,1.15};
struct State {
  uint64_t coded_bits=0, train_bits=0, holdout_bits=0;
  uint64_t train_pos_count[kPositions]={}, hold_pos_count[kPositions]={};
  double train[kModes]={}, holdout[kModes]={};
  double train_pos[kPositions][kModes]={}, hold_pos[kPositions][kModes]={};
  uint32_t pending_p=0;
  int pending_pos=-1;
  int global_select=0, pos_select[kPositions]={};
  bool selection_frozen=false;
};
inline State& S(){static State s;return s;}
inline bool Enabled(){static const bool on=std::getenv("OMR21_SHADOW_PREFIX_BYTES")!=nullptr;return on;}
inline int Position(uint32_t ctx){
  const int pos=31-__builtin_clz(ctx|1u);
  if(pos<0||pos>=kPositions)std::abort();
  return pos;
}
inline uint32_t Temperature(uint32_t p,int mode){
  if(mode<0||mode>=kModes||p==0)std::abort();
  if(mode==0)return p;
  constexpr double D=4294967296.0;
  const double logit=std::log((double)p/(D-(double)p));
  const double q=1.0/(1.0+std::exp(-kScale[mode]*logit));
  const double v=std::floor(q*D+0.5);
  return (uint32_t)(v<1.0?1.0:v>4294967295.0?4294967295.0:v);
}
inline double Bits(uint32_t p,int actual){
  constexpr double D=4294967296.0;
  const double q=(double)p/D;
  return -std::log2(actual?q:1.0-q);
}
inline uint32_t Before(uint32_t p,uint32_t ctx){
  if(!Enabled())return p;
  State& s=S();
  if(s.pending_pos!=-1)std::abort();
  s.pending_p=p;
  s.pending_pos=Position(ctx);
  return p; // strict observer identity: coder receives original probability
}
inline void Freeze(State& s){
  if(s.selection_frozen)return;
  if(s.train_bits!=kTrainBits)std::abort();
  for(int m=1;m<kModes;++m)
    if(s.train[m]<s.train[s.global_select])s.global_select=m;
  for(int k=0;k<kPositions;++k){
    int best=0;
    for(int m=1;m<kModes;++m)
      if(s.train_pos[k][m]<s.train_pos[k][best])best=m;
    s.pos_select[k]=best;
  }
  s.selection_frozen=true;
}
inline void After(int bit){
  if(!Enabled())return;
  State& s=S();
  if(s.pending_pos<0||(bit!=0&&bit!=1))std::abort();
  if(s.train_bits==kTrainBits)Freeze(s);
  const int k=s.pending_pos;
  const bool training=s.coded_bits<kTrainBits;
  for(int m=0;m<kModes;++m){
    const double b=Bits(Temperature(s.pending_p,m),bit);
    if(training){s.train[m]+=b;s.train_pos[k][m]+=b;}
    else{s.holdout[m]+=b;s.hold_pos[k][m]+=b;}
  }
  if(training){++s.train_bits;++s.train_pos_count[k];}
  else{++s.holdout_bits;++s.hold_pos_count[k];}
  ++s.coded_bits;
  s.pending_pos=-1;
}
inline double SpecialistHoldout(const State& s){
  double v=0;
  for(int k=0;k<kPositions;++k)v+=s.hold_pos[k][s.pos_select[k]];
  return v;
}
inline void Report(){
  if(!Enabled())return;
  State& s=S();
  if(s.pending_pos>=0)std::abort();
  if(s.train_bits==kTrainBits)Freeze(s);
  const double global_gain=s.holdout[0]-s.holdout[s.global_select];
  const double position_gain=s.holdout[0]-SpecialistHoldout(s);
  std::fprintf(stderr,"OMR22_TEMPERATURE_RESULT {\"coded_bits\":%llu,\"train_bits\":%llu,\"holdout_bits\":%llu,\"train_loss_bits\":[",
    (unsigned long long)s.coded_bits,(unsigned long long)s.train_bits,(unsigned long long)s.holdout_bits);
  for(int m=0;m<kModes;++m)std::fprintf(stderr,"%s%.8f",m?",":"",s.train[m]);
  std::fprintf(stderr,"],\"holdout_loss_bits\":[");
  for(int m=0;m<kModes;++m)std::fprintf(stderr,"%s%.8f",m?",":"",s.holdout[m]);
  std::fprintf(stderr,"],\"temperatures\":[");
  for(int m=0;m<kModes;++m)std::fprintf(stderr,"%s%.2f",m?",":"",kScale[m]);
  std::fprintf(stderr,"],\"global_train_choice\":%d,\"position_train_choices\":[",s.global_select);
  for(int k=0;k<kPositions;++k)std::fprintf(stderr,"%s%d",k?",":"",s.pos_select[k]);
  std::fprintf(stderr,"],\"global_holdout_gain_bits\":%.8f,\"position_holdout_gain_bits\":%.8f,\"real_probabilities_changed\":false}\n",global_gain,position_gain);
}
} // omr21_shadow
#endif
