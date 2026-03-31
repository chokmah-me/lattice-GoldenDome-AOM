ב״ה

**Golden Dome Latency Governance**

Autonomous Operations Model Extended to Boost-Phase Intercept Timelines

**Daniyel Yaacov Bilar** Chokmah LLC · chokmah-dyb@pm.me 				 י״ג בְּנִיסָן תשפ״ו

*A position paper for defense technologists making architecture decisions*

# 1. Executive Synthesis

The Autonomous Operations Model (AOM) defined in the companion paper (Bilar 2026, *Anduril LatticeOS: Autonomous Operations Model*) assigns decisions to governance tiers by cognitive budget. Golden Dome breaks that model. Boost-phase intercept and terminal-phase Hypersonic Glide Vehicle (HGV) engagements impose single-digit-second decision windows that no ground-routed control loop can reliably meet.

This paper makes three contributions. First, it quantifies the combined propagation-delay and ground-station-availability argument that closes human-in-the-loop (HITL) control as a viable option for HGV terminal intercept (Section 2). Second, it specifies a dual-axis latency-aware tier matrix and a 7-check Gating Check Matrix that is its operational implementation, combining the Build Doc V1.2 auditor check sequence with an adversarial-robustness layer derived from current ML security literature (Sections 3-4).. Third, it specifies a Hub-Tier Model Swap Protocol addressing the requirement, made concrete by a supply-chain risk designation in February 2026, that the edge kill chain must survive legal or political severance of any single foundation-model provider (Section 5).

All quantitative thresholds are proposed engineering defaults. Phase GD-0 hardware characterization on target rad-tolerant FPGA or CGRA hardware must validate the 5 ms budget before operational deployment.

# 2. The Physics Constraint

## 2.1 Why HITL Fails for HGV Terminal Intercept

An HGV in terminal phase travels at Mach 5 or above and executes lateral maneuvers. Track prediction degrades rapidly with time. The intercept window from initial track lock to required actuation is 5 to 15 seconds, and every system element (sensors, compute, decision, effector deployment) must complete within that window.

The question is whether any path from a LEO sensor node to a hub-tier reasoning engine and back can complete within that window reliably enough to support HITL governance. The answer depends on two independent constraints: propagation delay and ground-station availability.

**Propagation delay.** The table below shows corrected one-way and round-trip latency for each communication path, computed from speed-of-light propagation at 299,792 km/s with slant-range geometry for 5° minimum elevation angle.

| Path | One-Way (ms) | Round-Trip (ms) | Notes |
| - | - | - | - |
| LEO direct downlink (550 km, zenith) | 1.8 | 3.7 | Best-case geometry. Ground station directly below. |
| LEO direct downlink (550 km, 5° elev) | 7.4 | 14.7 | Worst usable geometry before loss of signal. |
| ISL mesh relay (1-6 hops, 500-5,000 km/hop) | 1.7-100 | 3.4-200 | SDA PWSA mesh. Hop count depends on constellation geometry and ground-station placement. |
| GEO relay (TDRSS-class) | 237 | 474 | LEO → GEO (117.5 ms) + GEO → ground (119.4 ms). Legacy path. |
| Hub processing (cloud inference) | - | 50-2,000 | Optimistic floor assumes pre-loaded model. Pessimistic includes queuing and multi-step reasoning. |
| Human confirmation (HITL) | - | 250-750 | Operator confirmation latency from human factors literature. |


**Best-case round-trip with HITL.** Direct downlink at zenith, fast hub, fast operator: 3.7 + 50 + 250 = 304 ms. This fits inside the 5-15 s HGV window. If propagation delay were the only constraint, HITL would be feasible for a fraction of engagement geometries.

**Ground-station availability.** A LEO satellite at 550 km altitude has an orbital period of 95.5 minutes. A single ground station sees the satellite for approximately 8 minutes per pass at 10° minimum elevation, yielding an 8.3% duty cycle. At any random moment, the probability that a given sensor node has direct line-of-sight to any one ground station is roughly 8%. With six globally distributed stations, generous estimates reach approximately 50% simultaneous availability, but this assumes ideal weather, no RF interference, and no adversary denial.

The engagement window opens at the adversary's choosing, not ours. A governance architecture that requires ground contact for authorization will have no ground contact available for a substantial fraction of engagement opportunities. During those gaps, the system either misses the intercept or must have pre-authorized the edge node to act independently. In either case, HITL is not available when needed.

**The combined constraint.** Neither propagation delay alone nor availability alone closes HITL in every case. Together they do. The GEO relay path adds 474 ms of irreducible propagation per round-trip, pushing total HITL latency to 774-3,224 ms. The direct downlink path has acceptable latency but is unavailable for most of the orbit. The ISL mesh path adds variable delay (up to 200 ms round-trip at 6 hops) and itself depends on link availability between nodes, which degrades under adversary jamming (the same threat environment where engagement is most likely). No single path provides both low latency and guaranteed availability during an engagement window that opens without warning.

