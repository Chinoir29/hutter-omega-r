// OMÉGA-R v0.28 — causal Bayesian aggregation of an existing bit predictor
// with a Krichevsky–Trofimov prefix-tree expert. Original research patch.
// When compiled into cmix-neif-2.0, the combined work is GPL-3.0-only.
//
// NO extra bytes of metadata, NO external weights, NO changes to the WRT/census
// stream. The same code is called from Encoder::Encode and Decoder::Decode.
// All probability and posterior operations are fixed-point uint128 arithmetic.
#ifndef OMR28_BAYES_BITMIX_H
#define OMR28_BAYES_BITMIX_H

#include <cstdint>
#include <cstdio>
#include <cmath>
#include <cstdlib>

namespace omr28_bitmix {
constexpr uint64_t kUnit = uint64_t{1} << 32;
struct Row {
  uint32_t n0 = 0;
  uint32_t n1 = 0;
  uint64_t posterior = 0;    // ignored only before the first observed bit
};
struct State {
  Row rows[256];
  uint32_t pending_context = 0;
  uint32_t pending_base = 0;
  uint32_t pending_kt = 0;
  uint32_t pending_mix = 0;
  uint64_t pending_weight = 0;
  uint64_t coded_bits = 0;
  uint64_t changed_probabilities = 0;
  double baseline_ideal_bits = 0.0;
  double bayes_ideal_bits = 0.0;
};
inline State& Current() {
  static State state = {};
  return state;
}
inline uint32_t ClampQ32(uint64_t p) {
  if (p == 0) return 1;
  if (p >= kUnit) return uint32_t(kUnit - 1);
  return uint32_t(p);
}
inline uint32_t KtProbability(const Row& row) {
  const uint64_t denom = uint64_t{2} * (uint64_t(row.n0) + row.n1 + 1);
  const uint64_t numerator = (uint64_t{2} * row.n1 + 1) * kUnit;
  return ClampQ32((numerator + denom / 2) / denom);
}
inline uint32_t Before(uint32_t cmix_p32, unsigned int bit_context) {
  if (bit_context == 0 || bit_context > 255 || cmix_p32 == 0) {
    std::abort();
  }
  State& s = Current();
  if (s.pending_context != 0) std::abort();
  Row& row = s.rows[bit_context];
  const uint64_t w = (row.n0 + row.n1) ? row.posterior : kUnit / 2;
  if (w > kUnit) std::abort();
  const uint32_t kt = KtProbability(row);
  const unsigned __int128 sum =
      (unsigned __int128)w * kt + (unsigned __int128)(kUnit - w) * cmix_p32;
  const uint32_t mixed = ClampQ32(uint64_t((sum + kUnit / 2) >> 32));
  s.pending_context = bit_context;
  s.pending_base = cmix_p32;
  s.pending_kt = kt;
  s.pending_weight = w;
  s.pending_mix = mixed;
  if (mixed != cmix_p32) ++s.changed_probabilities;
  return mixed;
}
inline void After(int bit) {
  State& s = Current();
  if (!s.pending_context || (bit != 0 && bit != 1)) std::abort();
  Row& row = s.rows[s.pending_context];
  const uint64_t kt_likelihood = bit ? s.pending_kt : (kUnit - s.pending_kt);
  const uint64_t base_likelihood = bit ? s.pending_base : (kUnit - s.pending_base);
  const uint64_t mix_likelihood = bit ? s.pending_mix : (kUnit - s.pending_mix);
  const unsigned __int128 denom =
      (unsigned __int128)s.pending_weight * kt_likelihood +
      (unsigned __int128)(kUnit - s.pending_weight) * base_likelihood;
  if (!denom) std::abort();
  const unsigned __int128 numerator =
      (unsigned __int128)s.pending_weight * kt_likelihood * kUnit;
  const uint64_t posterior = uint64_t((numerator + denom / 2) / denom);
  if (posterior > kUnit) std::abort();
  row.posterior = posterior;
  if (bit) {
    if (row.n1 == UINT32_MAX) std::abort();
    ++row.n1;
  } else {
    if (row.n0 == UINT32_MAX) std::abort();
    ++row.n0;
  }
  s.baseline_ideal_bits -= std::log2(double(base_likelihood) / double(kUnit));
  s.bayes_ideal_bits -= std::log2(double(mix_likelihood) / double(kUnit));
  ++s.coded_bits;
  s.pending_context = 0;
}
inline void Report() {
  const State& s = Current();
  if (s.pending_context) std::abort();
  unsigned used = 0;
  for (unsigned i = 1; i < 256; ++i)
    if (s.rows[i].n0 || s.rows[i].n1) ++used;
  std::fprintf(stderr,
      "OMR28_BAYES_REPORT coded_bits=%llu active_contexts=%u changed_probabilities=%llu baseline_ideal_bits=%.10f candidate_ideal_bits=%.10f ideal_gain_bits=%.10f\n",
      (unsigned long long)s.coded_bits, used,
      (unsigned long long)s.changed_probabilities,
      s.baseline_ideal_bits, s.bayes_ideal_bits,
      s.baseline_ideal_bits - s.bayes_ideal_bits);
}
}  // namespace omr28_bitmix
#endif
