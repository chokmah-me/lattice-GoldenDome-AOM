# BUILD DOC V1.4.2: GOLDEN DOME AUTONOMOUS OPERATIONS MODEL (AOM)

> **Status:** Draft, pending Phase GD-0 hardware characterization. All quantitative thresholds are proposed engineering defaults. Document is not locked until GD-0 Verify items are closed.
>
> **v1.4.2 (August 2026):** three additions tracking paper v8. (1) ISL availability constraint, Section 4. (2) Quantized-form recertification for replacement hub models, Sections 11 and 15. (3) Program calendar anchors, Section 12. No change to the 7-check gauntlet, clock-trust architecture, or thresholds.

---

### 1. Goal & Scope

To deploy a deterministic, high-integrity governance matrix for orbital edge nodes. The system enables pre-authorized kinetic intercepts against Hypersonic Glide Vehicles (HGVs) using a **Tier 1-E (Edge Autonomous)** model. The scope is limited to the Auditor Agent executing the 7-check gauntlet on-board the effector platform, running a unified operational and adversarial-robustness matrix within a non-negotiable 5.0 ms latency budget.

---

### 2. Context Snapshot

* **Environment:** LEO/GEO edge compute nodes. Space-to-hub-to-space propagation delays (e.g., 474 ms via GEO relay) and low ground-station availability (~8% duty cycle) mathematically preclude real-time HITL governance.
* **Threat Vector:** HGV terminal phase maneuvers (Mach 5+). Adversaries capable of physics-compliant spoofing, stale-state injection, and timestamp manipulation.
* **Execution Target:** Space-grade rad-hardened FPGA with hardware-enforced secure partitioning (e.g., Xilinx Versal RT or equivalent). LatticeOS RTOS.
* **Governance Model:** LatticeOS with tasks escalated by cognitive and latency budgets, utilizing pre-authorized MIO envelopes.

---

### 3. Acceptance Tests

* **Latency Pass:** Auditor agent completes the 7-stage check sequence (Schema, Hash, Physics/Cross-Modal, Temporal/Staleness, Confidence/PINN, Quorum, and Crypto Commit) in $\le 5.0$ ms and issues the `ENGAGE` command.
* **Fail:** Execution exceeds 5.0 ms, track violates physical bounds, or features fail normalization, triggering an automatic `HOLD` and async deferral.
* **Trust Pass:** Check 4 rejects any track where staleness evaluated against `t_auth` exceeds 500 ms. The payload `track_timestamp` field is never read by the auditor.
* **Robustness Pass:** Physics-compliant spoofing with spatial discontinuities $> 80$ m is rejected by Check 4's sliding-window median filter.

---

### 4. Constraints, Trade-offs & Rejected Alternates

* **Constraint (Timing):** Determinism is absolute. Any check exceeding its allocated sub-millisecond slice triggers an immediate `HOLD`.
* **Constraint (HITL):** Zero real-time HITL escalation for HGV terminal intercepts. Speed-of-light propagation and ground-station availability together foreclose it. Operators work in the outer MIO-authoring loop only.
* **Constraint (Security):** The reference clock cannot be derived from the track data payload. See Section 6 Known item (The Binary Cliff).
* **Constraint (ISL availability):** As of August 2026 the SDA Tranche 1 optical crosslink mesh has not been demonstrated on orbit (first activation targeted ~September 2026). Until it operates, `DEGRADED_QUORUM` is the prototype baseline, not a fault mode. All ISL-dependent elements (P2 clock, Check 6 quorum, multi-node deconfliction) are target-state. Test GD-B runs first as baseline characterization, then as fault injection once the mesh is live.
* **Constraint (Normalization):** Feature normalization to controlled variance is mandatory before Check 3 Mahalanobis computation to prevent INT8 quantization vulnerabilities.
* **Trade-off (Detection threshold):** We accept an adversarial sweet spot for spoofed tracks below the ~80 m temporal coherence threshold because achieving 100% detection is impossible without sacrificing legitimate intercept capability. This is an irreducible residual, not a design failure.
* **Trade-off (ISL jamming):** Under ISL denial we degrade to single-node authorization and conservative geo-fencing rather than risk an unauthorized kinetic event. Redundant engagement is the accepted residual.

---

### 5. System Map (FPGA-Nested)

The system is partitioned into two distinct hardware logic regions on a single die to ensure timing determinism and security isolation.

