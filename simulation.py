import random
import statistics
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# --- 1. CONFIGURATION & PARAMETERS (Unit: MINUTES of Active Touch Time) ---
N_TRIALS = 10_000

# 0. AS-IS Parameters (Baseline)
# Initial heavy manual entry (9-tabs), estimated by prior PO
TIME_ASIS_ENTRY = (5, 15, 30)
# User fixing a specific rejected field, estimated
TIME_ASIS_REWORK = (2, 5, 10)
TIME_RIS_CHECK = (10, 15, 25)
TIME_LIB_CHECK = (4, 8, 20)  # Estimated from library validator
TIME_FAC_CHECK = (1, 3, 10)  # Estimated from faculty validator

# EMPIRICAL REJECTION RATES (Based on 51,077 historical submissions, 2023-2025 data)
PROBS_REJECT = [0.0262, 0.0149, 0.0023]

# 1. Procedural Streamlining Parameters
TIME_STREAMLINE_ENTRY = (5, 15, 30)
# Combined validation step, based on expert feedback
TIME_1STEP_VALIDATION = (6, 10, 22)
PROB_STREAMLINE_NEEDS_EDIT = 0.20  # High error rate remains from manual entry
# Time penalty for user to fix errors during validation, estimated from expert feedback
TIME_IN_PLACE_EDIT = (2, 5, 10)

# 2. Expert Operations Parameters
# User does less, selects fewer fields, estimated
TIME_EXPERT_ENTRY = (3, 7, 10)
# Expert spends more time reviewing/fixing
TIME_EXPERT_VALIDATION = (6, 12, 26)
PROB_EXPERT_NEEDS_EDIT = 0.05

# 3. Maximum Automation Parameters (Full TO-BE / Import-First)
TIME_MAX_AUTO_ENTRY = (1, 3, 5)  # Just DOI + upload + institute
# Faster validation because data is API-clean
TIME_MAX_AUTO_VALIDATION = (5, 10, 15)
PROB_API_NEEDS_EDIT = 0.05

# Degenerate triangular distribution (constant) because system release is deterministic
TIME_SYS_RELEASE = (0.1, 0.1, 0.1)

# --- 2. CORE SAMPLERS ---


def sim_asis():
    """AS-IS: Sequential validation with rework loops"""
    time = random.triangular(*TIME_ASIS_ENTRY)  # Pay initial entry time ONCE
    published = False
    while not published:
        # Note: If rejected, entry time is NOT re-added, only the rework time below
        time += random.triangular(*TIME_RIS_CHECK)
        if random.random() < PROBS_REJECT[0]:
            time += random.triangular(*TIME_ASIS_REWORK)
            continue

        time += random.triangular(*TIME_LIB_CHECK)
        if random.random() < PROBS_REJECT[1]:
            time += random.triangular(*TIME_ASIS_REWORK)
            continue

        time += random.triangular(*TIME_FAC_CHECK)
        if random.random() < PROBS_REJECT[2]:
            time += random.triangular(*TIME_ASIS_REWORK)
            continue

        time += random.triangular(*TIME_SYS_RELEASE)
        published = True
    return time


def sim_streamlined():
    """Procedural Streamlining: 1-Step Validation with In-Place Correction"""
    time = random.triangular(*TIME_STREAMLINE_ENTRY)
    time += random.triangular(*TIME_1STEP_VALIDATION)
    if random.random() < PROB_STREAMLINE_NEEDS_EDIT:
        time += random.triangular(*TIME_IN_PLACE_EDIT)
    time += random.triangular(*TIME_SYS_RELEASE)
    return time


def sim_expert_operations():
    """Expert Operations: Shift manual burden to the Expert Validator"""
    time = random.triangular(*TIME_EXPERT_ENTRY)
    time += random.triangular(*TIME_EXPERT_VALIDATION)
    if random.random() < PROB_EXPERT_NEEDS_EDIT:
        time += random.triangular(*TIME_IN_PLACE_EDIT)
    time += random.triangular(*TIME_SYS_RELEASE)
    return time


def sim_max_automation():
    """Maximum Automation: API Fetch + 1-Step Validation"""
    time = random.triangular(*TIME_MAX_AUTO_ENTRY)
    time += random.triangular(*TIME_MAX_AUTO_VALIDATION)
    if random.random() < PROB_API_NEEDS_EDIT:
        time += random.triangular(*TIME_IN_PLACE_EDIT)
    time += random.triangular(*TIME_SYS_RELEASE)
    return time

# --- 3. REPORTING & STATISTICS ---


