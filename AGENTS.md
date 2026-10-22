# AGENTS.md — lattice-GoldenDome-AOM

Red-team simulation suite for a Tier 1-E (edge autonomous) intercept auditor. Adversarial falsification of a 7-check gating matrix. Not an operational fire-control system.

## Commands

```powershell
pip install -r requirements.txt
python simulate.py
python claims/verify_a_ghost.py
python claims/verify_b_quant.py
python claims/verify_c_lethal.py
python claims/verify_d_analytical.py
python claims/verify_e_montecarlo.py
```

## Work rules

- Pin `numpy==2.4.4` and `scipy==1.17.1`. Check 3a (Lorenz entropy tape / scipy RK45) is solver-sensitive; recorded green under that pair, red under scipy 1.11.4.
- Ghost-in-the-matrix bypass at \(\Delta t \le -500\) ms is binary. Do not rewrite it as a probability.
- Keep receipt-backed edits on claims and `results/` briefs.

## Pointers

- `README.md` — scenarios and findings
- `requirements.txt` — pin + adjudication note
- `claim-manifest.json` — computational-claim-gate
- `ZENODO.md` — paper/software DOIs
