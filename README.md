# Golden Dome Autonomous Operations Model (AOM)

## Project Description

**Golden Dome AOM** is a red-team simulation suite for a Tier 1-E (Edge Autonomous) lethal-intercept governance system. It models a sub-5 millisecond, 7-check auditor matrix running on LEO/GEO edge compute nodes to authorize kinetic intercepts against Hypersonic Glide Vehicles (HGVs) traveling at Mach 5+. The core research objective is adversarial falsification: systematically discovering the attack vectors and blind spots where the 7-check gating matrix fails to detect spoofed or manipulated tracks. The system operates under strict latency and network constraints (474 ms LEO-to-GEO relay delays, ~8% ground station availability) that preclude human-in-the-loop authorization, requiring full autonomous execution within an authenticated edge envelope.

## Setup

### Requirements
- Python 3.8+
- NumPy, SciPy, Matplotlib, Numba (see `requirements.txt`)

### Installation & Running

```bash
pip install -r requirements.txt
python simulate.py      # Runs scenarios A–D (Ghost-in-the-Matrix, Quantization Spoof, Lethal Compliance, Analytical Sensitivity)
python Esimulate.py     # Runs scenario E (Monte Carlo Sensitivity with 95% confidence intervals)
```

Output charts are saved to `results/`.

## Results: Attack Scenarios & Findings

### A_ghost_attack.png
**Ghost-in-the-Matrix Attack: Clock-Skew Injection**

This scenario sweeps a clock-skew delta-t from −1000 ms to +1000 ms, measuring the False Acceptance Rate (FAR) of the staleness check (Check 4). The chart demonstrates that injecting a timestamp manipulation of Δt ≤ −500 ms achieves 100% bypass of the staleness TTL gate, allowing a stale adversarial track to be accepted as fresh. A secondary panel shows the measured auditor latency distribution (base 3.8 ms + log-normal jitter from radiation Single Event Upsets), with P50, P99, and P99.9 percentiles annotated against the 5 ms hard real-time deadline. **Finding:** The system is vulnerable to spoofed timestamps unless the staleness TTL validation is bound to a cryptographically authenticated clock source (e.g., GPS M-code, atomic holdover) rather than untrusted payload timestamps.

### B_quant_spoof.png
**Quantization-Aware Spoofing: INT8 Mahalanobis Gate Exploitation**

This scenario quantifies the adversarial advantage created by the precision loss from INT8 quantization of features. The x-axis sweeps the INT8 Mahalanobis distance threshold from 50% to 150% of the reference FP32 chi-squared threshold. The y-axis plots the adversarial success rate — the fraction of crafted feature vectors that pass the quantized gate (Check 3) while failing the gold-standard FP32 gate. The chart shows a measurable percentage of synthetic adversarial candidates exploit the quantization gap. **Finding:** A zero-knowledge adversary (with no access to model weights) can craft feature vectors that fall in the quantization "dead zone," passing the INT8 gate while failing the floating-point reference. Strict feature normalization to controlled variance before the quantized Mahalanobis computation is a hard requirement to mitigate this risk.

### C_lethal_compliance.png
**Lethal Compliance: Physics-Valid Cold-Start Pop-In**

This scenario tests the temporal coherence check (Check 5) against a realistic adversarial track: a "pop-in" that appears without warning but maintains physics-valid speed and G-load at every instant of its existence (no kinematic violations). The chart plots genuine and adversarial track trajectories alongside the temporal coherence filter response. The key finding is a **spatial discontinuity threshold of ~80 meters**: pop-in attacks with lateral jump sizes below this threshold are missed by the temporal coherence filter, while larger jumps are correctly flagged as anomalous. **Finding:** The system has an accepted detection blind spot: a physics-valid cold-start adversarial track with a sub-80 m spatial discontinuity can bypass the temporal coherence gate. This threshold is acknowledged in the build doctrine as a trade-off between filter sensitivity and false positive rate.

### D_sensitivity.png
**Analytical Sensitivity: Detection Probability vs. Adversary Sophistication**

This scenario performs an analytical sweep of adversary sophistication (s, from 0 = naive random spoofing to 1 = nation-state level physics-aware attack) and plots the combined detection probability of all check layers. Individual curves show the detection probability for each check (Physics Envelope, Temporal Coherence, PINN Confidence, Quorum Agreement), while the combined curve (bottom) represents the aggregate fail-safe outcome. **Finding:** Against a highly sophisticated adversary (s > 0.7), combined detection probability falls meaningfully below 100%, indicating that no single check layer is insurmountable and that layered defenses are necessary but imperfect.

### E_sensitivity_full.png
**Monte Carlo Sensitivity Validation: 50,000 Trials with Confidence Bands**

This scenario empirically validates the analytical sensitivity curves through Monte Carlo simulation at five sophistication levels (s = 0.0, 0.25, 0.5, 0.75, 1.0), with 50,000 trials per level. The chart plots combined detection probability (%) vs. adversary sophistication with shaded 95% Wilson confidence interval bands in blue. **Finding:** The empirical Monte Carlo results confirm the analytical D curve and provide rigorous lower and upper confidence bounds on adversarial robustness claims, demonstrating that even at maximum sophistication, detection probability remains non-zero but with non-trivial uncertainty.

---

## Architecture & Build Documentation

For detailed technical specifications, design rationale, and build phases, see:
- `BuildDoc1-3.md` — Full architecture, 7-check gating matrix, acceptance tests, and constraints
- `golden_dome_v5.md` — System design and threat model

## License & Attribution

This project is part of the Golden Dome Autonomous Operations Model research suite.