## 2.2 Restructuring Governance Around Physics

The AOM cannot change the physics. It can relocate the authorization decision to a point where latency is governed by compute, not light-speed propagation. That point is the edge node itself. The edge node receives a track update from the co-located or short-range sensor mesh within 40 ms, runs the gating checks within 5 ms, and issues the engagement command without waiting for hub acknowledgment.

The hub's role is restructured, not eliminated. It authors the Mission Intent Object (MIO) that pre-authorizes the edge node to act within a defined engagement envelope. That authorization is computed and signed in advance, before the engagement window opens. Post-engagement, the hub receives the full engagement trace and conducts accountability review. Operators work in the outer learning loop (MIO authoring and post-hoc audit) on timescales where human judgment is effective. They are structurally barred from the inner control loop where they cannot be effective and where forced intervention would degrade performance through decision-chain phase lag, the control-theory equivalent of pilot-induced oscillation.

# 3. Latency-Aware Tier Matrix

## 3.1 The Dual-Axis Extension

The original AOM matrix has one axis: cognitive budget against task value. This correctly captures the tradeoff between decision quality and computational cost. It does not capture the constraint that some decisions must be made before any hub round-trip can complete with guaranteed availability. The extended matrix adds a latency budget axis. For each engagement class, both axes determine tier assignment.

| Engagement Class | Window | Cognitive Budget | AOM Tier (original) | AOM Tier-Extended (this paper) |
| - | - | - | - | - |
| Boost-phase ICBM | 180-300 s | Substantial | Tier 2 / HITL preferred | Tier 2 unchanged. HITL preferred. Tier 1-E fallback if uplink degraded. |
| HGV terminal phase | 5-15 s | \< 5 ms gate | Tier 1 / HITL mandated | Tier 1-E (Edge Autonomous): pre-authorized MIO envelope + 5 ms deterministic gating. HITL physically excluded. Full post-hoc audit mandatory. |
| Ballistic MaRV terminal | 10-30 s | 5-10 ms gate | Tier 1 / HITL mandated | Tier 1-E. Marginally longer window permits local ISL quorum across 2-3 nearest nodes if ISL links are healthy. ISL latency budget for local quorum estimated at 3-34 ms (1-2 hops at 500-5,000 km). Phase GD-1 must validate. |
| Counter-UAS / cruise | \> 60 s | Seconds | Tier 2 / HITL | Tier 2 unchanged. Original AOM matrix applies. |


The Tier 1-E (Edge Autonomous) designation is not a weakening of governance. It is recognition that governance must match the timescale of the decision. The pre-authorized MIO envelope is the governance instrument. Dual-authorization at MIO authoring, strict UTC validity windows, and a zero-collateral geo-fence constraint make autonomous execution within the envelope accountable.

## 3.2 Governance Instruments by Tier

**Tier 2 (HITL, unchanged).** Engagement authorization requires real-time human confirmation. Cognitive load monitoring active. Full hub-tier reasoning available on the timescales this tier operates.

**Tier 1-E (Edge Autonomous).** Engagement authorization is delegated entirely to the pre-signed MIO envelope. The edge auditor checks every track against the MIO deterministically within 5 ms. No hub confirmation during execution. Full post-hoc audit mandatory for every engagement attempt, authorized or held.

**MIO Authoring (outer loop, human-paced).** Operators author MIOs at the hub on strategic timescales. Dual-authorization required. All MIOs carry strict UTC expiration timestamps. Shortened TTL (4 hours) applies during model swap periods, forcing frequent re-authorization.

**Post-hoc Accountability (hub-tier).** Every engagement attempt is logged with its full gating trace (all 7 check outputs, confidence scores, entropy seed hash, quorum result) and shipped to hub. Forced-choice UI patterns prevent automation complacency during MIO review.

# 4. The 5 ms Gating Check Matrix

## 4.1 Design Rationale

The gating matrix integrates two previously separate contributions. The operational check sequence from Build Doc V1.2 (Schema, MIO Hash, Envelope Match, Confidence Floor, Geo-fence, Staleness) catches misconfigured, stale, or out-of-envelope tracks through deterministic fixed-point comparisons.  The adversarial-robustness layer from current ML security literature (cross-modal Mahalanobis consistency, temporal coherence filtering, chaotic-quantized Physics-Informed Neural Network) catches electronically fabricated tracks engineered to pass the operational checks.

These are not competing designs. They address different threat surfaces at different cost points within the 5 ms budget. The operational checks run first because they are cheapest and catch the largest population of rejected tracks. The adversarial checks run against the smaller population that passes operational validation, where the marginal compute cost of the PINN inference is justified by the threat class.

