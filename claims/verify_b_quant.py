#!/usr/bin/env python3
"""Claim B: Quantization-aware spoof — nominal INT8/FP32 success rate.

Non-claims: isolated seed-42 draw, not the post-A main() RNG stream; not a
measured sensor dynamic-range result; not Lean; not manuscript CoE.
Does not re-run the 30-threshold sweep — only the nominal χ²-95% gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import simulate


N_DIM = 8
N_CANDIDATES = 20_000
PUBLISHED_SUCCESS = 0.0006  # ~0.06%
MAX_SUCCESS = 0.005         # structural cap 0.5%


def main() -> int:
    simulate.RNG = np.random.default_rng(42)
    fp32_thresh = float(np.sqrt(chi2.ppf(0.95, df=N_DIM)))
    cov_diag = np.array([1.0, 1.0, 0.8, 0.8, 0.5, 0.5, 0.3, 0.3])
    cov_inv = np.linalg.inv(np.diag(cov_diag))
    mu = np.zeros(N_DIM)

    nom = simulate.craft_int8_adversarial(
        mu,
        cov_inv,
        fp32_thresh,
        fp32_thresh,
        n_dim=N_DIM,
        n_candidates=N_CANDIDATES,
    )
    rate = float(nom["success_rate"])
    n_adv = int(nom["n_adversarial"])
    print(
        f"B-quant: nominal success={rate*100:.3f}% "
        f"({n_adv}/{N_CANDIDATES}); fp32_thresh={fp32_thresh:.3f}"
    )

    if not (0.0 <= rate <= MAX_SUCCESS):
        print(
            f"FAIL: nominal INT8-pass/FP32-fail rate {rate*100:.3f}% "
            f"outside [0, {MAX_SUCCESS*100:.1f}%] "
            f"(published ~{PUBLISHED_SUCCESS*100:.2f}%)"
        )
        return 1

    print(
        f"OK: B-quant isolated seed=42 rate={rate*100:.3f}% "
        f"(published ~{PUBLISHED_SUCCESS*100:.2f}%; cap {MAX_SUCCESS*100:.1f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
