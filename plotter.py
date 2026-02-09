import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from datetime import datetime
from config import PLOT_FILE
from alerts import parse_ranges

def generate_plot(lines, dates):
    fig, axes = plt.subplots(len(lines), 1, figsize=(12, 2.5*len(lines)))

    if len(lines) == 1:
        axes = [axes]

    for ax, line, date_str in zip(axes, lines, dates):
        ranges = parse_ranges(line)

        ax.barh(y=0, width=24, left=0, height=0.3, color="green")

        for start, end in ranges:
            ax.barh(y=0,
                    width=(end-start)/60,
                    left=start/60,
                    height=0.3,
                    color="red")

        ax.set_xlim(0,24)
        ax.set_xticks(range(0,25))
        ax.set_yticks([])
        ax.set_title(f"{line.split('Електроенергії')[0].strip()} — {date_str}", fontsize=18, fontweight="bold")
        ax.tick_params(axis="x", labelsize=14)

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
    fig.text(0.95, 0.98, timestamp, ha="right", va="top")

    plt.tight_layout()
    plt.savefig(PLOT_FILE)
