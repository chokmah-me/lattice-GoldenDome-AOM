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
python simulate.py      # Runs scenarios A–E (Ghost-in-the-Matrix, Quantization Spoof, Lethal Compliance, Analytical Sensitivity, Monte Carlo Sensitivity with 95% confidence intervals)
```

Output charts are saved to `results/`.



## License & Attribution

This project is part of the Golden Dome Autonomous Operations Model research suite.
