// OMÉGA-R v0.21: diagnostic shadow probabilities only. GPL-3.0-only.
// Added to an ephemeral copy of cmix-neif-2.0; NEVER changes encoder probability.
#ifndef OMR21_SHADOW_H_
#define OMR21_SHADOW_H_
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace omr21_shadow {
static constexpr uint64_t kTrainBits = 262144;
static constexpr int kVariants = 4;
struct State {
  int32_t ema[32] = {};
  uint64_t bits = 0, train_n = 0, validation_n = 0;
  double train[kVariants] = {}, validation[kVariants] = {};
  uint32_t pending_p = 0;
  int pending_bucket = -1;
};
inline State& S() { static State s; return s; }
inline bool Enabled() {
  // Set only on a research-only build started with a canonical -e prefix flag.
  static const bool enabled = std::getenv("OMR21_SHADOW_PREFIX_BYTES") != nullptr;
  return enabled;
}
inline uint32_t Corrected(uint32_t p, int32_t ema_q16, int variant) {
  if (variant < 0 || variant >= kVariants) std::abort();
  const int64_t n = (int64_t)p + ((int64_t)ema_q16 * variant * 65536) / 4;
  return (uint32_t)(n < 1 ? 1 : (n > 4294967295LL ? 4294967295LL : n));
}
inline int Bucket(uint32_t p, uint32_t ctx) {
  const uint32_t k = 31u - (unsigned)__builtin_clz(ctx | 1u);
  const uint32_t dev = p > 0x80000000u ? p - 0x80000000u : 0x80000000u - p;
  const int c = dev < 0x10000000u ? 0 : dev < 0x40000000u ? 1 : dev < 0x70000000u ? 2 : 3;
  return (int)((k & 7u) * 4u) + c;
}
inline uint32_t Before(uint32_t p, uint32_t ctx) {
  if (!Enabled()) return p;   // strict no-op on uninstrumented runs
  State& s=S();
  if (s.pending_bucket >= 0) std::abort();
  s.pending_p=p;
  s.pending_bucket=Bucket(p,ctx);
  return p;                    // TRUE arithmetic encoder receives the original p
}
inline double Codelength(uint32_t p, int bit) {
  const double one=(double)p / 4294967296.0;
  return -std::log2(bit ? one : 1.0-one);
}
inline void After(int bit) {
  if (!Enabled()) return;
  State& s=S();
  if (s.pending_bucket < 0 || (bit!=0 && bit!=1)) std::abort();
  const int group=s.pending_bucket;
  const int32_t e=s.ema[group];
  double* scores;
  if(s.bits<kTrainBits) { scores=s.train; ++s.train_n; }
  else { scores=s.validation; ++s.validation_n; }
  for(int j=0;j<kVariants;++j) scores[j]+=Codelength(Corrected(s.pending_p,e,j),bit);
  const int32_t y=bit ? 65536 : 0;
  const int32_t err=y-(int32_t)(s.pending_p>>16);
  // Integer online residual smoother. All values depend solely on past coded bits.
  s.ema[group]+=(err-s.ema[group])/64;
  ++s.bits;
  s.pending_bucket=-1;
}
inline void Report() {
  if (!Enabled()) return;
  const State& s=S();
  if(s.pending_bucket>=0)std::abort();
  int selected=0;
  for(int j=1;j<kVariants;++j)if(s.train[j]<s.train[selected])selected=j;
  std::fprintf(stderr,"OMR21_SHADOW_RESULT {\\"coded_bits\\":%llu,\\"train_bits\\":%llu,\\"holdout_bits\\":%llu,\\"train_loss\\":[%.10f,%.10f,%.10f,%.10f],\\"holdout_loss\\":[%.10f,%.10f,%.10f,%.10f],\\"selected_mode\\":%d,\\"holdout_gain_bits\\":%.10f,\\"changed_real_probabilities\\":false}\\n",
    (unsigned long long)s.bits,(unsigned long long)s.train_n,(unsigned long long)s.validation_n,
    s.train[0],s.train[1],s.train[2],s.train[3],
    s.validation[0],s.validation[1],s.validation[2],s.validation[3],
    selected,s.validation[0]-s.validation[selected]);
}
}
#endif
