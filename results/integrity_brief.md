# Integrity brief — lattice-GoldenDome-AOM

## Status
lattice-GoldenDome-AOM — pass (I1 pass; I3 pass (2 resolved, 0 unresolved))

## Reproduce
```
python path/to/manuscript-integrity-gate/scripts/audit_manuscript.py --project lattice-GoldenDome-AOM --propose-bindings
python path/to/manuscript-integrity-gate/scripts/audit_manuscript.py --project lattice-GoldenDome-AOM
python path/to/manuscript-integrity-gate/scripts/audit_manuscript.py --project lattice-GoldenDome-AOM --online
```

## Checks

| Check | Status | Notes |
|-------|--------|-------|
| I1 numbers | pass | unbound buckets {} |
| I2 protocol | limited | |
| I3 references | pass | existence via Zenodo/Crossref/OSF APIs for identifiers in this draft — not a four-API ScientistOne audit; not citation support |
| I4 method–artifact | limited | |
| I5 overclaim | warn | |

## Residual human gates
none from this scan

## Evidence
- `results/integrity_audit.json`
- `results/unbound_result_claims.md`
