# Integrity brief — lattice-GoldenDome-AOM

## Status
`lattice-GoldenDome-AOM — pass (I1 pass; I3 pass online (2 resolved, 0 unresolved))`

This is a **structural integrity pass**, not scientific verification and not peer review. Do not call the paper Verified.

## Reproduce
```
python C:\Users\Elke Shayna\Documents\00Dev\manuscript-integrity-gate\scripts\audit_manuscript.py --project "C:\Users\Elke Shayna\Documents\00Dev\lattice-GoldenDome-AOM" --propose-bindings
python C:\Users\Elke Shayna\Documents\00Dev\manuscript-integrity-gate\scripts\audit_manuscript.py --project "C:\Users\Elke Shayna\Documents\00Dev\lattice-GoldenDome-AOM" --manuscript "C:\Users\Elke Shayna\Documents\00Dev\lattice-GoldenDome-AOM\dyb-2026i-goldendome-R-v8.1.md" --online
```

## Surfaces
- Manuscript: `dyb-2026i-goldendome-R-v8.1.md` (pinned; v8 sibling not scanned this pass)
- Bibliography: none (`.bib` absent; Chokmah inline + DOI/Zenodo)
- Manifest: `integrity-manifest.json`
- Results / code: `simulate.py`, `claims/verify_*.py`, `results/claim_verify_*`, `results/i1_bindings.json`
- Lean: none

## Checks

| Check | Status | Notes |
|-------|--------|-------|
| I1 numbers | pass | 42 proposed result-claims; all bound. Sim percents bound to published rounded figures in `results/i1_bindings.json`. CCG re-run digits recorded under `falsification_measured_ccg_20260817`. |
| I2 protocol | n/a | No “we prove / verified / reproduced” load-bearing language. `results/claim_verify_meta.json` exists from the prior computational-claim-gate run. |
| I3 references | pass (online) | `10.5281/zenodo.19266807` and `10.5281/zenodo.19368609` resolved 200 on Zenodo API. Offline author–year rows are WARN only. |
| I4 method–artifact | limited → **auditor: same algorithm class** | Paper names `simulate.py` / `per_check_detection_models()`. Suite is 7-check Bernoulli MC + INT8/FP32 Mahalanobis + update-residual Check 4. Not a different solver class. |
| I5 overclaim | warn | Scanner flagged “First” / “first”. All hits are contribution numbering or calendar (“first of four gates”), not novelty/SOTA claims. |

## Blocking
None remaining after one repair.

**Repair 1 (I3):** Section 6.4 had `DOI: 10.5281/zenodo.19368609;` — the scanner kept the semicolon and 404’d a fake id. The record itself exists (`GET /api/records/19368609` → 200). Prose split so the DOI is a clean token.

## WARN
1. **I3 author–year unindexed** (9): Evidence Table venue-years (`Oct 2025`, `Apr 1985`, …) and `August 2026`. Normal Chokmah inline bibliography; not a fail. Existence of those works was **not** resolved online except the two Zenodo DOIs.
2. **I3 support (not NLI):** not checked. FLP (1985) and the arXiv IDs in Section 10 are plausible; passage-level “does the cited paper say this?” is out of v1.
3. **I1 rounding vs CCG:** paper `~0.06%` vs isolated CCG draw `0.040%`; `~89` / `~99` / `~62` vs `89.18` / `99.03` / `61.65`. v8.1 already stripped false-precision CIs. Direction matches.
4. **I1 P99/P99.9** (`4.61` / `4.82` ms) are not scanner result-claims (not % / not `[0,1]` rates). CCG measured `4.611` / `4.819`. Auditor match; not in I1 JSON.
5. **I4 Check 3b:** method table says IR bloom vs optical RCS; code uses 8-d kinematic-feature proxies. Section 9 already discloses the proxy. Same algorithm class (Mahalanobis), different sensor model.
6. **I4 Check 3a table vs §6.3:** table lists angle / velocity / apogee; executed check is Mach 5–15 and ≤10 g. Same envelope class; feature list is not identical.
7. **I4 leftover `Esimulate.py`:** v4 4-check file still in the tree; paper does not cite it. Do not run it as the suite.
8. **I4 Figure C / plot-path sweep:** `run_lethal_compliance_sweep` still writes `x[5] = x[4] + jump` with `x[4]` NaN. On-disk `C_lethal_compliance.png` predates the Check 4 update-residual repair. The 80 m claim is now executed by `claims/verify_c_lethal.py`, not by that sweep.
9. **I5 lexicon:** “First, it quantifies…” / “first of four development gates” / “first activation” — not novelty claims.

## Not checked here
- Citation support NLI (does Pandey/Guesmi/Sensors actually report those percents?)
- Scientific novelty or operational importance
- `Golden Dome Latency Governance-v8.md` (superseded sibling)
- Hardware / wet-lab / FPGA timing
- Lean proofs (no lake project)
- Re-running the sim (owned by computational-claim-gate; already green)
- Deposit/DOI badge inventory (`release-sync`)
- Whether Zenodo **paper** concept `19368681` / version `21971208` appear in the manuscript body (they do not; only AOM `19266807` and software `19368609` do)

## Evidence
- `results/integrity_audit.json` (`status=pass`, `timestamp_utc=2026-08-17T07:07:02Z`)
- `results/integrity_brief.md`
- `results/unbound_result_claims.md`
- `results/proposed_bindings.json`
- `results/i1_bindings.json`
- `integrity-manifest.json`

## Residual (out of scope)
- computational-claim-gate already **Verified** (separate ladder)
- lake proofs: n/a
- release-sync / Zenodo mint: not run
- Regenerating figures A/C after the Check 4 / Scenario A predicate repairs

## Residual human gates
- Decide whether v8.1 PDF on Zenodo `21971208` must be reminted after the one DOI-punctuation edit (text-only; numbers unchanged).
- Decide whether to delete or quarantine `Esimulate.py`.
- If publishing Section 10 percentages as load-bearing, spot-check those preprints (support NLI is human).
