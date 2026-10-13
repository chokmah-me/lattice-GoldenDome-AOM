# Changelog

## Unreleased — 2026-10-13 — Paper reminted v8.1 → v8.2

- The 2026-10-12 in-place amendment of the v8.1 paper (entropy-tape
  replacement, 3b FP32 score 0.7 → 1.25, env pinning) was substantive, so
  it now ships as **v8.2** (`dyb-2026i-goldendome-R-v8.2.md`) with a fresh
  version line and Hebrew date (2 Cheshvan 5787). The amended v8.1 md +
  pdf moved to `archive/` (the amended v8.1 md was never published as a
  PDF; the Zenodo record 21971208 remains the pre-amendment v8.1).
- Zenodo deposit unchanged (v8.1, 10.5281/zenodo.21971208) until the user
  mints v8.2. v8.2 PDF rebuild pending (Typora). CITATION.cff
  preferred-citation stays at v8.1 until deposit.

## Unreleased — 2026-10-12 — Entropy source replacement + C-lethal adjudication

- `simulate.py`: Lorenz-attractor entropy tape (scipy `solve_ivp`/RK45) replaced
  with a version-stable AR(1) PRNG tape (PCG64, fixed seed, rank-normalised).
  The chaotic tape made check-3a solver-version-sensitive (red under scipy
  1.11.4: g_load 10.126 > 10.0 at one step). The AR(1) tape matches the old
  tape's character (lag-1 autocorr 0.9990, step std 0.0129) and is bit-identical
  across numpy/scipy versions; all five gates pass identically on
  numpy 1.26.4/scipy 1.11.4 and numpy 2.4.4/scipy 1.17.1.
- `claims/verify_c_lethal.py`: `PUBLISHED_FP32_SCORE` recalibrated 0.7 → 1.25
  (measured 1.252 on the new tape; detection unaffected, still < 3.9 threshold).
- `requirements.txt`: scipy==1.17.1, numpy==2.4.4, matplotlib==3.10.9 pinned to
  the author's recorded green env; CI Python 3.10 → 3.12; verifier-C step
  gating again (was informational while red).
- Paper (`dyb-2026i-goldendome-R-v8.1.md`): 3b FP32 score 0.7 → 1.25; simulation
  placeholder reworded (AR(1) PRNG tape); "Lorenz seed" → "entropy seed".
  PDF rebuild pending (Typora).
- `results/`: `claim_verify_out.txt` / `claim_verify_meta.json` regenerated
  (all five claims green); `claim_holds_brief.md` amended.

## Unreleased — 2026-08-17 — Tufte figure pass (no remint)

- Figure D (`results/D_sensitivity.png`): 7-check overlay → 2×4 small
  multiples, shared 0–100 frame; independence formula and source on the figure.
- Figure A (`results/A_ghost_attack.png`): boxed callouts removed; n and
  P99.9 vs 5 ms limit labeled.
- Paper md now embeds Figures A–E from `results/`. `dyb-2026i-goldendome-R-v8.1.pdf`
  rebuilt in Typora. Paper remains v8.1 / Zenodo `21971208`. Software remains
  1.0.1 / `21979227` (remint deferred).

## 1.0.1 software — 2026-08-17 — GitHub tag `1.0.1`

Claim-gate harness, Check 4 / Scenario A predicate repairs, regenerated
figures, Figure C coverage sweep now injects an in-series jump (the old
`x[4]+jump` path was NaN), `Esimulate.py` and superseded v8 drafts under
`archive/`. Figure C coverage panel: Check 4 is an in-series jump (50%
detect at 80 m); 3a/3b are cold-start offset (internally smooth). Paper
remains v8.1 / Zenodo `21971208` (not reminted). Software Zenodo version
DOI is `10.5281/zenodo.21979227` (concept `19368608`). Prior software version `19368609` is superseded.

## 2026-08-17 — Figures A/C regenerated; Esimulate quarantined

- Re-ran `python simulate.py` after the A/C predicate repairs. Figure A
  now shows 100% FAR for Δt ≤ −500 ms. Figure C default-track Check 4
  residuals are O(1–3 m) (update residual), and the 50 m pop-in is MISSED
  as published.
- `Esimulate.py` moved to `archive/` (v4 4-check leftover).

## 2026-08-17 — Computational claim gate + manuscript integrity (v8.1)

Executed re-run of load-bearing simulation claims and a structural integrity
pass on `dyb-2026i-goldendome-R-v8.1.md`. Not a hardware validation and not
peer review.

### Simulation (`simulate.py`)

- Plot output is repo-relative (`results/` next to the script). The old
  `G:\My Drive\...` path blocked a local re-run.
- Scenario A pass predicate now matches the published cliff: payload-timestamp
  spoof Δt ≤ −500 ms is 100% bypass.
- Check 4 residual is on consecutive updates. Absolute position vs a lagging
  median is always ≫ 80 m on a Mach-5+ track and could not implement the
  published pop-in threshold.

### Gates

- `claim-manifest.json` + `claims/verify_*.py` (A–E). Last full gate:
  `verify_claim_project.py` exit 0 (`results/claim_verify_meta.json`,
  2026-08-17T02:11:10Z).
- `integrity-manifest.json` + I1 bindings. Last scan: `audit_manuscript.py
  --online` status `pass` (`results/integrity_audit.json`, 2026-08-17T07:07:02Z).
- v8.1 §6.4 DOI punctuation: `10.5281/zenodo.19368609` is no longer glued to
  a semicolon (scanner 404 on a fake id; the Zenodo record exists).

### Residual

- D/E remain parametric assumptions (README Caveats).
- Figure C coverage sweep still uses `x[5] = x[4] + jump` with `x[4]` NaN
  (flat ~2% detect; annotated cross-over ~10 m). The 80 m claim is the
  Check 4 update-residual threshold, gated by `claims/verify_c_lethal.py`,
  not that sweep panel.
