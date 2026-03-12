"""
ReposiTUm — Multi-Variant Monte Carlo Simulation
Unit: MINUTES of Active Touch Time per publication
"""

import math
import random
import statistics

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & PARAMETERS
# ---------------------------------------------------------------------------

N_TRIALS = 10_000

TIME_ASIS_ENTRY      = (5, 15, 30)
TIME_ASIS_REWORK     = (2,  5, 10)
TIME_RIS_CHECK       = (10, 15, 25)
TIME_LIB_CHECK       = (4,   8, 20)
TIME_FAC_CHECK       = (1,   3, 10)

PROBS_REJECT = [0.0262, 0.0149, 0.0023]

TIME_STREAMLINE_ENTRY      = (5, 15, 30)
TIME_1STEP_VALIDATION      = (6, 10, 22)
TIME_EXPERT_ENTRY      = (3,  7, 10)
TIME_EXPERT_VALIDATION = (6, 12, 26)
TIME_MAX_AUTO_ENTRY      = (1,  3,  5)
TIME_MAX_AUTO_VALIDATION = (5, 10, 15)
TIME_SYS_RELEASE = (0.1, 0.1, 0.1)

# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------

def _tri(params: tuple) -> float:
    """Shorthand for random.triangular(*params)."""
    return random.triangular(*params)



def _asis_rejection_loop() -> tuple[float, float]:
    """
    Run the AS-IS sequential validation loop.
    Returns (total_validation_time, total_rework_time).
    """
    val = rework = 0.0
    published = False
    while not published:
        val += _tri(TIME_RIS_CHECK)
        if random.random() < PROBS_REJECT[0]:
            rework += _tri(TIME_ASIS_REWORK)
            continue

        val += _tri(TIME_LIB_CHECK)
        if random.random() < PROBS_REJECT[1]:
            rework += _tri(TIME_ASIS_REWORK)
            continue

        val += _tri(TIME_FAC_CHECK)
        if random.random() < PROBS_REJECT[2]:
            rework += _tri(TIME_ASIS_REWORK)
            continue

        published = True
    return val, rework

# ---------------------------------------------------------------------------
# 3. SIMULATION VARIANTS
# ---------------------------------------------------------------------------

def sim_asis() -> float:
    """AS-IS: Sequential validation with rework loops."""
    entry = _tri(TIME_ASIS_ENTRY)
    val, rework = _asis_rejection_loop()
    return entry + val + rework + _tri(TIME_SYS_RELEASE)


def sim_streamlined() -> float:
    """Procedural Streamlining: 1-Step Validation with In-Place Correction."""
    return (
        _tri(TIME_STREAMLINE_ENTRY)
        + _tri(TIME_1STEP_VALIDATION)
        + _tri(TIME_SYS_RELEASE)
    )


def sim_expert_operations() -> float:
    """Expert Operations: shift manual burden to the Expert Validator."""
    return (
        _tri(TIME_EXPERT_ENTRY)
        + _tri(TIME_EXPERT_VALIDATION)
        + _tri(TIME_SYS_RELEASE)
    )


def sim_max_automation() -> float:
    """Maximum Automation: API Fetch + 1-Step Validation."""
    return (
        _tri(TIME_MAX_AUTO_ENTRY)
        + _tri(TIME_MAX_AUTO_VALIDATION)
        + _tri(TIME_SYS_RELEASE)
    )

# ---------------------------------------------------------------------------
# 4. REPORTING
# ---------------------------------------------------------------------------

def _confidence_interval(data: list[float]) -> tuple[float, float]:
    n = len(data)
    mean = statistics.mean(data)
    margin = 1.96 * statistics.stdev(data) / math.sqrt(n)
    return mean - margin, mean + margin


def print_report(results_dict: dict[str, list[float]]) -> None:
    print("=" * 65)
    print(f"  REPOSITUM — MULTI-VARIANT MONTE CARLO SIMULATION ({N_TRIALS:,} Trials)")
    print("=" * 65)

    baseline_mean = statistics.mean(results_dict["AS-IS Baseline"])

    for name, data in results_dict.items():
        mean_val = statistics.mean(data)
        ci_lo, ci_hi = _confidence_interval(data)

        print(f"\n── {name.upper()} ──────────────────────────────────────────")
        print(f"  Mean active touch time : {mean_val:7.2f} min")
        print(f"  Std deviation          : {statistics.stdev(data):7.2f} min")
        print(f"  Median                 : {statistics.median(data):7.2f} min")
        print(f"  95th percentile        : {np.percentile(data, 95):7.2f} min  (worst-case)")
        print(f"  95% CI (mean)          : [{ci_lo:.2f}, {ci_hi:.2f}] min")

        if name != "AS-IS Baseline":
            reduction = (baseline_mean - mean_val) / baseline_mean * 100
            print(f"  vs Baseline            : -{reduction:.1f}% average effort reduction")

    print("\n" + "=" * 65)

# ---------------------------------------------------------------------------
# 5. VISUALISATION
# ---------------------------------------------------------------------------

COLORS = {
    "AS-IS Baseline":          "#e74c3c",
    "Procedural Streamlining": "#f39c12",
    "Expert Operations":       "#3498db",
    "Maximum Automation":      "#27ae60",
}