| Window | Check | Method | Pass → Action | Fail → Action |
| - | - | - | - | - |
| 0.0-0.2 ms | 1. Schema Validation | Verify IntentCapsule structure against canonical schema. Fixed-point arithmetic only. Zero floating-point operations. | Proceed to Check 2 | HALT. Log SCHEMA\_FAIL to async sidecar. |
| 0.2-0.5 ms | 2. MIO Hash Integrity | Compare mission\_context hash against active pre-loaded MIO. Cryptographic check in hardware. | Proceed to Check 3 | HALT. MIO expired or chain broken. Escalate via async trace. |
| 0.5-0.9 ms | 3. Physics Envelope + Cross-Modal Consistency | Fixed-point lookup against pre-authorized EngagementEnvelope (trajectory angle, velocity, apogee). Cross-modal Mahalanobis distance between IR bloom onset and optical RCS return checked against calibration covariance in read-only flash. | Proceed to Check 4 | HOLD. Physics violation or cross-modal inconsistency. Increment spoof counter. Escalate to async BFT. |
| 0.9-1.4 ms | 4. Temporal Coherence + Staleness TTL | Sliding-window median filter on last N track updates. Genuine targets show progressive refinement; injected tracks show discontinuous appearance ('pop-in' signature). Reject if track\_age \> staleness\_ttl\_ms (default: 500 ms). **Clock-trust dependency:** staleness gate assumes authenticated timestamps. See Section 4.3. | Proceed to Check 5 | HOLD. Anomalous initialization or stale data. Log TEMPORAL\_FAIL. |
| 1.4-2.8 ms | 5. Confidence Floor + Chaotic-Quantized PINN | Confidence floor (\>= 0.95) is a single fixed-point comparison completing in nanoseconds. The remainder of the 1.4 ms budget is allocated to the chaotic-quantized Physics-Informed NN, seeded by satellite radiation-event counter (a physically uncloneable entropy source). PINN outputs a physics residual score; elevated residual signals a physically compliant but adversarially synthesized track. | Proceed to Check 6 | HOLD. Confidence below floor or elevated physics residual. Log entropy seed hash for post-hoc forensics. |
| 2.8-3.3 ms | 6. Geo-fence + Local ISL Quorum | Verify target coordinates within zero-collateral or pre-authorized engagement zones. Approximate BFT vote with N nearest orbital neighbors over sub-ms optical ISL. Requires \>= 2/3 local majority. Degraded-mode fallback to single-node authorization if ISL jammed, logs DEGRADED\_QUORUM. | AUTHORIZE engagement. Proceed to Commit. | HOLD. Geo-fence violation or quorum failed. Defer. Escalate to full PBFT mesh vote. |
| 3.3-5.0 ms | 7. Cryptographic Trace Commit | Write all check outputs, confidence scores, entropy seed hash, and quorum result to tamper-evident append-only log before actuation. This record is the kill chain audit trail shipped to hub post-engagement. | Proceed to actuation. | Blocking commit failure → abort engagement. Alert hub. |


## 4.2 Adversarial Notes

**Physics-compliant spoofing.** Checks 3 and 5 together catch tracks that violate physical law or show cross-modal inconsistency. A nation-state adversary with sensor calibration data and orbital ephemeris can synthesize inputs that satisfy both checks simultaneously. The checks raise attack cost and complexity. They do not eliminate the threat. That is the honest design boundary.

Falsification testing (Appendix: Simulation Suite, Scenario C) confirms this boundary quantitatively. Adversarial tracks that maintain Mach 5-15 speed and sub-10g lateral acceleration pass the physics envelope check (Check 3) at all tested discontinuity magnitudes. The temporal coherence filter (Check 4) detects pop-in injection when the spatial discontinuity exceeds approximately 80 meters. Below that threshold, detection rates drop below 50%, creating an adversarial sweet spot where physics checks pass and coherence checks are unreliable. The 80 m detection threshold is an engineering default derived from simulation. Phase GD-0 must characterize the operationally correct threshold against representative sensor noise profiles on target hardware.

**Quantization security paradox.** Standard INT8 quantization reduces backdoor defense detection to near zero while attack success stays above 99% on the classification tasks studied in Hong et al. (arXiv:2512.06243). Check 5 uses chaotic Lorenz-noise quantization seeded by a hardware entropy source physically uncloneable from the ground. The adversary cannot predict the quantization noise pattern without physical access to the satellite. This moves the attack surface from the mathematical to the physical domain.

Falsification testing (Scenario B) shows that at nominal configuration (INT8 threshold equal to FP32 threshold), a zero-knowledge adversary achieves approximately 0.06% bypass rate with features normalized to O(1) variance. This figure is misleadingly low. The test uses unit-scale features. Real orbital sensor data (range in meters, velocity in m/s, IR intensity in W/sr) spans 3-4 orders of magnitude in dynamic range. The quantization gap between INT8 and FP32 scales with the ratio of feature dynamic range to quantization resolution. Without strict feature normalization to a controlled variance before the Mahalanobis computation, the effective bypass rate will be substantially higher. **Feature normalization discipline is a hard requirement for Check 3 and must be specified in the edge auditor calibration procedure.** This is added to Section 8 Limitations.

