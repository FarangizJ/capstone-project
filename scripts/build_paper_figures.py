"""
build_paper_figures.py
======================
Regenerate the 12 figures the capstone PAPER embeds, at 300 DPI on the unified
navy / teal / amber palette, into  paper/figures/ .

DESIGN PRINCIPLE — restyle, do not reinvent.
Every figure here ports the *verified* plotting logic from its original
generator (the scripts/build_*.py harnesses and the executed notebook cells) and
reads the SAME data already written to disk (processed CSVs, the research asset
JSON, the hard-coded country polygon). Only three things change versus the
verified figures: (1) palette -> navy/teal/amber via figure_style_for_notebooks,
(2) save DPI -> 300, (3) the two maps are enlarged ~30% for legibility. No
numbers are recomputed and no model is re-fit, so the paper figures cannot drift
from the analysis.

Data provenance per figure is noted in each function's docstring. Nothing is
written outside paper/figures/ (the canonical outputs/ and data/processed/ PNGs
are left untouched).

Run:  python scripts/build_paper_figures.py
"""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon, Patch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from figure_style_for_notebooks import (  # noqa: E402
    apply_style, NAVY, SKY, SKY_DEEP, TEAL, LEAF, AMBER, GOLD, PURPLE, BROWN, WARMGREY,
    INK, GREY, LGREY, PALE, RED, GREEN, NAVY_FILL,
    SCEN, TECH, FUEL, SOURCE, FAMILY,
)

DATA  = ROOT / "data" / "processed"
CLEAN = DATA / "uzstat_clean"
RESEARCH = ROOT / "research" / "uzbekistan-energy"
FIGS  = ROOT / "paper" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

apply_style()
STATUS_EDGE = {"op": "#222", "build": "#444", "plan": "#888"}
_done = []


# ═══════════════════════════════════════════════════════════════════════════
# DNV figure idiom — shared helpers
# Every restyled figure leads with a bold one-line TAKEAWAY (the finding), keeps
# only light horizontal gridlines behind the data, drops the bounding box, labels
# series directly at their endpoints where a legend would otherwise be needed,
# and closes with a thin grey provenance caption. These helpers change ONLY the
# visual treatment — never a plotted value.
# ═══════════════════════════════════════════════════════════════════════════
def dnv_clean(ax, grid="y"):
    """Strip chart-junk: hide top/right/left spines, soften the bottom baseline,
    draw light horizontal gridlines behind the data."""
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LGREY)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(length=0)
    if grid in ("y", "both"):
        ax.grid(axis="y", color=PALE, linewidth=0.8, alpha=0.9)
    if grid in ("x", "both"):
        ax.grid(axis="x", color=PALE, linewidth=0.8, alpha=0.9)
    if grid == "none":
        ax.grid(False)
    ax.set_axisbelow(True)
    return ax


def takeaway(fig, title, sub=None, x=0.012, y=0.985, size=13.5):
    """Bold navy one-line takeaway headline (the finding), with an optional
    lighter grey sub-line beneath. Figure-level so it spans all panels."""
    fig.text(x, y, title, ha="left", va="top", fontsize=size,
             fontweight="bold", color=NAVY)
    if sub:
        fig.text(x, y - 0.060, sub, ha="left", va="top", fontsize=9.3, color=GREY)


def figcap(fig, text, y=0.012, x=0.012, ha="left"):
    """Thin grey provenance caption beneath the figure (the LaTeX float owns the
    'Figure N' number; this line carries only the source/method)."""
    fig.text(x, y, text, ha=ha, va="bottom", fontsize=7.3, color=LGREY)


def end_label(ax, x, y, text, color, dx=7, dy=0, size=9, weight="bold", va="center"):
    """Direct end-of-series label that replaces a legend entry (DNV idiom)."""
    ax.annotate(text, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                color=color, fontsize=size, fontweight=weight, va=va, ha="left",
                annotation_clip=False)


