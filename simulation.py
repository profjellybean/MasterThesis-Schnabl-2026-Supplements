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
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from rich.text import Text
from rich.rule import Rule

console = Console()

# ---------------------------------------------------------------------------
# 1. CONFIGURATION & PARAMETERS
# ---------------------------------------------------------------------------

N_TRIALS = 10_000

TIME_ASIS_ENTRY = (5, 15, 30)
TIME_ASIS_REWORK = (2, 5, 10)
TIME_RIS_CHECK = (10, 15, 25)
TIME_LIB_CHECK = (4, 8, 20)
TIME_FAC_CHECK = (1, 3, 10)

PROBS_REJECT = [0.0646, 0.0385, 0.0058]

TIME_STREAMLINE_ENTRY = (5, 15, 30)
TIME_1STEP_VALIDATION = (6, 10, 22)
TIME_EXPERT_ENTRY = (3, 7, 10)
TIME_EXPERT_VALIDATION = (6, 12, 26)
TIME_MAX_AUTO_ENTRY = (1, 3, 5)
TIME_MAX_AUTO_VALIDATION = (5, 10, 15)
TIME_SYS_RELEASE = (0.1, 0.1, 0.1)

PROB_DOI_AVAILABLE = 0.43

# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------


def _tri(params: tuple) -> float:
    return random.triangular(*params)


def _asis_rejection_loop() -> tuple[float, float]:
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
    entry = _tri(TIME_ASIS_ENTRY)
    val, rework = _asis_rejection_loop()
    return entry + val + rework + _tri(TIME_SYS_RELEASE)


def sim_streamlined() -> float:
    return (
        _tri(TIME_STREAMLINE_ENTRY)
        + _tri(TIME_1STEP_VALIDATION)
        + _tri(TIME_SYS_RELEASE)
    )


def sim_expert_operations() -> float:
    return (
        _tri(TIME_EXPERT_ENTRY)
        + _tri(TIME_EXPERT_VALIDATION)
        + _tri(TIME_SYS_RELEASE)
    )


def sim_max_automation() -> float:
    if random.random() <= PROB_DOI_AVAILABLE:
        return _tri(TIME_MAX_AUTO_ENTRY) + _tri(TIME_MAX_AUTO_VALIDATION) + _tri(TIME_SYS_RELEASE)
    else:
        return _tri(TIME_EXPERT_ENTRY) + _tri(TIME_EXPERT_VALIDATION) + _tri(TIME_SYS_RELEASE)

# ---------------------------------------------------------------------------
# 4. REPORTING
# ---------------------------------------------------------------------------


def _confidence_interval(data: list[float]) -> tuple[float, float]:
    n = len(data)
    mean = statistics.mean(data)
    margin = 1.96 * statistics.stdev(data) / math.sqrt(n)
    return mean - margin, mean + margin


VARIANT_STYLES = {
    "AS-IS Baseline":          ("red",    "📋"),
    "Procedural Streamlining": ("yellow", "⚙️ "),
    "Expert Operations":       ("blue",   "👤"),
    "Maximum Automation":      ("green",  "🤖"),
}


