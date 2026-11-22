#!/usr/bin/env python3
"""Pin GPL upstream and apply v0.28 Bayesian mixture to BOTH native coder paths.

Reuses v0.25's proven zero-argument native prefix archive construction. Keeps
all upstream license and provenance files in an ephemeral scratch checkout;
never copies the resulting binary/model/corpus back to our repository.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "v25"))
import prepare_native as v25

UPSTREAM_BLOBS = {
    "src/coder/encoder.cpp": "c7299664111582c04c5d1fee4a545505e46f10d0",
    "src/coder/decoder.cpp": "58f5d01bb4520378968fc43f226486ea56ea9bc7",
}
END_OF_PROBABILITY = """      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7)));"""
ORIGINAL_OPEN = "  const unsigned int xmid = floor_stage::Mid(x1_, x2_, p_->SemCorrect(floor_.P32(p,"
PATCHED_OPEN = "  const uint32_t omr28_original_p32 = p_->SemCorrect(floor_.P32(p,"
PATCHED_END = """      (31 - __builtin_clz(p_->BbBitCtx() | 1u)) & 7));
  const unsigned int xmid = floor_stage::Mid(x1_, x2_,
      omr28_bitmix::Before(omr28_original_p32, p_->BbBitCtx()));"""


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def instrument(code: bytes, mode: str) -> bytes:
    if mode not in ("encoder", "decoder"):
        raise ValueError("MODE_MUST_BE_ENCODER_OR_DECODER")
    if git_blob(code) != UPSTREAM_BLOBS[f"src/coder/{mode}.cpp"]:
        raise ValueError("UPSTREAM_CODEC_DRIFT_" + mode)
    text = code.decode()
    include = f'#include "{mode}.h"'
    if text.count(include) != 1 or text.count(ORIGINAL_OPEN) != 1 or text.count(END_OF_PROBABILITY) != 1:
        raise ValueError("CODEC_ANCHOR_NOT_UNIQUE_" + mode)
    text = text.replace(include, include + '\n#include "../omr28_bayes_bitmix.h"', 1)
    text = text.replace(ORIGINAL_OPEN, PATCHED_OPEN, 1)
    text = text.replace(END_OF_PROBABILITY, PATCHED_END, 1)
    learn = "  p_->SemLearn(bit);"
    if text.count(learn) != 1:
        raise ValueError("SEMANTIC_LEARN_ANCHOR_NOT_UNIQUE_" + mode)
    text = text.replace(learn, learn + "\n  omr28_bitmix::After(bit);", 1)
    if mode == "encoder":
        flush = "  total_out_ += out_n_;\n  out_n_ = 0;\n}"
        if text.count(flush) != 1:
            raise ValueError("ENCODER_FLUSH_ANCHOR_DRIFT")
        text = text.replace(flush, "  total_out_ += out_n_;\n  out_n_ = 0;\n  omr28_bitmix::Report();\n}", 1)
    if (text.count("omr28_bitmix::Before(") != 1 or
        text.count("omr28_bitmix::After(") != 1 or
        text.count('omr28_bayes_bitmix.h') != 1):
        raise AssertionError("ASYMMETRIC_PATCH_" + mode)
    if mode == "decoder" and "omr28_bitmix::Report" in text:
        raise AssertionError("DECODER_MUST_NOT_REPORT")
    return text.encode()


def prepare(upstream: Path, output: Path, header: Path) -> dict:
    if not header.is_file():
        raise ValueError("MISSING_OWNED_BAYES_HEADER")
    base = v25.prepare(upstream, output)
    paths = {}
    for role in ("encoder", "decoder"):
        relative = Path("src/coder") / (role + ".cpp")
        file = output / relative
        changed = instrument(file.read_bytes(), role)
        file.write_bytes(changed)
        paths[str(relative)] = hashlib.sha256(changed).hexdigest()
    target = output / "src/omr28_bayes_bitmix.h"
    if target.exists():
        raise ValueError("UPSTREAM_HEADER_COLLISION")
    target.write_bytes(header.read_bytes())
    paths["src/omr28_bayes_bitmix.h"] = hashlib.sha256(target.read_bytes()).hexdigest()
    # Compare exact probability adjustment and feedback point count between coder paths.
    coder = (output / "src/coder/encoder.cpp").read_text()
    decoder = (output / "src/coder/decoder.cpp").read_text()
    for token in ("omr28_bitmix::Before(omr28_original_p32, p_->BbBitCtx())",
                  "omr28_bitmix::After(bit);"):
        if coder.count(token) != 1 or decoder.count(token) != 1:
            raise AssertionError("ENCODER_DECODER_NOT_SYMMETRIC")
    if base["native_comp9_assembles_archive9"] is not True:
        raise AssertionError("V25_NATIVE_ARCHIVE_CAPABILITY_MISSING")
    evidence = {
        "status": "SYMMETRIC_PROBABILITY_CODE_PREPARED_NOT_YET_BUILT",
        "upstream_commit": base["upstream_commit"],
        "v25_native_runner_sha256": base["v25_runner_sha256"],
        "source_patches_sha256": paths,
        "free_coded_bits_only": True,
        "no_new_side_data": True,
        "encoder_decoder_same_correction_and_update": True,
        "real_corpus_SHA_validated_at_runtime_not_yet": True,
        "preprocessed_prefix_cap_bytes": 524288,
        "eligible_hutter_score_S": None,
        "license": "GPL-3.0-only upstream and compatible research patch; scratch only",
    }
    (output.parent / "omr28-source-audit.json").write_text(json.dumps(evidence, indent=2) + "\n")
    return evidence


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--header", type=Path, default=Path(__file__).with_name("omr28_bayes_bitmix.h"))
    args = ap.parse_args()
    print(json.dumps(prepare(args.upstream, args.output, args.header), indent=2))


if __name__ == "__main__":
    main()