def _save(fig, name):
    dest = FIGS / name
    fig.savefig(dest, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    _done.append(name)
    print(f"  saved -> paper/figures/{name}")


# ── country base layer (verbatim polygon from NB02 cell 22) ──────────────────
COUNTRY = [[66.519,37.363],[66.546,37.975],[65.216,38.403],[64.17,38.892],[63.518,39.363],
 [62.374,40.054],[61.883,41.085],[61.547,41.266],[60.466,41.22],[60.083,41.425],[59.976,42.223],
 [58.629,42.752],[57.787,42.171],[56.932,41.826],[57.096,41.322],[55.968,41.309],[55.929,44.996],
 [58.503,45.587],[58.69,45.5],[60.24,44.784],[61.058,44.406],[62.013,43.504],[63.186,43.65],
 [64.901,43.728],[66.098,42.998],[66.023,41.995],[66.511,41.988],[66.714,41.168],[67.986,41.136],
 [68.26,40.662],[68.632,40.669],[69.07,41.384],[70.389,42.081],[70.962,42.266],[71.259,42.168],
 [70.42,41.52],[71.158,41.144],[71.87,41.393],[73.055,40.866],[71.775,40.146],[71.014,40.244],
 [70.601,40.219],[70.458,40.496],[70.667,40.96],[69.329,40.728],[69.012,40.086],[68.536,39.533],
 [67.701,39.58],[67.442,39.14],[68.176,38.902],[68.392,38.157],[67.83,37.145],[67.076,37.356],
 [66.519,37.363]]


def draw_country(ax, fill="#faf6ec", edge="#7a6a4a", lw=1.6):
    poly = Polygon(COUNTRY, closed=True, facecolor=fill, edgecolor=edge,
                   linewidth=lw, zorder=1)
    ax.add_patch(poly)
    ax.set_xlim(55.5, 73.5)
    ax.set_ylim(36.8, 46.0)
    ax.set_aspect(1.0 / np.cos(np.radians(41.5)))
    ax.set_xticks(np.arange(56, 74, 4))
    ax.set_yticks(np.arange(38, 46, 2))
    ax.tick_params(colors="#666", labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#aaa")
    ax.grid(alpha=0.18, linestyle=":", zorder=0)
    return ax


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2.1 — milestone history timeline   (port of build_history_timeline.py)
# ═══════════════════════════════════════════════════════════════════════════
def fig_history_timeline():
    C_HYDRO, C_THERM = NAVY, TECH["thermal"]["color"]
    eras = [
        (1925, 1948, "Soviet electrification", "#f3f4f6"),
        (1948, 1968, "Hydro build-out", "#e9f1f6"),
        (1968, 1991, "Gas-thermal backbone &\nCentral Asia Power System (Tashkent hub)", "#f7efe8"),
        (1991, 2009, "Independence ·\nstate monopoly", "#f3f4f6"),
        (2009, 2018, "National\nself-reliance", "#eef2f4"),
        (2018, 2027, "Reform &\ntransition", "#e9f6ef"),
    ]
    milestones = [
        (1932, "First Tashkent-area\nstations", +1, None, GREY),
        (1953, "Farhad HPP", -1, 126, C_HYDRO),
        (1972, "Charvak HPP", +1, 600, C_HYDRO),
        (1981, "Syrdarya TPP\n(first unit 1963)", -1, 3215, C_THERM),
        (1991, "Independence;\nUzbekenergo monopoly", +1, None, GREY),
        (2009, "Exit from Central\nAsia Power System", -1, None, GREY),
        (2019, "Renewable Energy Law (2018)\n& Uzbekenergo unbundled", +1, None, GREY),
        (2024, "Transition underway →", -1, None, GREY),
    ]
    fig, ax = plt.subplots(figsize=(13, 4.4))
    ax.set_xlim(1922, 2030); ax.set_ylim(-1.25, 1.30)
    for s, e, lab, tint in eras:
        ax.axvspan(s, e, color=tint, zorder=0)
        ax.axvline(e, color="white", lw=1.4, zorder=1)
        ax.text((s + e) / 2, 1.12, lab, ha="center", va="center",
                fontsize=8.6, color=GREY, fontweight="bold", linespacing=1.15, zorder=3)
    ax.plot([1925, 2027], [0, 0], color=INK, lw=2.2, zorder=2, solid_capstyle="round")
    for yr in [1930, 1950, 1970, 1990, 2010]:
        ax.plot([yr, yr], [-0.045, 0.045], color=GREY, lw=1.0, zorder=3)
        ax.text(yr, -0.16, str(yr), ha="center", va="top", fontsize=8, color=LGREY)
    cap_size = lambda mw: 26 + 6.2 * (mw ** 0.5)
    for yr, lab, side, mw, col in milestones:
        stem_top = 0.30 * side
        ax.plot([yr, yr], [0, stem_top], color=LGREY, lw=1.0, zorder=2)
        if mw is None:
            ax.scatter([yr], [0], s=34, color=col, edgecolor="white", lw=1.0, zorder=4)
            cap_txt = ""
        else:
            ax.scatter([yr], [0], s=cap_size(mw), color=col, edgecolor="white",
                       lw=1.2, zorder=4, alpha=0.92)
            cap_txt = f"\n~{mw:,} MW"
        va = "bottom" if side > 0 else "top"
        ax.text(yr, stem_top + 0.06 * side, f"$\\bf{{{yr}}}$\n{lab}{cap_txt}",
                ha="center", va=va, fontsize=8.3, color=GREY, linespacing=1.18, zorder=5)
    ax.text((1925 + 2027) / 2, -1.06,
            "Marker size ∝ nameplate capacity at commissioning  ·  hydro (navy) → gas-thermal (brown)",
            ha="center", va="center", fontsize=7.8, color=LGREY)
    ax.set_title("Uzbekistan's power sector, 1920s → 2026 — a milestone history",
                 fontsize=14, fontweight="bold", loc="left", pad=16, color=NAVY)
    fig.text(0.012, 0.018,
             "Historical context compiled from secondary sources; pre-1990 milestones are not part of the project dataset. "
             "Plant capacities are nameplate-at-commissioning (post-1940).",
             fontsize=8, color=LGREY)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    fig.subplots_adjust(left=0.012, right=0.992, top=0.84, bottom=0.10)
    _save(fig, "history_timeline_uzbekistan.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2.2 — fuel-mix evolution 1990-2023 + honest 2022-2024 split
#   (richer recompose of the NB02 energy-mix chart on the navy/teal/amber palette)
# ═══════════════════════════════════════════════════════════════════════════
def fig_energy_mix_evolution():
    """Generation by fuel, fully split — long-run context plus an honest 2024.

    LEFT  — stacked area 1990-2023, six real fuels (gas / coal / oil & other /
            hydro / solar / wind). Each band is a column of master_dataset_core;
            "oil & other fossil" = gen_fossil - gas - coal, so the six bands sum
            exactly to gen_total. The point the area makes is structural: gas is
            about three-quarters of output in every year and the solar/wind
            sliver is still under 1% even at the end of the confirmed record.
    RIGHT — recent split 2022-2024 as stacked bars. 2022 and 2023 are fully
            fuel-split (the split IS known and is shown, not hatched away); 2024
            is its StatSUZ-preliminary 82.0 TWh total with only the known
            solar/wind drawn on top and the thermal+hydro+coal remainder left
            hatched, because its per-fuel split is not yet published by the IEA
            and is not fabricated into shares.

    Data: master_dataset_core.csv (per-fuel to 2023; gen_total_twh_bridged for
    2024) and the UzStat national series (uzb_energy_national.csv) for 2024
    solar/wind output (mln kWh / 1000).
    """
    core = pd.read_csv(DATA / "master_dataset_core.csv"); core["year"] = core["year"].astype(int)
    nat = pd.read_csv(CLEAN / "uzb_energy_national.csv"); nat["year"] = nat["year"].astype(int)

    # on-brand fuel colours: fossils are muted neutrals, the renewable trio is
    # the brand (hydro=navy, solar=amber, wind=teal) so it reads identically here
    # and in the asset/oblast maps.
    C_GAS, C_COAL, C_OIL = "#8C6D46", "#3F3A36", "#B9A88C"
    C_HYD, C_SOL, C_WND = NAVY, AMBER, TEAL

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.4),
                             gridspec_kw={"width_ratios": [1.55, 1.0]})

    # ── LEFT: long-run stacked area, 1990-2023 (six fuels sum to gen_total) ───
    hist = core[(core["year"] >= 1990) & (core["year"] <= 2023)].sort_values("year")
    yr = hist["year"].to_numpy()
    gas = hist["gen_gas_twh"].fillna(0).to_numpy()
    coal = hist["gen_coal_twh"].fillna(0).to_numpy()
    fossil = hist["gen_fossil_twh"].fillna(0).to_numpy()
    oil = np.clip(fossil - gas - coal, 0, None)              # oil & other fossil
    hyd = hist["gen_hydro_twh"].fillna(0).to_numpy()
    sol = hist["gen_solar_twh"].fillna(0).to_numpy()
    wnd = hist["gen_wind_twh"].fillna(0).to_numpy()

    ax = axes[0]
    ax.stackplot(yr, gas, coal, oil, hyd, sol, wnd,
                 colors=[C_GAS, C_COAL, C_OIL, C_HYD, C_SOL, C_WND],
                 labels=["Gas", "Coal", "Oil & other fossil", "Hydropower", "Solar", "Wind"],
                 edgecolor="white", linewidth=0.25)
    ax.set_xlim(1990, 2023); ax.set_ylim(0, 80)
    ax.set_ylabel("TWh")
    ax.set_title("Generation by fuel, 1990–2023", fontsize=11, fontweight="bold", loc="left", color=GREY)
    ax.annotate("Gas — about three-quarters of\ngeneration in every year",
                xy=(2001, 18), fontsize=9.5, color="white", fontweight="bold",
                ha="left", va="center")
    ax.annotate("Solar + wind\nunder 1% (2023)", xy=(2022.7, 73.2), xytext=(2011.5, 62),
                fontsize=8, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1,
                                connectionstyle="arc3,rad=-0.2"))
    ax.legend(loc="upper left", ncol=2, fontsize=8, frameon=False,
              handlelength=1.4, columnspacing=1.2)
    dnv_clean(ax)

    # ── RIGHT: honest recent split, 2022-2024 ────────────────────────────────
    def _g(y, c):
        s = core.loc[core["year"] == y, c]
        return float(s.iat[0]) if len(s) and pd.notna(s.iat[0]) else 0.0

    def _n(y, c):
        s = nat.loc[nat["year"] == y, c]
        return float(s.iat[0]) / 1000 if len(s) and pd.notna(s.iat[0]) else 0.0

    tot24 = _g(2024, "gen_total_twh_bridged")
    sol24, wnd24 = _n(2024, "solar_output_mln_kwh"), _n(2024, "wind_output_mln_kwh")
    rem24 = tot24 - sol24 - wnd24                            # thermal+hydro+coal, split pending

    def _seg(y):
        if y == 2024:
            return [(rem24, C_OIL, "//"), (sol24, C_SOL, None), (wnd24, C_WND, None)]
        g, c, h = _g(y, "gen_gas_twh"), _g(y, "gen_coal_twh"), _g(y, "gen_hydro_twh")
        o = max(_g(y, "gen_fossil_twh") - g - c, 0.0)
        s, w = _g(y, "gen_solar_twh"), _g(y, "gen_wind_twh")
        return [(g, C_GAS, None), (c, C_COAL, None), (o, C_OIL, None),
                (h, C_HYD, None), (s, C_SOL, None), (w, C_WND, None)]

    ax = axes[1]
    yrs2 = [2022, 2023, 2024]
    x = np.arange(len(yrs2))
    for i, y in enumerate(yrs2):
        bottom = 0.0
        for h, col, hatch in _seg(y):
            if h <= 0:
                continue
            ax.bar(i, h, bottom=bottom, color=col, hatch=hatch, edgecolor="white", width=0.62)
            bottom += h
        ax.text(i, bottom + 0.9, f"{bottom:.1f}", ha="center", fontsize=9, fontweight="bold")

    # honest 2024 flags: the hatched pending block, and the sub-6% non-hydro RE sliver
    ax.annotate("Thermal + hydro\nsplit pending IEA", xy=(2, rem24 * 0.5),
                fontsize=7.4, color="white", fontweight="bold", ha="center", va="center")
    re24 = sol24 + wnd24
    ax.annotate(f"Solar + wind ≈ {re24:.1f} TWh\n(under 6%)",
                xy=(2, tot24 - 1.2), xytext=(1.18, tot24 + 6.5),
                fontsize=8, color=TEAL, fontweight="bold", ha="center", va="bottom",
                arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.1,
                                connectionstyle="arc3,rad=0.25"))
    ax.set_xticks(x); ax.set_xticklabels([str(y) for y in yrs2])
    ax.set_ylabel("TWh"); ax.set_ylim(0, tot24 * 1.20)
    ax.set_title("Recent fuel split, 2022–2024", fontsize=11, fontweight="bold", loc="left", color=GREY)
    dnv_clean(ax)

    fig.tight_layout(rect=[0, 0.03, 1, 0.90])
    takeaway(fig,
             "Gas is about three-quarters of generation every year — solar and wind remain under 6% in 2024",
             "Six-fuel generation history (left) and the honest 2022–2024 split (right), TWh")
    figcap(fig,
           "Source: master_dataset_core.csv (per-fuel to 2023; 2024 total StatSUZ preliminary, thermal/hydro split "
           "pending IEA); solar/wind from UzStat national series (uzb_energy_national.csv).")
    _save(fig, "energy_mix_evolution.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2.3 — fleet evolution 4-panel   (port of NB02 cells 20/22/28, +30%)
# ═══════════════════════════════════════════════════════════════════════════
def fig_fleet_evolution():
    ref = json.loads((RESEARCH / "uzbekistan_energy_projects.json").read_text())
    assets = pd.DataFrame(ref)
    assets["mw_eff"] = assets["mw"].fillna(0)

    def marker_size(mw):
        if pd.isna(mw):
            return 30
        return float(np.clip(np.sqrt(mw) * 6, 25, 600))

    def snapshot(ax, year_cut, title):
        draw_country(ax, fill="#faf6ec")
        sub = assets[assets["year"] <= year_cut].sort_values("mw", ascending=False, na_position="last")
        for _, r in sub.iterrows():
            c = TECH[r["tech"]]["color"]
            edge = STATUS_EDGE[r["status"]] if r["year"] <= year_cut else "#bbb"
            s = marker_size(r["mw"])
            ax.scatter(r["lng"], r["lat"], s=s, c=c, edgecolors=edge,
                       linewidths=1.3, alpha=0.92, zorder=4)
            if isinstance(r.get("retired"), str) and r["retired"].strip():
                ax.scatter(r["lng"], r["lat"], s=s * 1.6, facecolor="none",
                           edgecolors="#222", linewidths=0.9, linestyle=(0, (2, 2)), zorder=5)
        for _, r in sub.dropna(subset=["mw"]).nlargest(5, "mw").iterrows():
            ax.annotate(r["name"].split(" (")[0], (r["lng"], r["lat"]),
                        xytext=(7, 5), textcoords="offset points", fontsize=7.5, color="#222",
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#ccc", alpha=0.85),
                        zorder=6)
        n_op = (sub["status"] == "op").sum(); n_b = (sub["status"] == "build").sum()
        n_p = (sub["status"] == "plan").sum(); total = sub["mw"].sum()
        ax.text(0.98, 0.97, f"{title}\n{int(total):,} MW · {n_op} op / {n_b} build / {n_p} plan",
                transform=ax.transAxes, ha="right", va="top", fontsize=10, fontweight="bold", color="#222",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#888", linewidth=0.8))

    fig, axes = plt.subplots(2, 2, figsize=(18.2, 11.7))   # +30% vs 14x9
    fig.patch.set_facecolor("white")
    for ax, yr in zip(axes.flat, [1990, 2010, 2025, 2040]):
        snapshot(ax, yr, f"{yr}")
    leg = [mpatches.Patch(facecolor=v["color"], edgecolor="#222", label=v["label"]) for v in TECH.values()]
    leg += [mpatches.Patch(facecolor="white", edgecolor="#222", label="Operational (solid)"),
            mpatches.Patch(facecolor="white", edgecolor="#222", linestyle="--", label="Under construction"),
            mpatches.Patch(facecolor="white", edgecolor="#222", linestyle=":", label="Planned"),
            mpatches.Patch(facecolor="none", edgecolor="#222", linestyle=(0, (2, 2)), label="Has retired units")]
    fig.legend(handles=leg, loc="lower center", ncol=6, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Uzbekistan's generation fleet, 1990 → 2040 — from a gas-and-hydro core to a diversified build-out",
                 fontsize=14, fontweight="bold", color=NAVY, y=0.995)
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    _save(fig, "fleet_evolution_4panel.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2.4 — oblast resource atlas   (port of NB02 cells 44/46, +30%)
# ═══════════════════════════════════════════════════════════════════════════
def fig_oblast_resource():
    obl = pd.read_csv(DATA / "oblast_atlas.csv")
    fig, axes = plt.subplots(1, 2, figsize=(18.2, 7.8))   # +30% vs 14x6
    fig.patch.set_facecolor("white")

    ax = axes[0]
    draw_country(ax, fill="#fbf5e6")
    sc = ax.scatter(obl["lon"], obl["lat"], s=obl["total_re_mw"] / 4 + 30,
                    c=obl["solar_ghi"], cmap="YlOrRd", edgecolors="#222",
                    linewidths=1.0, alpha=0.92, zorder=4, vmin=1600, vmax=1870)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.75, label="Solar GHI (kWh/m²/yr)")
    cbar.ax.tick_params(labelsize=8)
    for _, r in obl.iterrows():
        ax.annotate(r["oblast"], (r["lon"], r["lat"]), xytext=(6, 5), textcoords="offset points",
                    fontsize=8, color="#222",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#ccc", alpha=0.85), zorder=6)
    ax.set_title("Solar irradiance & total RE capacity by oblast", fontsize=11, fontweight="bold", color=GREY)

    ax = axes[1]
    draw_country(ax, fill="#fbf5e6")
    for tech in ["solar", "wind", "hydro"]:
        sub = obl[obl["dominant"] == tech]
        ax.scatter(sub["lon"], sub["lat"], s=sub["total_re_mw"] / 4 + 30, c=TECH[tech]["color"],
                   edgecolors="#222", linewidths=1.0, alpha=0.92, label=tech.title(), zorder=4)
    for _, r in obl.iterrows():
        ax.annotate(r["oblast"], (r["lon"], r["lat"]), xytext=(6, 5), textcoords="offset points",
                    fontsize=8, color="#222",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#ccc", alpha=0.85), zorder=6)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.set_title("Dominant RE technology by oblast (bubble ∝ MW)", fontsize=11, fontweight="bold", color=GREY)
    fig.suptitle("Uzbekistan's renewable-resource atlas — where the solar and wind potential sits",
                 fontsize=14, fontweight="bold", color=NAVY, y=1.02)
    plt.tight_layout()
    _save(fig, "oblast_resource_map.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3.1 — data coverage & provenance   (port of build_data_coverage.py)
# ═══════════════════════════════════════════════════════════════════════════
def fig_data_coverage():
    md = pd.read_csv(DATA / "master_dataset.csv", index_col="year")
    panel_path = DATA / "central_asia_panel.csv"
    if not panel_path.is_file():
        panel_path = CLEAN / "central_asia_panel.csv"
    panel = pd.read_csv(panel_path)
    imf = pd.read_csv(DATA / "imf_weo_uzb.csv")

    def span(cols):
        cols = [c for c in cols if c in md.columns]
        sub = md[cols].dropna(how="all")
        return int(sub.index.min()), int(sub.index.max())

    def panel_span():
        p = panel.copy(); p["year"] = pd.to_numeric(p["year"], errors="coerce")
        uz = p[(p["country"] == "Uzbekistan") & p["electricity_demand"].notna()]
        return int(uz["year"].min()), int(uz["year"].max())

    def imf_span():
        y = pd.to_numeric(imf["year"], errors="coerce").dropna()
        return int(y.min()), int(y.max())

    d0, d1 = span(["elec_consumption_twh"])
    g0, g1 = span(["gen_gas_twh", "gen_hydro_twh", "gen_coal_twh", "gen_oil_twh"])
    c0, c1 = span(["co2_intensity_power_gco2kwh"])
    cap0, cap1 = span(["capacity_total_mw", "capacity_thermal_mw", "capacity_hydro_mw"])
    sw0, sw1 = span(["sc_solar_twh", "sc_wind_twh"])
    ir0, ir1 = span(["irena_re_share_generation_pct", "irena_re_share_capacity_pct"])
    mac0, mac1 = span(["wb_gdp_const2015_bn_usd", "wb_population", "wb_urban_pop_pct"])
    pa0, pa1 = panel_span(); im0, im1 = imf_span()

    rows = [
        ("Electricity demand (consumption)", "IEA", d0, d1, 2024, False),
        ("Generation by fuel", "IEA", g0, g1, 2024, False),
        ("CO₂ intensity of power", "IEA", c0, c1, None, False),
        ("Installed capacity (total/therm/hydro)", "StatSUZ", cap0, cap1, None, False),
        ("Solar & wind generation", "StatSUZ", sw0, sw1, None, False),
        ("Renewable shares & capacity", "IRENA", ir0, ir1, None, False),
        ("Macro covariates (GDP, pop, urban)", "World Bank", mac0, mac1, None, False),
        ("Cross-country panel (5 CA states)", "Supplementary", pa0, pa1, None, False),
        ("IMF WEO GDP / population outlook", "Supplementary", max(2024, im0), im1, None, True),
    ]
    fig, ax = plt.subplots(figsize=(12.4, 6.2))
    ax.set_xlim(1988, 2032); n = len(rows); ax.set_ylim(-0.8, n - 0.2)
    ax.axvspan(2023.5, 2026.5, color="#fef3c7", zorder=0)
    ax.text(2025.0, n - 0.55, "preliminary\n2024–26", ha="center", va="top",
            fontsize=7.6, color="#b45309", fontweight="bold", linespacing=1.05, zorder=2)
    ax.axvline(2023.5, color=GREY, lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.text(2023.4, -0.66, "IEA public cut-off → StatSUZ bridge", ha="right", va="center",
            fontsize=7.8, color=GREY, style="italic")
    for i, (lab, src, s, e, br, fw) in enumerate(rows):
        y = n - 1 - i; col = SOURCE[src]
        ax.barh(y, e - s, left=s, height=0.56, color=col, alpha=0.40 if fw else 0.90,
                edgecolor=col, linewidth=1.2, zorder=3, hatch="////" if fw else None)
        if br is not None and br > e:
            ax.barh(y, br - e, left=e, height=0.56, color=col, alpha=0.30,
                    edgecolor=col, linewidth=1.0, hatch="xxxx", zorder=3)
        ax.text(1988.6, y, lab, ha="left", va="center", fontsize=9, color=GREY, zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.75))
        end_txt = f"{s}–{br}" if (br and br > e) else f"{s}–{e}"
        if fw:
            end_txt = f"{s}–{e} (forward)"
        ax.text(max(e, br or e) + 0.5, y, end_txt, ha="left", va="center", fontsize=8, color=LGREY, zorder=5)
    for yr in [1990, 2000, 2010, 2020]:
        ax.axvline(yr, color="#e5e7eb", lw=0.9, zorder=0)
    ax.set_xticks([1990, 2000, 2010, 2020, 2030])
    ax.set_xticklabels(["1990", "2000", "2010", "2020", "2030"], fontsize=9, color=GREY)
    ax.set_yticks([])
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(LGREY); ax.tick_params(axis="x", length=0)
    handles = [Patch(facecolor=SOURCE[k], edgecolor=SOURCE[k], alpha=0.9, label=k)
               for k in ["IEA", "StatSUZ", "IRENA", "World Bank", "Supplementary"]]
    handles.append(Patch(facecolor="white", edgecolor=GREY, hatch="xxxx", label="bridged to 2024"))
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.005, -0.205), ncol=6,
              frameon=False, fontsize=8.2, handlelength=1.4, columnspacing=1.2, handletextpad=0.5)
    ax.set_title("Four sources on one annual spine give ~30 confirmed modelling years, bridged to 2024",
                 fontsize=13, fontweight="bold", loc="left", pad=14, color=NAVY)
    fig.text(0.012, 0.012,
             "Four primary sources on one annual spine. The confirmed electricity record runs 1990–2023 (≈30 modelling years); "
             "2024 is filled on the IEA consumption basis by ratio-scaling StatSUZ (×0.92), and 2024–2026 are flagged preliminary.",
             fontsize=7.8, color=LGREY)
    fig.subplots_adjust(left=0.012, right=0.99, top=0.88, bottom=0.16)
    _save(fig, "data_coverage_provenance.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4.1 — ex-ante model scoreboard   (port of build_forecast_scoreboard.py)
# ═══════════════════════════════════════════════════════════════════════════
def fig_scoreboard():
    sb = pd.read_csv(DATA / "forecast_scoreboard_advanced.csv")
    LABELS = {
        "Ridge CV-alpha (UZB, minimal)": "Ridge — Uzbekistan (minimal)",
        "Ridge CV-alpha (UZB, extended + UzStat)": "Ridge — Uzbekistan (extended)",
        "BayesianRidge (UZB, minimal)": "Bayesian Ridge — Uzbekistan (minimal)",
        "BayesianRidge (UZB, extended)": "Bayesian Ridge — Uzbekistan (extended)",
        "Pooled Ridge CV-alpha (4 CA + FE)": "Pooled Ridge — 4 Central-Asia + fixed effects",
        "Pooled BayesianRidge (4 CA + FE)": "Pooled Bayesian Ridge — 4 Central-Asia + fixed effects",
    }
    DEPLOYED = "BayesianRidge (UZB, extended)"
    sb["family"] = np.where(sb["model"].str.startswith("Pooled"), "pooled", "single")
    sb["label"] = sb["model"].map(LABELS).fillna(sb["model"])
    sb = sb.sort_values(["family", "exante_mape%"], ascending=[True, False]).reset_index(drop=True)
    n = len(sb)
    fig, ax = plt.subplots(figsize=(12.2, 5.8))
    y = np.arange(n)[::-1]
    ax.axvspan(0, 10, color="#ecfdf5", zorder=0)
    ax.axvspan(10, 20, color="#fffbeb", zorder=0)
    ax.axvline(10, color="#d1d5db", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.text(10, n - 0.3, "  Lewis 10% — high-accuracy threshold", ha="left", va="center",
            fontsize=7.6, color=LGREY, style="italic", zorder=4)
    for i, (_, r) in enumerate(sb.iterrows()):
        yi = y[i]; col = FAMILY[r["family"]]
        ax.barh(yi, r["exante_mape%"], height=0.56, color=col, alpha=0.92, edgecolor=col, linewidth=1.2, zorder=3)
        ax.plot([r["conditional_mape% [ref]"], r["exante_mape%"]], [yi, yi], color=LGREY, lw=1.0, ls=(0, (2, 2)), zorder=2)
        ax.scatter([r["conditional_mape% [ref]"]], [yi], s=46, facecolor="white", edgecolor=INK, linewidth=1.3, zorder=4)
        r2 = r["exante_r2"]; r2col = GREEN if r2 > 0 else RED
        ax.text(r["exante_mape%"] + 0.25, yi, f"R² = {r2:+.2f}", ha="left", va="center",
                fontsize=8.4, color=r2col, fontweight="bold", zorder=5)
        lab = r["label"] + ("  ◀ deployed" if r["model"] == DEPLOYED else "")
        ax.text(0.18, yi, lab, ha="left", va="center", fontsize=9, color=INK, zorder=6,
                bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="none", alpha=0.80))
    ax.set_xlim(0, 13.6); ax.set_ylim(-0.7, n - 0.3); ax.set_yticks([])
    ax.set_xlabel("Hold-out MAPE, 2019–2023  (%)", fontsize=9.5, color=GREY)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(LGREY); ax.tick_params(axis="x", colors=GREY, length=0)
    ax.text(13.45, np.mean(y[sb["family"].values == "single"]), "single-country\n(deployed family)",
            ha="right", va="center", fontsize=8.2, color=FAMILY["single"], fontweight="bold", linespacing=1.1)
    ax.text(13.45, np.mean(y[sb["family"].values == "pooled"]), "pooled\n(validation)",
            ha="right", va="center", fontsize=8.2, color=FAMILY["pooled"], fontweight="bold", linespacing=1.1)
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=FAMILY["single"], markeredgecolor=FAMILY["single"], markersize=10, label="ex-ante MAPE — single-country"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=FAMILY["pooled"], markeredgecolor=FAMILY["pooled"], markersize=10, label="ex-ante MAPE — pooled"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=INK, markersize=9, label="conditional backcast (reference)"),
    ]
    ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, -0.205), ncol=3, frameon=False,
              fontsize=8.2, handletextpad=0.4, columnspacing=1.3)
    ax.set_title("Ex-ante is the honest headline — every single-country model posts negative hold-out R²",
                 fontsize=13, fontweight="bold", loc="left", pad=12, color=NAVY)
    fig.text(0.012, 0.012,
             "Same 2019–2023 hold-out across all models. Bars show ex-ante error (each model forecasts its own drivers and feeds the demand "
             "lag recursively); hollow markers show the conditional backcast on observed drivers, kept only as the optimistic reference. "
             "Single-country models post negative hold-out R² against the post-2018 structural break; the pooled models turn R² positive.",
             fontsize=7.6, color=LGREY)
    fig.subplots_adjust(left=0.012, right=0.99, top=0.89, bottom=0.17)
    _save(fig, "forecast_scoreboard_exante.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 5.1 — Bayesian-ridge demand forecast   (history + 90% band from CSV)
#   NB: the 2019-2023 ex-ante hold-out error bars are NOT persisted to disk;
#   that diagnostic is carried quantitatively by Figure 4.1. This panel shows
#   the verified history (master_dataset_core) and the forecast 90% predictive
#   interval read from forecast_demand_bayes_ridge.csv.
# ═══════════════════════════════════════════════════════════════════════════
def fig_demand_bayes():
    core = pd.read_csv(DATA / "master_dataset_core.csv")
    col = "elec_consumption_twh_bridged" if "elec_consumption_twh_bridged" in core.columns else "elec_consumption_twh"
    hist = core[["year", col]].dropna()
    hist = hist[hist["year"] <= 2023]
    fc = pd.read_csv(DATA / "forecast_demand_bayes_ridge.csv")
    fig, ax = plt.subplots(figsize=(12, 5))
    # COVID-19 demand shock: 2020 consumption fell ~1.8% (the only contraction in the
    # 2015-2023 run-up) then rebounded ~23% in 2021 — shaded so the 2020 dip stays visible.
    ax.axvspan(2020, 2021, color=AMBER, alpha=0.13, zorder=0, lw=0)
    ax.annotate("COVID-19\ndemand dip", xy=(2020.5, 0.97), xycoords=("data", "axes fraction"),
                ha="center", va="top", fontsize=7.3, color=AMBER, fontweight="bold")
    ax.plot(hist["year"], hist[col], "o-", color=INK, lw=1.8, ms=4, label="History (master_dataset_core)")
    ax.fill_between(fc["year"], fc["lo90_twh"], fc["hi90_twh"], color=NAVY, alpha=0.18,
                    label="90% predictive interval (forecast)")
    ax.plot(fc["year"], fc["mu_twh"], "^-", color=NAVY, lw=2, label="Forecast μ (Bayesian Ridge, extended)")
    ax.axvline(2023.5, color=GREY, ls=":", lw=1)
    _last = fc.iloc[-1]
    end_label(ax, _last["year"], _last["mu_twh"], f"{_last['mu_twh']:.0f} TWh\nby {int(_last['year'])}",
              NAVY, dx=6, size=8.5)
    ax.set_title("Bayesian Ridge demand forecast — UZB national", fontsize=11, fontweight="bold",
                 loc="left", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("Electricity demand (TWh)")
    ax.legend(loc="upper left", frameon=False); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.04, 1, 0.91])
    takeaway(fig,
             "The deployed model carries demand above today's ~73 TWh — its 90% band is a lower bound on true uncertainty",
             size=12)
    figcap(fig,
           "Deployed model: extended Bayesian Ridge (NB07 §3). Predictive intervals are model ±1.645σ and are LOWER bounds on "
           "true uncertainty (they price coefficient noise, not structural-break or scenario risk). Hold-out accuracy: Figure 4.1.")
    _save(fig, "forecast_demand_bayes_ridge.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 5.2 — supply scenarios: RE share & total generation  (NB07 cell 33)
# ═══════════════════════════════════════════════════════════════════════════
def fig_scenarios():
    master = pd.read_csv(DATA / "master_dataset_core.csv")
    scen = pd.read_csv(DATA / "forecast_scenarios.csv")
    order = ["BAU", "Government", "Accelerated"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    re_hist = master[["year", "re_penetration_pct"]].dropna()
    ax.plot(re_hist["year"], re_hist["re_penetration_pct"], "o-", color=INK, lw=2, ms=4, label="History")
    for s in order:
        d = scen[scen["scenario"] == s]
        ax.plot(d["year"], d["re_share_pct"], "--", color=SCEN[s], lw=2, label=s)
    ax.axhline(30, color=GREY, ls=":", lw=1)
    ax.text(scen["year"].min(), 31, "Strategy 2030 target: 30%+ RE share", fontsize=8, color=GREY)
    for s in order:
        d = scen[scen["scenario"] == s].sort_values("year")
        ax.plot(d["year"].iloc[-1], d["re_share_pct"].iloc[-1], "o", color=SCEN[s], ms=5, zorder=5)
        end_label(ax, d["year"].iloc[-1], d["re_share_pct"].iloc[-1],
                  f"{s}  {d['re_share_pct'].iloc[-1]:.0f}%", SCEN[s], size=8.3)
    ax.set_title("Renewable share of generation", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("% of total generation"); dnv_clean(ax)
    ax.set_xlim(re_hist["year"].min(), 2044)
    ax = axes[1]
    gen_hist = master[["year", "gen_total_twh_bridged"]].dropna()
    ax.plot(gen_hist["year"], gen_hist["gen_total_twh_bridged"], "o-", color=INK, lw=2, ms=4, label="History")
    for s in order:
        d = scen[scen["scenario"] == s]
        ax.plot(d["year"], d["gen_total_twh"], "--", color=SCEN[s], lw=2, label=s)
    _g = scen[scen["scenario"] == "Government"].sort_values("year")
    end_label(ax, _g["year"].iloc[-1], _g["gen_total_twh"].iloc[-1],
              f"{_g['gen_total_twh'].iloc[-1]:.0f} TWh\nby 2040 (all scenarios)", INK, size=8.3)
    ax.set_title("Total generation = baseline demand × (1 + 9% losses)", loc="left", fontsize=11,
                 fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("TWh"); dnv_clean(ax)
    ax.set_xlim(gen_hist["year"].min(), 2044)
    fig.tight_layout(rect=[0, 0.04, 1, 0.90])
    takeaway(fig,
             "Even business-as-usual clears ~43% renewables by 2030, then slips to ~36% by 2040 as demand outgrows new RE",
             "Renewable share (left) and total generation (right) under the three supply scenarios")
    figcap(fig, "Source: demand = NB07 BayesianRidge (Baseline); capacity targets = MoE Uzbekistan 2030 strategy + Apr-2025 update, "
                "IRENA 2024, IEA Solar Roadmap; CF solar 0.18 / wind 0.30 / hydro 0.36 / thermal 0.55.")
    _save(fig, "forecast_scenarios.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 5.3 — power-sector CO2 emissions & intensity  (NB07 cell 34)
# ═══════════════════════════════════════════════════════════════════════════
def fig_co2():
    master = pd.read_csv(DATA / "master_dataset_core.csv")
    co2 = pd.read_csv(DATA / "forecast_co2.csv")
    order = ["BAU", "Government", "Accelerated"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    co2_hist = master[["year", "wb_co2_power_mt"]].dropna()
    ax.plot(co2_hist["year"], co2_hist["wb_co2_power_mt"], "o-", color=INK, lw=2, ms=4, label="History (WB)")
    for s in order:
        d = co2[co2["scenario"] == s]
        ax.plot(d["year"], d["co2_power_mt"], "--", color=SCEN[s], lw=2, label=s)
    for s in order:
        d = co2[co2["scenario"] == s].sort_values("year")
        end_label(ax, d["year"].iloc[-1], d["co2_power_mt"].iloc[-1],
                  f"{s}  {d['co2_power_mt'].iloc[-1]:.0f} Mt", SCEN[s], size=8.3)
    ax.legend([Line2D([0], [0], color=INK, marker="o", lw=2)], ["History (WB)"],
              loc="upper left", frameon=False, fontsize=8)
    ax.set_title("Power-sector CO₂ emissions", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("Mt CO₂ / yr"); dnv_clean(ax)
    ax.set_xlim(co2_hist["year"].min(), 2046)
    ax = axes[1]
    for s in order:
        d = co2[co2["scenario"] == s]
        ax.plot(d["year"], d["co2_intensity_gco2_per_kwh"], "--", color=SCEN[s], lw=2, label=s)
    hist_int = co2_hist.merge(master[["year", "gen_total_twh_bridged"]], on="year").dropna()
    hist_int["intensity"] = hist_int["wb_co2_power_mt"] * 1e3 / hist_int["gen_total_twh_bridged"]
    ax.plot(hist_int["year"], hist_int["intensity"], "o-", color=INK, lw=2, ms=4, label="History (computed)")
    ax.axhline(445, color=GREY, ls=":", lw=1)
    ax.text(co2["year"].min(), 455, "World average 445 gCO₂/kWh (IEA, 2024)", fontsize=8, color=GREY)
    for s in order:
        d = co2[co2["scenario"] == s].sort_values("year")
        end_label(ax, d["year"].iloc[-1], d["co2_intensity_gco2_per_kwh"].iloc[-1],
                  f"{s}  {d['co2_intensity_gco2_per_kwh'].iloc[-1]:.0f}", SCEN[s], size=8.3)
    ax.legend([Line2D([0], [0], color=INK, marker="o", lw=2)], ["History (computed)"],
              loc="lower left", frameon=False, fontsize=8)
    ax.set_title("Carbon intensity of power", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("gCO₂/kWh"); dnv_clean(ax)
    ax.set_xlim(co2["year"].min(), 2046)
    ax.set_xticks(list(range(2025, 2046, 5)))
    fig.tight_layout(rect=[0, 0.04, 1, 0.90])
    takeaway(fig,
             "Grid carbon intensity splits from 436 to 90 gCO₂/kWh by 2040 — on build-out ambition alone",
             "Power-sector CO₂ (left) and carbon intensity (right); the BAU–Accelerated gap is the decarbonisation prize")
    figcap(fig, "Source: thermal generation × fuel-weighted EF (88% gas / 12% coal); gas EF 650→380 gCO₂/kWh by 2040 "
                "(held at 650 under BAU); calibrated to WB 2023 power-sector CO₂. World-average reference: IEA (2024).")
    _save(fig, "forecast_co2.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 6.1 — T&D losses   (port of NB03 cell 10)
# ═══════════════════════════════════════════════════════════════════════════
def fig_td_losses():
    m = pd.read_csv(DATA / "master_dataset.csv")
    col = "td_losses_pct" if "td_losses_pct" in m.columns else "wb_td_losses_pct"
    td = m[["year", col]].dropna().sort_values("year")
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(td["year"], td[col], "o-", color=NAVY, lw=2)
    ax.axhline(15, ls="--", color=RED, lw=1.2)
    ax.text(td["year"].min(), 15.4, "15% — IFI grid-rehab priority threshold", fontsize=8, color=RED)
    ax.axhline(9, ls=":", color=LEAF, lw=1.6)
    ax.text(td["year"].min(), 9.35, "9% — forward target assumed by the supply scenarios", fontsize=8, color=LEAF)
    _l = td.iloc[-1]
    ax.plot(_l["year"], _l[col], "o", color=NAVY, ms=8, zorder=5)
    end_label(ax, _l["year"], _l[col], f"{_l[col]:.1f}% ({int(_l['year'])})", NAVY, size=9)
    ax.set_xlim(td["year"].min(), td["year"].max() + 3)
    ax.set_xlabel("Year"); ax.set_ylabel("Losses (% of output)"); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.05, 1, 0.88])
    takeaway(fig, "Realised T&D losses sit near 16% — well above the 9% the supply scenarios assume", size=12)
    figcap(fig, f"Source: master_dataset.csv ({col}). The gap between realised losses and the 9% planning target is itself a "
                "deferred-investment signal: every point of loss is generation built but never delivered.")
    _save(fig, "eda_td_losses.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 6.2 — capital envelope by technology & scenario  (from investment_signals.csv)
#   The original generator lives only in an archived notebook and the on-disk
#   PNG predates the current investment_signals.csv; this redraw reads the live
#   CSV so the figure matches the report's cited $27.3 / $56.9 / $79.3 bn totals.
# ═══════════════════════════════════════════════════════════════════════════
def fig_investment():
    inv = pd.read_csv(DATA / "investment_signals.csv")
    order = ["BAU", "Government", "Accelerated"]
    techs = ["solar", "wind", "hydro", "thermal", "storage", "transmission"]
    tech_col = {"solar": AMBER, "wind": TEAL, "hydro": NAVY,
                "thermal": TECH["thermal"]["color"], "storage": "#4F7D52", "transmission": "#6B7280"}
    piv = inv.pivot_table(index="scenario", columns="tech", values="capex_bn_usd", aggfunc="sum").reindex(order)
    fig, ax = plt.subplots(figsize=(11, 5.4))
    x = np.arange(len(order)); bottom = np.zeros(len(order))
    for t in techs:
        vals = piv[t].values if t in piv.columns else np.zeros(len(order))
        ax.bar(x, vals, bottom=bottom, color=tech_col[t], edgecolor="white", linewidth=0.7, label=t.title())
        bottom += np.nan_to_num(vals)
    for i, s in enumerate(order):
        ax.text(i, bottom[i] + 1.2, f"${bottom[i]:.1f} bn", ha="center", va="bottom", fontsize=10, fontweight="bold", color=INK)
    ax.set_xticks(x); ax.set_xticklabels(order, fontsize=10)
    ax.set_ylabel("Capital envelope 2024–2040  (US$ bn)")
    ax.set_ylim(0, bottom.max() * 1.16)
    ax.set_title("Capital envelope by technology and scenario, 2024–2040", loc="left", fontsize=11,
                 fontweight="bold", color=GREY)
    ax.legend(ncol=3, loc="upper left", fontsize=8.5, frameon=False)
    dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.05, 1, 0.89])
    takeaway(fig, "Decarbonising costs more up front — the capital envelope runs \\$27bn (BAU) to \\$79bn (Accelerated) by 2040",
             size=12)
    figcap(fig, "Undiscounted, constant-cost upper bounds (unit cost × capacity added; no discounting, learning or financing). "
                "Source: investment_signals.csv (project Notebook 08).")
    _save(fig, "forecast_investment.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 6.3 — Plan B nuclear sensitivity overlay  (port of NB08 cell 13)
# ═══════════════════════════════════════════════════════════════════════════
def fig_planb_nuclear():
    base = pd.read_csv(DATA / "forecast_scenarios.csv")
    nuc = pd.read_csv(DATA / "forecast_scenarios_with_nuclear.csv")
    sens = pd.read_csv(DATA / "planb_nuclear_sensitivity.csv")
    order = ["BAU", "Government", "Accelerated"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    for s in order:
        col = SCEN[s]
        d_base = base[base["scenario"] == s]
        d_nuc = nuc[nuc["scenario"] == s]
        ax.plot(d_base["year"], d_base["re_share_pct"], "-", color=col, lw=2, label=f"{s} (no nuclear)")
        ax.plot(d_nuc["year"], d_nuc["re_plus_nuclear_share_pct"], "--", color=col, lw=2, label=f"{s} (+1.2 GW nuclear)")
    ax.axhline(54, color=GREY, ls=":", lw=1)
    ax.text(base["year"].min(), 55, "54% — presidential low-carbon aspiration", fontsize=8, color=GREY)
    ax.set_title("RE + nuclear share, with & without Plan B (1.2 GW from 2032)", loc="left", fontsize=11,
                 fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("% of generation")
    ax.legend(loc="upper left", fontsize=7.3, frameon=False); dnv_clean(ax)
    ax = axes[1]
    for cyr, color, marker in [(2030, NAVY, "s"), (2032, TEAL, "o"), (2034, AMBER, "^")]:
        sub = sens[(sens["capacity_mw"] > 0) & (sens["commission_year"] == cyr)].sort_values("capacity_mw")
        if len(sub):
            ax.plot(sub["capacity_mw"], sub["re_plus_nuclear_share_2040"], marker=marker, ls="-",
                    label=f"commission {cyr}", color=color, lw=2, ms=8)
    ax.set_title("2040 low-carbon share vs nuclear capacity (Government scenario)", loc="left", fontsize=11,
                 fontweight="bold", color=GREY)
    ax.set_xlabel("Nuclear capacity (MW)"); ax.set_ylabel("% RE + nuclear of generation")
    ax.legend(frameon=False, fontsize=8); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.04, 1, 0.90])
    takeaway(fig,
             "Adding 1.2 GW of nuclear from 2032 lifts the low-carbon share several points — most decisively under slower build-out",
             "Plan B overlay (left) and 2040 sensitivity to nuclear size and timing (right)")
    figcap(fig, "Source: forecast_scenarios_with_nuclear.csv and planb_nuclear_sensitivity.csv (project Notebook 08); "
                "Jizzakh first phase ≈1.2 GW modelled from 2032.")
    _save(fig, "signal_planb_nuclear.png")


# ═══════════════════════════════════════════════════════════════════════════
# Raw-source readers for the new (Step-1) figures
#   IEA per-topic CSVs carry three metadata rows then a header whose first column
#   is the (unnamed) year; StatSUZ wide files carry the national total on row
#   code 1700 with one column per year. Both are read verbatim — no value is
#   recomputed; the figures only display what the source files contain.
# ═══════════════════════════════════════════════════════════════════════════
def _read_iea(rel):
    df = pd.read_csv(ROOT / "data" / "raw" / rel, skiprows=3)
    df = df.rename(columns={df.columns[0]: "year"})
    df = df[pd.to_numeric(df["year"], errors="coerce").notna()].copy()
    df["year"] = df["year"].astype(int)
    if "Units" in df.columns:
        df = df.drop(columns=["Units"])
    return df.sort_values("year").reset_index(drop=True)


def _statsuz_nat(fn):
    df = pd.read_csv(ROOT / "data" / "raw" / "statsuz" / fn)
    df.columns = [str(c).lstrip("﻿") for c in df.columns]
    yrs = [c for c in df.columns if c.isdigit()]
    r = df[df["Code"].astype(str) == "1700"].iloc[0]
    return pd.Series({int(y): float(r[y]) for y in yrs if pd.notna(r[y])}).sort_index()


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4.x — ex-ante hold-out predictions vs actual demand, 2019-2023
# ═══════════════════════════════════════════════════════════════════════════
def fig_holdout_actuals():
    """Reads forecast_holdout_predictions.csv (persisted by build_holdout_predictions.py,
    which re-runs NB07's exact ex-ante machinery and is asserted to reproduce the
    published scoreboard). Shows why the single-country models post negative R²:
    they cluster low and none captures the post-2021 demand step."""
    df = pd.read_csv(DATA / "forecast_holdout_predictions.csv").sort_values("year")
    preds = ["pred_ridge_min", "pred_ridge_ext", "pred_bayes_min", "pred_bayes_ext"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    lo = df[preds].min(axis=1); hi = df[preds].max(axis=1)
    ax.fill_between(df["year"], lo, hi, color=SKY, alpha=0.45, lw=0, zorder=1)
    for p in preds:
        ax.plot(df["year"], df[p], "-", color=SKY_DEEP, lw=1.2, alpha=0.9, zorder=2)
    ax.plot(df["year"], df["actual_cons_twh"], "o-", color=INK, lw=2.6, ms=6, zorder=4)
    ax.axvspan(2020.6, 2021.4, color=AMBER, alpha=0.12, lw=0, zorder=0)
    ya = df["actual_cons_twh"].iloc[-1]; yb = hi.iloc[-1]
    end_label(ax, df["year"].iloc[-1], ya, f"Actual {ya:.0f} TWh", INK, size=9)
    end_label(ax, df["year"].iloc[-1], df["pred_ridge_ext"].iloc[-1], "4 single-country\nmodels", SKY_DEEP, size=8, dy=-8)
    gap = (ya - yb) / ya * 100
    ax.annotate(f"≈{ya - yb:.0f} TWh / {gap:.0f}% under-shoot by 2023",
                xy=(2023, (ya + yb) / 2), xytext=(2020.85, (ya + yb) / 2 + 2.4),
                fontsize=8.3, color=RED, fontweight="bold", ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.1))
    ax.text(2021.0, df["actual_cons_twh"].max() * 1.005, "2021 demand step", ha="center", va="bottom",
            fontsize=7.6, color=AMBER, fontweight="bold")
    ax.set_xticks(df["year"]); ax.set_xlim(2018.7, 2024.6)
    ax.set_xlabel("Hold-out year"); ax.set_ylabel("Electricity demand (TWh)"); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.05, 1, 0.87])
    takeaway(fig, "Every single-country model under-shoots the post-2021 demand surge — the source of the negative hold-out R²",
             size=11.5)
    figcap(fig, "Source: forecast_holdout_predictions.csv (reproduces NB07's ex-ante machinery; recomputed MAPE/R² match the "
                "published scoreboard to 3 dp). Each model forecasts its own drivers and feeds demand recursively, 2019–2023.")
    _save(fig, "forecast_holdout_actuals.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2.x / 6.x — natural-gas production vs demand and self-sufficiency
# ═══════════════════════════════════════════════════════════════════════════
def fig_gas_balance():
    """Reads the processed StatSUZ energy-balance series carried in master_dataset.csv
    (sc_gas_prod_tj / sc_gas_cons_tj / gas_self_sufficiency_pct). Production crosses
    below domestic demand in 2023 — self-sufficiency falls ~125% (2010) → ~88% (2024)."""
    m = pd.read_csv(DATA / "master_dataset.csv")
    g = m[["year", "sc_gas_prod_tj", "sc_gas_cons_tj", "gas_self_sufficiency_pct"]].dropna(
        subset=["sc_gas_prod_tj", "sc_gas_cons_tj"]).sort_values("year")
    prod = g["sc_gas_prod_tj"] / 1000.0   # TJ -> PJ
    cons = g["sc_gas_cons_tj"] / 1000.0
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.fill_between(g["year"], prod, cons, where=(cons >= prod), interpolate=True,
                    color=RED, alpha=0.14, lw=0, zorder=1)
    ax.plot(g["year"], prod, "o-", color=NAVY, lw=2.2, ms=4, zorder=3)
    ax.plot(g["year"], cons, "o-", color=BROWN, lw=2.2, ms=4, zorder=3)
    end_label(ax, g["year"].iloc[-1], prod.iloc[-1], f"Production {prod.iloc[-1]:.0f} PJ", NAVY, size=8.3)
    end_label(ax, g["year"].iloc[-1], cons.iloc[-1], f"Demand {cons.iloc[-1]:.0f} PJ", BROWN, size=8.3, dy=-12)
    ax.annotate("output dips below\ndemand in 2023", xy=(2022.9, 1800),
                xytext=(2014.2, 1640), fontsize=8.2, color=RED, fontweight="bold",
                ha="left", va="center", arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0,
                connectionstyle="arc3,rad=0.2"))
    ax.set_title("Gas production vs domestic demand (PJ)", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("PJ / yr"); ax.set_xlim(g["year"].min(), g["year"].max() + 3); dnv_clean(ax)
    ax = axes[1]
    ax.plot(g["year"], g["gas_self_sufficiency_pct"], "o-", color=NAVY, lw=2.2, ms=4)
    ax.axhline(100, color=RED, ls="--", lw=1.2)
    ax.text(g["year"].min(), 101.5, "100% — self-sufficiency", fontsize=8, color=RED)
    for yv in (g["year"].min(), g["year"].max()):
        v = float(g.loc[g["year"] == yv, "gas_self_sufficiency_pct"].iloc[0])
        ax.annotate(f"{v:.0f}%", xy=(yv, v), xytext=(0, 9 if yv == g['year'].min() else -15),
                    textcoords="offset points", ha="center", color=NAVY, fontweight="bold", fontsize=9)
    ax.set_title("Gas self-sufficiency (production ÷ demand)", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("%"); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.04, 1, 0.90])
    takeaway(fig, "Gas output slipped below domestic demand in 2023 — self-sufficiency fell from ~125% (2010) to ~88% (2024)",
             "Production and demand on the StatSUZ energy-balance basis (PJ); the start of the structural import era")
    figcap(fig, "Source: master_dataset.csv — sc_gas_prod_tj / sc_gas_cons_tj / gas_self_sufficiency_pct (StatSUZ energy "
                "balances, ktoe converted to TJ→PJ). The physical StatSUZ volume series agrees on the 2023 crossing.")
    _save(fig, "gas_production_consumption.png")


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4.x — climate demand-drivers (CDD / HDD / mean temperature)
# ═══════════════════════════════════════════════════════════════════════════
def fig_climate_drivers():
    """Reads demand_drivers_panel_v2.csv (cdd24_natl / hdd18_natl / tmean_c_natl,
    Open-Meteo ERA5, pop-weighted). Cooling degree-days trend up, heating degree-days
    ease and mean temperature rises — the warming signal behind cooling-led demand."""
    d = pd.read_csv(DATA / "demand_drivers_panel_v2.csv").sort_values("year")
    d = d[["year", "cdd24_natl", "hdd18_natl", "tmean_c_natl"]].dropna()
    yr = d["year"].to_numpy(float)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))

    def _trend(ax, y, color):
        b1, b0 = np.polyfit(yr, y, 1)
        ax.plot(yr, b0 + b1 * yr, "--", color=color, lw=1.4, alpha=0.9)
        return b1

    ax = axes[0]
    ax.plot(d["year"], d["cdd24_natl"], "o-", color=GOLD, lw=1.8, ms=3)
    s = _trend(ax, d["cdd24_natl"].to_numpy(), GOLD)
    ax.set_title("Cooling degree-days (CDD, base 24 °C)", loc="left", fontsize=10.5, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("degree-days / yr"); dnv_clean(ax)
    ax.annotate(f"trend +{s*10:.0f}/decade", xy=(0.04, 0.93), xycoords="axes fraction",
                fontsize=8.2, color=GOLD, fontweight="bold")

    ax = axes[1]
    ax.plot(d["year"], d["hdd18_natl"], "o-", color=NAVY, lw=1.8, ms=3)
    s = _trend(ax, d["hdd18_natl"].to_numpy(), NAVY)
    ax.set_title("Heating degree-days (HDD, base 18 °C)", loc="left", fontsize=10.5, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("degree-days / yr"); dnv_clean(ax)
    ax.annotate(f"trend {s*10:.0f}/decade", xy=(0.04, 0.10), xycoords="axes fraction",
                fontsize=8.2, color=NAVY, fontweight="bold")

    ax = axes[2]
    ax.plot(d["year"], d["tmean_c_natl"], "o-", color=RED, lw=1.8, ms=3)
    s = _trend(ax, d["tmean_c_natl"].to_numpy(), RED)
    ax.set_title("Mean temperature", loc="left", fontsize=10.5, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("°C"); dnv_clean(ax)
    ax.annotate(f"trend +{s*10:.2f} °C/decade", xy=(0.04, 0.93), xycoords="axes fraction",
                fontsize=8.2, color=RED, fontweight="bold")

    fig.tight_layout(rect=[0, 0.04, 1, 0.88])
    takeaway(fig, "Cooling degree-days trend up while heating degree-days ease — a warming signal in the demand drivers",
             "National pop-weighted climate series, 1990–2024 (dashed = linear trend)")
    figcap(fig, "Source: demand_drivers_panel_v2.csv — Open-Meteo (ERA5) reanalysis, population-weighted across 13 oblast "
                "capitals (UzStat 2023 weights).")
    _save(fig, "climate_drivers.png")


# ═══════════════════════════════════════════════════════════════════════════
# Appendix G — economy-wide energy CO₂ by source and per capita (IEA)
# ═══════════════════════════════════════════════════════════════════════════
def fig_co2_economy():
    """Reads two IEA files (CO2 emissions by energy source; CO2 emissions per capita).
    Natural gas is ~three-quarters of energy-CO₂; per-capita emissions fell from
    5.8 to 3.4 tCO₂ as the economy de-intensified."""
    src = _read_iea("emissions (source - IEA)/CO2 emissions by energy source - Uzbekistan.csv")
    pc = _read_iea("emissions (source - IEA)/CO2 emissions per capita - Uzbekistan.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    yr = src["year"].to_numpy()
    coal = src["Coal"].fillna(0).to_numpy(); oil = src["Oil"].fillna(0).to_numpy()
    gas = src["Natural gas"].fillna(0).to_numpy()
    ax.stackplot(yr, gas, oil, coal, colors=[BROWN, WARMGREY, "#3F3A36"],
                 labels=["Natural gas", "Oil", "Coal"], edgecolor="white", linewidth=0.25)
    tot = gas + oil + coal
    gshare = gas[-1] / tot[-1] * 100
    ax.annotate(f"Gas ≈ {gshare:.0f}% of\nenergy-CO₂ (2023)", xy=(yr[-1] - 7, gas[-1] * 0.5),
                fontsize=8.6, color="white", fontweight="bold", ha="left", va="center")
    ax.set_title("Energy CO₂ by source", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("MtCO₂ / yr"); ax.set_xlim(yr.min(), yr.max())
    ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=3); dnv_clean(ax)
    ax = axes[1]
    ax.plot(pc["year"], pc["CO2/population"], "o-", color=NAVY, lw=2.2, ms=3)
    for yv in (pc["year"].min(), pc["year"].max()):
        v = float(pc.loc[pc["year"] == yv, "CO2/population"].iloc[0])
        ax.annotate(f"{v:.1f}", xy=(yv, v), xytext=(0, 8), textcoords="offset points",
                    ha="center", color=NAVY, fontweight="bold", fontsize=9)
    ax.set_title("CO₂ per capita", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("tCO₂ per capita"); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.04, 1, 0.89])
    takeaway(fig, "Natural gas drives ~73% of energy-CO₂; per-capita emissions have fallen from 5.8 to 3.4 tCO₂ since 1990",
             "IEA economy-wide CO₂ from fuel combustion, by source (left) and per capita (right)")
    figcap(fig, "Source: IEA Greenhouse Gas Emissions from Energy (CO₂ by energy source) and IEA Energy Transitions "
                "Indicators (CO₂ per capita), Uzbekistan 1990–2023.")
    _save(fig, "appendixG_co2_economy.png")


# ═══════════════════════════════════════════════════════════════════════════
# Appendix G — liquids production (crude + condensate) and 2024 refined slate
# ═══════════════════════════════════════════════════════════════════════════
def fig_liquids():
    """Reads StatSUZ national production volumes (thousand tonnes). Crude output has
    fallen ~65% since 2010; gas condensate is now the larger component of a shrinking
    liquids pool. The right panel shows the 2024 refined slate."""
    crude = _statsuz_nat("Volume of oil production.csv")
    cond = _statsuz_nat("Volume of gas condensate production.csv")
    diesel = _statsuz_nat("Volume of diesel fuel production.csv")
    fueloil = _statsuz_nat("Volume of fuel oil production.csv")
    gasoline = _statsuz_nat("Volume of gasoline fuel production.csv")
    yrs = sorted(set(crude.index) & set(cond.index))
    cr = crude.reindex(yrs); cd = cond.reindex(yrs); tot = cr + cd
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0), gridspec_kw={"width_ratios": [1.3, 1.0]})
    ax = axes[0]
    ax.plot(yrs, tot, "o-", color=INK, lw=2.0, ms=3, zorder=4)
    ax.plot(yrs, cr, "o-", color=NAVY, lw=2.0, ms=3)
    ax.plot(yrs, cd, "o-", color=GOLD, lw=2.0, ms=3)
    end_label(ax, yrs[-1], tot.iloc[-1], f"Total {tot.iloc[-1]:.0f}", INK, size=8.3)
    end_label(ax, yrs[-1], cr.iloc[-1], f"Crude {cr.iloc[-1]:.0f}", NAVY, size=8.3, dy=-6)
    end_label(ax, yrs[-1], cd.iloc[-1], f"Condensate {cd.iloc[-1]:.0f}", GOLD, size=8.3, dy=8)
    drop = (cr.iloc[0] - cr.iloc[-1]) / cr.iloc[0] * 100
    ax.annotate(f"crude −{drop:.0f}% since 2010", xy=(yrs[len(yrs) // 2], cr.iloc[len(yrs) // 2]),
                xytext=(yrs[2], cr.max() * 0.55), fontsize=8.2, color=NAVY, fontweight="bold",
                ha="left", va="center", arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.0))
    ax.set_title("Liquids production (thousand tonnes)", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("kt / yr"); ax.set_xlim(min(yrs), max(yrs) + 4); dnv_clean(ax)
    ax = axes[1]
    ref = {"Diesel": diesel.iloc[-1], "Gasoline": gasoline.iloc[-1], "Fuel oil": fueloil.iloc[-1]}
    ref = dict(sorted(ref.items(), key=lambda kv: kv[1]))
    ax.barh(list(ref.keys()), list(ref.values()), color=SKY_DEEP, height=0.6)
    for i, (k, v) in enumerate(ref.items()):
        ax.text(v + max(ref.values()) * 0.02, i, f"{v:.0f}", va="center", fontsize=9, color=INK, fontweight="bold")
    ax.set_title("2024 refined output (kt)", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("kt"); ax.set_xlim(0, max(ref.values()) * 1.18); dnv_clean(ax, grid="x")
    fig.tight_layout(rect=[0, 0.04, 1, 0.89])
    takeaway(fig, "Crude-oil output has fallen ~65% since 2010 — gas condensate is now the larger share of a shrinking liquids pool",
             "StatSUZ liquids production 2010–2024 (left) and the 2024 refined slate (right)")
    figcap(fig, "Source: StatSUZ national production volumes (thousand tonnes): oil, gas condensate, diesel, gasoline and "
                "fuel oil. Total liquids = crude + condensate.")
    _save(fig, "appendixG_liquids.png")


# ═══════════════════════════════════════════════════════════════════════════
# Appendix G — total energy supply (TES) by source, 1990-2023 (IEA, PJ)
# ═══════════════════════════════════════════════════════════════════════════
def fig_primary_energy():
    """Reads the IEA World Energy Balances TES-by-source file. Natural gas is
    roughly four-fifths of primary supply — the structural fact behind every
    decarbonisation lever in the power sector."""
    t = _read_iea("energy production data (source - IEA)/Total energy supply (TES) by source - Uzbekistan.csv")
    yr = t["year"].to_numpy()

    def col(c):
        return t[c].fillna(0).to_numpy() / 1000.0   # TJ -> PJ

    gas = col("Natural gas"); oil = col("Oil and oil products"); coal = col("Coal and coal products")
    hyd = col("Hydropower"); bio = col("Biofuels and waste"); sw = col("Solar, wind and other renewables")
    fig, ax = plt.subplots(figsize=(14, 5.0))
    ax.stackplot(yr, gas, oil, coal, hyd, bio, sw,
                 colors=[BROWN, WARMGREY, "#3F3A36", NAVY, LEAF, GOLD],
                 labels=["Natural gas", "Oil", "Coal", "Hydro", "Biofuels & waste", "Solar/wind"],
                 edgecolor="white", linewidth=0.25)
    tot = gas + oil + coal + hyd + bio + sw
    gshare = gas[-1] / tot[-1] * 100
    ax.annotate(f"Natural gas ≈ {gshare:.0f}%\nof primary supply", xy=(yr[0] + 6, gas[-1] * 0.45),
                fontsize=9.5, color="white", fontweight="bold", ha="left", va="center")
    ax.set_xlim(yr.min(), yr.max()); ax.set_ylim(0, tot.max() * 1.05)
    ax.set_xlabel("Year"); ax.set_ylabel("Primary energy supply (PJ)")
    ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=3); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.05, 1, 0.88])
    takeaway(fig, "Primary energy supply is roughly four-fifths natural gas — the structural fact behind every decarbonisation lever",
             size=11.5)
    figcap(fig, "Source: IEA World Energy Balances — total energy supply by source, Uzbekistan 1990–2023 (TJ converted to PJ). "
                "Solar/wind remains a sliver of primary supply even at the end of the record.")
    _save(fig, "appendixG_primary_energy.png")


# ═══════════════════════════════════════════════════════════════════════════
# Appendix G — energy intensity of GDP and primary energy per capita (IEA)
# ═══════════════════════════════════════════════════════════════════════════
def fig_energy_intensity():
    """Reads the IEA TES-per-GDP and TES-per-capita files. Energy intensity has
    fallen ~75% as the post-Soviet economy de-intensified; primary energy per
    capita is down ~40% over the same window."""
    gdp = _read_iea("energy production data (source - IEA)/Total energy supply (TES) by GDP - Uzbekistan.csv")
    pc = _read_iea("energy production data (source - IEA)/Total energy supply (TES) per capita - Uzbekistan.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0))
    ax = axes[0]
    g = gdp.dropna(subset=["TES/GDP"])
    ax.plot(g["year"], g["TES/GDP"], "o-", color=NAVY, lw=2.2, ms=3)
    d0 = g["TES/GDP"].iloc[0]; d1 = g["TES/GDP"].iloc[-1]
    ax.annotate(f"−{(d0 - d1) / d0 * 100:.0f}% since 1990", xy=(g['year'].iloc[-1], d1),
                xytext=(-4, 20), textcoords="offset points", ha="right", color=NAVY, fontweight="bold", fontsize=9)
    ax.set_title("Energy intensity of GDP", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("MJ per 2015 USD"); dnv_clean(ax)
    ax = axes[1]
    p = pc.dropna(subset=["TES/population"])
    ax.plot(p["year"], p["TES/population"] / 1000.0, "o-", color=SKY_DEEP, lw=2.2, ms=3)  # MJ -> GJ
    q0 = p["TES/population"].iloc[0] / 1000.0; q1 = p["TES/population"].iloc[-1] / 1000.0
    ax.annotate(f"−{(q0 - q1) / q0 * 100:.0f}% since 1990", xy=(p['year'].iloc[-1], q1),
                xytext=(-4, 18), textcoords="offset points", ha="right", color=SKY_DEEP, fontweight="bold", fontsize=9)
    ax.set_title("Primary energy per capita", loc="left", fontsize=11, fontweight="bold", color=GREY)
    ax.set_xlabel("Year"); ax.set_ylabel("GJ per capita"); dnv_clean(ax)
    fig.tight_layout(rect=[0, 0.04, 1, 0.89])
    takeaway(fig, "Energy intensity of GDP has fallen ~75% since 1990; primary energy per capita is down ~40%",
             "IEA total energy supply per unit GDP (left) and per capita (right), 1990–2023")
    figcap(fig, "Source: IEA World Energy Balances — TES per unit GDP (MJ per 2015 USD) and TES per capita (MJ→GJ per "
                "capita), Uzbekistan 1990–2023.")
    _save(fig, "appendixG_energy_intensity.png")


def main():
    apply_style()
    builders = [
        fig_history_timeline, fig_energy_mix_evolution, fig_fleet_evolution, fig_oblast_resource,
        fig_data_coverage, fig_scoreboard, fig_demand_bayes, fig_holdout_actuals, fig_scenarios, fig_co2,
        fig_td_losses, fig_investment, fig_planb_nuclear,
        fig_gas_balance, fig_climate_drivers,
        fig_co2_economy, fig_liquids, fig_primary_energy, fig_energy_intensity,
    ]
    print(f"Regenerating {len(builders)} paper figures -> paper/figures/  (DNV palette, 300 DPI)\n")
    for b in builders:
        print(f"[{b.__name__}]")
        b()
    print(f"\nDONE: {len(_done)}/{len(builders)} figures written to paper/figures/")


if __name__ == "__main__":
    main()