def _reduction_bar(pct: float, width: int = 20) -> str:
    """ASCII progress bar for reduction percentage."""
    filled = round(pct / 100 * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {pct:.1f}%"


def print_report(results_dict: dict[str, list[float]]) -> None:
    baseline_mean = statistics.mean(results_dict["AS-IS Baseline"])

    console.print()
    console.print(Panel.fit(
        f"[bold white]ReposiTUm — Monte Carlo Simulation[/bold white]\n"
        f"[dim]{N_TRIALS:,} independent trials · Unit: active touch-time (minutes)[/dim]",
        border_style="bright_white",
        padding=(0, 2),
    ))
    console.print()

    # ── Main stats table ────────────────────────────────────────────────────
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white",
        border_style="bright_black",
        padding=(0, 1),
        title="[bold]Simulation Results by Variant[/bold]",
        title_style="white",
    )

    table.add_column("Variant",          style="bold",         min_width=24)
    table.add_column("Mean",             justify="right",      min_width=9)
    table.add_column("Median",           justify="right",      min_width=9)
    table.add_column("Std Dev",          justify="right",      min_width=9)
    table.add_column("95th pct",         justify="right",      min_width=9)
    table.add_column("95% CI",           justify="center",     min_width=18)

    for name, data in results_dict.items():
        color, icon = VARIANT_STYLES[name]
        mean_val = statistics.mean(data)
        median = statistics.median(data)
        std = statistics.stdev(data)
        p95 = np.percentile(data, 95)
        ci_lo, ci_hi = _confidence_interval(data)

        table.add_row(
            Text(f"{icon} {name}", style=f"bold {color}"),
            Text(f"{mean_val:.2f} min",  style=color),
            Text(f"{median:.2f} min",    style="dim"),
            Text(f"± {std:.2f}",         style="dim"),
            Text(f"{p95:.2f} min",       style="dim"),
            Text(f"[{ci_lo:.2f}, {ci_hi:.2f}]", style="dim"),
        )

    console.print(table)
    console.print()

    # ── Reduction summary panel ─────────────────────────────────────────────
    rows = []
    for name, data in list(results_dict.items())[1:]:
        color, icon = VARIANT_STYLES[name]
        mean_val = statistics.mean(data)
        reduction = (baseline_mean - mean_val) / baseline_mean * 100
        saved = baseline_mean - mean_val
        rows.append(
            f"[{color}]{icon} {name:<26}[/{color}]"
            f"[white]{mean_val:5.1f} min[/white]  "
            f"[{color}]−{saved:.1f} min saved[/{color}]  "
            f"[bold {color}]−{reduction:.1f}%[/bold {color}]"
        )

    console.print(Panel(
        "\n".join(rows),
        title="[bold white]Effort Reduction Summary[/bold white]",
        border_style="bright_black",
        padding=(0, 2),
    ))
    console.print()


def print_labor_breakdown(means_dict: dict) -> None:
    """Pretty-print the entry/validation split."""

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white",
        border_style="bright_black",
        padding=(0, 1),
        title="[bold]Labor Composition — Entry vs. Validation[/bold]",
        title_style="white",
    )

    table.add_column("Variant",           style="bold",     min_width=24)
    table.add_column("Researcher Entry",  justify="right",  min_width=18)
    table.add_column("Validator Review",  justify="right",  min_width=18)
    table.add_column("Total",             justify="right",  min_width=10)

    for name, cats in means_dict.items():
        color, icon = VARIANT_STYLES[name]
        entry = cats["Entry"]
        val = cats["Validation"]
        total = entry + val
        share = entry / total * 100

        table.add_row(
            Text(f"{icon} {name}", style=f"bold {color}"),
            Text(f"{entry:.1f} min", style="cyan"),
            Text(f"{val:.1f} min",   style="blue"),
            Text(f"{total:.1f} min", style=f"bold {color}"),
        )

    console.print(table)
    console.print()

# ---------------------------------------------------------------------------
# 5. VISUALISATION (unchanged logic, same output)
# ---------------------------------------------------------------------------


COLORS = {
    "AS-IS Baseline":          "#e74c3c",
    "Procedural Streamlining": "#f39c12",
    "Expert Operations":       "#3498db",
    "Maximum Automation":      "#27ae60",
}


def plot_results(results_dict: dict[str, list[float]]) -> None:
    fig = plt.figure(figsize=(15, 11))
    fig.suptitle(
        "ReposiTUm Workflow — Impact of Solution Packages on Active Touch Time",
        fontsize=16, fontweight="bold",
    )
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, :])
    for name, data in results_dict.items():
        ax1.hist(data, bins=50, alpha=0.5,
                 color=COLORS[name], label=name, density=True)
        ax1.axvline(statistics.mean(data),
                    color=COLORS[name], linestyle="--", lw=1.5)
    ax1.set_title("Density Distribution Across All Trials (dashed = mean)")
    ax1.set_xlabel("Minutes per Publication (Active Human Effort)")
    ax1.set_ylabel("Density")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    ax2 = fig.add_subplot(gs[1, 0])
    labels = list(results_dict.keys())
    filtered_data = [
        [v for v in results_dict[name] if v <= 100] for name in labels
    ]
    bp = ax2.boxplot(filtered_data, tick_labels=labels,
                     patch_artist=True, notch=True)
    for patch, name in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS[name])
        patch.set_alpha(0.7)
    ax2.set_title("Box Plot (notch = 95% CI of median)")
    ax2.set_ylabel("Total Active Touch Time (Minutes)")
    ax2.tick_params(axis="x", labelrotation=15)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

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
        console.print("[dim]  Charts saved → simulation_results.pdf[/dim]")
    except Exception as exc:
        console.print(f"[red]Could not save PDF: {exc}[/red]")


