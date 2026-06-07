"""
build_forecast_scoreboard.py
----------------------------
Renders the Chapter-4 (Methodology) headline figure: the demand-model scoreboard
on the single honest 2019-2023 hold-out, contrasting the EX-ANTE error (each model
forecasts its own drivers and feeds the demand lag recursively) against the
CONDITIONAL backcast (model fed the observed drivers) kept only as a reference.

The figure carries the chapter's central claim visually:
  * single-country models cluster at ~9-10% ex-ante MAPE with NEGATIVE hold-out R^2,
  * the pooled Central-Asia models lead at ~6% with POSITIVE R^2,
  * every model's conditional backcast (~4-5%) is the optimistic bound, not the headline.

Every value is READ from the notebook's exported scoreboard (read-only); nothing is
hard-coded, so the figure cannot drift from the model run.

Input (read-only):  data/processed/forecast_scoreboard_advanced.csv
Output:             outputs/forecast_scoreboard_exante.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT  = ROOT / "outputs"; OUT.mkdir(exist_ok=True)

# ── visual language (matches NB02 / Ch2-Ch3 figures) ─────────────────────────
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
C_SINGLE = "#b5612e"   # brown  — single-country family
C_POOL   = "#2c6e9e"   # blue   — pooled family (validation)
C_GREY   = "#374151"
C_LGREY  = "#9ca3af"
C_REF    = "#9ca3af"   # ghosted conditional reference
C_POS    = "#2f8f5b"   # green  — positive R^2
C_NEG    = "#b91c1c"   # red    — negative R^2

# ── load (read-only) ─────────────────────────────────────────────────────────
sb = pd.read_csv(DATA / "forecast_scoreboard_advanced.csv")

# short, English-only labels for the report figure (notebook labels are terse codes)
LABELS = {
    "Ridge CV-alpha (UZB, minimal)":            "Ridge — Uzbekistan (minimal)",
    "Ridge CV-alpha (UZB, extended + UzStat)":  "Ridge — Uzbekistan (extended)",
    "BayesianRidge (UZB, minimal)":             "Bayesian Ridge — Uzbekistan (minimal)",
    "BayesianRidge (UZB, extended)":            "Bayesian Ridge — Uzbekistan (extended)",
    "Pooled Ridge CV-alpha (4 CA + FE)":        "Pooled Ridge — 4 Central-Asia + fixed effects",
    "Pooled BayesianRidge (4 CA + FE)":         "Pooled Bayesian Ridge — 4 Central-Asia + fixed effects",
}
DEPLOYED = "BayesianRidge (UZB, extended)"   # the single-country model that carries the headline path

sb["family"]   = np.where(sb["model"].str.startswith("Pooled"), "pooled", "single")
sb["label"]    = sb["model"].map(LABELS).fillna(sb["model"])
# order: single-country block first (worst at top), pooled block last (best) → reads top-to-bottom worst→best
sb = sb.sort_values(["family", "exante_mape%"], ascending=[True, False]).reset_index(drop=True)

print("Scoreboard rows (as plotted):")
for _, r in sb.iterrows():
    print(f"  {r['label']:54s} ex-ante {r['exante_mape%']:5.1f}%  R2={r['exante_r2']:+.2f}  cond {r['conditional_mape% [ref]']:.1f}%")

# ── plot ─────────────────────────────────────────────────────────────────────
n = len(sb)
fig, ax = plt.subplots(figsize=(12.2, 5.8))
y = np.arange(n)[::-1]   # first row at top

# Lewis interpretive bands (faint): <10% "high accuracy", 10-20% "good"
ax.axvspan(0, 10, color="#ecfdf5", zorder=0)
ax.axvspan(10, 20, color="#fffbeb", zorder=0)
ax.axvline(10, color="#d1d5db", lw=1.0, ls=(0, (4, 3)), zorder=1)
ax.text(10, n - 0.3, "  Lewis 10% — high-accuracy threshold", ha="left", va="center",
        fontsize=7.6, color=C_LGREY, style="italic", zorder=4)

for i, (_, r) in enumerate(sb.iterrows()):
    yi  = y[i]
    col = C_POOL if r["family"] == "pooled" else C_SINGLE
    # ex-ante bar (the headline)
    ax.barh(yi, r["exante_mape%"], height=0.56, color=col,
            alpha=0.92, edgecolor=col, linewidth=1.2, zorder=3)
    # conditional backcast — ghosted hollow marker + connector (the optimistic reference)
    ax.plot([r["conditional_mape% [ref]"], r["exante_mape%"]], [yi, yi],
            color=C_REF, lw=1.0, ls=(0, (2, 2)), zorder=2)
    ax.scatter([r["conditional_mape% [ref]"]], [yi], s=46, facecolor="white",
               edgecolor=C_GREY, linewidth=1.3, zorder=4)
    # R^2 chip at the bar end
    r2 = r["exante_r2"]
    r2col = C_POS if r2 > 0 else C_NEG
    ax.text(r["exante_mape%"] + 0.25, yi, f"R² = {r2:+.2f}", ha="left", va="center",
            fontsize=8.4, color=r2col, fontweight="bold", zorder=5)
    # model label (left, inside a clean margin)
    lab = r["label"]
    if r["model"] == DEPLOYED:
        lab += "  ◀ deployed"
    ax.text(0.18, yi, lab, ha="left", va="center", fontsize=9, color=C_GREY, zorder=6,
            bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="none", alpha=0.80))

ax.set_xlim(0, 13.6)
ax.set_ylim(-0.7, n - 0.3)
ax.set_yticks([])
ax.set_xlabel("Hold-out MAPE, 2019–2023  (%)", fontsize=9.5, color=C_GREY)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(C_LGREY)
ax.tick_params(axis="x", colors=C_GREY, length=0)

# family brace labels on the right
ax.text(13.45, np.mean(y[sb["family"].values == "single"]), "single-country\n(deployed family)",
        ha="right", va="center", fontsize=8.2, color=C_SINGLE, fontweight="bold", linespacing=1.1)
ax.text(13.45, np.mean(y[sb["family"].values == "pooled"]), "pooled\n(validation)",
        ha="right", va="center", fontsize=8.2, color=C_POOL, fontweight="bold", linespacing=1.1)

# legend
handles = [
    Line2D([0], [0], marker="s", color="none", markerfacecolor=C_SINGLE, markeredgecolor=C_SINGLE,
           markersize=10, label="ex-ante MAPE — single-country"),
    Line2D([0], [0], marker="s", color="none", markerfacecolor=C_POOL, markeredgecolor=C_POOL,
           markersize=10, label="ex-ante MAPE — pooled"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=C_GREY,
           markersize=9, label="conditional backcast (reference)"),
]
ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, -0.205),
          ncol=3, frameon=False, fontsize=8.2, handletextpad=0.4, columnspacing=1.3)

ax.set_title("Ex-ante is the honest headline — demand-model hold-out error",
             fontsize=14, fontweight="bold", loc="left", pad=12, color="#111827")
fig.text(0.012, 0.012,
         "Same 2019–2023 hold-out across all models. Bars show ex-ante error (each model forecasts its own drivers and feeds the demand "
         "lag recursively); hollow markers show the conditional backcast on observed drivers, kept only as the optimistic reference. "
         "Single-country models post negative hold-out R² against the post-2018 structural break; the pooled models turn R² positive.",
         fontsize=7.6, color=C_LGREY)

fig.subplots_adjust(left=0.012, right=0.99, top=0.89, bottom=0.17)
dest = OUT / "forecast_scoreboard_exante.png"
fig.savefig(dest, dpi=150, bbox_inches="tight", facecolor="white")
print(f"saved -> {dest}")
