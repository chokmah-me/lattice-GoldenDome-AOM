# Changelog

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