def run_detailed_simulation(n_trials: int = N_TRIALS) -> dict:
    components: dict[str, dict[str, list]] = {
        variant: {"Entry": [], "Validation": []}
        for variant in ("AS-IS Baseline", "Procedural Streamlining",
                        "Expert Operations", "Maximum Automation")
    }

    for _ in range(n_trials):
        # 1. AS-IS Baseline (Fixed: Added rework to Entry, sys_release to Validation)
        entry = _tri(TIME_ASIS_ENTRY)
        val, rework = _asis_rejection_loop()
        components["AS-IS Baseline"]["Entry"].append(entry + rework)
        components["AS-IS Baseline"]["Validation"].append(
            val + _tri(TIME_SYS_RELEASE))

        # 2. Procedural Streamlining (Fixed: Added sys_release)
        components["Procedural Streamlining"]["Entry"].append(
            _tri(TIME_STREAMLINE_ENTRY))
        components["Procedural Streamlining"]["Validation"].append(
            _tri(TIME_1STEP_VALIDATION) + _tri(TIME_SYS_RELEASE))

        # 3. Expert Operations (Fixed: Added sys_release)
        components["Expert Operations"]["Entry"].append(
            _tri(TIME_EXPERT_ENTRY))
        components["Expert Operations"]["Validation"].append(
            _tri(TIME_EXPERT_VALIDATION) + _tri(TIME_SYS_RELEASE))

        # 4. Maximum Automation (Fixed: Added sys_release to both branches)
        if random.random() <= PROB_DOI_AVAILABLE:
            components["Maximum Automation"]["Entry"].append(
                _tri(TIME_MAX_AUTO_ENTRY))
            components["Maximum Automation"]["Validation"].append(
                _tri(TIME_MAX_AUTO_VALIDATION) + _tri(TIME_SYS_RELEASE))
        else:
            components["Maximum Automation"]["Entry"].append(
                _tri(TIME_EXPERT_ENTRY))
            components["Maximum Automation"]["Validation"].append(
                _tri(TIME_EXPERT_VALIDATION) + _tri(TIME_SYS_RELEASE))

    return {
        variant: {cat: statistics.mean(vals) for cat, vals in cats.items()}
        for variant, cats in components.items()
    }


def plot_stacked_bar_chart(means_dict: dict) -> None:
    labels = list(means_dict.keys())
    entry_m = [means_dict[l]["Entry"] for l in labels]
    val_m = [means_dict[l]["Validation"] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.5

    p1 = ax.bar(labels, entry_m, width,
                label="Researcher Entry Time",  color="#34495e")
    p2 = ax.bar(labels, val_m,   width, label="Validator Review Time",   color="#3498db",
                bottom=entry_m)

    ax.set_title("Shift in Labour Composition Across Architectures",
                 fontsize=14, fontweight="bold")
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
    console.print(
        "[dim]  Chart saved → labor_composition_stacked_bar.pdf[/dim]")

# ---------------------------------------------------------------------------
# 6. ENTRY POINT
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    random.seed(42)

    results = {
        "AS-IS Baseline":          [sim_asis() for _ in range(N_TRIALS)],
        "Procedural Streamlining": [sim_streamlined() for _ in range(N_TRIALS)],
        "Expert Operations":       [sim_expert_operations() for _ in range(N_TRIALS)],
        "Maximum Automation":      [sim_max_automation() for _ in range(N_TRIALS)],
    }

    print_report(results)
    plot_results(results)

    console.print()
    random.seed(42)
    detailed_means = run_detailed_simulation(N_TRIALS)
    plot_stacked_bar_chart(detailed_means)

    console.print()
    print_labor_breakdown(detailed_means)