```text
External signals
  GPS III M-code (P1) ──┐
  ISL optical time (P2) ─┤──► [Region A: SECURE PARTITION]
  Atomic clock Rb (P3) ──┘       Clock Arbiter
                                  Crypto Provenance Binding
                                  Provenance Validator
                                  └──► t_auth (signed) ──────────────────┐
                                                                          │
[Sensor Mesh] ──► Raw Telemetry ──► [Region B: AUDITOR PIPELINE] ◄───────┘
                                       Check 1: Schema
                                       Check 2: MIO Hash
                                       Check 3: Physics + Cross-Modal
                                       Check 4: Staleness TTL (← t_auth)
                                       Check 5: Confidence + PINN
                                       Check 6: Geo-fence + ISL Quorum
                                       Check 7: Crypto Trace Commit
                                            │
                    [Hub-Tier (Maven/AIP)] ◄─┤ Async trace (post-engagement)
                                            │
                                      [Effector] ◄── ENGAGE pulse
```

Reference diagram: `clock_trust_fpga_dark.svg` / `.png` (v2, August 2026), included in the software deposit under `docs/`.

**Region A (Secure Partition):** Handles P1 (GPS M-code), P2 (ISL time transfer), and P3 (atomic holdover) inputs. Contains the Clock Arbiter (priority selector: P1 → P2 → P3), Crypto Provenance Binding (signs timestamp + source ID), and Provenance Validator (rejects payload timestamps). Emits `t_auth` across the hardware partition boundary. Logic tiles are locked via bitstream hardening to prevent reconfiguration.

**Region B (Auditor Pipeline):** Executes the 7-check sequential gauntlet. Consumes `t_auth` exclusively for Check 4. The payload `track_timestamp` field is structurally inaccessible to the auditor logic. A failure at any check triggers `HOLD`; execution does not continue.

**ISL common-mode note:** The P2 clock source and Check 6's quorum vote share the same optical ISL links. ISL jamming degrades both simultaneously. Under combined GPS denial and ISL jamming, Region A falls back to P3 atomic holdover as sole time source and Region B logs `DEGRADED_QUORUM`. See Section 14.

---

### 6. Known / Assumed / Verify Ledger

* **Known:** Timestamp manipulation by $\Delta t \le -500$ ms achieves 100% bypass of the staleness check when the timestamp is read from the payload. This is a step function (the "Binary Cliff"), not a probabilistic degradation. TTL tightening does not help; it moves the cliff. Authenticated `t_auth` from Region A eliminates this surface entirely.
* **Known:** Without strict feature normalization before Check 3, the INT8-to-FP32 Mahalanobis quantization gap scales with raw sensor dynamic range (3–4 orders of magnitude). Bypass rate climbs proportionally.
* **Assumed:** Physical separation of FPGA logic tiles is sufficient to prevent EMI/cross-talk between the PINN inference (Check 5) and the Clock Arbiter (Region A).
* **Assumed:** The onboard CSAC (P3) provides adequate holdover during combined GPS/ISL denial for engagement sequences of operationally relevant duration. Rb drift ~1 µs/day is negligible against the 500 ms TTL.
* **Verify (GD-0):** Characterize target hardware to confirm all 7 checks complete in $< 5.0$ ms under representative SEU jitter. If budget is exceeded, degrade to Checks 1, 2, 3 (Physics only), and 6 (Geo-fence only).
* **Verify (GD-0):** Quantify internal FPGA routing latency for the `t_auth` signal from Region A to Check 4 in Region B. Confirm it does not introduce non-deterministic jitter into the 0.9–1.4 ms Check 4 window.
* **Verify (GD-0):** Validate feature normalization procedure for Check 3 against target hardware and representative sensor dynamic ranges.
* **Verify (GD-0):** Characterize the ~80 m temporal coherence detection threshold against representative sensor noise profiles on target hardware. The 80 m figure is an arbitrary engineering default, not a validated operational value.
* **Verify (GD-1):** Validate local ISL quorum latency for MaRV engagement class (estimated 3–34 ms; must fit within 10–30 s window with margin).

---

### 7. Bill of Materials

* **Primary Compute:** Space-grade rad-hardened FPGA with secure partitioning (e.g., Xilinx Versal RT or equivalent). Secure partition tiles must support bitstream logic-lock.
* **Timing Stack — P1:** Multi-constellation GPS III M-code receiver with authenticated timing signal.
* **Timing Stack — P2:** Optical Inter-Satellite Link (ISL) transceiver (shared with Check 6 quorum path).
* **Timing Stack — P3:** Chip-Scale Atomic Clock (CSAC), rubidium oscillator. Crystal oscillators are not suitable for holdover.
* **Entropy Source:** Satellite radiation-event counter (hardware PUF for PINN Lorenz-noise seed).
* **Storage:** Tamper-evident append-only log memory for Check 7 trace commit.

---

### 8. Tools & Consumables

* Mission Intent Object (MIO) authoring suite.
* Hardware-in-the-Loop (HIL) latency profiler for GD-0 budget characterization.
* OpenTelemetry GenAI sidecar for async trace logging.
* Model-Abstraction Layer (Hub-Tier) for LLM swap and shadow-mode recertification.

---

### 9. Human-Machine Interface (HMI) Bounds

