#!/bin/sh
set -eu
cd "$(dirname "$0")"
CXX=${CXX:-g++}
TBITS=${TBITS:-18}
MATCH_BITS=${MATCH_BITS:-20}
RING_BITS=${RING_BITS:-22}
OUT=${OUT:-comp9}
"$CXX" -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror \
  -ffunction-sections -fdata-sections -Wl,--gc-sections -s \
  -DOMR6_TBITS="$TBITS" -DOMR6_MATCH_BITS="$MATCH_BITS" -DOMR6_RING_BITS="$RING_BITS" \
  omr6_sfx.cpp -o "$OUT"
sha256sum "$OUT"; ls -lh "$OUT"
