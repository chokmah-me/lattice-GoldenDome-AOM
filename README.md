# Golden Dome Autonomous Operations Model (AOM)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19368609.svg)](https://doi.org/10.5281/zenodo.19368609)

## Project Description

**Golden Dome AOM** is a red-team simulation suite for a Tier 1-E (Edge Autonomous) 
lethal-intercept governance system. It models a sub-5 ms, 7-check auditor matrix 
running on LEO/GEO edge compute nodes to authorize kinetic intercepts against 
Hypersonic Glide Vehicles (HGVs) at Mach 5+.

The core objective is adversarial falsification: systematically finding where the 
7-check gating matrix fails to detect spoofed or manipulated tracks. The system 
operates under strict latency and availability constraints (474 ms LEO-to-GEO relay, 
~8% ground-station duty cycle) that preclude human-in-the-loop authorization.

Companion paper: Bilar (2026), *Golden Dome Latency Governance: Autonomous Operations 
Model Extended to Boost-Phase Intercept Timelines*, DOI: [paper DOI here]  
Companion AOM paper: Bilar (2026), *Anduril LatticeOS: Autonomous Operations Model*, 
DOI: 10.5281/zenodo.19266807

---

## Scenarios

### A. Ghost-in-the-Matrix (Stale-State Injection)
Sweeps clock offset Δt from −1000 ms to +1000 ms against Check 4's staleness gate.

**Finding:** Bypass is binary, not probabilistic. At Δt ≤ −500 ms, staleness check 
bypass is 100%. The defense requires authenticated timestamps (GPS M-code, atomic 
holdover), not a tighter TTL. Auditor latency under log-normal SEU jitter: P99 = 
4.61 ms, P99.9 = 4.82 ms. Both inside the 5 ms budget.

### B. Quantization-Aware Spoofing (INT8 vs. FP32)
Crafts adversarial inputs that pass the INT8 Mahalanobis gate (Check 3b) while 
failing the FP32 gate, using zero model-weight knowledge.

**Finding:** At nominal configuration with unit-scale features, adversarial success 
rate is ~0.06%. This understates the operational risk. The INT8/FP32 precision gap 
scales with feature dynamic range. Real sensor data (range in meters, velocity in m/s, 
IR intensity in W/sr) spans 3-4 orders of magnitude. Without strict feature 
normalization to controlled variance before the Mahalanobis computation, the effective 
bypass rate is substantially higher. Adversarial success climbs monotonically as the 
INT8 threshold loosens relative to FP32.

### C. Lethal Compliance (Physics-Valid, Temporally Incoherent)
Injects a cold-start track that is physically valid at every point (Mach 5-15, 
sub-10g G-load) but appears abruptly with no prior history.

**Finding:** Check 3a (kinematic bounds) passes the adversarial track at all tested 
discontinuity magnitudes. Check 3b (cross-modal Mahalanobis) also passes at the 
default 50 m pop-in offset (FP32 score = 0.7, threshold = 3.9): the adversary's 
aggregate kinematic statistics stay close to the genuine track's calibration 
distribution. Detection falls entirely to Check 4. The temporal coherence filter 
correctly catches the pop-in when spatial discontinuity exceeds ~80 m. Below that 
threshold, coherence detection drops below 50%, creating an adversarial sweet spot 
where both Check 3 sub-checks pass and coherence is unreliable. The 80 m threshold 
is an arbitrary engineering default; Phase GD-0 must characterize it against 
representative sensor noise on target hardware.

### D. Per-Check Analytical Sensitivity
Analytical curves of per-check detection probability vs. adversary sophistication 
(s = 0 to 1) for all 7 checks.

**Finding:** At low sophistication, schema, physics, and temporal checks dominate. 
At high sophistication, the PINN (flat at ~72%) becomes the primary remaining 
defense because its chaotic Lorenz quantization is seeded by a hardware entropy 
source a zero-knowledge adversary cannot replicate. The geo-fence and staleness 
curves degrade sharply above s = 0.6 as the adversary learns zone geometry and 
clock manipulation. Combined detection stays above 90% until s ≈ 0.85.

### E. 7-Check Monte Carlo Sensitivity (50,000 trials per point)
Monte Carlo combined detection across 20 sophistication levels with Wilson 95% 
confidence intervals. Includes a PINN-zeroed degradation scenario (p_pinn forced 
to 0) to bound the cost of hardware entropy source compromise.

**Finding (full 7-check model):**

| Sophistication | Detection (%) | 95% CI | SE (%) |
|---|---|---|---|
| 0.00 (random) | 100.00 | [99.99, 100.00] | 0.00 |
| 0.26 (opportunistic) | 100.00 | [99.99, 100.00] | 0.00 |
| 0.53 (semi-capable) | 99.93 | [99.90, 99.95] | 0.01 |
| 0.74 (nation-state) | 99.03 | [98.94, 99.11] | 0.04 |
| 1.00 (nation-state + calibration access) | 89.18 | [88.91, 89.45] | 0.14 |

**Finding (PINN-zeroed, 6-check degradation):**  
At s = 1.0: detection drops from 89.2% to 61.7% (95% CI: [61.2, 62.1]).  
At s = 0.74: drops from 99.0% to 96.1%.  
The PINN accounts for a 27.5 percentage-point gap at maximum sophistication and 
is the single largest per-check contributor at high adversary capability.

---

## Setup

### Requirements
- Python 3.8+
- NumPy, SciPy, Matplotlib
- Numba (optional, falls back to scipy.integrate.solve_ivp if absent)

### Installation & Running
```bash
pip install -r requirements.txt
python simulate.py
```

Output charts saved to `results/`:

| File | Content |
|---|---|
| `A_ghost_attack.png` | Staleness bypass cliff + auditor latency distribution |
| `B_quant_spoof.png` | INT8/FP32 score space, precision-loss distribution, FAR sweep |
| `C_lethal_compliance.png` | Trajectory, coherence residuals, speed/G-load, check-coverage sweep |
| `D_sensitivity.png` | Per-check detection curves vs. adversary sophistication |
| `E_sensitivity_full.png` | Monte Carlo combined detection + PINN-zeroed comparison |

---

## Caveats

The per-check detection models (D and E) are parametric assumptions informed by 
Scenarios A-C and ML security literature. They are not measured hardware failure 
rates. The combined detection figures are only as reliable as those assumptions. 
Phase GD-0 must replace them with measured rates on target rad-tolerant hardware.

---

## License & Attribution

MIT License. Part of the Golden Dome Autonomous Operations Model research suite.  
Author: Daniyel Yaacov Bilar, Chokmah LLC (chokmah-dyb@pm.me)
