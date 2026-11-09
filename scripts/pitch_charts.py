"""Two charts for the 11.11.2026 pitch (docs/pitch-draft.md), from the real-arm data in data/:

  docs/pitch/shoulder_before_after.png   the shoulder: what the operator asked vs what the safety layer sent,
                                         before the fix (run 1) and after it (run 4)
  docs/pitch/held_share_before_after.png share of following time the safety layer held each joint, before vs after

Run (matplotlib is not one of the app's requirements):
  uv run --no-project --with pandas==3.1.0 --with pyarrow==26.0.0 --with matplotlib python scripts/pitch_charts.py

"Held" = while following, the safety layer sent the same goal as the row before or after while the leader was
elsewhere. Counted this way, the numbers match the robot's own count of held cycles (Dummy,
measurements/2026-11-09/analysis.md).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "pitch"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
LEADER, SENT, HELD = "#2a78d6", "#eb6834", "#d03b3b"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 12, "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "legend.frameon": False,
})


def held(run: pd.DataFrame, joint: str) -> np.ndarray:
    a, leader = run[f"action.{joint}"].to_numpy(), run[f"leader.{joint}"].to_numpy()
    same = np.abs(np.diff(a)) < 0.005
    const = np.r_[False, same] | np.r_[same, False]
    return (run["mode"].to_numpy() == "following") & const & (np.abs(leader - a) > 0.005)


def spans(t: np.ndarray, mask: np.ndarray):
    i = 0
    while i < len(mask):
        if mask[i]:
            k = i
            while k + 1 < len(mask) and mask[k + 1]:
                k += 1
            yield t[i], t[k] + 1 / 30
            i = k + 1
        else:
            i += 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(ROOT / "data" / "dummy_real_teleop_2026-11-09.parquet")
    runs = {r: g.reset_index(drop=True) for r, g in df.groupby("run_index")}

    # 1. the shoulder before and after
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, (k, window, title) in zip(axs, ((0, (190, 262), "Before the fix (run 1)"),
                                             (3, (25, 34), "After the fix (run 4)"))):
        r = runs[k]
        w = r[(r.t >= window[0]) & (r.t <= window[1])]
        for t0, t1 in spans(w.t.to_numpy(), held(w, "shoulder_lift")):
            ax.axvspan(t0, t1, color=HELD, alpha=0.12, lw=0)
        ax.plot(w.t, w["leader.shoulder_lift"], color=LEADER, lw=2.2, label="what I asked (leader arm)")
        ax.plot(w.t, w["action.shoulder_lift"], color=SENT, lw=2.2, label="what the safety layer sent")
        ax.set_title(title, loc="left", fontsize=14, color=INK)
        ax.set_xlabel("seconds")
    axs[0].set_ylabel("shoulder angle (deg)")
    axs[0].annotate("the safety layer's goal:\nstuck at -109 deg the whole run", (200, -109.45), xytext=(191, 25),
                    fontsize=12, color=INK2, arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
    axs[1].annotate("+77 deg in 3.2 s;\nthe two lines are one: it follows", (31.7, -23.2), xytext=(25.2, 25),
                    fontsize=12, color=INK2, arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
    handles, labels = axs[0].get_legend_handles_labels()
    handles.append(plt.Rectangle((0, 0), 1, 1, color=HELD, alpha=0.12))
    labels.append("joint locked by the stall rule")
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=11, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT / "shoulder_before_after.png", dpi=150)
    plt.close(fig)

    # 2. share of following time each joint was held, before (runs 1-3) vs after (runs 4-5)
    share = {}
    for name, ks in (("before", (0, 1, 2)), ("after", (3, 4))):
        fol = sum((runs[k]["mode"] == "following").sum() for k in ks)
        share[name] = [100 * sum(held(runs[k], j).sum() for k in ks) / fol for j in JOINTS]
    fig, ax = plt.subplots(figsize=(11, 4.4))
    x, w = np.arange(len(JOINTS)), 0.36
    for i, (name, color, label) in enumerate((("before", SENT, "before the fix (3 runs, 11.3 min)"),
                                              ("after", LEADER, "after the fix (2 runs, 4.4 min)"))):
        bars = ax.bar(x + (i - 0.5) * (w + 0.03), share[name], w, color=color, label=label)
        for b, v in zip(bars, share[name]):
            if v >= 1:
                ax.annotate(f"{v:.0f}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                            ha="center", fontsize=11, color=INK2)
    ax.set_xticks(x, ["base pan", "shoulder", "elbow", "wrist", "wrist roll", "gripper*"])
    ax.set_ylabel("% of the time the joint\nwas locked")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right", fontsize=11)
    ax.annotate("* the gripper 'locks' when it is fully closed: harmless", (0.0, -0.22), xycoords="axes fraction",
                fontsize=10, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / "held_share_before_after.png", dpi=150)
    plt.close(fig)
    for name in share:
        print(name, {j: round(v, 1) for j, v in zip(JOINTS, share[name])})


if __name__ == "__main__":
    main()
