"""
build_history_timeline.py
--------------------------
Renders the Chapter-2 historical-background figure:
a clean horizontal milestone timeline of Uzbekistan's power sector, 1920s -> 2026.

IMPORTANT: this figure is HISTORICAL BACKGROUND compiled from SECONDARY SOURCES.
Pre-1990 milestones are NOT part of the project dataset. Plant capacities shown are
nameplate-at-commissioning from secondary literature (post-1940 only), used to convey
the hydro-then-gas scale shift, not a continuous data series.

Output: outputs/history_timeline_uzbekistan.png
"""
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)

# ── visual language (matches NB02 figures) ───────────────────────────────────
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
C_GREY   = "#374151"
C_LGREY  = "#9ca3af"
C_HYDRO  = "#2c6e9e"   # hydro / thermal palette from NB02 TECH dict
C_THERM  = "#b5612e"
C_LINE   = "#111827"

# ── era bands: (start, end, label, tint) — sequential, non-overlapping ────────
eras = [
    (1925, 1948, "Soviet electrification",                        "#f3f4f6"),
    (1948, 1968, "Hydro build-out",                               "#e9f1f6"),
    (1968, 1991, "Gas-thermal backbone &\nCentral Asia Power System (Tashkent hub)", "#f7efe8"),
    (1991, 2009, "Independence ·\nstate monopoly",                "#f3f4f6"),
    (2009, 2018, "National\nself-reliance",                       "#eef2f4"),
    (2018, 2027, "Reform &\ntransition",                          "#e9f6ef"),
]

# ── milestones: (year, label, side(+above/-below), capacity_MW or None, colour) ─
milestones = [
    (1932, "First Tashkent-area\nstations",                          +1, None, C_GREY),
    (1953, "Farhad HPP",                                             -1, 126,  C_HYDRO),
    (1972, "Charvak HPP",                                            +1, 600,  C_HYDRO),
    (1981, "Syrdarya TPP\n(first unit 1963)",                        -1, 3215, C_THERM),
    (1991, "Independence;\nUzbekenergo monopoly",                    +1, None, C_GREY),
    (2009, "Exit from Central\nAsia Power System",                   -1, None, C_GREY),
    (2019, "Renewable Energy Law (2018)\n& Uzbekenergo unbundled",   +1, None, C_GREY),
    (2024, "Transition underway →",                             -1, None, C_GREY),
]

fig, ax = plt.subplots(figsize=(13, 4.4))
X0, X1 = 1922, 2030
ax.set_xlim(X0, X1)
ax.set_ylim(-1.25, 1.30)

# era bands + band labels
for s, e, lab, tint in eras:
    ax.axvspan(s, e, color=tint, zorder=0)
    ax.axvline(e, color="white", lw=1.4, zorder=1)
    ax.text((s + e) / 2, 1.12, lab, ha="center", va="center",
            fontsize=8.6, color=C_GREY, fontweight="bold", linespacing=1.15, zorder=3)

# main timeline spine
ax.plot([1925, 2027], [0, 0], color=C_LINE, lw=2.2, zorder=2, solid_capstyle="round")

# decade ticks
for yr in [1930, 1950, 1970, 1990, 2010]:
    ax.plot([yr, yr], [-0.045, 0.045], color=C_GREY, lw=1.0, zorder=3)
    ax.text(yr, -0.16, str(yr), ha="center", va="top", fontsize=8, color=C_LGREY)

def cap_size(mw):
    # area scaling, compressed so the largest marker stays readable
    return 26 + 6.2 * (mw ** 0.5)

# milestones
for yr, lab, side, mw, col in milestones:
    stem_top = 0.30 * side
    ax.plot([yr, yr], [0, stem_top], color=C_LGREY, lw=1.0, zorder=2)
    if mw is None:
        ax.scatter([yr], [0], s=34, color=col, edgecolor="white", lw=1.0, zorder=4)
        cap_txt = ""
    else:
        ax.scatter([yr], [0], s=cap_size(mw), color=col, edgecolor="white",
                   lw=1.2, zorder=4, alpha=0.92)
        cap_txt = f"\n~{mw:,} MW".replace("~126", "126")
    va = "bottom" if side > 0 else "top"
    y_lab = stem_top + (0.06 * side)
    ax.text(yr, y_lab, f"$\\bf{{{yr}}}$\n{lab}{cap_txt}", ha="center", va=va,
            fontsize=8.3, color=C_GREY, linespacing=1.18, zorder=5)

# capacity note (markers are labelled inline with their MW)
ax.text((1925 + 2027) / 2, -1.06,
        "Marker size ∝ nameplate capacity at commissioning  ·  hydro (blue) → gas-thermal (brown)",
        ha="center", va="center", fontsize=7.8, color=C_LGREY)

# title + source
ax.set_title("Uzbekistan's power sector, 1920s → 2026 — a milestone history",
             fontsize=14, fontweight="bold", loc="left", pad=16, color=C_LINE)
fig.text(0.012, 0.018,
         "Historical context compiled from secondary sources; pre-1990 milestones are not part of the project dataset. "
         "Plant capacities are nameplate-at-commissioning (post-1940).",
         fontsize=8, color=C_LGREY)

for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])

fig.subplots_adjust(left=0.012, right=0.992, top=0.84, bottom=0.10)
dest = OUT / "history_timeline_uzbekistan.png"
fig.savefig(dest, dpi=150, bbox_inches="tight", facecolor="white")
print(f"saved -> {dest}")