* **Operator Mode:** Strategic/Knowledge-Based. Operators author MIOs and conduct post-hoc audit. They do not participate in engagement execution.
* **HMI Contract:** Operators are structurally barred from the inner control loop by speed-of-light constraints. No HITL path exists for HGV terminal intercept. Post-engagement accountability relies entirely on the cryptographic trace committed in Check 7 and shipped to the Hub-Tier.
* **MIO Authoring:** Dual-authorization required. All MIOs carry strict UTC expiration timestamps. TTL shortens to 4 hours during model swap periods, forcing frequent re-authorization.

---

### 10. Step-by-Step Build Procedure (The 7-Check Gauntlet)

This pipeline operates strictly sequentially. A failure at any step triggers `HOLD`. Execution does not continue past a failed check.

1. **Schema Validation (0.0–0.2 ms):** Verify IntentCapsule structure against canonical schema. Zero floating-point operations. Hardware fixed-point arithmetic only.

2. **MIO Hash Integrity (0.2–0.5 ms):** Compare `mission_context` hash against the active pre-loaded MIO via hardware SHA-3 cryptographic check. MIO expired or chain broken → `HALT`, escalate via async trace.

3. **Physics Envelope + Cross-Modal Consistency (0.5–0.9 ms):** Apply strict feature normalization to controlled variance before computation. (3a) Fixed-point lookup against pre-authorized EngagementEnvelope (trajectory angle, velocity, apogee). (3b) Compute cross-modal Mahalanobis distance between IR bloom onset and optical RCS return against calibration covariance in read-only flash. Both sub-checks must pass. Failure → `HOLD`, increment spoof counter.

4. **Temporal Coherence + Staleness TTL (0.9–1.4 ms):** Execute sliding-window median filter on last N track updates to detect spatial discontinuity pop-ins ($> 80$ m). Evaluate staleness using `t_auth` from Region A exclusively. `track_timestamp` from the payload is not read. Reject if $t_{\text{auth\_now}} - t_{\text{auth\_track}} > 500$ ms. Failure → `HOLD`, log `TEMPORAL_FAIL`.

5. **Confidence Floor + Chaotic-Quantized PINN (1.4–2.8 ms):** Verify confidence $\ge 0.95$ (single fixed-point comparison, nanoseconds). Remaining budget allocated to the chaotic-quantized Physics-Informed NN, seeded by the satellite radiation-event counter (hardware PUF, physically uncloneable from the ground). PINN outputs a physics residual score; elevated residual signals a physically compliant but adversarially synthesized track. Failure → `HOLD`, log entropy seed hash for post-hoc forensics.

6. **Geo-fence + Local ISL Quorum (2.8–3.3 ms):** Verify target coordinates are within zero-collateral or pre-authorized engagement zones (geo-fence is evaluated first, locally, without ISL). Execute approximate BFT vote with N nearest orbital neighbors over optical ISL. Requires $\ge 2/3$ local majority. If ISL is jammed, fall back to single-node authorization and log `DEGRADED_QUORUM`. Geo-fence failure → `HOLD`. Quorum failure → defer, escalate to full PBFT mesh vote.

7. **Cryptographic Trace Commit (3.3–5.0 ms):** Write all check outputs, confidence scores, entropy seed hash, and quorum result to tamper-evident append-only log *before* actuation. This record is the kill-chain audit trail shipped to Hub-Tier post-engagement. Blocking commit failure → abort engagement, alert hub.

---

### 11. Configuration / Software Steps

* **Bitstream Hardening:** Enable logic-lock on the Secure Partition tiles (Region A) to prevent reconfiguration of clock-trust logic post-deployment.
* **Normalization Constants:** Load pre-computed variance tables for target HGV sensor classes into FPGA Block RAM (BRAM) before operational deployment. Tables are bound to the task, not the hub model.
* **Model-Abstraction Layer:** Deploy at the Hub-Tier to enforce canonical MIO output schema decoupled from any specific LLM provider. Enables forced model swap via shadow-mode recertification without interrupting edge-node engagement capability. Replacement models are recertified in their deployed quantized form (INT8 or lower); FP32-only certification is insufficient because quantization-conditioned backdoors activate only after weight rounding (paper Section 5.2 Step 4b; arXiv:2606.29239). See paper Section 5 for full swap runbook.

---

### 12. Verification & Test Plan

