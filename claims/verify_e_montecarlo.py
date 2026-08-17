#!/usr/bin/env python3
"""Claim E: 7-check Monte Carlo table + PINN-zeroed gap (50k × 20, seed=42).

Non-claims: parametric Bernoulli model, not measured hardware rates
(README Caveats); does not reduce n_trials; not Lean; not manuscript CoE.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import simulate


N_TRIALS = 50_000
N_LEVELS = 20
SEED = 42

# README published points; keys are the s values named in the table.
PUBLISHED_FULL = {
    0.00: 100.00,
    0.26: 100.00,
    0.53: 99.93,
    0.74: 99.03,
    1.00: 89.18,
}
PUBLISHED_PINN_ZERO = {
    0.74: 96.1,
    1.00: 61.7,
}
PUBLISHED_GAP_PP = 27.5
MIN_ABS_PP = 0.25


def _nearest(levels: np.ndarray, target: float) -> float:
    return float(levels[int(np.argmin(np.abs(levels - target)))])


def _tol_pp(se: float) -> float:
    return max(MIN_ABS_PP, 2.0 * float(se) * 100.0)


def main() -> int:
    mc = simulate.monte_carlo_sensitivity(
        n_trials=N_TRIALS, n_levels=N_LEVELS, seed=SEED
    )
    levels = np.asarray(mc["sophistication_levels"])
    full = mc["full"]
    pinn = mc["pinn_zeroed"]
    failed = False

    print("E-montecarlo full 7-check (nearest linspace points):")
    for target, expected in PUBLISHED_FULL.items():
        s = _nearest(levels, target)
        row = full[s]
        mean_pp = float(row["mean"]) * 100.0
        se_pp = float(row["se"]) * 100.0
        tol = _tol_pp(row["se"])
        delta = abs(mean_pp - expected)
        print(
            f"  s_req={target:.2f} s={s:.4f} mean={mean_pp:.2f}% "
            f"SE={se_pp:.3f} expected={expected:.2f} tol={tol:.2f} "
            f"Δ={delta:.2f}"
        )
        if delta > tol:
            print(
                f"FAIL: full-model mean at s≈{target:.2f} is {mean_pp:.2f}% "
                f"(expected {expected:.2f} ± {tol:.2f} pp)"
            )
            failed = True

    print("E-montecarlo PINN-zeroed:")
    for target, expected in PUBLISHED_PINN_ZERO.items():
        s = _nearest(levels, target)
        row = pinn[s]
        mean_pp = float(row["mean"]) * 100.0
        tol = _tol_pp(row["se"])
        delta = abs(mean_pp - expected)
        print(
            f"  s_req={target:.2f} s={s:.4f} mean={mean_pp:.2f}% "
            f"expected={expected:.1f} tol={tol:.2f} Δ={delta:.2f}"
        )
        if delta > tol:
            print(
                f"FAIL: PINN-zeroed mean at s≈{target:.2f} is {mean_pp:.2f}% "
                f"(expected {expected:.1f} ± {tol:.2f} pp)"
            )
            failed = True

    s1 = _nearest(levels, 1.0)
    gap = (float(full[s1]["mean"]) - float(pinn[s1]["mean"])) * 100.0
    gap_tol = max(MIN_ABS_PP, _tol_pp(full[s1]["se"]) + _tol_pp(pinn[s1]["se"]))
    print(f"E-montecarlo PINN gap at s=1: {gap:.2f} pp (published {PUBLISHED_GAP_PP})")
    if abs(gap - PUBLISHED_GAP_PP) > gap_tol:
        print(
            f"FAIL: PINN gap {gap:.2f} pp not within ±{gap_tol:.2f} of "
            f"{PUBLISHED_GAP_PP}"
        )
        failed = True

    if failed:
        return 1
    print(
        f"OK: E-montecarlo {N_TRIALS}×{N_LEVELS} seed={SEED} "
        f"matches published table within max(0.25 pp, 2·SE); gap={gap:.2f} pp"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
