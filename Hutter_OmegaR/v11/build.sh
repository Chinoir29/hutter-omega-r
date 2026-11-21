#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for m in 0 1 2 3; do
  g++ -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror \
    -ffunction-sections -fdata-sections -Wl,--gc-sections -s \
    -DOMR6_TBITS=18 -DOMR6_MATCH_BITS=20 -DOMR6_RING_BITS=22 \
    -DOMR11_FOLD="$m" omr11_fold_word.cpp -o "comp9_mode$m"
  sha256sum "comp9_mode$m"
done
