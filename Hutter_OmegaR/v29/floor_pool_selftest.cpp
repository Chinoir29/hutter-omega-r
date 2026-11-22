// OMÉGA-R v0.29 synthetic likelihood test for *real* floor_stage.h at source pin.
#include "floor_stage.h"
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
int main(int argc,char**argv) {
  if(argc!=2 || (argv[1][0]!='m' && argv[1][0]!='b')) return 2;
  const bool mismatched=(argv[1][0]=='m');
  floor_stage::Stage stage;
  uint32_t state=0x40caf3e1u;
  double logloss=0;
  uint64_t checksum=1469598103934665603ull;
  uint64_t prediction_checksum=1469598103934665603ull;
  uint64_t errors=0;
  constexpr unsigned COUNT=400000;
  for(unsigned i=0;i<COUNT;++i) {
    state=state*1664525u+1013904223u;
    // Simulate correctly signed high-confidence predictions from the existing
    // adaptive-depth stage with 16 positions and widely dispersed logit bins.
    const unsigned bp=(i >> 1) & 7u;
    const bool side=(i & 1u) != 0u;
    const unsigned z_bin=(i / 32u) % 48u;
    const float z=7.0f + 0.25f * z_bin;
    // Floor probability is down to 1/65536 for high-confidence bits.
    unsigned f=(unsigned)std::floor(65536.0/(1.0+std::exp(double(z)))+0.5);
    if(f < 1) f=1;
    const unsigned p16=side ? 65536u-f : f;
    const uint32_t draw=(state>>9) % 1'000'000u;
    const unsigned expected_error=(unsigned)std::floor((double(f)/65536.)*1'000'000.);
    const bool err=draw < (mismatched ? 3500u : expected_error);
    const int bit=side ^ err;
    const uint32_t actual=stage.P32(p16,0,1,0,z,0.0f,0,bp);
    const double q1=double(actual)/4294967296.0;
    logloss -= std::log2(bit ? q1 : 1.0 - q1);
    prediction_checksum=(prediction_checksum ^ actual)*1099511628211ull;
    stage.Update(bit);
    errors += err;
    checksum=(checksum ^ ((uint64_t(bit)<<32)|p16))*1099511628211ull;
  }
  std::printf("OMR29_FLOOR_TEST case=%s bits=%u errors=%llu loss_bits=%.9f input_checksum=%016llx prediction_checksum=%016llx\n",
      mismatched?"mismatch":"baseline",COUNT,(unsigned long long)errors,logloss,
      (unsigned long long)checksum, (unsigned long long)prediction_checksum);
}
