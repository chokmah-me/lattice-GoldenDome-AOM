#!/usr/bin/env python3
"""Claim C: Lethal compliance — 3a/3b pass at 50 m; coherence ~80 m.

Non-claims: crossover is measured on a continuous genuine track plus a
single spatial jump (plot-path sweep writes x[5]=x[4]+jump with x[4] NaN);
not measured sensor noise; not Lean; not manuscript CoE.
Does not import Esimulate.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import simulate


PUBLISHED_FP32_SCORE = 0.7
PUBLISHED_THRESHOLD = 3.9
SCORE_ATOL = 0.4
THRESH_ATOL = 0.15
CROSSOVER_M = 80.0
CROSSOVER_ATOL_M = 5.0
JUMP_INDEX = 20


def _straight_track(n: int = 40) -> dict:
    """Noise-free constant-velocity track so residual == injected jump."""
    t = np.arange(n) * simulate.DT_TRACK
    return dict(x=2000.0 * t, y=np.zeros(n), t=t)


def _jump_track(base: dict, jump_m: float) -> dict:
    trk = dict(base)
    trk["x"] = base["x"].copy()
    trk["x"][JUMP_INDEX:] = trk["x"][JUMP_INDEX:] + jump_m
    return trk


def _crossover_m(base: dict) -> float:
    """Smallest jump (m) that trips Check 4 (implemented threshold 80 m)."""
    jumps = np.linspace(60.0, 100.0, 41)
    for jump in jumps:
        tc = simulate.temporal_coherence_check(_jump_track(base, jump))
        if tc["any_fail"]:
            return float(jump)
    print("FAIL: no jump in [60, 100] m tripped Check 4")
    raise SystemExit(1)


def main() -> int:
    simulate.RNG = np.random.default_rng(42)
    tracks = simulate.generate_physics_valid_track(
        n_steps=simulate.N_STEPS, pop_in_step=5, entropy_offset=1234
    )
    pe = simulate.physics_envelope_check(tracks["adversarial"])
    cm = simulate.cross_modal_mahalanobis_check(
        tracks["adversarial"], tracks["genuine"]
    )

    print(
        f"C-lethal default 50 m: 3a_pass={pe['passes']} "
        f"3b_fp32={cm['fp32_score']:.3f} thresh={cm['threshold']:.3f} "
        f"3b_pass={cm['passes_fp32']}"
    )

    if not pe["passes"]:
        print("FAIL: Check 3a (kinematic bounds) rejected the default adversarial track")
        return 1
    if not cm["passes_fp32"]:
        print(
            f"FAIL: Check 3b detected the 50 m pop-in "
            f"(FP32={cm['fp32_score']:.3f} > {cm['threshold']:.3f})"
        )
        return 1
    if abs(cm["threshold"] - PUBLISHED_THRESHOLD) > THRESH_ATOL:
        print(
            f"FAIL: 3b threshold {cm['threshold']:.3f} not within ±{THRESH_ATOL} "
            f"of published {PUBLISHED_THRESHOLD}"
        )
        return 1
    if abs(cm["fp32_score"] - PUBLISHED_FP32_SCORE) > SCORE_ATOL:
        print(
            f"FAIL: 3b FP32 score {cm['fp32_score']:.3f} not within ±{SCORE_ATOL} "
            f"of published {PUBLISHED_FP32_SCORE}"
        )
        return 1

    base = _straight_track()
    large = _jump_track(base, 200.0)
    tc_large = simulate.temporal_coherence_check(large)
    if not tc_large["any_fail"]:
        print("FAIL: Check 4 missed a 200 m spatial jump (expected detect)")
        return 1

    small = _jump_track(base, 40.0)
    tc_small = simulate.temporal_coherence_check(small)
    if tc_small["any_fail"]:
        print("FAIL: Check 4 flagged a 40 m jump on a noise-free track")
        return 1

    cross_m = _crossover_m(base)
    print(f"C-lethal: Check 4 first-detect jump ≈ {cross_m:.1f} m (published ~80 m)")
    if abs(cross_m - CROSSOVER_M) > CROSSOVER_ATOL_M:
        print(
            f"FAIL: crossover {cross_m:.1f} m not within ±{CROSSOVER_ATOL_M} of "
            f"{CROSSOVER_M}"
        )
        return 1

    print(
        f"OK: C-lethal 3a/3b pass at 50 m "
        f"(FP32={cm['fp32_score']:.2f}, thr={cm['threshold']:.2f}); "
        f"200 m detected; crossover={cross_m:.0f} m"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