**FLP impossibility and ISL jamming.** Check 6's local quorum is defeated if the adversary jams inter-satellite optical links. The degraded-mode fallback to single-node authorization accepts elevated false-positive risk in exchange for maintained engagement capability. This trade-off is not solvable by algorithm. It is a mission doctrine dial that must be set by appropriate authorities, not by the system architect.

## 4.3 Clock-Trust Dependency

The staleness gate in Check 4 rejects tracks older than staleness\_ttl\_ms (default 500 ms). This check is only as strong as the trust chain on the timestamp.

Falsification testing (Scenario A) demonstrates this directly. An adversary who can manipulate the timestamp field by any amount Δt ≤ -500 ms achieves 100% bypass of the staleness check. This is a step function, not a probability. The attack surface includes compromised ground relay injection, GPS spoofing on the track timestamp, and replay of previously valid track capsules with shifted timestamps.

The timestamp used by Check 4 must come from an authenticated clock source. Candidates include:

**GPS-disciplined oscillator with authenticated timing (GPS III military signals).** Provides sub-microsecond accuracy with spoofing resistance from the M-code signal. Vulnerable to GPS denial in contested space environments.

**Inter-satellite time transfer via optical ISL.** Constellation-internal time synchronization independent of ground-based GPS. Accuracy depends on ISL link quality and is degraded under the same jamming conditions that affect Check 6. Creates a circular dependency: the clock that validates Check 4 relies on the same ISL links whose availability Check 6 assesses.

**Onboard atomic clock (free-running, periodic sync).** Provides holdover timing during GPS denial. Drift accumulates. A rubidium oscillator drifts approximately 1 μs per day, which is negligible for the 500 ms staleness TTL. A crystal oscillator drifts orders of magnitude faster and is not suitable.

The architecture should layer these sources: GPS-disciplined primary, ISL-synced secondary, atomic holdover tertiary. The specific implementation is a Phase GD-0 deliverable. The critical design requirement is that **the staleness TTL must be evaluated against a timestamp whose provenance is cryptographically bound to an authenticated clock source, not simply read from the track data payload.**

## 4.4 Asynchronous Sidecar Processing

Checks deferred from the blocking chain run in the asynchronous sidecar. Sidecar results do not gate the current engagement but feed the post-hoc accountability system and the hub-tier threat picture. Deferred check results are logged with reason code LATENCY\_CRITICAL.

| Process | Trigger | Purpose |
| - | - | - |
| Full PBFT Mesh Vote | Any HOLD from Tier 1 | BFT consensus across full constellation. Result informs post-hoc review, not current engagement. |
| Cosine Drift Scoring | Every engagement attempt | Measures semantic drift between current Hub-Tier LLM outputs and MIO certification baseline. Flags model reasoning degradation before it reaches engagement logic. |
| Spoof Campaign Detection | Rolling 60-second window | Anomaly detection on rate and geographic distribution of HOLD flags. Coordinated injections targeting multiple nodes produce a detectable cluster signature. Escalates mesh to BFT-mandatory mode. |
| Forensic Log Reconciliation | After engagement window closes | Reconciles authorization records across nodes using cryptographic hash chain. Identifies nodes whose logged outputs are inconsistent with engagement outcome. Flags compromised nodes for decommissioning. |
| Calibration Audit | Weekly or post-model-swap | Calibration tables bound to the task, not the model. After any hub model change, replacement must demonstrate calibration equivalence on canonical task dataset before its MIOs enter the live pipeline. |


## 4.5 Multi-Node Engagement Deconfliction

The Tier 1-E architecture places autonomous engagement authority on each edge node independently. When multiple sensor nodes track the same target, independent authorization creates two operational risks: redundant engagement (multiple interceptors fired at the same target, wasting limited effector inventory) and fratricide (one node's effector enters another node's engagement zone).

The ISL quorum mechanism in Check 6 partially addresses this. Nodes that can communicate via optical ISL share track IDs and can coordinate effector assignment through the approximate BFT vote. Under normal ISL conditions, this provides deconfliction within the local quorum group.

Under ISL-denied conditions (DEGRADED\_QUORUM), deconfliction fails. Each node operating on single-node authority may independently authorize against the same track. The MIO envelope should include an effector allocation constraint (maximum interceptors per track ID per orbital sector) to bound the cost of redundant engagement. This constraint is deterministic and can be evaluated locally without ISL communication, at the cost of potentially leaving a track unengaged if the allocated node fails.

Full deconfliction under ISL denial is another instance of the FLP impossibility constraint. It cannot be solved without communication between nodes. The mission doctrine must accept either redundant engagement or missed intercept as the residual.

# 5. Hub-Tier Model Swap Protocol

## 5.1 Architectural Requirement