* **Calendar anchors (August 2026):** SBI competition closed Gate 1 of 4; ground tests before end 2026; orbital flight demos 2027; initial capability 2028; intercept demos not before mid-2029. Target: GD-0 closed before Gate 2; GD-1 before 2027 flight demos; GD-3 before any intercept demo.
* **Phase GD-0 — Hardware Characterization:** Profile all 7 checks on target rad-hardened FPGA under representative SEU jitter. Confirm P99.9 latency $< 5.0$ ms. If budget is exceeded, degrade to Checks 1, 2, 3, and 6. Validate clock-trust architecture, `t_auth` routing latency, feature normalization procedure, and temporal coherence detection threshold. Replace parametric per-check detection models with measured hardware failure rates.
* **Phase GD-0 — Test GD-A (The Binary Cliff):** Inject track payloads with varying $\Delta t$. Confirm 0% bypass for all $\Delta t \le -500$ ms when using authenticated `t_auth`. Confirm the step function is eliminated by Region A.
* **Phase GD-0 — Test GD-B (Common-Mode ISL Failure):** Simulate ISL jamming. Confirm P2 clock loss and Check 6 quorum degradation occur simultaneously and that Region A correctly falls back to P3 atomic holdover. Confirm `DEGRADED_QUORUM` is logged.
* **Phase GD-1 — Prototype Validation:** Run synthetic track injection tests against the full pipeline. Measure `auditor.latency_ms` distributions across the threat class space. Validate local ISL quorum latency for MaRV engagement class.
* **Phase GD-2 — Model Swap Simulation:** Execute a simulated forced model swap in shadow mode. Validate that edge nodes maintain engagement capability throughout at 4-hour MIO TTL.
* **Phase GD-3 — End-to-End Simulation:** Validate sidecar trace completeness above 99.9% against synthetic engagement traffic. Confirm post-hoc forensic log reconciliation correctly identifies injected inconsistencies in a simulated compromised-node scenario.

---

### 13. Observability & Telemetry Triggers

* `auditor.latency_ms` — Alert at $> 4.0$ ms, halt at $> 5.0$ ms.
* `capsule.rejection_rate` — Anomaly indicator for spoofing campaigns or model confidence distribution shift.
* `edge.quorum_degraded_events` — ISL jamming frequency tracker.
* `comms.trace_ship_lag_ms` — Serialization bloat indicator post-model-swap.
* `hub.mio_reauth_rate` — Elevated during swap periods; normalized post-restore.

---

### 14. Risks & Mitigations

* **Risk:** Physics-compliant spoofing below the ~80 m coherence threshold bypasses the gauntlet. **Mitigation:** Irreducible residual risk. Rely on upstream sensor diversity and rigorous MIO authoring. Phase GD-0 must characterize the operationally correct threshold.
* **Risk:** INT8 quantization collapses backdoor defenses. **Mitigation:** Mandatory feature normalization to controlled variance prior to Check 3 computation. Specified in edge auditor calibration procedure.
* **Risk:** Binary Cliff attack via timestamp injection. **Mitigation:** `t_auth` sourced exclusively from Region A (Secure Partition). Payload `track_timestamp` structurally inaccessible to auditor logic.
* **Risk:** ISL common-mode failure — jamming removes P2 clock source and Check 6 quorum simultaneously. **Mitigation:** P3 atomic holdover (CSAC/Rb) maintains staleness protection. Degraded-mode single-node authorization maintains engagement capability. Both degradation events are logged. Residual: two of seven checks degrade in exactly the threat environment where engagement is most likely. This is a mission doctrine decision, not an algorithmic one.
* **Risk:** PINN entropy source compromise (adversary models radiation environment). **Mitigation:** Satellite radiation-event counter is physically isolated in orbit. Lorenz seed is not transmitted. Residual: at maximum adversary sophistication (s=1.0), combined detection drops from 89.2% to 61.7% if PINN assumption fails.
* **Risk:** AI provider supply-chain severance. **Mitigation:** Model-Abstraction Layer enforces canonical MIO schema decoupled from provider. Shadow-mode recertification maintains edge continuity. Shortened TTL dead-man switch.

---

### 15. Maintenance & Upgrade Notes

* Calibration tables are bound to the task, not the hub model. After any hub model change, the replacement model must demonstrate calibration equivalence on the canonical task dataset before its MIOs are pushed to the edge pipeline.
* Replacement hub model certification must include a quantized-form pass (paper runbook Step 4b). A model that passes calibration and drift gates in FP32 but diverges in INT8/FP4 is rejected.
* MIO updates must be cryptographically signed by the Hub-Tier and transmitted via authenticated channels. Dual-authorization required at authoring.
* Post-model-swap: monitor `comms.trace_ship_lag_ms` to confirm replacement model output formatting does not degrade sidecar trace completeness below the 99.9% target.

---

### 16. Rollback / Safe-Fail Procedure

* **Trigger:** Any gauntlet check failure, Auditor Agent crash, or hardware health-check timeout exceeding 500 ms.
* **Action:** Immediate dead-man interlock of the kinetic chain. The Auditor enters Passive Sentry mode — logging all data for async Hub-Tier analysis, refusing actuation. The node degrades to scripted-only (CFT) operation. All non-deterministic outputs are held until Hub-Tier re-authorization.
