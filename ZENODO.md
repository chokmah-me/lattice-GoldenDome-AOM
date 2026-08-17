# Zenodo deposits

Two separate Zenodo **concepts** (do not merge paper and software):

| Role | DOI | Status |
|---|---|---|
| **Paper concept** | [10.5281/zenodo.19368681](https://doi.org/10.5281/zenodo.19368681) | **Stable.** Always resolves to the latest paper PDF. |
| **Paper (current version)** | [10.5281/zenodo.21971208](https://doi.org/10.5281/zenodo.21971208) | v8.1; 2026-08-16. **Published.** |
| **Software concept** | [10.5281/zenodo.19368608](https://doi.org/10.5281/zenodo.19368608) | Always latest software zip. |
| **Software (current version)** | [10.5281/zenodo.21979227](https://doi.org/10.5281/zenodo.21979227) | GitHub Release `1.0.1` (2026-08-17). Concept `19368608` resolves here. Do not merge into the **paper** concept. |
| **Software (prior version)** | [10.5281/zenodo.19368609](https://doi.org/10.5281/zenodo.19368609) | GitHub Release `1.0.0`. Superseded. |

## Paper version history

| Version DOI | Status | Notes |
|---|---|---|
| [10.5281/zenodo.19368682](https://doi.org/10.5281/zenodo.19368682) | **Superseded after mint** | v7 / Zenodo version `1.0.0`; 2026-03-31. Catalog URL path fragment. |
| 10.5281/zenodo.21971138 | discarded | Unpublished v8 draft; deleted. |
| [10.5281/zenodo.21971208](https://doi.org/10.5281/zenodo.21971208) | **Current** | v8.1; 2026-08-16. PDF + source + Figure F. |

## External links

- **GitHub:** https://github.com/chokmah-me/lattice-GoldenDome-AOM
- **Release:** https://github.com/chokmah-me/lattice-GoldenDome-AOM/releases/tag/1.0.1 (current software). Prior: [`1.0.0`](https://github.com/chokmah-me/lattice-GoldenDome-AOM/releases/tag/1.0.0).
- **OSF (legacy v7 mirror):** https://osf.io/sxt7v/ — do not open a new child
- **Catalog (v8.1):** https://chokmah.me/research/golden-dome-latency-governance-autonomous-operations-model-e-21971208/  
  Historical v7 slug: `…-19368682/` (page now points at v8.1 + concept)

## Citation

**Paper (prefer concept DOI; version DOI for a pinned PDF):**

Bilar, D. Y. (2026). *Golden Dome Latency Governance: Autonomous Operations Model Extended to Boost-Phase Intercept Timelines* (v8.1). Zenodo.  
https://doi.org/10.5281/zenodo.19368681 (concept); https://doi.org/10.5281/zenodo.21971208 (this PDF)

**Software:**

Bilar, D. Y. (2026). *lattice-GoldenDome-AOM: Golden Dome AOM falsification suite*. Zenodo.  
https://doi.org/10.5281/zenodo.19368608 (concept)

Simulation results are parametric assumptions, not measured hardware failure rates.

## Deposit files (v8.1 paper record)

- `dyb-2026i-goldendome-R-v8.1.pdf`
- `clock_trust_fpga_dark_v2.png` (Figure F)

Source markdown stays in the repo only; it is not on the Zenodo record.

Do **not** re-upload `simulate.py`, `requirements.txt`, or figures A–E onto the paper record.

## Related identifiers (v8.1)

| Relation | Identifier |
|---|---|
| `isSupplementedBy` | 10.5281/zenodo.21979227 (software 1.0.1; prior 10.5281/zenodo.19368609) |
| `isNewVersionOf` | 10.5281/zenodo.19368682 |
| `continues` | 10.5281/zenodo.19266807 |