On February 27, 2026, the Department of Defense designated Anthropic PBC as a supply-chain risk under 10 U.S.C. § 3252, following Anthropic's refusal to remove safety constraints preventing use of its models in fully autonomous lethal weapons systems without human oversight. A presidential directive of the same date ordered all federal agencies to cease use of Anthropic technology with a six-month phase-out. On March 26, 2026, U.S. District Judge Rita F. Lin (N.D. Cal.) issued a preliminary injunction blocking enforcement of the § 3252 designation and the directive, finding likely First Amendment and Due Process violations. The separate FASCSA designation under 41 U.S.C. § 4713 remains active pending a D.C. Circuit ruling.

This sequence demonstrates the operational risk. Regardless of how *this* case resolves, any foundation model provider at the hub tier is subject to political severance on timelines of hours to days, far shorter than system re-architecture permits. Any hub-tier component that can be severed politically must have a pre-planned swap protocol that does not interrupt edge-node engagement capability.

The architectural solution has two parts. First, the Model-Abstraction Layer enforces a canonical MIO output schema decoupled from any specific model provider. The edge auditor parser reads the schema, not the model; replacing the model does not break the parser. Second, the swap follows a phased shadow-mode recertification sequence that keeps edge nodes on valid pre-signed MIOs throughout, using a shortened TTL as a dead-man's switch forcing frequent human re-authorization while the replacement is evaluated.

The key known fact about model substitution is that different foundation models exhibit different logit spreads. Confidence scores are not natively transferable between models. A replacement model that produces numerically similar outputs on general benchmarks may produce systematically different confidence distributions on the specific target classification task. The edge auditor's confidence floor check (Check 5) will silently reject a disproportionate fraction of MIOs from a replacement model whose distribution has shifted, without any explicit error. The calibration equivalence gate exists to catch this before it affects operations.

## 5.2 Swap Runbook

| Step | Action | Acceptance Gate | Fail Behavior |
| - | - | - | - |
| 1 | Isolate ejected model: disable outbound API route to MIO signing module immediately. | Zero MIO traffic from ejected model. | N/A. Immediate and irreversible. |
| 2 | Shorten MIO TTL to 4 hours globally. Forces human re-authorization at high frequency during transition. Acts as dead-man's switch. | lattice-cli confirms TTL constraint applied. | Halt and investigate configuration layer. |
| 3 | Initialize replacement model in shadow mode, routing outputs to metrics\_only. | Shadow deployment healthy. Zero traffic to MIO generator. | Roll back shadow deployment. Remain in degraded-manual mode. |
| 4 | Run canonical task dataset through shadow model. Measure confidence distribution. | Rolling mean within 2σ of ejected model's certification baseline. | Model rejected. Escalate to Certifying Authority. Procure alternate model. Restart at Step 3. |
| 5 | Drift recertification: validate sentence-transformer embeddings separate known-drifted vs. compliant capsules. | Separation accuracy \> 95%. Certifying Authority approves any deviation. Vendor override prohibited. | Reject replacement model. Hub remains in degraded-manual mode. Procure alternate. |
| 6 | Phased reintroduction: route replacement model to Tier 0 advisory dashboards. Monitor 72 hours. | auditor.rejection\_rate stable at baseline. No false-positive spike. | Revert to shadow mode. Investigate output formatting. |
| 7 | Full restore: re-enable MIO write access. Return TTL windows to operational defaults. | Edge nodes accept new MIOs without rejection rate increase. | Halt restore. Hub remains in extended degraded mode. |


If the replacement model fails the calibration equivalence gate at Step 4, the system halts the swap. The hub tier remains in degraded mode on 4-hour human-authorized MIO envelopes. The organization must procure a different replacement model and restart from Step 3. Tolerance deviations from the 2σ gate must be accepted by a human Certifying Authority. Vendor override of the gate is prohibited.

## 5.3 Post-Restore Validation

After full restore, monitor comms.trace\_ship\_lag\_ms to confirm the replacement model's output formatting does not create serialization bloat in the sidecar trace logs. A replacement model with a different output schema can silently degrade sidecar completeness (reducing forensic log completeness below the 99.9% target) without affecting the deterministic gating pipeline. The two failure modes are independent.

# 6. Falsification Results

This section summarizes findings from the simulation suite (simulate.py, included in the Zenodo archive). The suite tests three attack scenarios against the 7-check gating matrix and produces a sensitivity analysis of combined detection probability across adversary sophistication levels.

## 6.1 Scenario A: Ghost-in-the-Matrix (Stale-State Injection)

The adversary manipulates track timestamps to make stale data appear fresh, bypassing Check 4's staleness gate.

**Finding:** The staleness check is a binary gate on timestamp authenticity. At clock offset Δt ≤ -500 ms, bypass is 100%. This is not a probabilistic degradation; it is complete circumvention. The defense requires authenticated timestamps, not a tighter TTL. See Section 4.3.

**Latency validation:** Auditor latency under a log-normal SEU jitter model shows P99 = 4.61 ms and P99.9 = 4.82 ms. Both fall inside the 5 ms budget. The latency architecture holds under the modeled radiation environment.

