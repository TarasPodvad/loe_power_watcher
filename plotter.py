import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from alerts import parse_ranges
from config import PLOT_FILE, now


def _segments(start, end):
    """Split a range crossing midnight (e.g. 22:00-02:00) into same-day pieces."""
    if end < start:
        return [(start, 24 * 60), (0, end)]
    return [(start, end)]


def generate_plot(lines, dates):
    fig, axes = plt.subplots(len(lines), 1, figsize=(12, 2.5 * len(lines)))
    if len(lines) == 1:
        axes = [axes]

    for ax, line, date_str in zip(axes, lines, dates):
        ax.barh(y=0, width=24, left=0, height=0.3, color="green")
        for start, end in parse_ranges(line):
            for s, e in _segments(start, end):
                ax.barh(y=0, width=(e - s) / 60, left=s / 60, height=0.3, color="red")

        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25))
        ax.set_yticks([])
        title = line.split("Електроенерг")[0].strip()
        ax.set_title(f"{title} — {date_str}", fontsize=18, fontweight="bold")
        ax.tick_params(axis="x", labelsize=14)

    fig.text(0.95, 0.98, now().strftime("%d-%m-%Y %H:%M"), ha="right", va="top")
    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close(fig)
