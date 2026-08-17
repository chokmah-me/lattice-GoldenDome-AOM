<p class="hebrew-epigraph" dir="rtl" lang="he">אִם יִרְצֶה הַשֵּׁם</p>
<p class="hebrew-date" dir="rtl" lang="he">ג׳ בֶּאֱלוּל תשפ״ו</p>

# **Golden Dome Latency Governance**

### Autonomous Operations Model Extended to Boost-Phase Intercept Timelines

**Daniyel Yaacov Bilar**, Chokmah LLC, chokmah-dyb@pm.me ORCID: [0000-0002-9040-6914](https://orcid.org/0000-0002-9040-6914)

*A technical position paper for defense technologists making architecture decisions*

*Version 8.1, August 2026. Revision of v8. Changes: stripped false-precision CIs from parametric model results (Sections 6.4, 11), labeled timing budget as notional (Section 4.1), added scalar-model caveat (Section 6.4), qualified PINN entropy claim (Section 4.1), condensed AI statement, updated Build Doc reference. Architecture, thresholds, and simulation results are unchanged.*

# 1. Executive Synthesis

The Autonomous Operations Model (AOM) defined in the companion paper (Bilar 2026, *Anduril LatticeOS: Autonomous Operations Model*, DOI: 10.5281/zenodo.19266807) assigns decisions to governance tiers by cognitive budget. Golden Dome breaks that model. Boost-phase intercept and terminal-phase Hypersonic Glide Vehicle (HGV) engagements impose single-digit-second decision windows that no ground-routed control loop can reliably meet.

This paper makes three contributions. First, it quantifies the combined propagation-delay and ground-station-availability argument that closes human-in-the-loop (HITL) control as a viable option for HGV terminal intercept (Section 2). Second, it specifies a dual-axis latency-aware tier matrix and a 7-check Gating Check Matrix that is its operational implementation, combining the Build Doc V1.4.2 auditor check sequence (6 operational checks) with an adversarial-robustness layer derived from current ML security literature, yielding a unified 7-check matrix with a cryptographic trace commit (Sections 3-4). Third, it specifies a Hub-Tier Model Swap Protocol addressing the requirement, made concrete by supply-chain risk events in February-March 2026, that the edge kill chain must survive legal or political severance of any single foundation-model provider (Section 5).

All quantitative thresholds are proposed engineering defaults. Phase GD-0 hardware characterization on target rad-tolerant FPGA or CGRA hardware must validate the 5 ms budget before operational deployment.

Since the March release, the program office has said in public what this paper argued from physics. At the Space and Missile Defense Symposium (August 11, 2026), the Golden Dome director described an operator-selectable automation setting running from none to fully automated response, and said the fight will push toward automation because it runs at machine speed, faster than human speed (Aviation Week, August 2026). That is the availability-versus-false-positive dial of Section 11. This paper specifies what sits behind the dial at the edge and what turning it costs. Section 12 records what else changed between March and August 2026.

# 2. The Physics Constraint

## 2.1 Why HITL Fails for HGV Terminal Intercept

An HGV in terminal phase travels at Mach 5 or above and executes lateral maneuvers. Track prediction degrades rapidly with time. The intercept window from initial track lock to required actuation is 5 to 15 seconds, and every system element (sensors, compute, decision, effector deployment) must complete within that window.

The question is whether any path from a LEO sensor node to a hub-tier reasoning engine and back can complete within that window reliably enough to support HITL governance. The answer depends on two independent constraints: propagation delay and ground-station availability.

**Propagation delay.** The table below shows corrected one-way and round-trip latency for each communication path, computed from speed-of-light propagation at 299,792 km/s with slant-range geometry for 5° minimum elevation angle. (The ground-station availability calculation below uses a 10° minimum elevation angle, which is the more conservative antenna-pointing constraint; the 5° figure here represents the geometric limit before loss of signal.)

| Path                                        | One-Way (ms) | Round-Trip (ms) | Notes                                                        |
| ------------------------------------------- | ------------ | --------------- | ------------------------------------------------------------ |
| LEO direct downlink (550 km, zenith)        | 1.8          | 3.7             | Best-case geometry. Ground station directly below.           |
| LEO direct downlink (550 km, 5° elev)       | 7.4          | 14.7            | Worst usable geometry before loss of signal.                 |
| ISL mesh relay (1-6 hops, 500-5,000 km/hop) | 1.7-100      | 3.4-200         | SDA PWSA mesh. Hop count depends on constellation geometry and ground-station placement. |
| GEO relay (TDRSS-class)                     | 237          | 474             | LEO to GEO (117.5 ms) + GEO to ground (119.4 ms). Legacy path. |
| Hub processing (cloud inference)            | -            | 50-2,000        | Floor assumes pre-loaded model with warm cache. Ceiling includes queuing and multi-step reasoning. |
| Human confirmation (HITL)                   | -            | 250-750         | Operator confirmation latency from human factors literature. |

**Best-case round-trip with HITL.** Direct downlink at zenith, fast hub, fast operator: 3.7 + 50 + 250 = 304 ms. This fits inside the 5-15 s HGV window. If propagation delay were the only constraint, HITL would be feasible for a fraction of engagement geometries.

**Ground-station availability.** A LEO satellite at 550 km altitude has an orbital period of 95.5 minutes. A single ground station sees the satellite for approximately 8 minutes per pass at 10° minimum elevation, yielding an 8.3% duty cycle. At any random moment, the probability that a given sensor node has direct line-of-sight to any one ground station is roughly 8%. With six globally distributed stations, generous estimates reach approximately 50% simultaneous availability, but this assumes ideal weather, no RF interference, and no adversary denial.

The engagement window opens at the adversary's choosing, not ours. A governance architecture that requires ground contact for authorization will have no ground contact available for a substantial fraction of engagement opportunities. During those gaps, the system either misses the intercept or must have pre-authorized the edge node to act independently. In either case, HITL is not available when needed.

**The combined constraint.** Neither propagation delay alone nor availability alone closes HITL in every case. Together they do. The GEO relay path adds 474 ms of irreducible propagation per round-trip, pushing total HITL latency to 774-3,224 ms. The direct downlink path has acceptable latency but is unavailable for most of the orbit. The ISL mesh path adds variable delay (up to 200 ms round-trip at 6 hops) and itself depends on link availability between nodes, which degrades under adversary jamming (the same threat environment where engagement is most likely). No single path provides both low latency and guaranteed availability during an engagement window that opens without warning.

**Fielded state of the ISL mesh (August 2026).** The ISL figures above are geometric. The mesh itself is not yet on orbit. As of mid-July 2026 SDA had not demonstrated an operating Tranche 1 optical crosslink mesh, citing development and production cadence of the optical terminals (Breaking Defense, July 2026), with first activation targeted for roughly September 2026 and Tranche 1 described as about a year behind its original schedule. Until the mesh operates, every ISL-dependent path in this paper (relay to hub, P2 time transfer in Section 4.3, local quorum in Check 6) is a design assumption, not a fielded capability. This does not weaken the HITL argument; it removes the one path that might have rescued it.

## 2.2 Restructuring Governance Around Physics

The AOM cannot change the physics. It can relocate the authorization decision to a point where latency is governed by compute, not light-speed propagation. That point is the edge node itself. The edge node receives a track update from the co-located or short-range sensor mesh within 40 ms, runs the gating checks within 5 ms, and issues the engagement command without waiting for hub acknowledgment.

The hub's role is restructured, not eliminated. It authors the Mission Intent Object (MIO) that pre-authorizes the edge node to act within a defined engagement envelope. That authorization is computed and signed in advance, before the engagement window opens. Post-engagement, the hub receives the full engagement trace and conducts accountability review. Operators work in the outer learning loop (MIO authoring and post-hoc audit) on timescales where human judgment is effective. They are structurally barred from the inner control loop where they cannot be effective and where forced intervention would degrade performance through decision-chain phase lag, the control-theory equivalent of pilot-induced oscillation.

# 3. Latency-Aware Tier Matrix

## 3.1 The Dual-Axis Extension

The original AOM matrix has one axis: cognitive budget against task value. This correctly captures the tradeoff between decision quality and computational cost. It does not capture the constraint that some decisions must be made before any hub round-trip can complete with guaranteed availability. The extended matrix adds a latency budget axis. For each engagement class, both axes determine tier assignment.

| Engagement Class        | Window    | Cognitive Budget | AOM Tier (original)     | AOM Tier-Extended (this paper)                               |
| ----------------------- | --------- | ---------------- | ----------------------- | ------------------------------------------------------------ |
| Boost-phase ICBM        | 180-300 s | Substantial      | Tier 2 / HITL preferred | Tier 2 unchanged. HITL preferred. Tier 1-E fallback if uplink degraded. |
| HGV terminal phase      | 5-15 s    | < 5 ms gate      | Tier 1 / HITL mandated  | Tier 1-E (Edge Autonomous): pre-authorized MIO envelope + 5 ms deterministic gating. HITL physically excluded. Full post-hoc audit mandatory. |
| Ballistic MaRV terminal | 10-30 s   | 5-10 ms gate     | Tier 1 / HITL mandated  | Tier 1-E. Marginally longer window permits local ISL quorum across 2-3 nearest nodes if ISL links are healthy. ISL latency budget for local quorum estimated at 3-34 ms (1-2 hops at 500-5,000 km). Phase GD-1 must validate. |
| Counter-UAS / cruise    | > 60 s    | Seconds          | Tier 2 / HITL           | Tier 2 unchanged. Original AOM matrix applies.               |

The Tier 1-E (Edge Autonomous) designation is not a weakening of governance. It is recognition that governance must match the timescale of the decision. The pre-authorized MIO envelope is the governance instrument. Dual-authorization at MIO authoring, strict UTC validity windows, and a zero-collateral geo-fence constraint make autonomous execution within the envelope accountable.

## 3.2 Governance Instruments by Tier

**Tier 2 (HITL, unchanged).** Engagement authorization requires real-time human confirmation. Cognitive load monitoring active. Full hub-tier reasoning available on the timescales this tier operates.

**Tier 1-E (Edge Autonomous).** Engagement authorization is delegated entirely to the pre-signed MIO envelope. The edge auditor checks every track against the MIO deterministically within 5 ms. No hub confirmation during execution. Full post-hoc audit mandatory for every engagement attempt, authorized or held.

**MIO Authoring (outer loop, human-paced).** Operators author MIOs at the hub on strategic timescales. Dual-authorization required. All MIOs carry strict UTC expiration timestamps. Shortened TTL (4 hours) applies during model swap periods, forcing frequent re-authorization.

**Post-hoc Accountability (hub-tier).** Every engagement attempt is logged with its full gating trace (all 7 check outputs, confidence scores, entropy seed hash, quorum result) and shipped to hub. Forced-choice UI patterns prevent automation complacency during MIO review.

# 4. The 5 ms Gating Check Matrix

## 4.1 Design Rationale

The gating matrix integrates two previously separate contributions. The operational check sequence from Build Doc V1.4.2 (Schema, MIO Hash, Envelope Match, Confidence Floor, Geo-fence, Staleness) catches misconfigured, stale, or out-of-envelope tracks through deterministic fixed-point comparisons. The adversarial-robustness layer from current ML security literature (cross-modal Mahalanobis consistency, temporal coherence filtering, chaotic-quantized Physics-Informed Neural Network) catches electronically fabricated tracks engineered to pass the operational checks. The unified 7-check matrix (this paper) merges these two layers into a single sequential pipeline with a cryptographic trace commit as the final gate.

These are not competing designs. They address different threat surfaces at different cost points within the 5 ms budget. The operational checks run first because they are cheapest and catch the largest population of rejected tracks. The adversarial checks run against the smaller population that passes operational validation, where the marginal compute cost of the PINN inference is justified by the threat class.

Check 3 has two sub-checks that test different properties. Check 3a (kinematic bounds) verifies that trajectory angle, velocity, and apogee fall within the pre-authorized engagement envelope using fixed-point lookup. Check 3b (cross-modal consistency) computes the Mahalanobis distance between IR bloom onset and optical RCS return against calibration covariance. Both must pass for Check 3 to pass. The simulation suite (Section 6) tests these sub-checks independently to characterize which attacks each one catches.

*All timing windows below are notional targets from non-rad-hardened analogues. Phase GD-0 must validate on target hardware.*

| Window (notional) | Check                                         | Method                                                       | Pass -> Action                           | Fail -> Action                                               |
| ----------------- | --------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------------ |
| 0.0-0.2 ms        | 1. Schema Validation                          | Verify IntentCapsule structure against canonical schema. Fixed-point arithmetic only. Zero floating-point operations. | Proceed to Check 2                       | HALT. Log SCHEMA_FAIL to async sidecar.                      |
| 0.2-0.5 ms        | 2. MIO Hash Integrity                         | Compare mission_context hash against active pre-loaded MIO. Cryptographic check in hardware. | Proceed to Check 3                       | HALT. MIO expired or chain broken. Escalate via async trace. |
| 0.5-0.9 ms        | 3. Physics Envelope + Cross-Modal Consistency | (3a) Fixed-point lookup against pre-authorized EngagementEnvelope (trajectory angle, velocity, apogee). (3b) Cross-modal Mahalanobis distance between IR bloom onset and optical RCS return checked against calibration covariance in read-only flash. *CRITICAL:* Strict feature normalization to controlled variance must be applied before the Mahalanobis computation. | Proceed to Check 4                       | HOLD. Physics violation or cross-modal inconsistency. Increment spoof counter. Escalate to async BFT. |
| 0.9-1.4 ms        | 4. Temporal Coherence + Staleness TTL         | Sliding-window median filter on last N track updates. Genuine targets show progressive refinement; injected tracks show discontinuous appearance ('pop-in' signature). Reject if track_age > staleness_ttl_ms (default: 500 ms). **Clock-trust dependency:** staleness gate assumes authenticated timestamps. See Section 4.3. | Proceed to Check 5                       | HOLD. Anomalous initialization or stale data. Log TEMPORAL_FAIL. |
| 1.4-2.8 ms        | 5. Confidence Floor + Chaotic-Quantized PINN  | Confidence floor (>= 0.95) is a single fixed-point comparison completing in nanoseconds. The remainder of the 1.4 ms budget is allocated to the chaotic-quantized Physics-Informed NN, seeded by satellite radiation-event counter (a physically uncloneable entropy source). PINN outputs a physics residual score; elevated residual signals a physically compliant but adversarially synthesized track. | Proceed to Check 6                       | HOLD. Confidence below floor or elevated physics residual. Log entropy seed hash for post-hoc forensics. |
| 2.8-3.3 ms        | 6. Geo-fence + Local ISL Quorum               | Verify target coordinates within zero-collateral or pre-authorized engagement zones. Approximate BFT vote with N nearest orbital neighbors over sub-ms optical ISL. Requires >= 2/3 local majority. Degraded-mode fallback to single-node authorization if ISL jammed, logs DEGRADED_QUORUM. | AUTHORIZE engagement. Proceed to Commit. | HOLD. Geo-fence violation or quorum failed. Defer. Escalate to full PBFT mesh vote. |
| 3.3-5.0 ms        | 7. Cryptographic Trace Commit                 | Write all check outputs, confidence scores, entropy seed hash, and quorum result to tamper-evident append-only log before actuation. This record is the kill chain audit trail shipped to hub post-engagement. | Proceed to actuation.                    | Blocking commit failure -> abort engagement. Alert hub.      |

## 4.2 Adversarial Notes

**Physics-compliant spoofing.** Checks 3 and 5 together catch tracks that violate physical law or show cross-modal inconsistency. A nation-state adversary with sensor calibration data and orbital ephemeris can synthesize inputs that satisfy both checks simultaneously. The checks raise attack cost and complexity. They do not eliminate the threat. That is the design boundary.

Falsification testing (Section 6, Scenario C) confirms this boundary quantitatively. Adversarial tracks that maintain Mach 5-15 speed and sub-10g lateral acceleration pass the kinematic bounds sub-check (Check 3a) at all tested discontinuity magnitudes. The cross-modal Mahalanobis sub-check (Check 3b), tested using kinematic-feature proxies, also passes the adversarial track at the default pop-in offset: the adversary's aggregate kinematic statistics remain close enough to the genuine track's calibration distribution that the Mahalanobis distance stays below threshold. This means that for cold-start injection attacks, Check 3b does not provide independent detection. Detection of the pop-in falls to the temporal coherence filter (Check 4), which detects injection when the spatial discontinuity exceeds approximately 80 meters. Below that threshold, detection rates drop below 50%, creating an adversarial sweet spot where both Check 3 sub-checks pass and coherence checks are unreliable. The 80 m detection threshold is an arbitrary engineering default chosen as a round-number starting point. Phase GD-0 must characterize the operationally correct threshold against representative sensor noise profiles on target hardware.

**Quantization security paradox.** Standard INT8 quantization reduces backdoor defense detection to near zero while attack success stays above 99% on the classification tasks studied in Pandey and Ye (arXiv:2512.06243). Check 5 uses chaotic Lorenz-noise quantization seeded by a hardware entropy source (satellite radiation-event counter) that is physically uncloneable from the ground in the production architecture. The simulation uses a deterministic Lorenz tape as a placeholder; the hardware entropy interface is a Phase GD-0 deliverable. The adversary cannot predict the quantization noise pattern without physical access to the satellite. This moves the attack surface from the mathematical to the physical domain.

Falsification testing (Scenario B) shows that at nominal configuration (INT8 threshold equal to FP32 threshold), a zero-knowledge adversary achieves approximately 0.06% bypass rate with features normalized to O(1) variance. This figure is misleadingly low. The test uses unit-scale features. Real orbital sensor data (range in meters, velocity in m/s, IR intensity in W/sr) spans 3-4 orders of magnitude in dynamic range. The quantization gap between INT8 and FP32 scales with the ratio of feature dynamic range to quantization resolution. Without strict feature normalization to a controlled variance before the Mahalanobis computation, the effective bypass rate will be substantially higher. **Feature normalization discipline is a hard requirement for Check 3 and must be specified in the edge auditor calibration procedure.** This is added to Section 8 Limitations.

**FLP impossibility and ISL jamming.** Check 6's local quorum is defeated if the adversary jams inter-satellite optical links. The degraded-mode fallback to single-node authorization accepts elevated false-positive risk in exchange for maintained engagement capability. This trade-off is not solvable by algorithm. It is a mission doctrine dial that must be set by appropriate authorities, not by the system architect.

## 4.3 Clock-Trust Dependency

The staleness gate in Check 4 rejects tracks older than staleness_ttl_ms (default 500 ms). This check is only as strong as the trust chain on the timestamp.

Falsification testing (Scenario A) demonstrates this directly. An adversary who can manipulate the timestamp field by any amount Δt ≤ -500 ms achieves 100% bypass of the staleness check. This is a step function, not a probability. The attack surface includes compromised ground relay injection, GPS spoofing on the track timestamp, and replay of previously valid track capsules with shifted timestamps.

The timestamp used by Check 4 must come from an authenticated clock source. Candidates include:

**GPS-disciplined oscillator with authenticated timing (GPS III military signals).** Provides sub-microsecond accuracy with spoofing resistance from the M-code signal. Vulnerable to GPS denial in contested space environments.

**Inter-satellite time transfer via optical ISL.** Constellation-internal time synchronization independent of ground-based GPS. Accuracy depends on ISL link quality and is degraded under the same jamming conditions that affect Check 6. Creates a circular dependency: the clock that validates Check 4 relies on the same ISL links whose availability Check 6 assesses.

**Onboard atomic clock (free-running, periodic sync).** Provides holdover timing during GPS denial. Drift accumulates. A rubidium oscillator drifts approximately 1 μs per day, which is negligible for the 500 ms staleness TTL. A crystal oscillator drifts orders of magnitude faster and is not suitable.

The architecture should layer these sources: GPS-disciplined primary, ISL-synced secondary, atomic holdover tertiary. The specific implementation is a Phase GD-0 deliverable. Figure F (clock_trust_fpga_dark, supplementary) shows the reference implementation: a logic-locked FPGA secure partition (Region A) that arbitrates P1/P2/P3, signs the selected timestamp with its source ID, and emits `t_auth` across a hardware partition boundary to Check 4 in the auditor region (Region B). The payload `track_timestamp` field is not routed into Region A and is structurally inaccessible to the auditor. Build Doc v1.4.2 Section 5 gives the block-level specification. The critical design requirement is that **the staleness TTL must be evaluated against a timestamp whose provenance is cryptographically bound to an authenticated clock source, not simply read from the track data payload.**

## 4.4 Asynchronous Sidecar Processing

The blocking 7-check pipeline handles the engagement-critical path. Everything that cannot complete within 5 ms, or that informs post-hoc accountability rather than the current engagement decision, runs in the asynchronous sidecar. Sidecar results do not gate the current engagement but feed the post-hoc accountability system and the hub-tier threat picture. Deferred check results are logged with reason code LATENCY_CRITICAL.

| Process                     | Trigger                        | Purpose                                                      |
| --------------------------- | ------------------------------ | ------------------------------------------------------------ |
| Full PBFT Mesh Vote         | Any HOLD from Tier 1           | BFT consensus across full constellation. Result informs post-hoc review, not current engagement. |
| Cosine Drift Scoring        | Every engagement attempt       | Measures semantic drift between current Hub-Tier LLM outputs and MIO certification baseline. Flags model reasoning degradation before it reaches engagement logic. |
| Spoof Campaign Detection    | Rolling 60-second window       | Anomaly detection on rate and geographic distribution of HOLD flags. Coordinated injections targeting multiple nodes produce a detectable cluster signature. Escalates mesh to BFT-mandatory mode. |
| Forensic Log Reconciliation | After engagement window closes | Reconciles authorization records across nodes using cryptographic hash chain. Identifies nodes whose logged outputs are inconsistent with engagement outcome. Flags compromised nodes for decommissioning. |
| Calibration Audit           | Weekly or post-model-swap      | Calibration tables bound to the task, not the model. After any hub model change, replacement must demonstrate calibration equivalence on canonical task dataset before its MIOs enter the live pipeline. |

## 4.5 Multi-Node Engagement Deconfliction

The Tier 1-E architecture places autonomous engagement authority on each edge node independently. When multiple sensor nodes track the same target, independent authorization creates two operational risks: redundant engagement (multiple interceptors fired at the same target, wasting limited effector inventory) and fratricide (one node's effector enters another node's engagement zone).

The ISL quorum mechanism in Check 6 partially addresses this. Nodes that can communicate via optical ISL share track IDs and can coordinate effector assignment through the approximate BFT vote. Under normal ISL conditions, this provides deconfliction within the local quorum group.

Under ISL-denied conditions (DEGRADED_QUORUM), deconfliction fails. Each node operating on single-node authority may independently authorize against the same track. The MIO envelope should include an effector allocation constraint (maximum interceptors per track ID per orbital sector) to bound the cost of redundant engagement. This constraint is deterministic and can be evaluated locally without ISL communication, at the cost of potentially leaving a track unengaged if the allocated node fails.

Full deconfliction under ISL denial is another instance of the FLP impossibility constraint. It cannot be solved without communication between nodes. The mission doctrine must accept either redundant engagement or missed intercept as the residual. Note that until the SDA optical mesh is operating (Section 2.1), the ISL-denied case is not a degraded mode but the baseline: early Tier 1-E prototypes will run with DEGRADED_QUORUM as the normal state and must be evaluated on that basis.

# 5. Hub-Tier Model Swap Protocol

## 5.1 Architectural Requirement

Any foundation model provider at the hub tier is subject to political severance on timelines of hours to days, far shorter than system re-architecture permits. Any hub-tier component that can be severed politically must have a pre-planned swap protocol that does not interrupt edge-node engagement capability. This is a structural requirement independent of any specific provider or dispute.

The February-March 2026 Anthropic designation illustrates the operational reality. The dispute has run for six months without a final ruling, which is itself the point: a hub-tier provider can sit in legal limbo for longer than a swap protocol takes to execute.

*Status as of August 16, 2026.* On February 27, 2026, the Department of War designated Anthropic PBC a supply-chain risk under 10 U.S.C. § 3252 and 41 U.S.C. § 4713 (FASCSA), following Anthropic's refusal to remove two usage restrictions from its models: mass domestic surveillance and fully autonomous weapons without human oversight. A presidential directive of the same date ordered federal agencies to cease use of Anthropic technology with a six-month phase-out. On March 26, 2026, Judge Rita F. Lin (N.D. Cal.) issued a preliminary injunction against the § 3252 designation and the directive. On April 8, 2026, the D.C. Circuit denied Anthropic's emergency stay of the § 4713 designation but ordered expedited review; oral argument was heard May 19, 2026, the case was consolidated with a second petition in June, and supplemental briefing closed August 3, 2026. No merits opinion has issued. The § 3252 designation is enjoined; the FASCSA designation stands. The six-month phase-out clock runs out at the end of August 2026. Any reader after that date should check the D.C. Circuit docket (No. 26-1049) before citing this paragraph.

The architectural solution has two parts. First, the Model-Abstraction Layer enforces a canonical MIO output schema decoupled from any specific model provider. The edge auditor parser reads the schema, not the model; replacing the model does not break the parser. Second, the swap follows a phased shadow-mode recertification sequence that keeps edge nodes on valid pre-signed MIOs throughout, using a shortened TTL as a dead-man's switch forcing frequent human re-authorization while the replacement is evaluated.

The key known fact about model substitution is that different foundation models exhibit different logit spreads. Confidence scores are not natively transferable between models. A replacement model that produces numerically similar outputs on general benchmarks may produce systematically different confidence distributions on the specific target classification task. The edge auditor's confidence floor check (Check 5) will silently reject a disproportionate fraction of MIOs from a replacement model whose distribution has shifted, without any explicit error. The calibration equivalence gate exists to catch this before it affects operations.

## 5.2 Swap Runbook

| Step | Action                                                       | Acceptance Gate                                              | Fail Behavior                                                |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 1    | Isolate ejected model: disable outbound API route to MIO signing module immediately. | Zero MIO traffic from ejected model.                         | N/A. Immediate and irreversible.                             |
| 2    | Shorten MIO TTL to 4 hours globally. Forces human re-authorization at high frequency during transition. Acts as dead-man's switch. | lattice-cli confirms TTL constraint applied.                 | Halt and investigate configuration layer.                    |
| 3    | Initialize replacement model in shadow mode, routing outputs to metrics_only. | Shadow deployment healthy. Zero traffic to MIO generator.    | Roll back shadow deployment. Remain in degraded-manual mode. |
| 4    | Run canonical task dataset through shadow model. Measure confidence distribution. | Rolling mean within 2σ of ejected model's certification baseline. | Model rejected. Escalate to Certifying Authority. Procure alternate model. Restart at Step 3. |
| 4b   | Repeat Step 4 with the replacement model in its deployed quantized form (INT8 or lower), not FP32. Compare quantized and FP32 outputs on the canonical dataset. | Quantized-vs-FP32 output divergence within the ejected model's certified bound. No output class appears only after quantization. | Model rejected. A backdoor conditioned on quantization rounding is assumed until shown otherwise. Restart at Step 3. |
| 5    | Drift recertification: validate sentence-transformer embeddings separate known-drifted vs. compliant capsules. | Separation accuracy > 95%. Certifying Authority approves any deviation. Vendor override prohibited. | Reject replacement model. Hub remains in degraded-manual mode. Procure alternate. |
| 6    | Phased reintroduction: route replacement model to Tier 0 advisory dashboards. Monitor 72 hours. | auditor.rejection_rate stable at baseline. No false-positive spike. | Revert to shadow mode. Investigate output formatting.        |
| 7    | Full restore: re-enable MIO write access. Return TTL windows to operational defaults. | Edge nodes accept new MIOs without rejection rate increase.  | Halt restore. Hub remains in extended degraded mode.         |

Step 4b exists because a class of backdoor now documented for LLMs fires only after quantization: the model behaves cleanly in FP32 and turns malicious once its weights are rounded to INT8 or FP4 (see the quantization-conditioned backdoor row in Section 10). A replacement model certified in FP32 can therefore pass Steps 4 and 5 and still be compromised in the form that actually runs. Certification must happen in the deployed precision.

If the replacement model fails the calibration equivalence gate at Step 4 or 4b, the system halts the swap. The hub tier remains in degraded mode on 4-hour human-authorized MIO envelopes. The organization must procure a different replacement model and restart from Step 3. Tolerance deviations from the 2σ gate must be accepted by a human Certifying Authority. Vendor override of the gate is prohibited.

## 5.3 Post-Restore Validation

After full restore, monitor comms.trace_ship_lag_ms to confirm the replacement model's output formatting does not create serialization bloat in the sidecar trace logs. A replacement model with a different output schema can silently degrade sidecar completeness (reducing forensic log completeness below the 99.9% target) without affecting the deterministic gating pipeline. The two failure modes are independent.

# 6. Falsification Results

This section summarizes findings from the simulation suite (simulate.py, included in the repository archive). The suite tests three attack scenarios against the 7-check gating matrix and produces both an analytical per-check sensitivity analysis and a 7-check Monte Carlo sensitivity analysis of combined detection probability across adversary sophistication levels. The analytical and Monte Carlo models use the same per-check parametric detection functions (defined once in `per_check_detection_models()`) so their results are consistent by construction.

## 6.1 Scenario A: Ghost-in-the-Matrix (Stale-State Injection)

The adversary manipulates track timestamps to make stale data appear fresh, bypassing Check 4's staleness gate.

**Finding:** The staleness check is a binary gate on timestamp authenticity. At clock offset Δt ≤ -500 ms, bypass is 100%. This is not a probabilistic degradation; it is complete circumvention. The defense requires authenticated timestamps, not a tighter TTL. See Section 4.3. The staleness bypass is a step function, not a gradient: Figure A (left panel) shows the binary cliff at Δt = −500 ms. The right panel shows the auditor latency distribution; P99.9 = 4.82 ms stays inside the 5 ms budget under the modeled SEU jitter.

**Latency validation:** Auditor latency under a log-normal SEU jitter model shows P99 = 4.61 ms and P99.9 = 4.82 ms. Both fall inside the 5 ms budget. The latency architecture holds under the modeled radiation environment.

## 6.2 Scenario B: Quantization-Aware Spoofing (INT8 vs. FP32)

The adversary exploits the precision gap between FP32 Mahalanobis distance (used in design validation) and INT8 Mahalanobis distance (used in deployed edge hardware) to craft inputs that pass the quantized check while failing the full-precision check.

**Finding:** At nominal configuration with unit-scale features, zero-knowledge adversarial success rate is approximately 0.06%. This figure is an artifact of favorable feature scaling. The adversarial success rate climbs monotonically as the INT8 threshold loosens relative to FP32, and scales with feature dynamic range. With raw sensor features spanning 3-4 orders of magnitude, the effective gap widens proportionally. The chaotic Lorenz quantization defense is sound in principle but depends on feature normalization to a controlled variance before the Mahalanobis computation. This normalization requirement is not optional. Figure B shows the adversarial cluster in FP32/INT8 score space (left), the quantization precision-loss distribution (center), and the monotonic climb in adversarial success rate as the INT8 threshold loosens relative to FP32 (right).

## 6.3 Scenario C: Lethal Compliance (Physics-Valid, Temporally Incoherent)

The adversary injects a track that is physically valid at every point where it exists (Mach 5-15, sub-10g G-load) but appears abruptly with no prior track history ('cold start' injection).

**Finding:** The simulation tests the two sub-checks of Check 3 independently against the adversarial track. The kinematic bounds sub-check (Check 3a) passes at all tested discontinuity magnitudes, as designed: the adversary's track stays within speed and G-load limits. The cross-modal Mahalanobis sub-check (Check 3b), using kinematic-feature proxies, also passes the adversarial track at the default 50 m pop-in offset (FP32 score = 0.7, threshold = 3.9). This is because the adversarial track's aggregate kinematic statistics (mean speed, mean acceleration, etc.) remain close to the genuine track's calibration distribution even though the track appeared abruptly. The cross-modal check catches tracks whose overall kinematic profile is anomalous, not tracks whose only anomaly is a discontinuous appearance. That detection falls to Check 4. The temporal coherence filter (Check 4) correctly detects the pop-in when the spatial discontinuity exceeds approximately 80 m.

Below ~80 m, the coherence detection rate and the kinematic-bounds pass rate cross over: kinematic bounds continue to pass while coherence detection drops below 50%. This cross-over point is distinct from the 80 m per-track median-filter threshold. The cross-over measures the population-level rate at which coherence detection fails to catch small-jump adversarial tracks, while the 80 m threshold is the per-track residual cutoff in the sliding-window median filter. Phase GD-0 must characterize both values against representative sensor noise profiles on target hardware. Figure C shows the trajectory divergence, the coherence residual spike at pop-in, the speed and G-load profiles confirming kinematic compliance, and the check-coverage sweep across pop-in magnitudes.

## 6.4 Sensitivity: Combined Detection vs. Adversary Sophistication

The 7-check matrix was evaluated using Monte Carlo simulation (simulate.py, Bilar 2026, DOI: 10.5281/zenodo.19368609). 50,000 trials per sophistication level, 20 levels from s=0.0 to s=1.0, seed = 42. At each level, the adversary's capability to evade each of the 7 checks is modeled as a Bernoulli draw with probability set by the canonical per-check parametric models (defined in `per_check_detection_models()`). These models cover schema-crafting ability, physics compliance, temporal smoothing, INT8 exploitation, PINN evasion, zone knowledge, and clock manipulation. A track is detected if any of the 7 checks fires.

The per-check detection probabilities are parametric assumptions informed by the Scenario A-C simulation results and by ML security literature but not independently validated at each sophistication level. The combined detection rate is computed from 50,000 independent trials per point. The analytical per-check curves (plot D) and Monte Carlo combined rates (plot E) use the same per-check functions, so discrepancies between D and E reflect only Monte Carlo sampling variance. The reported figures capture sampling noise but not model uncertainty; they should be read as approximate, not precise.

**Finding (7-check combined detection):**

*Estimates from parametric per-check models (50,000 Monte Carlo trials per level). Model uncertainty is not quantified; these are not measured failure rates.*

| Sophistication                           | Combined Detection (%) |
| ---------------------------------------- | ---------------------- |
| 0.00 (random)                            | ~100                   |
| 0.26 (opportunistic)                     | ~100                   |
| 0.53 (semi-capable)                      | ~99.9                  |
| 0.74 (nation-state)                      | ~99                    |
| 1.00 (nation-state + calibration access) | ~89                    |

Combined detection exceeds 99% for adversaries below sophistication 0.75. At nation-state sophistication (s=0.74), combined detection is approximately 99%. At maximum sophistication (s=1.0, nation-state with calibration data access), combined detection drops to approximately 89%. These figures reflect parametric assumptions, not measured rates; the sophistication scalar is a modeling convenience, not an operational threat taxonomy (see caveat below). Figure D shows per-check detection probability across the full sophistication range; the PINN flat line at ~72% is the floor the hardware entropy source provides against a zero-knowledge adversary. Figure E (left panel) shows the full 7-check Monte Carlo curve.

**PINN degradation scenario.** The PINN's detection contribution depends on the hardware entropy source (satellite radiation-event counter) being physically secure. If an adversary gains co-orbital access or builds a sufficiently accurate radiation-environment model to predict the Lorenz seed, the PINN's detection floor collapses. The simulation includes a named PINN-zeroed scenario (p_pinn forced to 0 in the Monte Carlo) that computes the degraded combined detection rate directly. With the PINN zeroed out, the remaining 6-check model yields combined detection at s=1.0 of approximately 62%, down from ~89% with the full 7-check model. At s=0.74 (nation-state), 6-check detection is approximately 96% versus ~99% with all 7 checks. The gap widens sharply at high sophistication: the PINN contributes little at low s (where other checks already catch nearly everything) but accounts for an approximately 27 percentage-point difference at s=1.0. If the PINN assumption fails in the orbital domain, the system retains majority detection capability but loses the margin that separates operationally adequate from operationally marginal against the most capable adversaries. Figure E (right panel) shows the gap directly: the blue and red curves track together until s ≈ 0.6, then diverge sharply to the ~89% vs. ~62% endpoints at s = 1.0.

**Caveat on per-check models and the sophistication scalar.** The individual check detection probabilities at each sophistication level are parametric assumptions (e.g., "P(physics check detects) = 1 - 0.92s"), not measured failure rates. Their functional forms are informed by the Scenario A-C simulation results and by the ML security literature, but they are not empirically validated at each point. The combined rate is the product of these assumptions processed through Monte Carlo sampling. The headline numbers are only as reliable as the per-check models they rest on. Phase GD-0 must replace the parametric per-check models with measured hardware failure rates.

**The sophistication scalar s is a modeling convenience, not an operational threat taxonomy.** It compresses real adversary capabilities (RF spoofing, calibration data exfiltration, co-orbital presence, supply-chain infiltration) into a single dimension. The labels "nation-state" and "nation-state + calibration access" are illustrative, not definitional. Phase GD-0 should map discrete adversary capability classes to specific per-check bypass assumptions, replacing the scalar with a threat matrix grounded in operational intelligence.

# 7. Implementation Roadmap

The program now has a public calendar to anchor these phases. The space-based interceptor competition closed its first of four development gates in August 2026, with ground tests planned before end of 2026, orbital flight demonstrations in 2027, an initial on-orbit capability target of 2028, and intercept demonstrations not before mid-2029 (Breaking Defense and Bloomberg, August 2026). Phase GD-0 should close before Gate 2; GD-1 before the 2027 flight demonstrations; GD-3 before any intercept demonstration. Funding for the program is not assured; the director has said publicly that without the requested reconciliation funding there is no Golden Dome. The governance work is cheap relative to the hardware and should not wait on the appropriation.

## Phase GD-0: Hardware Characterization

Profile all 7 gating checks on target rad-tolerant FPGA or CGRA hardware. The 5 ms budget is an engineering estimate from non-rad-hardened analogues. Radiation-induced single-event upsets affect timing. If the full 7-check sequence cannot complete within 5 ms, degrade to Schema, MIO Hash, Physics Envelope, and Geo-fence. Generate chaotic quantization calibration curves specific to the hardware entropy source. Validate that the cross-modal Mahalanobis covariance matrices produce expected false-alarm rates against injected spoof tracks. **Characterize the temporal coherence detection threshold (currently 80 m arbitrary default) against representative sensor noise profiles on target hardware.** Specify and validate the feature normalization procedure for Check 3 Mahalanobis computation. Validate clock-trust architecture (Section 4.3) on target hardware. **Validate the per-check parametric assumptions used in the Section 6.4 Monte Carlo model against measured check failure rates.**

## Phase GD-1: Prototype Validation

Run synthetic track injection tests against the full pipeline. Measure auditor.latency_ms distributions across the threat class space. Test degraded-mode ISL-jammed scenarios for DEGRADED_QUORUM logging behavior. Validate local ISL quorum latency for MaRV engagement class (estimated 3-34 ms; must fit within 10-30 s window with margin).

## Phase GD-2: Model Swap Simulation

Execute a simulated forced model swap in shadow mode. Eject the primary model, run the recertification sequence with a known-compliant replacement, and validate that edge nodes maintain engagement capability throughout at 4-hour MIO TTL. Target: recertification completes within 4 weeks. Deliberately test a non-compliant replacement model to confirm rejection at Step 4 of the runbook.

## Phase GD-3: End-to-End Simulation

Validate sidecar trace completeness above 99.9% against synthetic engagement traffic. Confirm post-hoc forensic log reconciliation correctly identifies injected inconsistencies in a simulated compromised-node scenario.

## Observability

- auditor.latency_ms: Alert > 4.0 ms, halt > 5.0 ms.
- capsule.rejection_rate: Anomaly indicator for spoofing campaigns or model confidence distribution shift.
- comms.trace_ship_lag_ms: Serialization bloat indicator post-model-swap.
- edge.quorum_degraded_events: ISL jamming frequency tracker.
- hub.mio_reauth_rate: Elevated during swap periods; normalized post-restore.

# 8. Risk Assessment

| Risk                                                         | Level    | Mitigations                                                  | Residual                                                     |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Physics-compliant spoof synthesis                            | Critical | Cross-modal Mahalanobis check (IR + optical). Chaotic-quantized PINN with hardware entropy seed. Temporal coherence filter rejects pop-in tracks above ~80 m discontinuity. | Adversary with sensor calibration access can synthesize inputs satisfying all checks. Sweet spot below ~80 m coherence threshold is quantified but not eliminated. Not fully eliminable. |
| MIO envelope incorrectness (friendly-fire / civilian casualty) | Critical | Dual-authorization at MIO authoring. Zero-collateral geo-fence hard constraint. Strict UTC validity windows. Cryptographic trace commit provides post-hoc forensic record. | Errors in MIO authoring propagate through all hardware checks undetected because the gating matrix has no ground truth independent of the MIO. Phase GD-0 validation mandatory before deployment. |
| Combined GPS denial + ISL jamming degrades Checks 4 and 6 simultaneously | High     | Layered clock-trust architecture provides holdover timing (Check 4). Degraded-mode single-node authorization maintains engagement capability (Check 6). Both degradation events logged. | Under sustained combined denial, the staleness check loses protection beyond atomic holdover accuracy, and multi-node deconfliction fails. Two of seven checks become ineffective at the same time, in exactly the threat environment where attack is most likely. Redundant engagement and stale-track acceptance become concurrent risks. This is not solvable by algorithm; it is a mission doctrine decision. |
| Clock-source compromise bypasses staleness check             | High     | Layered clock-trust architecture: GPS-disciplined primary (M-code authenticated), ISL-synced secondary, atomic holdover tertiary. Cryptographic binding of timestamp provenance. | Under combined GPS denial and ISL jamming, holdover clock is the sole time source. Adversary with sustained jamming capability can exceed holdover accuracy bounds over extended engagement sequences. |
| ISL jamming severs local quorum                              | High     | Degraded-mode fallback to single-node authorization with elevated false-positive risk, logged as DEGRADED_QUORUM. | FLP impossibility is the acknowledged constraint. Multi-node deconfliction also fails, creating redundant engagement risk. Mission doctrine sets the availability-vs-false-positive dial. |
| INT8 quantization collapses backdoor defenses                | High     | Chaotic (Lorenz-noise) quantization seeded by hardware entropy source. Security evaluated in deployed quantized form, not FP32. | Defense effectiveness depends on strict feature normalization to controlled variance before Mahalanobis computation. Without normalization discipline, quantization gap scales with sensor feature dynamic range (3-4 orders of magnitude). |
| PINN entropy source compromise                               | High     | Satellite radiation-event counter is physically isolated in orbit. Lorenz seed is not transmitted. | If adversary achieves co-orbital access or builds a sufficiently accurate radiation-environment model, the PINN detection floor collapses. Monte Carlo simulation (Section 6.4, PINN-zeroed scenario) shows combined detection at s=1.0 drops from ~89% to ~62%. The PINN accounts for an approximately 27 percentage-point gap at maximum sophistication. |
| AI provider supply-chain severance                           | High     | Model-Abstraction Layer enforces canonical MIO schema decoupled from provider. Shadow-mode recertification protocol (Section 5) maintains edge continuity. Shortened TTL dead-man's switch. | Re-integration minimum 4 weeks. Hub advisory capability degraded. Operator workload sharply elevated during gap. |
| Replacement model fails calibration gate                     | High     | 2σ confidence gate blocks deployment. Drift separation must exceed 95%. Certifying Authority must approve any deviation. | Hub remains in degraded-manual mode until a compliant model is certified. |
| Foundation model reasoning drift                             | Medium   | Deferred to async sidecar. Cosine drift scoring monitors MIO output quality continuously. Deterministic Tier 1 pipeline insulated from model drift. | Sidecar forensics quality degrades if model not periodically re-validated. |

The two Critical-level risks share a common structure: they cannot be detected by the gating checks because the gating checks assume valid inputs and a correct MIO. Physics-compliant spoofing satisfies all physics checks by construction. MIO errors propagate through hardware undetected because the hardware has no ground truth. Both require governance responses upstream of the technical architecture: sensor diversity, independent track validation, and rigorous MIO authoring procedures. The gating matrix is not a substitute for those.

# 9. Limitations

This is a position paper, not a validated system specification. All thresholds (the 5 ms compute budget, the 0.95 confidence floor, the 2σ calibration gate, the 95% drift separation requirement, the 80 m temporal coherence detection threshold) are proposed engineering defaults requiring Phase GD-0 characterization before any operational use.

The PINN approach assumes a physics model adequate to distinguish genuine engagement signatures from adversarially synthesized ones can be specified, trained, and maintained under operational conditions. This has not been validated in the orbital domain. Chaotic quantization defense has been demonstrated on classification benchmarks; its behavior on sensor time-series data in a rad-hardened environment is not established. Monte Carlo simulation (Section 6.4, PINN-zeroed scenario) directly computes the degraded combined detection rate with the PINN contribution removed. At maximum adversary sophistication, combined detection drops from ~89% to ~62%. The PINN is the single largest per-check contributor at high sophistication, but the remaining 6 checks still provide majority detection. If the hardware entropy source (radiation-event counter) is predictable from the ground, by co-orbital measurement, or by radiation-environment modeling, the PINN assumption fails and the system operates at the 6-check baseline.

The INT8 Mahalanobis check (Check 3b, cross-modal consistency) requires strict feature normalization to controlled variance before computation. Without this normalization, the quantization gap between INT8 and FP32 scales with the dynamic range of raw sensor features, which can span 3-4 orders of magnitude. The simulation uses unit-scale features and therefore understates the operational quantization gap. Feature normalization discipline must be specified as part of the edge auditor calibration procedure and validated in Phase GD-0.

The Scenario C simulation tests Check 3's kinematic bounds (Check 3a) and cross-modal Mahalanobis (Check 3b) independently, using kinematic feature vectors derived from the track's own position and velocity data. Both sub-checks pass the adversarial track: the kinematic bounds pass because the adversary stays within Mach 5-15 and sub-10g, and the cross-modal check passes because the adversary's aggregate kinematic statistics remain close to the genuine track's calibration distribution despite the discontinuous appearance. In deployment, the cross-modal check compares IR bloom onset against optical RCS return, which are physically distinct sensor modalities. The simulation's kinematic-feature proxy does not capture the full dimensionality of this cross-modal comparison. A true IR/optical cross-modal check may detect adversarial tracks that the kinematic proxy misses, or may exhibit different failure modes. Phase GD-0 must validate Check 3b using multi-sensor data from representative engagement scenarios.

The staleness check (Check 4) is a binary gate on timestamp trust, not a probabilistic filter. Its effectiveness depends entirely on the clock-trust architecture described in Section 4.3. Under combined GPS denial and ISL jamming, the staleness check provides no protection against replay or stale-injection attacks beyond the holdover accuracy of the onboard atomic clock. This degradation is correlated with Check 6 (ISL quorum) degradation, since both depend on ISL link availability. See the combined GPS/ISL denial risk in Section 8.

The sensitivity analysis (Section 6.4) uses Monte Carlo sampling over parametric per-check detection models. The per-check functional forms (e.g., physics detection probability = 1 - 0.92s) are informed by the Scenario A-C results and by ML security literature but are not independently validated. The combined detection figures are empirical products of these modeled inputs. Phase GD-0 must replace the parametric per-check models with measured hardware failure rates. The analytical per-check curves (plot D) and the Monte Carlo combined rates (plot E) use the same per-check model functions (`per_check_detection_models()`), so their combined results agree within Monte Carlo sampling noise.

The model swap protocol assumes a calibration-equivalent replacement model can be procured within the operational gap period. Organizations must maintain pre-qualified backup models and must not reach a state where only one provider can satisfy the calibration gate.

The latency table in Section 2.1 uses speed-of-light propagation in vacuum. Atmospheric absorption, link-layer framing overhead, ISL acquisition and pointing delays (SDA standard requires < 100 s for initial acquisition, with a stretch goal of < 10 s), and ground-station weather degradation add variable latency not captured in the propagation-only figures. These additional delays strengthen the argument against HITL reliability but should be quantified in Phase GD-0.

Nothing in this paper constitutes legal, doctrinal, or weapons-employment authority. Questions of Rules of Engagement, international humanitarian law, and autonomous weapons governance are outside scope and must be resolved by appropriate authorities before any implementation proceeds.

# 10. Evidence Table

| Claim                                                        | Source                                                       | Confidence                                                   | Domain Gap                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Wavelet/Fourier feature extraction achieves F1 ~0.92 with 60% energy reduction | Sensors 25(21):6629 (Oct 2025)                               | High (peer-reviewed)                                         | IoT domain. Orbital hardware validation needed.              |
| FPGA/CGRA autoencoder pipeline for time-critical edge anomaly detection demonstrated | Electronics 15(2):414 (Jan 2026)                             | High (peer-reviewed)                                         | Smart grid domain. Architecture directly transferable.       |
| INT8 quantization reduces backdoor defense detection to near 0%; attack success stays > 99% | Pandey and Ye, "Quantization Blindspots: How Model Compression Breaks Backdoor Defenses," arXiv:2512.06243 (Dec 2025) | Medium (preprint, unreplicated, two authors, classification tasks only) | Classification tasks. Sensor time-series gap exists. Feature normalization dependence not characterized. |
| Patch attacks achieve > 70% success at 2-bit quantization; transfers across bitwidths | Guesmi, Ouni, and Shafique, "Breaking the Limits of Quantization-Aware Defenses: QADT-R," arXiv:2503.07058 (Mar 2025) | High (preprint, thorough experimental design)                | Physical spoofing maps to patch-class attack.                |
| Lorenz/Henon chaotic quantization improves adversarial accuracy by up to 43% | Akhtar et al., Neural Networks 171, pp. 490-503 (Jan 2024)   | Medium-High (peer-reviewed, classification benchmarks only)  | Rad-hardened deployment unvalidated.                         |
| SNN Hierarchical Temporal Defense reduces adversarial success rate on neuromorphic hardware | Patel and Liu, "Spiking Hierarchical Temporal Memory for Adversarial Robustness on Neuromorphic Hardware," NeurIPS ML4PS 2025 Workshop | Medium (workshop paper)                                      | Space-qualified rad-hardened platforms not yet validated.    |
| Byzantine-resilient satellite thrust consensus with 3-layer validation scales to 100+ nodes | ScienceDirect (Mar 2026)                                     | High (peer-reviewed)                                         | Orbital control domain. Directly applicable.                 |
| Approximate BFT outperforms exact BFT under LEO latency constraints | arXiv:2312.05213                                             | High (preprint)                                              | Supports local quorum fallback design.                       |
| FLP impossibility: consensus impossible in async system with even one faulty process | Fischer, Lynch, and Paterson, JACM 32(2):374-382 (Apr 1985)  | Definitive                                                   | Sets the availability-vs-false-positive dial requirement.    |
| LEO visibility to single ground station: ~8% duty cycle at 550 km, 10° min elevation | Computed from orbital mechanics (this paper)                 | High (first-principles geometry)                             | Does not account for atmospheric or weather degradation.     |
| SDA PWSA Tranche 1 optical ISL mesh not yet demonstrated on orbit; optical terminal production cadence cited; first activation targeted ~September 2026 | Breaking Defense, March and July 2026; SatNews, April 2026   | Current reporting                                            | All ISL-dependent paths in this paper are design assumptions until the mesh operates. Tranche 1 reported about one year behind original schedule. |
| Golden Dome director: operator-selectable automation from none to fully automated; fight will move toward automation at machine speed | Aviation Week; Defense Daily, August 11, 2026 (SMD Symposium) | Current reporting (public remarks)                           | Program-office statement of the doctrine dial this paper formalizes. Not a technical specification. |
| SBI competition passed Gate 1 of 4; ground tests 2026, flight demos 2027, initial capability 2028, intercept demos not before June 2029 | Breaking Defense; Bloomberg; InsideDefense, August 2026      | Current reporting                                            | Anchors GD-0 through GD-3 to program milestones.             |
| Quantization-conditioned backdoors in LLMs activate only after INT8/FP4/NF4 rounding; QuantGuard defense restores clean behavior across six models | arXiv:2606.29239 (June 2026)                                 | Medium (preprint, LLM code and text tasks)                   | Motivates Step 4b of the swap runbook: certify replacement hub models in deployed precision. Not yet shown on MIO-style structured output. |
| On-orbit compute identified as critical to Golden Dome latency requirements by U.S. Space Command | Air & Space Forces Magazine, March 2026                      | Current reporting                                            | Supports edge-compute architecture direction.                |

# 11. Conclusion

Golden Dome's engagement timelines do not bend to governance preferences. For HGV terminal intercept, the combination of propagation delay and ground-station availability closes HITL as a reliable governance mechanism. The correct response is not to pretend the constraint does not exist, and not to accept a missed-intercept rate from trying to insert human confirmation into a window that may have no ground link. It is to restructure governance around the timescale at which it can be effective.

The pre-authorized MIO envelope is governance at the right timescale: strategic, deliberate, dual-authorized, and time-bounded. The 7-check deterministic gating matrix is execution at the right timescale: sub-5 ms, hardware-fixed, and adversarially hardened against gradient-based attacks through a physically uncloneable entropy source. The Model-Abstraction Layer and swap protocol are supply-chain resilience at the right timescale: weeks, human-certified at each gate, with no single-provider dependency in the kill chain.

The irreducible residuals (physics-compliant spoofing below the ~80 m coherence threshold, FLP impossibility under ISL jamming, MIO envelope errors, clock-trust degradation under combined denial, PINN entropy-source compromise) are not failures of the architecture. They are statements of what a finite-compute, speed-of-light-bounded system cannot guarantee against a capable adversary. Under the parametric per-check models, Monte Carlo simulation places combined detection at approximately 99% against a nation-state adversary (s=0.74) and approximately 89% against a nation-state with calibration access (s=1.0). With the PINN assumption removed, the remaining 6-check system detects approximately 62% of maximum-sophistication attacks. These numbers reflect parametric assumptions, not measured failure rates; both the per-check models and the PINN's hardware entropy assumption must be validated in Phase GD-0.

The dial between engagement availability and false-positive risk is set by mission doctrine. The program office has now said it intends to build that dial (Section 1). The architect's job is to make it explicit, calibrated, and accountable, and to say plainly that at the far end of the dial, for HGV terminal intercept, there is no human position on it. This paper specifies what the dial looks like and what turning it costs.

# 12. Postscript: March to August 2026

This section records what changed between the v7 release (March 31, 2026) and this revision, and what did not.

**Predicted and confirmed.** The paper argued that governance must be a dial set by doctrine, with HITL excluded at the fast end. The program director now describes an operator-selectable automation range and expects operations to move toward the automated end as engagement tempo rises. The paper argued that hub-tier provider severance is a structural risk on hour-to-day timelines. The Anthropic designation is in its sixth month with no final ruling, and the phase-out period ends this month. Both arguments held.

**Assumptions that got weaker.** The ISL mesh. The paper treated optical crosslinks as available with variable latency. They are not yet operating on orbit. Every ISL-dependent element (relay, P2 time transfer, Check 6 quorum, multi-node deconfliction) should be read as a target state. Early prototypes will run in what this paper calls degraded mode as their normal condition.

**New threat surface.** Quantization-conditioned backdoors (Section 10) add a gate to the model swap runbook. The architecture is unchanged; the certification procedure gains one step.

**What did not change.** The 7-check matrix, the 5 ms budget, the clock-trust requirement, the simulation results (~89% at s=1.0, ~99% at s=0.74, ~62% PINN-zeroed), and the Phase GD-0 open items. None of the program news since March bears on them. Hardware characterization remains the gate.

**AI Use Statement**

Draft generation and review assisted by Claude (Anthropic) and Gemini (Google). The author directed all arguments, specified all architectural decisions, and takes full responsibility for the content.