## 6.2 Scenario B: Quantization-Aware Spoofing (INT8 vs. FP32)

The adversary exploits the precision gap between FP32 Mahalanobis distance (used in design validation) and INT8 Mahalanobis distance (used in deployed edge hardware) to craft inputs that pass the quantized check while failing the full-precision check.

**Finding:** At nominal configuration with unit-scale features, zero-knowledge adversarial success rate is approximately 0.06%. This figure is an artifact of favorable feature scaling. The adversarial success rate climbs monotonically as the INT8 threshold loosens relative to FP32, and scales with feature dynamic range. With raw sensor features spanning 3-4 orders of magnitude, the effective gap widens proportionally. The chaotic Lorenz quantization defense is sound in principle but depends on feature normalization to a controlled variance before the Mahalanobis computation. This normalization requirement is not optional.

## 6.3 Scenario C: Lethal Compliance (Physics-Valid, Temporally Incoherent)

The adversary injects a track that is physically valid at every point where it exists (Mach 5-15, sub-10g G-load) but appears abruptly with no prior track history ('cold start' injection).

**Finding:** The physics envelope check (Check 3) passes, as designed. The adversary's track stays within all kinematic bounds. The temporal coherence filter (Check 4) correctly detects the pop-in when the spatial discontinuity exceeds approximately 80 m. Below ~80 m, detection and physics-pass rates cross over: physics continues to pass while coherence detection drops below 50%. This is the adversarial sweet spot. The 80 m threshold is an engineering default requiring hardware characterization in Phase GD-0.

## 6.4 Sensitivity: Combined Detection vs. Adversary Sophistication

The 7-check matrix was modeled as a layered detection system where any single check catching the adversary counts as detection.

**Finding:** Combined detection probability exceeds 99% for adversaries below sophistication 0.5 (opportunistic to semi-capable). At nation-state sophistication (0.7), combined detection is approximately 99.3%. At maximum sophistication (1.0, nation-state with calibration data access), combined detection drops to approximately 89.1%. The residual at s=1.0 is dominated by the PINN's flat 72% detection floor, which depends on the hardware entropy source being physically uncloneable from the ground. If the PINN assumption fails in the orbital domain (Section 8), combined detection at s=1.0 drops substantially.

All four figures are included in the Zenodo archive as A\_ghost\_attack.png, B\_quant\_spoof.png, C\_lethal\_compliance.png, and D\_sensitivity.png.

# 7. Implementation Roadmap

## Phase GD-0: Hardware Characterization

Profile all 7 gating checks on target rad-tolerant FPGA or CGRA hardware. The 5 ms budget is an engineering estimate from non-rad-hardened analogues. Radiation-induced single-event upsets affect timing. If the full 7-check sequence cannot complete within 5 ms, degrade to Schema, MIO Hash, Physics Envelope, and Geo-fence. Generate chaotic quantization calibration curves specific to the hardware entropy source. Validate that the cross-modal Mahalanobis covariance matrices produce expected false-alarm rates against injected spoof tracks. **Characterize the temporal coherence detection threshold (currently 80 m default) against representative sensor noise profiles on target hardware.** Specify and validate the feature normalization procedure for Check 3 Mahalanobis computation. Validate clock-trust architecture (Section 4.3) on target hardware.

## Phase GD-1: Prototype Validation

Run synthetic track injection tests against the full pipeline. Measure auditor.latency\_ms distributions across the threat class space. Test degraded-mode ISL-jammed scenarios for DEGRADED\_QUORUM logging behavior. Validate local ISL quorum latency for MaRV engagement class (estimated 3-34 ms; must fit within 10-30 s window with margin).

## Phase GD-2: Model Swap Simulation

Execute a simulated forced model swap in shadow mode. Eject the primary model, run the recertification sequence with a known-compliant replacement, and validate that edge nodes maintain engagement capability throughout at 4-hour MIO TTL. Target: recertification completes within 4 weeks. Deliberately test a non-compliant replacement model to confirm rejection at Step 4 of the runbook.

## Phase GD-3: End-to-End Simulation

Validate sidecar trace completeness above 99.9% against synthetic engagement traffic. Confirm post-hoc forensic log reconciliation correctly identifies injected inconsistencies in a simulated compromised-node scenario.

## Observability

- auditor.latency\_ms: Alert \> 4.0 ms, halt \> 5.0 ms.

- capsule.rejection\_rate: Anomaly indicator for spoofing campaigns or model confidence distribution shift.

- comms.trace\_ship\_lag\_ms: Serialization bloat indicator post-model-swap.

- edge.quorum\_degraded\_events: ISL jamming frequency tracker.

- hub.mio\_reauth\_rate: Elevated during swap periods; normalized post-restore.

# 8. Risk Assessment

