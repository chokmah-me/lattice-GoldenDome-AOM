#!/usr/bin/env python3
"""Claim D: Analytical 7-check combined detection stays >90% until s≈0.85.

Non-claims: parametric curves, not measured hardware rates (README Caveats);
not Lean; not manuscript CoE. Deterministic — no RNG.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import simulate


S_FLOOR = 0.85
P_MIN = 0.90


def main() -> int:
    sens = simulate.sensitivity_analysis(n_points=60)
    s = np.asarray(sens["sophistication"])
    p = np.asarray(sens["p_detected_combined"])
    p_at_07 = float(np.interp(0.7, s, p))
    p_at_10 = float(p[-1])
    p_at_085 = float(np.interp(S_FLOOR, s, p))

    mask = s < S_FLOOR
    n_below = int(np.sum(p[mask] <= P_MIN))
    print(
        f"D-analytical: p(s=0.7)={p_at_07*100:.2f}%  "
        f"p(s=0.85)={p_at_085*100:.2f}%  p(s=1.0)={p_at_10*100:.2f}%  "
        f"n(s<{S_FLOOR} and p≤{P_MIN})={n_below}"
    )

    if n_below:
        worst = float(np.min(p[mask]))
        s_worst = float(s[mask][np.argmin(p[mask])])
        print(
            f"FAIL: combined detection dropped to {worst*100:.2f}% at s={s_worst:.3f} "
            f"(required >{P_MIN*100:.0f}% for all s<{S_FLOOR})"
        )
        return 1

    print(
        f"OK: D-analytical combined >{P_MIN*100:.0f}% for all s<{S_FLOOR} "
        f"(s=0.7 → {p_at_07*100:.1f}%; s=1.0 → {p_at_10*100:.1f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