def plot_results(results_dict: dict[str, list[float]]) -> None:
    """Overlapping histogram, box plot, and CDF in a single figure."""
    fig = plt.figure(figsize=(15, 11))
    fig.suptitle(
        "ReposiTUm Workflow — Impact of Solution Packages on Active Touch Time",
        fontsize=16, fontweight="bold",
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    # Top: Overlapping density histograms
    ax1 = fig.add_subplot(gs[0, :])
    for name, data in results_dict.items():
        ax1.hist(data, bins=50, alpha=0.5, color=COLORS[name], label=name, density=True)
        ax1.axvline(statistics.mean(data), color=COLORS[name], linestyle="--", lw=1.5)
    ax1.set_title("Density Distribution Across All Trials (dashed = mean)")
    ax1.set_xlabel("Minutes per Publication (Active Human Effort)")
    ax1.set_ylabel("Density")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Bottom-left: Notched box plot
    ax2 = fig.add_subplot(gs[1, 0])
    labels = list(results_dict.keys())
    bp = ax2.boxplot(
        list(results_dict.values()),
        tick_labels=labels,
        patch_artist=True,
        notch=True,
    )
    for patch, name in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS[name])
        patch.set_alpha(0.7)
    ax2.set_title("Box Plot (notch = 95% CI of median)")
    ax2.set_ylabel("Total Active Touch Time (Minutes)")
    ax2.tick_params(axis="x", labelrotation=15)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    # Bottom-right: CDF
    ax3 = fig.add_subplot(gs[1, 1])
    for name, data in results_dict.items():
        sorted_s = np.sort(data)
        cdf = np.arange(1, len(sorted_s) + 1) / len(sorted_s)
        ax3.plot(sorted_s, cdf, color=COLORS[name], label=name, lw=2)
    ax3.axhline(0.95, color="grey", linestyle=":", lw=1, label="95th pct")
    ax3.set_title("Cumulative Distribution Function (CDF)")
    ax3.set_xlabel("Minutes per Publication (Active Human Effort)")
    ax3.set_ylabel("Cumulative Probability")
    ax3.legend()
    ax3.grid(linestyle="--", alpha=0.5)

    try:
        plt.savefig("simulation_results.pdf", format="pdf", dpi=300)
        print("Charts saved → simulation_results.pdf")
    except Exception as exc:
        print(f"Could not save PDF: {exc}")

    #plt.show()


def run_detailed_simulation(n_trials: int = N_TRIALS) -> dict:
    """
    Re-runs the simulation tracking Entry / Validation separately.
    Returns per-variant means for the stacked bar chart.
    """
    components: dict[str, dict[str, list]] = {
        variant: {"Entry": [], "Validation": []}
        for variant in ("AS-IS Baseline", "Procedural Streamlining",
                        "Expert Operations", "Maximum Automation")
    }

    for _ in range(n_trials):
        # AS-IS Baseline
        entry = _tri(TIME_ASIS_ENTRY)
        val, _ = _asis_rejection_loop()
        components["AS-IS Baseline"]["Entry"].append(entry)
        components["AS-IS Baseline"]["Validation"].append(val)

        # Procedural Streamlining
        components["Procedural Streamlining"]["Entry"].append(_tri(TIME_STREAMLINE_ENTRY))
        components["Procedural Streamlining"]["Validation"].append(_tri(TIME_1STEP_VALIDATION))

        # Expert Operations
        components["Expert Operations"]["Entry"].append(_tri(TIME_EXPERT_ENTRY))
        components["Expert Operations"]["Validation"].append(_tri(TIME_EXPERT_VALIDATION))

        # Maximum Automation
        components["Maximum Automation"]["Entry"].append(_tri(TIME_MAX_AUTO_ENTRY))
        components["Maximum Automation"]["Validation"].append(_tri(TIME_MAX_AUTO_VALIDATION))

    return {
        variant: {cat: statistics.mean(vals) for cat, vals in cats.items()}
        for variant, cats in components.items()
    }


def plot_stacked_bar_chart(means_dict: dict) -> None:
    """Stacked bar chart showing the composition of labour across architectures."""
    labels  = list(means_dict.keys())
    entry_m = [means_dict[l]["Entry"]      for l in labels]
    val_m   = [means_dict[l]["Validation"] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.5

    p1 = ax.bar(labels, entry_m, width,                 label="Researcher Entry Time", color="#34495e")
    p2 = ax.bar(labels, val_m,   width, bottom=entry_m, label="Validator Review Time", color="#3498db")

    ax.set_title("Shift in Labour Composition Across Architectures", fontsize=14, fontweight="bold")
    ax.set_ylabel("Average Active Touch Time (Minutes)", fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    for bars in (p1, p2):
        for bar in bars:
            h = bar.get_height()
            if h > 1:
                ax.annotate(
                    f"{h:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + h / 2),
                    ha="center", va="center",
                    color="white", fontweight="bold",
                )

    plt.tight_layout()
    plt.savefig("labor_composition_stacked_bar.pdf", format="pdf", dpi=300)
    #plt.show()

# ---------------------------------------------------------------------------
# 6. ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)

    results = {
        "AS-IS Baseline":          [sim_asis()               for _ in range(N_TRIALS)],
        "Procedural Streamlining": [sim_streamlined()        for _ in range(N_TRIALS)],
        "Expert Operations":       [sim_expert_operations()  for _ in range(N_TRIALS)],
        "Maximum Automation":      [sim_max_automation()     for _ in range(N_TRIALS)],
    }

    print_report(results)
    plot_results(results)
    random.seed(42)
    detailed_means = run_detailed_simulation(N_TRIALS)
    plot_stacked_bar_chart(detailed_means)
    print(detailed_means)
