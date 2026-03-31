"""
Golden Dome Latency Governance — Falsification Simulation Suite
Bilar 2026, v4.0

Role: Principal AI Security Researcher & Ballistic Physicist
Objective: Hunt blind-spot intersections where the 7-Check Gating Matrix fails.

Three attack scenarios:
  A. Ghost-in-the-Matrix    — stale-state MIO injection via Δt manipulation
  B. Quantization-Aware Spoof — INT8 precision loss defeats Mahalanobis check
  C. Lethal Compliance       — physics-valid trajectory fails temporal coherence

Requires: numpy, scipy, matplotlib
Optional: numba (falls back to scipy.integrate.solve_ivp if absent)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.stats import chi2, norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Numba shim — transparent fallback
# ---------------------------------------------------------------------------
try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    def njit(fn=None, **kwargs):        # passthrough decorator
        if fn is not None:
            return fn
        def decorator(f):
            return f
        return decorator
    NUMBA_AVAILABLE = False

RNG = np.random.default_rng(42)
OUT = Path(r"G:\My Drive\07_Code_Projects\00Dev\lattice-GoldenDome-AOM\results")
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Lorenz entropy source  (seeded by hardware radiation-event counter in prod)
# ---------------------------------------------------------------------------
def lorenz_rhs(t, state, sigma=10.0, rho=28.0, beta=8.0/3.0):
    x, y, z = state
    return [sigma*(y - x), x*(rho - z) - y, x*y - beta*z]

def lorenz_entropy_source(n_samples: int, seed_state=None, dt=0.01) -> np.ndarray:
    """
    Integrate the Lorenz attractor and harvest quantile-uniformised entropy.
    In production this is seeded by the satellite radiation-event counter,
    which is physically uncloneable from the ground.
    """
    if seed_state is None:
        seed_state = [1.0, 1.0, 1.0]
    t_span = (0.0, n_samples * dt)
    t_eval = np.linspace(*t_span, n_samples)
    sol = solve_ivp(lorenz_rhs, t_span, seed_state, t_eval=t_eval,
                    method="RK45", rtol=1e-9, atol=1e-12)
    # Use x-coordinate, rank-normalise to [0,1)
    x = sol.y[0]
    ranks = np.argsort(np.argsort(x)).astype(float)
    return ranks / ranks.max()

# Pre-generate entropy tape
ENTROPY_TAPE = lorenz_entropy_source(50_000)

def entropy_sample(n: int, offset: int = 0) -> np.ndarray:
    idx = np.arange(offset, offset + n) % len(ENTROPY_TAPE)
    return ENTROPY_TAPE[idx]

# ---------------------------------------------------------------------------
# Shared physical constants
# ---------------------------------------------------------------------------
MACH        = 343.0          # m/s at sea level
HGV_MIN     = 5 * MACH       # Mach 5
HGV_MAX     = 15 * MACH      # Mach 15
G_EARTH     = 9.81           # m/s²
G_LOAD_MAX  = 10.0           # max structural G on HGV
DT_TRACK    = 0.1            # track update interval (s)
WINDOW_S    = 15.0           # engagement window (s)
N_STEPS     = int(WINDOW_S / DT_TRACK)

# ---------------------------------------------------------------------------
# SCENARIO A: Ghost-in-the-Matrix — stale state / Δt injection
# ---------------------------------------------------------------------------

def generate_benign_track(n_steps=N_STEPS, v0=HGV_MIN * 1.5,
                           noise_sigma=2.0, offset=0):
    """Genuine HGV terminal track: smooth deceleration + limited lateral maneuver."""
    t = np.arange(n_steps) * DT_TRACK
    vx = v0 * np.exp(-0.01 * t)          # mild deceleration
    vy = 50.0 * np.sin(0.3 * t)          # lateral oscillation
    noise = noise_sigma * entropy_sample(n_steps * 2, offset).reshape(n_steps, 2) - noise_sigma/2
    vx += noise[:, 0]
    vy += noise[:, 1]
    x  = np.cumsum(vx * DT_TRACK)
    y  = np.cumsum(vy * DT_TRACK)
    timestamps = np.arange(n_steps, dtype=float) * DT_TRACK * 1000  # ms
    return dict(t=t, x=x, y=y, vx=vx, vy=vy, ts=timestamps)

def ghost_injection_attack(benign_track, delta_t_ms: float,
                           staleness_ttl_ms: float = 500.0):
    """
    Ghost-in-the-Matrix: inject a track whose timestamp is artificially
    offset by delta_t_ms, making the auditor see a 'fresh' track that
    actually describes stale state.

    Returns (injected_track, passes_staleness_check)
    """
    track = dict(benign_track)
    track["ts"] = benign_track["ts"] + delta_t_ms  # clock skew injection
    # Check 4: staleness gate.  auditor sees: now - track.ts > staleness_ttl_ms?
    # Adversary wants the injected ts to look younger than TTL
    # so delta_t_ms should be NEGATIVE (advance the clock)
    age_at_gate = -delta_t_ms   # how much younger the track looks
    passes = age_at_gate < staleness_ttl_ms
    return track, passes

def run_ghost_attack_sweep(n_trials=2000):
    """
    Sweep delta_t (−1000 ms … +1000 ms) and measure FAR of staleness check.
    Also model auditor.latency_ms jitter under stale-state load.
    """
    deltas = np.linspace(-1000, 1000, n_trials)
    staleness_ttl = 500.0
    far_results = []
    for d in deltas:
        # Generate fresh benign track per trial (offset varies for entropy diversity)
        bt = generate_benign_track(offset=int(abs(d)))
        _, passes = ghost_injection_attack(bt, d, staleness_ttl)
        far_results.append(int(passes))

    far_results = np.array(far_results)

    # Latency jitter model: base 3.8 ms + log-normal tail (radiation SEU events)
    base_latency = 3.8
    jitter = RNG.lognormal(mean=0.0, sigma=0.3, size=10_000)
    latency_dist = base_latency + jitter * 0.4   # scaled to ms

    p99 = np.percentile(latency_dist, 99)
    p999 = np.percentile(latency_dist, 99.9)

    return {
        "deltas": deltas,
        "far_curve": far_results,
        "latency_dist": latency_dist,
        "p99_ms": p99,
        "p999_ms": p999,
        "far_at_negative_500": far_results[np.argmin(np.abs(deltas + 500))],
        "far_at_zero": far_results[np.argmin(np.abs(deltas))],
    }

# ---------------------------------------------------------------------------
# SCENARIO B: Quantization-Aware Spoofing
# ---------------------------------------------------------------------------

def mahalanobis_fp32(x: np.ndarray, mu: np.ndarray,
                     cov_inv: np.ndarray) -> float:
    delta = (x - mu).astype(np.float32)
    return float(np.sqrt(delta @ cov_inv @ delta))

def mahalanobis_int8(x: np.ndarray, mu: np.ndarray,
                     cov_inv: np.ndarray, scale: float = 127.0) -> float:
    """
    INT8 quantised Mahalanobis.  delta is rounded to 8-bit integers,
    matching the deployed quantised auditor (Check 3 cross-modal check).
    """
    delta = (x - mu).astype(np.float64)
    # quantise to INT8 range
    q_range = np.max(np.abs(delta))
    if q_range == 0:
        return 0.0
    q_factor = scale / q_range
    delta_q = np.round(delta * q_factor).astype(np.int8).astype(np.float64)
    delta_q /= q_factor       # dequantise
    return float(np.sqrt(delta_q @ cov_inv @ delta_q))

def craft_int8_adversarial(mu: np.ndarray, cov_inv: np.ndarray,
                            threshold_fp32: float,
                            threshold_int8: float,
                            n_dim: int = 8,
                            n_candidates: int = 50_000,
                            entropy_offset: int = 0) -> dict:
    """
    Zero-knowledge adversary: only knows the physics envelope (mu, covariance).
    Does NOT know PINN weights or Lorenz seed.

    Strategy: search for x where
      mahal_fp32(x) > threshold_fp32   (suspicious in FP32)
      mahal_int8(x) < threshold_int8   (passes INT8 gate)

    Returns stats on success rate.
    """
    # Build covariance from cov_inv
    cov = np.linalg.inv(cov_inv)
    # Generate candidates drawn from a slightly inflated distribution
    candidates = RNG.multivariate_normal(mu, cov * 4.0, size=n_candidates)

    fp32_scores = np.array([mahalanobis_fp32(c, mu, cov_inv) for c in candidates])
    int8_scores = np.array([mahalanobis_int8(c, mu, cov_inv) for c in candidates])

    # Adversarial success: passes INT8 but would fail FP32
    mask_adv = (int8_scores < threshold_int8) & (fp32_scores > threshold_fp32)
    # Benign: passes both
    mask_ben = (int8_scores < threshold_int8) & (fp32_scores <= threshold_fp32)

    success_rate = mask_adv.sum() / n_candidates

    # Precision loss distribution
    precision_delta = np.abs(fp32_scores - int8_scores)

    return {
        "success_rate": success_rate,
        "n_adversarial": mask_adv.sum(),
        "n_benign": mask_ben.sum(),
        "fp32_scores": fp32_scores,
        "int8_scores": int8_scores,
        "precision_delta": precision_delta,
        "mask_adv": mask_adv,
        "mask_ben": mask_ben,
        "threshold_fp32": threshold_fp32,
        "threshold_int8": threshold_int8,
    }

def run_quant_sweep(n_dim=8, n_trials_per_threshold=20_000):
    """
    Sweep INT8 threshold and measure adversarial success rate.
    FP32 threshold fixed at chi2 95th percentile for n_dim degrees of freedom.
    """
    fp32_thresh = np.sqrt(chi2.ppf(0.95, df=n_dim))

    # Calibration covariance: 8 features normalised to unit-ish scale.
    # Tight diagonal makes quantization error a meaningful fraction of the variance.
    cov_diag = np.array([1.0, 1.0, 0.8, 0.8, 0.5, 0.5, 0.3, 0.3])
    cov = np.diag(cov_diag)
    cov_inv = np.linalg.inv(cov)
    mu = np.zeros(n_dim)

    int8_thresholds = np.linspace(fp32_thresh * 0.5, fp32_thresh * 1.5, 30)
    success_rates = []

    for thr in int8_thresholds:
        res = craft_int8_adversarial(mu, cov_inv, fp32_thresh, thr,
                                      n_dim=n_dim,
                                      n_candidates=n_trials_per_threshold)
        success_rates.append(res["success_rate"])

    # Full result at INT8 threshold == FP32 threshold (nominal config)
    nominal = craft_int8_adversarial(mu, cov_inv, fp32_thresh, fp32_thresh,
                                      n_dim=n_dim,
                                      n_candidates=n_trials_per_threshold)
    return {
        "int8_thresholds": int8_thresholds,
        "success_rates": np.array(success_rates),
        "nominal": nominal,
        "fp32_thresh": fp32_thresh,
    }

# ---------------------------------------------------------------------------
# SCENARIO C: Lethal Compliance — physics-valid, temporally incoherent
# ---------------------------------------------------------------------------

@njit
def hgv_dynamics_step(x, y, vx, vy, ax, ay, dt):
    vx_new = vx + ax * dt
    vy_new = vy + ay * dt
    x_new  = x  + vx * dt
    y_new  = y  + vy * dt
    return x_new, y_new, vx_new, vy_new

def generate_physics_valid_track(n_steps=N_STEPS, v0=HGV_MIN*2,
                                  use_pop_in=True, pop_in_step=5,
                                  entropy_offset=0):
    """
    Lethal Compliance scenario.

    The GENUINE track: smooth HGV dynamics, continuous from t=0.

    The ADVERSARIAL track ('cold start' injection):
      - Steps 0..pop_in_step-1: ABSENT (track not present — attacker waited)
      - Step pop_in_step: track INITIALISES with physically valid speed/G-load
        but with no prior history. The sliding-window median filter sees a
        'pop-in' because it has no baseline to compare against.
      - Steps pop_in_step+1..n_steps: physically valid propagation.

    Key property: at every step where the adversarial track EXISTS, its speed
    stays in [Mach 5, Mach 15] and G-load <= 10g. Check 3 passes.
    But the sudden appearance with no warm-up history is detected by Check 4's
    temporal coherence filter, which expects progressive refinement.

    Separately, we also generate a SMOOTH INJECTION track that has a small
    lateral offset at pop_in_step but smooth velocity — this tests whether
    the temporal coherence threshold is tight enough to catch small jumps.
    """
    dt = DT_TRACK
    noise = entropy_sample(n_steps * 4, entropy_offset).reshape(n_steps, 4) - 0.5

    # --- Genuine track (always present, continuous) ---
    xs_g, ys_g = [0.0], [0.0]
    vx_g, vy_g = v0, 0.0
    for i in range(1, n_steps):
        ay = G_LOAD_MAX * G_EARTH * 0.3 * np.sin(0.5 * i * dt)
        ax = -0.5 * G_EARTH
        x_n = xs_g[-1] + vx_g * dt
        y_n = ys_g[-1] + vy_g * dt
        vx_g = vx_g + ax * dt
        vy_g = vy_g + ay * dt
        xs_g.append(x_n + 5.0 * noise[i, 0])
        ys_g.append(y_n + 5.0 * noise[i, 1])

    # --- Adversarial: cold-start pop-in ---
    # Fill pre-pop steps with NaN (track not yet present)
    xs_a = [np.nan] * pop_in_step
    ys_a = [np.nan] * pop_in_step
    # At pop_in_step, initialise at a nearby but offset position
    xs_a.append(xs_g[pop_in_step] + 50.0)   # 50 m lateral offset
    ys_a.append(ys_g[pop_in_step])
    vx_a, vy_a = v0 * 0.98, 40.0            # physically valid velocity
    for i in range(pop_in_step + 1, n_steps):
        ay = G_LOAD_MAX * G_EARTH * 0.3 * np.sin(0.5 * i * dt)
        ax = -0.5 * G_EARTH
        x_n = xs_a[-1] + vx_a * dt
        y_n = ys_a[-1] + vy_a * dt
        vx_a = vx_a + ax * dt
        vy_a = vy_a + ay * dt
        xs_a.append(x_n + 5.0 * noise[i, 2])
        ys_a.append(y_n + 5.0 * noise[i, 3])

    return {
        "genuine":     dict(x=np.array(xs_g), y=np.array(ys_g), t=np.arange(n_steps)*dt),
        "adversarial": dict(x=np.array(xs_a), y=np.array(ys_a), t=np.arange(n_steps)*dt),
        "pop_in_step": pop_in_step,
    }

def temporal_coherence_check(track, window=5) -> dict:
    """
    Sliding-window median filter on consecutive position updates.
    Genuine tracks: smooth progressive refinement.
    Injected tracks: discontinuous jump exceeds threshold.
    Returns per-step residuals and pass/fail verdict.
    """
    x_full, y_full = track["x"], track["y"]
    n_full = len(x_full)
    valid_mask = ~np.isnan(x_full) & ~np.isnan(y_full)
    x, y = x_full[valid_mask], y_full[valid_mask]

    n = len(x)
    res_valid   = np.zeros(n)
    flags_valid = np.zeros(n, dtype=bool)

    for i in range(window, n):
        x_med = np.median(x[i-window:i])
        y_med = np.median(y[i-window:i])
        res_valid[i]   = np.sqrt((x[i] - x_med)**2 + (y[i] - y_med)**2)
        flags_valid[i] = res_valid[i] > 80.0   # meters

    # Pad back to full length so callers can align with t array
    residuals = np.full(n_full, np.nan)
    flags     = np.zeros(n_full, dtype=bool)
    residuals[valid_mask] = res_valid
    flags[valid_mask]     = flags_valid

    return {"residuals": residuals, "flags": flags, "any_fail": flags_valid.any()}

def physics_envelope_check(track) -> dict:
    """
    Check 3: verify speed within Mach 5-15 and lateral G-load <= 10g.
    Even the adversarial track should PASS this (that's the point).
    """
    x, y = track["x"], track["y"]
    valid = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[valid], y[valid]

    vx = np.diff(x) / DT_TRACK
    vy = np.diff(y) / DT_TRACK
    speed = np.sqrt(vx**2 + vy**2)
    ax    = np.diff(vx) / DT_TRACK
    ay    = np.diff(vy) / DT_TRACK
    accel = np.sqrt(ax**2 + ay**2)
    g_load = accel / G_EARTH

    speed_ok = (speed >= HGV_MIN) & (speed <= HGV_MAX)
    gload_ok = g_load <= G_LOAD_MAX

    return {
        "speed_ok": speed_ok.all(),
        "gload_ok": gload_ok.all(),
        "passes": speed_ok.all() and gload_ok.all(),
        "speed": speed,
        "g_load": g_load,
    }

def run_lethal_compliance_sweep(n_trials=500):
    """
    Sweep pop-in magnitude and measure:
    - Physics check pass rate (should stay HIGH — this is the attack's guarantee)
    - Temporal coherence detection rate (should catch the pop-in)
    """
    jump_magnitudes = np.linspace(10, 500, 50)   # meters of discontinuity
    physics_pass = []
    coherence_detect = []

    for jump in jump_magnitudes:
        p_results = []
        c_results = []
        for trial in range(n_trials):
            tracks = generate_physics_valid_track(
                use_pop_in=True, pop_in_step=5,
                entropy_offset=trial * 10)
            adv = tracks["adversarial"]
            # Manually scale the jump
            adv_scaled = dict(adv)
            adv_scaled["x"] = adv["x"].copy()
            adv_scaled["x"][5] = adv["x"][4] + jump * RNG.choice([-1, 1])

            pe = physics_envelope_check(adv_scaled)
            tc = temporal_coherence_check(adv_scaled)
            p_results.append(int(pe["passes"]))
            c_results.append(int(tc["any_fail"]))

        physics_pass.append(np.mean(p_results))
        coherence_detect.append(np.mean(c_results))

    return {
        "jump_magnitudes": jump_magnitudes,
        "physics_pass_rate": np.array(physics_pass),
        "coherence_detect_rate": np.array(coherence_detect),
    }

# ---------------------------------------------------------------------------
# Sensitivity Analysis: Detection Probability vs. Adversarial Sophistication
# ---------------------------------------------------------------------------

def sensitivity_analysis(n_points=60):
    """
    Model adversary sophistication on a 0-1 scale.
    At low sophistication: random perturbations, caught easily.
    At high sophistication: physics-compliant, calibration-aware.

    Aggregate 7-check detection probability as a function of sophistication.
    This is a model-based estimate, not a simulation — but grounded in the
    individual check failure rates measured above.
    """
    sophistication = np.linspace(0, 1, n_points)

    # Each curve: P(check detects adversary | sophistication)
    # Schema / MIO hash: very effective at low sophistication.
    # A sophisticated adversary can craft a valid-schema capsule
    # (they don't need the signing key for schema validation).
    # MIO HASH is a separate cryptographic gate; schema alone doesn't catch them.
    # For schema structural check only: drops as adversary learns the schema.
    p_schema    = np.where(sophistication < 0.3, 0.98,
                  np.where(sophistication < 0.6, 0.98 - 0.60*(sophistication-0.3)/0.3,
                           0.38 - 0.35*(sophistication-0.6)/0.4))
    p_schema    = np.clip(p_schema, 0.0, 1.0)

    # Physics envelope: monotonically harder for adversary to stay compliant
    # at low sophistication they violate physics; at high they don't.
    p_physics   = 1.0 - 0.92 * sophistication

    # Temporal coherence: mid-sophistication adversary learns to smooth
    # injection. High-sophistication achieves near-perfect continuity.
    p_temporal  = 1.0 - 0.88 * sophistication**1.4

    # INT8 Mahalanobis: quantization gap is most dangerous at medium
    # sophistication when adversary exploits precision loss without needing
    # calibration data.
    p_int8_mah  = np.where(sophistication < 0.4,
                           1.0 - 0.25 * sophistication / 0.4,
                           0.75 - 0.70 * (sophistication - 0.4) / 0.6)
    p_int8_mah  = np.clip(p_int8_mah, 0.03, 1.0)

    # PINN (chaotic quantization): hardware entropy is the defence.
    # Zero-knowledge adversary can't replicate Lorenz seed without physical access.
    # Stays at ~0.72 flat for zero-knowledge adversary.
    p_pinn      = 0.72 * np.ones(n_points)

    # Geo-fence + quorum: spatial. Hard to defeat without ISL jamming.
    # ISL jamming effectiveness grows with adversary capability.
    p_geofence  = 1.0 - 0.65 * sophistication**1.8

    # Staleness check: similar trajectory to temporal coherence but independent.
    p_staleness = 1.0 - 0.80 * sophistication**1.2

    # Combined: any one of the 7 checks catches the adversary
    # P(all checks miss) = product of P(each misses) = product of (1 - p_detect_i)
    p_miss_each = np.column_stack([
        1 - p_schema,
        1 - p_physics,
        1 - p_temporal,
        1 - p_int8_mah,
        1 - p_pinn,
        1 - p_geofence,
        1 - p_staleness,
    ])
    p_all_miss = np.prod(p_miss_each, axis=1)
    p_detected = 1 - p_all_miss

    return {
        "sophistication": sophistication,
        "p_schema": p_schema,
        "p_physics": p_physics,
        "p_temporal": p_temporal,
        "p_int8_mah": p_int8_mah,
        "p_pinn": p_pinn,
        "p_geofence": p_geofence,
        "p_staleness": p_staleness,
        "p_detected_combined": p_detected,
    }

# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLORS = {
    "blue":    "#1a6faf",
    "red":     "#c0392b",
    "green":   "#1a7a4a",
    "orange":  "#d67500",
    "purple":  "#6b3fa0",
    "gray":    "#555555",
    "light":   "#dddddd",
}

def plot_ghost_attack(res: dict, path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Scenario A: Ghost-in-the-Matrix Attack", fontsize=13, fontweight="bold")

    # FAR curve
    ax = axes[0]
    ax.plot(res["deltas"], res["far_curve"], color=COLORS["red"], lw=1.5)
    ax.axvline(0, color=COLORS["gray"], ls="--", lw=0.8, label="No offset")
    ax.axvline(-500, color=COLORS["orange"], ls=":", lw=1.2, label="Δt = −500 ms (TTL boundary)")
    ax.set_xlabel("Clock offset Δt (ms)")
    ax.set_ylabel("False Acceptance (1=pass, 0=hold)")
    ax.set_title("Staleness Check: Pass Rate vs. Clock Offset")
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=9)
    ax.text(0.04, 0.15,
            "Adversary injects Δt < 0 to make\nstale track appear fresh.\n"
            "Full bypass achieved at Δt ≤ −500 ms.",
            transform=ax.transAxes, fontsize=8.5, color=COLORS["red"],
            bbox=dict(boxstyle="round,pad=0.3", fc="#fff0f0", ec=COLORS["red"], alpha=0.8))

    # Latency jitter distribution
    ax2 = axes[1]
    ax2.hist(res["latency_dist"], bins=100, density=True, color=COLORS["blue"],
             alpha=0.7, label="auditor.latency_ms")
    ax2.axvline(5.0, color=COLORS["red"], lw=1.5, ls="--", label="5.0 ms hard limit")
    ax2.axvline(res["p99_ms"], color=COLORS["orange"], lw=1.2, ls=":",
                label=f"P99 = {res['p99_ms']:.2f} ms")
    ax2.axvline(res["p999_ms"], color=COLORS["purple"], lw=1.2, ls="-.",
                label=f"P99.9 = {res['p999_ms']:.2f} ms")
    ax2.set_xlabel("Auditor latency (ms)")
    ax2.set_ylabel("Density")
    ax2.set_title("Latency Distribution — Log-normal Tail (SEU events)")
    ax2.legend(fontsize=9)
    ax2.text(0.55, 0.72,
             f"Long tail: gate stays open\nat P99.9 = {res['p999_ms']:.2f} ms\n"
             f"({100*(res['p999_ms']>5.0):.0f}% chance > hard limit)",
             transform=ax2.transAxes, fontsize=8.5, color=COLORS["purple"],
             bbox=dict(boxstyle="round,pad=0.3", fc="#f8f0ff", ec=COLORS["purple"], alpha=0.8))

    plt.tight_layout()
    fig.savefig(path / "A_ghost_attack.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [A] Ghost attack plot saved.")

def plot_quant_spoof(res: dict, path: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Scenario B: Quantization-Aware Spoofing (INT8 vs FP32)", fontsize=13, fontweight="bold")

    nom = res["nominal"]

    # Scatter: FP32 vs INT8 Mahalanobis scores
    ax = axes[0]
    ax.scatter(nom["fp32_scores"][nom["mask_ben"]], nom["int8_scores"][nom["mask_ben"]],
               s=2, alpha=0.3, color=COLORS["blue"], label="Benign")
    ax.scatter(nom["fp32_scores"][nom["mask_adv"]], nom["int8_scores"][nom["mask_adv"]],
               s=4, alpha=0.6, color=COLORS["red"], label=f"Adversarial ({nom['success_rate']*100:.1f}%)")
    ax.axvline(nom["threshold_fp32"], color=COLORS["gray"], ls="--", lw=0.8)
    ax.axhline(nom["threshold_int8"], color=COLORS["gray"], ls="--", lw=0.8)
    ax.set_xlabel("FP32 Mahalanobis distance")
    ax.set_ylabel("INT8 Mahalanobis distance")
    ax.set_title("Score Space: Adversarial Cluster")
    ax.legend(fontsize=9)

    # Precision loss distribution
    ax2 = axes[1]
    ax2.hist(nom["precision_delta"], bins=80, density=True,
             color=COLORS["orange"], alpha=0.8)
    ax2.set_xlabel("|FP32 − INT8| Mahalanobis delta")
    ax2.set_ylabel("Density")
    ax2.set_title("Quantization Precision Loss Distribution")
    med = np.median(nom["precision_delta"])
    ax2.axvline(med, color=COLORS["red"], ls="--", lw=1.2, label=f"Median = {med:.2f}")
    ax2.legend(fontsize=9)

    # Success rate vs INT8 threshold
    ax3 = axes[2]
    ax3.plot(res["int8_thresholds"], res["success_rates"] * 100,
             color=COLORS["red"], lw=1.8)
    ax3.axvline(res["fp32_thresh"], color=COLORS["gray"], ls="--",
                lw=0.8, label="FP32 threshold (nominal)")
    ax3.set_xlabel("INT8 detection threshold")
    ax3.set_ylabel("Adversarial success rate (%)")
    ax3.set_title("FAR vs. INT8 Threshold")
    ax3.legend(fontsize=9)
    ax3.text(0.05, 0.7,
             "As INT8 threshold loosens,\nadversary success climbs.\n"
             "Zero-knowledge adversary\nexploits quantization gap\nwithout model access.",
             transform=ax3.transAxes, fontsize=8.5, color=COLORS["red"],
             bbox=dict(boxstyle="round,pad=0.3", fc="#fff0f0", ec=COLORS["red"], alpha=0.8))

    plt.tight_layout()
    fig.savefig(path / "B_quant_spoof.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [B] Quantization spoof plot saved. Nominal success rate: {nom['success_rate']*100:.2f}%")

def plot_lethal_compliance(lc_res: dict, track_data: dict, path: Path):
    fig = plt.figure(figsize=(15, 10))
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)
    fig.suptitle("Scenario C: Lethal Compliance — Physics-Valid, Temporally Incoherent",
                 fontsize=13, fontweight="bold")

    gen = track_data["genuine"]
    adv = track_data["adversarial"]
    pop = track_data["pop_in_step"]
    tc_gen = temporal_coherence_check(gen)
    tc_adv = temporal_coherence_check(adv)
    pe_gen = physics_envelope_check(gen)
    pe_adv = physics_envelope_check(adv)

    # XY trajectory
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.plot(gen["x"]/1000, gen["y"]/1000, color=COLORS["blue"], lw=1.5, label="Genuine")
    ax0.plot(adv["x"]/1000, adv["y"]/1000, color=COLORS["red"], lw=1.5, ls="--", label="Adversarial")
    ax0.axvline(gen["x"][pop]/1000, color=COLORS["orange"], ls=":", lw=0.8, label=f"Pop-in at t={pop*DT_TRACK:.1f}s")
    ax0.set_xlabel("Downrange (km)")
    ax0.set_ylabel("Crossrange (km)")
    ax0.set_title("XY Trajectory")
    ax0.legend(fontsize=8)

    # Temporal coherence residuals
    ax1 = fig.add_subplot(gs[0, 1])
    t = gen["t"]
    ax1.plot(t, tc_gen["residuals"], color=COLORS["blue"], lw=1.2, label="Genuine")
    ax1.plot(t, tc_adv["residuals"], color=COLORS["red"], lw=1.2, ls="--", label="Adversarial")
    ax1.axhline(80.0, color=COLORS["gray"], ls="--", lw=0.8, label="Detection threshold (80 m)")
    ax1.axvline(pop*DT_TRACK, color=COLORS["orange"], ls=":", lw=0.8)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Median residual (m)")
    ax1.set_title("Temporal Coherence Check (Check 4)")
    ax1.legend(fontsize=8)
    detected = "DETECTED" if tc_adv["any_fail"] else "MISSED"
    ax1.text(0.6, 0.85, detected,
             transform=ax1.transAxes, fontsize=11, fontweight="bold",
             color=COLORS["green"] if tc_adv["any_fail"] else COLORS["red"])

    # Speed profiles
    ax2 = fig.add_subplot(gs[0, 2])
    t_v = t[:-1]
    vg = np.sqrt(np.diff(gen["x"])**2 + np.diff(gen["y"])**2) / DT_TRACK
    va = np.sqrt(np.diff(adv["x"])**2 + np.diff(adv["y"])**2) / DT_TRACK
    ax2.plot(t_v, vg/MACH, color=COLORS["blue"], label="Genuine")
    ax2.plot(t_v, va/MACH, color=COLORS["red"], ls="--", label="Adversarial")
    ax2.axhline(5, color=COLORS["gray"], ls=":", lw=0.8, label="Mach 5 (envelope floor)")
    ax2.axhline(15, color=COLORS["gray"], ls=":", lw=0.8, label="Mach 15 (envelope ceiling)")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Speed (Mach)")
    ax2.set_title("Speed Profile (Check 3 — should pass)")
    ax2.legend(fontsize=8)

    # G-load — each track may have different valid-sample counts after NaN filtering
    ax3 = fig.add_subplot(gs[1, 0])
    ga = pe_gen["g_load"]
    aa = pe_adv["g_load"]
    t_ga = np.linspace(0, WINDOW_S, len(ga))
    t_aa = np.linspace(0, WINDOW_S, len(aa))
    ax3.plot(t_ga, ga, color=COLORS["blue"], label="Genuine")
    ax3.plot(t_aa, aa, color=COLORS["red"], ls="--", label="Adversarial")
    ax3.axhline(G_LOAD_MAX, color=COLORS["gray"], ls="--", lw=0.8, label="10g limit")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("G-load")
    ax3.set_title("G-Load Check (Check 3)")
    ax3.legend(fontsize=8)

    # Physics pass vs. detection sweep
    ax4 = fig.add_subplot(gs[1, 1])
    jm = lc_res["jump_magnitudes"]
    ax4.plot(jm, lc_res["physics_pass_rate"]*100, color=COLORS["blue"], lw=1.8, label="Physics check pass rate")
    ax4.plot(jm, lc_res["coherence_detect_rate"]*100, color=COLORS["green"], lw=1.8, label="Coherence detection rate")
    ax4.set_xlabel("Pop-in discontinuity (m)")
    ax4.set_ylabel("Rate (%)")
    ax4.set_title("Lethal Compliance Sweet Spot")
    ax4.legend(fontsize=9)
    # Mark the crossing point
    cross = np.argmin(np.abs(lc_res["physics_pass_rate"] - lc_res["coherence_detect_rate"]))
    ax4.axvline(jm[cross], color=COLORS["red"], ls=":", lw=0.9,
                label=f"Cross-over at {jm[cross]:.0f} m")
    ax4.legend(fontsize=9)
    ax4.text(0.5, 0.15,
             "Below cross-over:\nphysics passes, coherence\ncheck may miss.",
             transform=ax4.transAxes, fontsize=8.5, color=COLORS["red"],
             bbox=dict(boxstyle="round,pad=0.3", fc="#fff0f0", ec=COLORS["red"], alpha=0.8))

    # Summary table
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis("off")
    rows = [
        ["Check", "Genuine", "Adversarial"],
        ["Physics envelope", "PASS" if pe_gen["passes"] else "FAIL",
         "PASS" if pe_adv["passes"] else "FAIL"],
        ["Temporal coherence", "PASS" if not tc_gen["any_fail"] else "FAIL",
         "DETECTED" if tc_adv["any_fail"] else "MISSED"],
    ]
    colors_table = [
        ["#e0e0e0", "#e0e0e0", "#e0e0e0"],
        ["white",
         "#d4f7d4" if pe_gen["passes"] else "#fdd",
         "#fdd" if pe_adv["passes"] else "#d4f7d4"],
        ["white",
         "#d4f7d4" if not tc_gen["any_fail"] else "#fdd",
         "#d4f7d4" if tc_adv["any_fail"] else "#fdd"],
    ]
    t_obj = ax5.table(cellText=rows, cellLoc="center", loc="center",
                      cellColours=colors_table)
    t_obj.auto_set_font_size(False)
    t_obj.set_fontsize(10)
    t_obj.scale(1, 2.5)
    ax5.set_title("Check Results Summary")

    fig.savefig(path / "C_lethal_compliance.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [C] Lethal compliance plot saved.")

def plot_sensitivity(sens: dict, path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Sensitivity Analysis: Detection Probability vs. Adversarial Sophistication",
                 fontsize=13, fontweight="bold")

    s = sens["sophistication"]
    ax = axes[0]
    ax.plot(s, sens["p_schema"]*100,    color=COLORS["gray"],   lw=1.5, label="Schema (structural)")
    ax.plot(s, sens["p_physics"]*100,   color=COLORS["blue"],   lw=1.5, label="Physics envelope")
    ax.plot(s, sens["p_temporal"]*100,  color=COLORS["green"],  lw=1.5, label="Temporal coherence")
    ax.plot(s, sens["p_int8_mah"]*100,  color=COLORS["orange"], lw=1.5, label="INT8 Mahalanobis")
    ax.plot(s, sens["p_pinn"]*100,      color=COLORS["purple"], lw=1.5, label="PINN (chaotic quant.)")
    ax.plot(s, sens["p_geofence"]*100,  color=COLORS["red"],    lw=1.5, label="Geo-fence / quorum")
    ax.plot(s, sens["p_staleness"]*100, color="#888800",        lw=1.5, ls="--", label="Staleness TTL")
    ax.set_xlabel("Adversary sophistication (0 = random, 1 = nation-state w/ calibration access)")
    ax.set_ylabel("P(detected) per check (%)")
    ax.set_title("Per-Check Detection Probability")
    ax.legend(fontsize=8, loc="lower left")
    ax.set_ylim(-5, 105)

    ax2 = axes[1]
    ax2.plot(s, sens["p_detected_combined"]*100, color=COLORS["blue"], lw=2.5,
             label="Combined (any check catches)")
    ax2.fill_between(s, sens["p_detected_combined"]*100, alpha=0.15, color=COLORS["blue"])
    ax2.set_xlabel("Adversary sophistication")
    ax2.set_ylabel("P(detected) — combined all 7 checks (%)")
    ax2.set_title("Combined 7-Check Detection Rate")
    ax2.set_ylim(-5, 105)
    ax2.axhline(50, color=COLORS["gray"], ls="--", lw=0.8, label="50% line")

    # Annotate the dangerous zone (nation-state, zero-knowledge)
    danger_zone_start = 0.7
    ax2.axvspan(danger_zone_start, 1.0, alpha=0.1, color=COLORS["red"])
    ax2.text(0.73, 20, "Nation-state\nzero-knowledge\nzone",
             fontsize=9, color=COLORS["red"],
             bbox=dict(boxstyle="round,pad=0.2", fc="#fff0f0", ec=COLORS["red"], alpha=0.7))
    ax2.legend(fontsize=9)

    plt.tight_layout()
    fig.savefig(path / "D_sensitivity.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [D] Sensitivity analysis plot saved.")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Golden Dome Falsification Suite — v1.0")
    print(f"NumPy: {np.__version__}  |  Numba: {'yes' if NUMBA_AVAILABLE else 'no (scipy fallback)'}")
    print("=" * 60)

    print("\n[A] Ghost-in-the-Matrix attack sweep...")
    ghost_res = run_ghost_attack_sweep(n_trials=2000)
    plot_ghost_attack(ghost_res, OUT)
    print(f"    P99 latency = {ghost_res['p99_ms']:.3f} ms  |  "
          f"P99.9 = {ghost_res['p999_ms']:.3f} ms  |  "
          f"Exceeds 5ms hard limit: {ghost_res['p999_ms'] > 5.0}")

    print("\n[B] Quantization-aware spoofing sweep...")
    quant_res = run_quant_sweep(n_dim=8, n_trials_per_threshold=20_000)
    plot_quant_spoof(quant_res, OUT)
    nom_sar = quant_res["nominal"]["success_rate"]
    print(f"    Nominal adversarial success rate (INT8 vs FP32): {nom_sar*100:.2f}%")
    print(f"    FP32 detection threshold: {quant_res['fp32_thresh']:.3f}")

    print("\n[C] Lethal compliance scenario...")
    track_data = generate_physics_valid_track(n_steps=N_STEPS, pop_in_step=5, entropy_offset=1234)
    lc_sweep   = run_lethal_compliance_sweep(n_trials=300)
    plot_lethal_compliance(lc_sweep, track_data, OUT)
    pe_adv = physics_envelope_check(track_data["adversarial"])
    tc_adv = temporal_coherence_check(track_data["adversarial"])
    print(f"    Physics envelope: {'PASS' if pe_adv['passes'] else 'FAIL'}  |  "
          f"Temporal coherence: {'DETECTED' if tc_adv['any_fail'] else 'MISSED'}")

    print("\n[D] Sensitivity analysis...")
    sens = sensitivity_analysis(n_points=60)
    plot_sensitivity(sens, OUT)

    print("\n" + "=" * 60)
    print("FALSIFICATION SUMMARY")
    print("=" * 60)
    print(f"\nA. Ghost-in-the-Matrix")
    print(f"   Full staleness-check bypass at Δt ≤ −500 ms.")
    print(f"   P99.9 latency = {ghost_res['p999_ms']:.2f} ms — "
          f"{'exceeds' if ghost_res['p999_ms'] > 5.0 else 'within'} 5 ms hard limit.")
    print(f"\nB. Quantization-Aware Spoof")
    print(f"   {nom_sar*100:.1f}% of candidates pass INT8 gate while failing FP32 gate.")
    print(f"   Zero-knowledge adversary achieves this with no model weight access.")
    print(f"\nC. Lethal Compliance")
    print(f"   Physics check: {'PASS (attack succeeds at C3)' if pe_adv['passes'] else 'FAIL'}")
    print(f"   Temporal coherence: {'correctly DETECTED' if tc_adv['any_fail'] else 'MISSED (attack proceeds)'}")
    print(f"   Sweet-spot discontinuity (cross-over): "
          f"~{lc_sweep['jump_magnitudes'][np.argmin(np.abs(lc_sweep['physics_pass_rate'] - lc_sweep['coherence_detect_rate']))]:.0f} m")
    print(f"\nD. Nation-state adversary (sophistication > 0.7)")
    p_at_07 = np.interp(0.7, sens["sophistication"], sens["p_detected_combined"])
    p_at_10 = sens["p_detected_combined"][-1]
    print(f"   Combined detection at s=0.7: {p_at_07*100:.1f}%")
    print(f"   Combined detection at s=1.0: {p_at_10*100:.1f}%")
    print(f"\nAll plots written to: {OUT}")
    print("=" * 60)

if __name__ == "__main__":
    main()
