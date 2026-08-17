#!/usr/bin/env python3
"""Claim A: Ghost-in-the-Matrix — staleness bypass cliff + auditor latency.

Non-claims: not a hardware SEU measurement; not Lean; not manuscript CoE.
Latency percentiles come from simulate.RNG log-normal draws (seed 42), not
from a flight clock. Bypass is a TTL comparison, not a crypto proof.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import simulate


PUBLISHED_P99_MS = 4.61
PUBLISHED_P999_MS = 4.82
P_ATOL_MS = 0.15
HARD_LIMIT_MS = 5.0
TTL_MS = 500.0


def main() -> int:
    simulate.RNG = np.random.default_rng(42)
    res = simulate.run_ghost_attack_sweep(n_trials=2000)

    deltas = np.asarray(res["deltas"])
    far = np.asarray(res["far_curve"])
    cliff = far[deltas <= -TTL_MS]
    if cliff.size == 0:
        print("FAIL: no sweep points at Δt ≤ −500 ms")
        return 1
    if not np.all(cliff == 1):
        n_fail = int(np.sum(cliff != 1))
        print(
            f"FAIL: staleness bypass is not binary; {n_fail}/{cliff.size} "
            f"points at Δt ≤ −{TTL_MS:.0f} ms did not pass"
        )
        return 1

    p99 = float(res["p99_ms"])
    p999 = float(res["p999_ms"])
    print(
        f"A-ghost: bypass@Δt≤−{TTL_MS:.0f}ms = 100% "
        f"({cliff.size} points); P99={p99:.3f} ms; P99.9={p999:.3f} ms"
    )

    if abs(p99 - PUBLISHED_P99_MS) > P_ATOL_MS:
        print(
            f"FAIL: P99={p99:.3f} ms not within ±{P_ATOL_MS} of "
            f"published {PUBLISHED_P99_MS}"
        )
        return 1
    if abs(p999 - PUBLISHED_P999_MS) > P_ATOL_MS:
        print(
            f"FAIL: P99.9={p999:.3f} ms not within ±{P_ATOL_MS} of "
            f"published {PUBLISHED_P999_MS}"
        )
        return 1
    if p99 >= HARD_LIMIT_MS or p999 >= HARD_LIMIT_MS:
        print(
            f"FAIL: latency not inside {HARD_LIMIT_MS} ms budget "
            f"(P99={p99:.3f}, P99.9={p999:.3f})"
        )
        return 1

    print(
        f"OK: A-ghost cliff + latency "
        f"(P99={p99:.3f}, P99.9={p999:.3f} vs {PUBLISHED_P99_MS}/{PUBLISHED_P999_MS})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