def confidence_interval(data):
    n = len(data)
    mean = statistics.mean(data)
    std_err = statistics.stdev(data) / math.sqrt(n)
    margin = 1.96 * std_err
    return mean - margin, mean + margin


def print_report(results_dict):
    print("=" * 65)
    print(
        f"  REPOSITUM — MULTI-VARIANT MONTE CARLO SIMULATION ({N_TRIALS:,} Trials)")
    print("=" * 65)

    baseline_mean = statistics.mean(results_dict["AS-IS Baseline"])

    for name, data in results_dict.items():
        mean_val = statistics.mean(data)
        ci_lo, ci_hi = confidence_interval(data)

        print(f"\n── {name.upper()} ──────────────────────────────────────────")
        print(f"  Mean active touch time : {mean_val:7.2f} min")
        print(f"  Std deviation          : {statistics.stdev(data):7.2f} min")
        print(f"  Median                 : {statistics.median(data):7.2f} min")
        print(
            f"  95th percentile        : {np.percentile(data, 95):7.2f} min (Worst-case)")
        print(f"  95% CI (mean)          : [{ci_lo:.2f}, {ci_hi:.2f}] min")

        if name != "AS-IS Baseline":
            reduction = ((baseline_mean - mean_val) / baseline_mean) * 100
            print(
                f"  vs Baseline            : -{reduction:.1f}% average effort reduction")

    print("\n" + "=" * 65)

# --- 4. VISUALIZATION ---


def plot_results(results_dict):
    fig = plt.figure(figsize=(15, 11))
    fig.suptitle("ReposiTUm Workflow — Impact of Solution Packages on Active Touch Time",
                 fontsize=16, fontweight="bold")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    colors = {"AS-IS Baseline": "#e74c3c", "Procedural Streamlining": "#f39c12",
              "Expert Operations": "#3498db", "Maximum Automation": "#27ae60"}

    # 1. Top Panel: Overlapping Histograms (Density)
    ax1 = fig.add_subplot(gs[0, :])
    for name, data in results_dict.items():
        ax1.hist(data, bins=50, alpha=0.5,
                 color=colors[name], label=name, density=True)
        ax1.axvline(statistics.mean(data),
                    color=colors[name], linestyle="--", lw=1.5)
    ax1.set_title(
        "Density Distribution Across All Trials (Dashed line = Mean)")
    ax1.set_xlabel("Minutes per Publication (Active Human Effort)")
    ax1.set_ylabel("Density")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # 2. Bottom Left: Box Plot (Notched)
    ax2 = fig.add_subplot(gs[1, 0])
    labels = list(results_dict.keys())
    data_lists = list(results_dict.values())
    bp = ax2.boxplot(data_lists, tick_labels=labels,
                     patch_artist=True, notch=True)

    for patch, name in zip(bp["boxes"], labels):
        patch.set_facecolor(colors[name])
        patch.set_alpha(0.7)

    ax2.set_title("Box Plot (Notch = 95% CI of median)")
    ax2.set_ylabel("Total Active Touch Time (Minutes)")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    # 3. Bottom Right: CDF (Predictability)
    ax3 = fig.add_subplot(gs[1, 1])
    for name, data in results_dict.items():
        sorted_s = np.sort(data)
        cdf = np.arange(1, len(sorted_s) + 1) / len(sorted_s)
        ax3.plot(sorted_s, cdf, color=colors[name], label=name, lw=2)

    ax3.axhline(0.95, color="grey", linestyle=":", lw=1, label="95th pct")
    ax3.set_title("Cumulative Distribution Function (CDF)")
    ax3.set_xlabel("Minutes per Publication (Active Human Effort)")
    ax3.set_ylabel("Cumulative Probability")
    ax3.legend()
    ax3.grid(linestyle="--", alpha=0.5)

    try:
        plt.savefig("simulation_results.pdf", format="pdf", dpi=300)
        print("Charts saved → simulation_results.pdf")
    except Exception as e:
        print(f"Could not save PDF: {e}")

    plt.show()

# --- 5. EXECUTION ---


if __name__ == "__main__":
    random.seed(42)
    results = {
        "AS-IS Baseline": [sim_asis() for _ in range(N_TRIALS)],
        "Procedural Streamlining": [sim_streamlined() for _ in range(N_TRIALS)],
        "Expert Operations": [sim_expert_operations() for _ in range(N_TRIALS)],
        "Maximum Automation": [sim_max_automation() for _ in range(N_TRIALS)]
    }
    print_report(results)
    plot_results(results)
