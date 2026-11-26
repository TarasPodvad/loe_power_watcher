"""Phone-friendly schedule chart: one row per day, outages labelled with their times."""
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from alerts import parse_ranges
from config import GROUP_NAME, PLOT_FILE, now

# colors: status "critical" for outages, quiet tint for power-on, neutral inks
OFF = "#dc3c3d"
ON = "#d9efdc"
INK = "#191919"
INK_2 = "#666666"
GRID = "#e6e6e6"
SURFACE = "#ffffff"
GOOD_TEXT = "#0a7d1c"

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
plt.rcParams["font.family"] = "DejaVu Sans"  # bundled with matplotlib, has Cyrillic


def _segments(start, end):
    """Minutes -> same-day pieces (a 22:00-02:00 range is split at midnight)."""
    if end < start:
        return [(start, 24 * 60), (0, end)]
    return [(start, end)]


def _hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def _duration(minutes):
    h, m = divmod(minutes, 60)
    return f"{h} год" + (f" {m} хв" if m else "")


def _bar(ax, x0, x1, y, h, color):
    ax.add_patch(FancyBboxPatch((x0, y - h / 2), x1 - x0, h,
                                boxstyle="round,pad=0,rounding_size=0.12",
                                linewidth=0, facecolor=color, mutation_aspect=1 / 3))


def generate_plot(schedule):
    """schedule: [(date, line), ...] for one group."""
    n = len(schedule)
    fig, axes = plt.subplots(n, 1, figsize=(7.2, 0.9 + 1.55 * n), dpi=150, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    current = now()

    for ax, (day, line) in zip(axes[:, 0], schedule):
        segs = sorted(s for a, b in parse_ranges(line) for s in _segments(a, b))
        off_min = sum(b - a for a, b in segs)

        ax.set_xlim(0, 24)
        ax.set_ylim(-0.9, 1.25)
        ax.axis("off")

        # day header
        ax.text(0, 1.2, f"{WEEKDAYS[day.weekday()]}, {day:%d.%m}", ha="left", va="top",
                fontsize=13, fontweight="bold", color=INK)
        summary, col = (f"без світла {_duration(off_min)}", OFF) if off_min else ("світло весь день", GOOD_TEXT)
        ax.text(24, 1.2, summary, ha="right", va="top", fontsize=11, color=col, fontweight="bold")

        # 3-hour grid + ticks
        for hr in range(0, 25, 3):
            ax.plot([hr, hr], [-0.28, 0.28], color=GRID, lw=1, zorder=0)
            ax.text(hr, -0.42, f"{hr:02d}", ha="center", va="top", fontsize=8.5, color=INK_2)

        # power-on base, then outages with a 2px-ish surface gap
        _bar(ax, 0, 24, 0, 0.42, ON)
        last_label_end = -99
        for a, b in segs:
            x0, x1 = a / 60, b / 60
            _bar(ax, x0 + 0.03, x1 - 0.03, 0, 0.42, OFF)
            label = f"{_hhmm(a)}–{_hhmm(b)}"
            cx = min(max((x0 + x1) / 2, 1.6), 22.4)
            # stagger labels that would collide (short neighbouring outages)
            y = 0.33 if cx - 1.6 > last_label_end else 0.62
            ax.text(cx, y, label, ha="center", va="bottom", fontsize=9.5, color=INK, fontweight="bold")
            last_label_end = cx + 1.6 if y == 0.33 else last_label_end


    fig.text(0.03, 0.995, GROUP_NAME.rstrip("."), ha="left", va="top", fontsize=10, color=INK_2)
    fig.text(0.97, 0.995, f"оновлено {current:%d.%m %H:%M}", ha="right", va="top", fontsize=9, color=INK_2)
    fig.subplots_adjust(left=0.04, right=0.96, top=1 - 0.32 / (0.9 + 1.55 * n), bottom=0.02, hspace=0.25)
    fig.savefig(PLOT_FILE, facecolor=SURFACE)
    plt.close(fig)
