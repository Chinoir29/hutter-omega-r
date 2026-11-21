#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for model in 0 1; do
  g++ -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror \
    -ffunction-sections -fdata-sections -Wl,--gc-sections -s \
    -DOMR6_TBITS=18 -DOMR6_MATCH_BITS=20 -DOMR6_RING_BITS=22 \
    -DOMR10_EXTRA="$model" omr10_folded_context.cpp -o "comp9_variant$model"
  sha256sum "comp9_variant$model"
done