| Risk | Level | Mitigations | Residual |
| - | - | - | - |
| Physics-compliant spoof synthesis | Critical | Cross-modal Mahalanobis check (IR + optical). Chaotic-quantized PINN with hardware entropy seed. Temporal coherence filter rejects pop-in tracks above ~80 m discontinuity. | Adversary with sensor calibration access can synthesize inputs satisfying all checks. Sweet spot below ~80 m coherence threshold is quantified but not eliminated. Not fully eliminable. |
| MIO envelope incorrectness (friendly-fire / civilian casualty) | Critical | Dual-authorization at MIO authoring. Zero-collateral geo-fence hard constraint. Strict UTC validity windows. Cryptographic trace commit provides post-hoc forensic record. | Errors in MIO authoring propagate through all hardware checks undetected because the gating matrix has no ground truth independent of the MIO. Phase GD-0 validation mandatory before deployment. |
| Clock-source compromise bypasses staleness check | High | Layered clock-trust architecture: GPS-disciplined primary (M-code authenticated), ISL-synced secondary, atomic holdover tertiary. Cryptographic binding of timestamp provenance. | Under combined GPS denial and ISL jamming, holdover clock is the sole time source. Adversary with sustained jamming capability can exceed holdover accuracy bounds over extended engagement sequences. |
| ISL jamming severs local quorum | High | Degraded-mode fallback to single-node authorization with elevated false-positive risk, logged as DEGRADED\_QUORUM. | FLP impossibility is the acknowledged constraint. Multi-node deconfliction also fails, creating redundant engagement risk. Mission doctrine sets the availability-vs-false-positive dial. |
| INT8 quantization collapses backdoor defenses | High | Chaotic (Lorenz-noise) quantization seeded by hardware entropy source. Security evaluated in deployed quantized form, not FP32. | Defense effectiveness depends on strict feature normalization to controlled variance before Mahalanobis computation. Without normalization discipline, quantization gap scales with sensor feature dynamic range (3-4 orders of magnitude). |
| AI provider supply-chain severance | High | Model-Abstraction Layer enforces canonical MIO schema decoupled from provider. Shadow-mode recertification protocol (Section 5) maintains edge continuity. Shortened TTL dead-man's switch. | Re-integration minimum 4 weeks. Hub advisory capability degraded. Operator workload sharply elevated during gap. |
| Replacement model fails calibration gate | High | 2σ confidence gate blocks deployment. Drift separation must exceed 95%. Certifying Authority must approve any deviation. | Hub remains in degraded-manual mode until a compliant model is certified. |
| Foundation model reasoning drift | Medium | Deferred to async sidecar. Cosine drift scoring monitors MIO output quality continuously. Deterministic Tier 1 pipeline insulated from model drift. | Sidecar forensics quality degrades if model not periodically re-validated. |


The two Critical-level risks share a common structure: they cannot be detected by the gating checks because the gating checks assume valid inputs and a correct MIO. Physics-compliant spoofing satisfies all physics checks by construction. MIO errors propagate through hardware undetected because the hardware has no ground truth. Both require governance responses upstream of the technical architecture: sensor diversity, independent track validation, and rigorous MIO authoring procedures. The gating matrix is not a substitute for those.

# 9. Limitations

This is a position paper, not a validated system specification. All thresholds (the 5 ms compute budget, the 0.95 confidence floor, the 2σ calibration gate, the 95% drift separation requirement, the 80 m temporal coherence detection threshold) are proposed engineering defaults requiring Phase GD-0 characterization before any operational use.

The PINN approach assumes a physics model adequate to distinguish genuine engagement signatures from adversarially synthesized ones can be specified, trained, and maintained under operational conditions. This has not been validated in the orbital domain. Chaotic quantization defense has been demonstrated on classification benchmarks; its behavior on sensor time-series data in a rad-hardened environment is not established. The combined detection rate at maximum adversary sophistication (89.1% in simulation) depends heavily on the PINN's 72% detection floor, which in turn depends on the hardware entropy source being physically secure.

The INT8 Mahalanobis check (Check 3 cross-modal consistency) requires strict feature normalization to controlled variance before computation. Without this normalization, the quantization gap between INT8 and FP32 scales with the dynamic range of raw sensor features, which can span 3-4 orders of magnitude. The simulation uses unit-scale features and therefore understates the operational quantization gap. Feature normalization discipline must be specified as part of the edge auditor calibration procedure and validated in Phase GD-0.

The staleness check (Check 4) is a binary gate on timestamp trust, not a probabilistic filter. Its effectiveness depends entirely on the clock-trust architecture described in Section 4.3. Under combined GPS denial and ISL jamming, the staleness check provides no protection against replay or stale-injection attacks beyond the holdover accuracy of the onboard atomic clock.

The model swap protocol assumes a calibration-equivalent replacement model can be procured within the operational gap period. Organizations must maintain pre-qualified backup models and must not reach a state where only one provider can satisfy the calibration gate.

