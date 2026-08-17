# Claim-holds brief — lattice-GoldenDome-AOM

## Status
**Verified** — `verify_claim_project.py` exit 0 on 2026-08-17T02:11:10Z (`status=pass` in `claim_verify_meta.json`).

This is a computational re-run, not Lean, not manuscript CoE, not a hardware measurement.

## Claims

| id | command | exit | ms | notes |
|----|---------|------|----|-------|
| A-ghost | `python claims/verify_a_ghost.py` | 0 | 15131 | 100% bypass at Δt ≤ −500 ms (500 points). P99=4.611 ms, P99.9=4.819 ms (published 4.61 / 4.82). |
| B-quant | `python claims/verify_b_quant.py` | 0 | 14479 | Isolated seed=42 nominal success=0.040% (8/20000); published ~0.06%; cap 0.5%. |
| C-lethal | `python claims/verify_c_lethal.py` | 0 | 13537 | Default 50 m: 3a pass, 3b FP32=0.719 vs thr=3.938. Check 4 first-detect=81 m on a noise-free jump. |
| D-analytical | `python claims/verify_d_analytical.py` | 0 | 13711 | Combined >90% for all s<0.85 (s=0.7 → 99.27%; s=1.0 → 89.14%). |
| E-montecarlo | `python claims/verify_e_montecarlo.py` | 0 | 16623 | 50k×20 seed=42 matches README table (100 / 100 / 99.93 / 99.03 / 89.18; PINN-zeroed 96.13 / 61.65; gap 27.53 pp). |

## Seeds / env / platform
- `simulate.RNG` reseeds: `np.random.default_rng(42)` per A/B/C harness; E uses `monte_carlo_sensitivity(..., seed=42)`.
- Python 3.14.4, numpy 2.4.4, scipy 1.17.1, matplotlib 3.10.9, **numba absent** (scipy fallback).
- Host: Windows. Interpreter: `python` on PATH.
- Import still builds `ENTROPY_TAPE` (50k Lorenz / `solve_ivp`) — ~13–15 s of each claim’s wall time.

## Repairs this gate (4)
1. `OUT` is repo-relative (`Path(__file__).parent / "results"`). The old `G:\My Drive\...` path blocked local import.
2. `ghost_injection_attack`: pass predicate was inverted vs every published “Δt ≤ −500 → 100% bypass” statement. Now `passes = (−Δt) ≥ TTL`.
3. `temporal_coherence_check`: residual is now on **consecutive updates**. Absolute position vs lagging median is always ≫ 80 m on a Mach-5+ track, so the published pop-in cliff could not execute.
4. C oracle measures that 80 m cliff on a noise-free constructed jump. The plot-path sweep still does `x[5] = x[4] + jump` with `x[4]` NaN — not used as the oracle.

## Not checked here
- D/E **parametric assumptions**, not measured hardware / PINN / Lorenz uncloneability.
- `Esimulate.py` (v4 4-check leftover; would override v5 `monte_carlo_sensitivity`).
- PNG identity (`A_ghost_attack.png` … `E_sensitivity_full.png` not hashed). Figures A and C on disk were generated **before** repairs 2–3; re-run `simulate.py` if the paper figures must match the repaired predicates.
- Plot-path C sweep 50×300 and the in-series NaN jump.
- B as the post-A `main()` RNG stream (0.06% vs isolated 0.040%).
- Lean / lake proofs (none in repo).
- Manuscript CoE (cites, method≠artifact, overclaim) — `manuscript-integrity-gate`.
- DOI / Zenodo / `release-sync`.

## Evidence
- `results/claim_verify_meta.json`
- `results/claim_verify_out.txt`
- `results/claim_verify_brief.md`
- `claim-manifest.json`
- `claims/verify_{a_ghost,b_quant,c_lethal,d_analytical,e_montecarlo}.py`

Re-run:

```powershell
python "C:\Users\Elke Shayna\Documents\00Dev\computational-claim-gate\scripts\verify_claim_project.py" `
  --project "C:\Users\Elke Shayna\Documents\00Dev\lattice-GoldenDome-AOM"
```

## Residual risk
- Existing paper figures A/C may not match the repaired Check 4 / Scenario A predicates until plots are regenerated. Prose already stated the repaired A sign; C’s “~80 m” now has an executable update-residual meaning.
- B published 0.06% is an order-of-magnitude figure; this run’s isolated draw is 0.040%.
- Combined detection in D/E is only as reliable as the per-check parametric curves (README Caveats).
