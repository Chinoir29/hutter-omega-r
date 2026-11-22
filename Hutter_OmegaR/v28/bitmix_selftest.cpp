// v0.28 isolated C++ proof-oriented adversarial tests, no Wikipedia required.
#include "omr28_bayes_bitmix.h"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdint>
int main(int argc, char** argv) {
  const bool positive = argc == 2 && std::strcmp(argv[1], "positive") == 0;
  const bool control = argc == 2 && std::strcmp(argv[1], "control") == 0;
  assert(positive || control);
  uint64_t checksum = UINT64_C(1469598103934665603);
  uint32_t seed = 0xBADC0DEu;
  const uint32_t raw_p = positive ? 858993459u : 2147483648u;
  const unsigned length = positive ? 100000 : 250000;
  for (unsigned i = 0; i < length; ++i) {
    unsigned context;
    int bit;
    if (positive) {
      context = 1;  // one densely repeated known metadata bit position
      bit = (i % 5) != 0;  // 80% ones, when the baseline predicts 20%
    } else {
      seed = (uint32_t)(seed * 1664525u + 1013904223u);
      context = 1u + ((seed >> 16) % 255u);
      bit = (seed >> 31) != 0;
    }
    const uint32_t q = omr28_bitmix::Before(raw_p, context);
    assert(q >= 1 && q < omr28_bitmix::kUnit);
    checksum ^= q; checksum *= UINT64_C(1099511628211);
    omr28_bitmix::After(bit);
    assert(omr28_bitmix::Current().pending_context == 0);
  }
  const auto& s = omr28_bitmix::Current();
  unsigned rows = 0;
  for (unsigned c = 1; c <= 255; ++c)
    if (s.rows[c].n0 || s.rows[c].n1) ++rows;
  assert(s.coded_bits == length);
  assert(s.changed_probabilities > 0);
  assert(std::isfinite(s.baseline_ideal_bits) && std::isfinite(s.bayes_ideal_bits));
  // On exact real-number Bayesian probabilities, per-group regret <=1 bit.
  // Allow 0.1-bit for Q32 rounding and summation in this finite test.
  assert(s.bayes_ideal_bits - s.baseline_ideal_bits < double(rows) + 0.1);
  if (positive) {
    assert(rows == 1);
    assert(s.baseline_ideal_bits - s.bayes_ideal_bits > 10000.0);
  }
  std::printf("OMR28_SELFTEST_OK mode=%s bits=%llu rows=%u checksum=%016llx ideal_gain_bits=%.6f\n",
     positive ? "positive" : "control", (unsigned long long)s.coded_bits,
     rows, (unsigned long long)checksum, s.baseline_ideal_bits-s.bayes_ideal_bits);
  omr28_bitmix::Report();
  return 0;
}