The latency table in Section 2.1 uses speed-of-light propagation in vacuum. Atmospheric absorption, link-layer framing overhead, ISL acquisition and pointing delays (SDA standard requires \< 100 s for initial acquisition, with a stretch goal of \< 10 s), and ground-station weather degradation add variable latency not captured in the propagation-only figures. These additional delays strengthen the argument against HITL reliability but should be quantified in Phase GD-0.

Nothing in this paper constitutes legal, doctrinal, or weapons-employment authority. Questions of Rules of Engagement, international humanitarian law, and autonomous weapons governance are outside scope and must be resolved by appropriate authorities before any implementation proceeds.

# 10. Evidence Table

| Claim | Source | Confidence | Domain Gap |
| - | - | - | - |
| Wavelet/Fourier feature extraction achieves F1 ~0.92 with 60% energy reduction | Sensors 25(21):6629 (Oct 2025) | High (peer-reviewed) | IoT domain. Orbital hardware validation needed. |
| FPGA/CGRA autoencoder pipeline for time-critical edge anomaly detection demonstrated | Electronics 15(2):414 (Jan 2026) | High (peer-reviewed) | Smart grid domain. Architecture directly transferable. |
| INT8 quantization reduces backdoor defense detection to near 0%; attack success stays \> 99% | Hong et al., arXiv:2512.06243 | High (preprint, specific to classification tasks studied) | Classification tasks. Sensor time-series gap exists. Feature normalization dependence not characterized. |
| Patch attacks achieve \> 70% success at 2-bit quantization; transfers across bitwidths | arXiv:2503.07058 (Mar 2025) | High (preprint) | Physical spoofing maps to patch-class attack. |
| Lorenz/Henon chaotic quantization improves adversarial accuracy by up to 43% | Neural Networks, ScienceDirect (Jan 2024) | Medium-High (peer-reviewed, classification benchmarks only) | Rad-hardened deployment unvalidated. |
| SNN Hierarchical Temporal Defense reduces adversarial success rate on neuromorphic hardware | NeurIPS ML4PS 2025 Workshop | Medium (workshop paper) | Space-qualified rad-hardened platforms not yet validated. |
| Byzantine-resilient satellite thrust consensus with 3-layer validation scales to 100+ nodes | ScienceDirect (Mar 2026) | High (peer-reviewed) | Orbital control domain. Directly applicable. |
| Approximate BFT outperforms exact BFT under LEO latency constraints | arXiv:2312.05213 | High (preprint) | Supports local quorum fallback design. |
| FLP impossibility: consensus impossible in async system with even one faulty process | Fischer, Lynch, Paterson (JACM 1985) | Definitive | Sets the availability-vs-false-positive dial requirement. |
| LEO visibility to single ground station: ~8% duty cycle at 550 km, 10° min elevation | Computed from orbital mechanics (this paper) | High (first-principles geometry) | Does not account for atmospheric or weather degradation. |
| SDA PWSA optical ISL mesh 3+ months behind schedule; mesh network not yet established for Tranche 1 | Breaking Defense, March 2026 | Current reporting | ISL mesh availability assumptions in this paper may be optimistic relative to fielded capability timeline. |
| On-orbit compute identified as critical to Golden Dome latency requirements by U.S. Space Command | Air & Space Forces Magazine, March 2026 | Current reporting | Supports edge-compute architecture direction. |


# 11. Conclusion

Golden Dome's engagement timelines do not bend to governance preferences. For HGV terminal intercept, the combination of propagation delay and ground-station availability closes HITL as a reliable governance mechanism. The correct response is not to pretend the constraint does not exist, and not to accept a missed-intercept rate from trying to insert human confirmation into a window that may have no ground link. It is to restructure governance around the timescale at which it can be effective.

The pre-authorized MIO envelope is governance at the right timescale: strategic, deliberate, dual-authorized, and time-bounded. The 7-check deterministic gating matrix is execution at the right timescale: sub-5 ms, hardware-fixed, and adversarially hardened against gradient-based attacks through a physically uncloneable entropy source. The Model-Abstraction Layer and swap protocol are supply-chain resilience at the right timescale: weeks, human-certified at each gate, with no single-provider dependency in the kill chain.

The irreducible residuals (physics-compliant spoofing below the ~80 m coherence threshold, FLP impossibility under ISL jamming, MIO envelope errors, clock-trust degradation under combined denial) are not failures of the architecture. They are honest statements of what a finite-compute, speed-of-light-bounded system cannot guarantee against a capable adversary. The dial between engagement availability and false-positive risk is set by mission doctrine. The architect's job is to make that dial explicit, calibrated, and accountable. This paper specifies what the dial looks like and what turning it costs.

**AI Utilization Statement**

Research synthesis, critical evaluation, and draft generation assisted by Claude (Anthropic), Gemini 3, proprietary NovaKit Utilities  v3, proprietary "Engineering Engine" build system architecture via Chokmah LLC internal workflow. The author directed all arguments, specified all architectural decisions, supplied all source documents, and takes full responsibility for the content.

