"""
build_data_coverage.py
----------------------
Renders the Chapter-3 (Data) provenance figure: a coverage matrix showing which
source supplies which series over 1990–2026, the IEA→StatSUZ bridge seam at the
2023/2024 boundary, and the preliminary-year band.

Every bar's span is COMPUTED from the actual data files (read-only) rather than
hard-coded, so the figure cannot drift from the dataset.

Inputs (read-only):
  data/processed/master_dataset.csv
  data/processed/central_asia_panel.csv  (or uzstat_clean/central_asia_panel.csv)
  data/processed/imf_weo_uzb.csv

Output: outputs/data_coverage_provenance.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT  = ROOT / "outputs"; OUT.mkdir(exist_ok=True)

# ── visual language (matches NB02 / history-timeline figures) ─────────────────
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
C_IEA   = "#2c6e9e"   # blue
C_SC    = "#b5612e"   # brown  (StatSUZ)
C_IRENA = "#2f8f5b"   # green
C_WB    = "#6b7280"   # slate
C_SUPP  = "#7c6aa8"   # muted purple (supplementary feeds)
C_GREY  = "#374151"
C_LGREY = "#9ca3af"
C_PRELIM = "#fef3c7"  # amber-50 band

SRC_COLOR = {"IEA": C_IEA, "StatSUZ": C_SC, "IRENA": C_IRENA,
             "World Bank": C_WB, "Supplementary": C_SUPP}

# ── load (read-only) ──────────────────────────────────────────────────────────
md = pd.read_csv(DATA / "master_dataset.csv", index_col="year")

panel_path = DATA / "central_asia_panel.csv"
if not panel_path.is_file():
    panel_path = DATA / "uzstat_clean" / "central_asia_panel.csv"
panel = pd.read_csv(panel_path)

imf = pd.read_csv(DATA / "imf_weo_uzb.csv")

def span(cols):
    """Min/max year over which ANY of the given master columns is non-null."""
    cols = [c for c in cols if c in md.columns]
    sub = md[cols].dropna(how="all")
    return int(sub.index.min()), int(sub.index.max())

def panel_span():
    p = panel.copy()
    p["year"] = pd.to_numeric(p["year"], errors="coerce")
    uz = p[(p["country"] == "Uzbekistan") & p["electricity_demand"].notna()]
    return int(uz["year"].min()), int(uz["year"].max())

def imf_span():
    y = pd.to_numeric(imf["year"], errors="coerce").dropna()
    return int(y.min()), int(y.max())

# ── rows: (label, source, start, end, bridged_to, forward) ───────────────────
d0, d1   = span(["elec_consumption_twh"])
g0, g1   = span(["gen_gas_twh", "gen_hydro_twh", "gen_coal_twh", "gen_oil_twh"])
c0, c1   = span(["co2_intensity_power_gco2kwh"])
cap0,cap1= span(["capacity_total_mw", "capacity_thermal_mw", "capacity_hydro_mw"])
sw0, sw1 = span(["sc_solar_twh", "sc_wind_twh"])
ir0, ir1 = span(["irena_re_share_generation_pct", "irena_re_share_capacity_pct"])
mac0,mac1= span(["wb_gdp_const2015_bn_usd", "wb_population", "wb_urban_pop_pct"])
pa0, pa1 = panel_span()
im0, im1 = imf_span()

rows = [
    ("Electricity demand (consumption)",       "IEA",           d0, d1, 2024, False),
    ("Generation by fuel",                     "IEA",           g0, g1, 2024, False),
    ("CO₂ intensity of power",            "IEA",           c0, c1, None, False),
    ("Installed capacity (total/therm/hydro)", "StatSUZ",       cap0, cap1, None, False),
    ("Solar & wind generation",                "StatSUZ",       sw0, sw1, None, False),
    ("Renewable shares & capacity",            "IRENA",         ir0, ir1, None, False),
    ("Macro covariates (GDP, pop, urban)",     "World Bank",    mac0, mac1, None, False),
    ("Cross-country panel (5 CA states)",      "Supplementary", pa0, pa1, None, False),
    # IMF WEO carries history too, but the project only USES it as the forward
    # GDP/population path for the NB07 scenarios — show that span, not the file's.
    ("IMF WEO GDP / population outlook",       "Supplementary", max(2024, im0), im1, None, True),
]

# diagnostic print so the spans are auditable in the build log
print("Computed coverage spans:")
for lab, src, s, e, br, fw in rows:
    print(f"  {lab:42s} {src:14s} {s}-{e}" + (f"  (bridged->{br})" if br else "")
          + ("  [forward]" if fw else ""))

# ── plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.4, 6.2))
X0, X1 = 1988, 2032
ax.set_xlim(X0, X1)
n = len(rows)
ax.set_ylim(-0.8, n - 0.2)

BAR_H = 0.56

# preliminary / forward band (2023.5 -> 2026.5) behind everything
ax.axvspan(2023.5, 2026.5, color=C_PRELIM, zorder=0)
ax.text(2025.0, n - 0.55, "preliminary\n2024–26", ha="center", va="top",
        fontsize=7.6, color="#b45309", fontweight="bold", linespacing=1.05, zorder=2)

# IEA public cut-off / bridge seam
ax.axvline(2023.5, color=C_GREY, lw=1.0, ls=(0, (4, 3)), zorder=1)
ax.text(2023.4, -0.66, "IEA public cut-off → StatSUZ bridge",
        ha="right", va="center", fontsize=7.8, color=C_GREY, style="italic")

for i, (lab, src, s, e, br, fw) in enumerate(rows):
    y = n - 1 - i
    col = SRC_COLOR[src]
    # main coverage bar
    ax.barh(y, e - s, left=s, height=BAR_H, color=col,
            alpha=0.40 if fw else 0.90, edgecolor=col, linewidth=1.2,
            zorder=3, hatch="////" if fw else None)
    # bridged one-year extension (hatched cap)
    if br is not None and br > e:
        ax.barh(y, br - e, left=e, height=BAR_H, color=col, alpha=0.30,
                edgecolor=col, linewidth=1.0, hatch="xxxx", zorder=3)
    # series label (left, inside plot area against a clean margin)
    ax.text(X0 + 0.6, y, lab, ha="left", va="center", fontsize=9,
            color=C_GREY, zorder=5,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.75))
    # span annotation at the right end
    end_txt = f"{s}–{br}" if (br and br > e) else f"{s}–{e}"
    if fw:
        end_txt = f"{s}–{e} (forward)"
    ax.text(max(e, br or e) + 0.5, y, end_txt, ha="left", va="center",
            fontsize=8, color=C_LGREY, zorder=5)

# decade gridlines
for yr in [1990, 2000, 2010, 2020]:
    ax.axvline(yr, color="#e5e7eb", lw=0.9, zorder=0)
ax.set_xticks([1990, 2000, 2010, 2020, 2030])
ax.set_xticklabels(["1990", "2000", "2010", "2020", "2030"], fontsize=9, color=C_GREY)
ax.set_yticks([])
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(C_LGREY)
ax.tick_params(axis="x", length=0)

# legend
handles = [Patch(facecolor=SRC_COLOR[k], edgecolor=SRC_COLOR[k], alpha=0.9, label=k)
           for k in ["IEA", "StatSUZ", "IRENA", "World Bank", "Supplementary"]]
handles.append(Patch(facecolor="white", edgecolor=C_GREY, hatch="xxxx", label="bridged to 2024"))
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.005, -0.205),
          ncol=6, frameon=False, fontsize=8.2, handlelength=1.4,
          columnspacing=1.2, handletextpad=0.5)

ax.set_title("Data coverage and provenance, 1990 → 2026",
             fontsize=14, fontweight="bold", loc="left", pad=14, color="#111827")
fig.text(0.012, 0.012,
         "Four primary sources on one annual spine. The confirmed electricity record runs 1990–2023 (≈30 modelling years); "
         "2024 is filled on the IEA consumption basis by ratio-scaling StatSUZ (×0.92), and 2024–2026 are flagged preliminary.",
         fontsize=7.8, color=C_LGREY)

fig.subplots_adjust(left=0.012, right=0.99, top=0.88, bottom=0.16)
dest = OUT / "data_coverage_provenance.png"
fig.savefig(dest, dpi=150, bbox_inches="tight", facecolor="white")
print(f"saved -> {dest}")
