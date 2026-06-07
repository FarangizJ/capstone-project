"""
figure_style_for_notebooks.py
=============================
Single source of truth for the paper's visual language: the navy / teal / amber
palette, the locked supply-scenario colours (BAU / Government / Accelerated), the
technology and data-source palettes, and a 300-DPI rcParams profile.

USAGE
-----
From a notebook (notebooks/ runs one level down):

    import sys; sys.path.append('..')
    from figure_style_for_notebooks import apply_style, NAVY, TEAL, AMBER, SCEN
    apply_style()                      # call once, right after `import matplotlib`

From a script at repo root or in scripts/:

    from figure_style_for_notebooks import apply_style, SCEN, TECH, FUEL, SOURCE
    apply_style()

The palette is deliberately small: NAVY is the primary, TEAL the secondary,
AMBER the accent. Everything else is a neutral (ink / grey) or a semantic
signal (RED negative / threshold, GREEN positive). Scenario lines use a fixed
{BAU: grey, Government: navy, Accelerated: teal} mapping everywhere so the same
scenario reads the same colour across the demand, supply, carbon and Plan-B
figures.
"""

import matplotlib.pyplot as plt

# ── brand palette ────────────────────────────────────────────────────────────
NAVY  = "#0D4D7A"   # primary   — central/official series, hydro, "Government"
TEAL  = "#0E7C7B"   # secondary — ambition/upside, wind, "Accelerated"
AMBER = "#D98A1E"   # accent    — solar, thresholds, highlights

# ── neutrals / semantic signals ──────────────────────────────────────────────
INK    = "#1F2937"   # near-black for history lines & headings
GREY   = "#6B7280"   # axis labels, secondary text
LGREY  = "#9CA3AF"   # captions, baseline ("BAU") series
PALE   = "#E5E7EB"   # gridlines
RED    = "#B91C1C"   # negative R², loss/over-threshold markers
GREEN  = "#2F8F5B"   # positive R², "good" bands
NAVY_FILL = "#DCE7F1"  # pale-navy fill for shaded header cells / bands

# ── locked supply-scenario colours (used identically in §5 and §6) ───────────
SCEN = {
    "BAU":         LGREY,   # business-as-usual — muted, lets the action paths pop
    "Government":  NAVY,    # central legislated path
    "Accelerated": TEAL,    # stretch / upside path
}

# ── technology palette for the asset & oblast maps (stay distinguishable) ─────
#   hydro → navy, solar → amber, wind → teal are on-brand; the rest are
#   deliberately distinct neutrals/secondaries so 7 techs never collide.
TECH = {
    "thermal":  {"color": "#8C6D46", "label": "Gas & thermal"},
    "hydro":    {"color": NAVY,      "label": "Hydropower"},
    "solar":    {"color": AMBER,     "label": "Solar PV"},
    "wind":     {"color": TEAL,      "label": "Wind"},
    "nuclear":  {"color": "#7A4FB0", "label": "Nuclear"},
    "storage":  {"color": "#4F7D52", "label": "Storage (BESS)"},
    "gasfield": {"color": "#9B8B73", "label": "Gas field"},
}

# ── fuel palette for the generation-mix bars ─────────────────────────────────
FUEL = {
    "solar":   AMBER,
    "wind":    TEAL,
    "hydro":   NAVY,
    "thermal": "#8C6D46",
    "residual": LGREY,      # thermal+hydro mass (2024 split pending)
}

# ── data-source palette for the coverage/provenance matrix ───────────────────
SOURCE = {
    "IEA":           NAVY,
    "StatSUZ":       AMBER,
    "IRENA":         TEAL,
    "World Bank":    "#6B7280",
    "Supplementary": "#7A4FB0",
}

# ── single/pooled family palette for the model scoreboard ────────────────────
FAMILY = {
    "single": AMBER,   # single-country (deployed family)
    "pooled": NAVY,    # pooled Central-Asia (validation)
}


def apply_style():
    """Install the navy/teal/amber rcParams profile at 300-DPI save quality."""
    plt.rcParams.update({
        "figure.dpi":        120,          # comfortable on screen
        "savefig.dpi":       300,          # print / paper quality
        "savefig.facecolor": "white",
        "savefig.bbox":      "tight",
        "figure.facecolor":  "white",
        "font.family":       "DejaVu Sans",
        "font.size":         10,
        "axes.titlesize":    12,
        "axes.titleweight":  "bold",
        "axes.titlecolor":   INK,
        "axes.labelcolor":   INK,
        "axes.edgecolor":    "#AAAAAA",
        "axes.linewidth":    0.9,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         False,
        "grid.color":        PALE,
        "grid.linewidth":    0.8,
        "grid.alpha":        0.7,
        "text.color":        INK,
        "xtick.color":       GREY,
        "ytick.color":       GREY,
        "xtick.labelcolor":  GREY,
        "ytick.labelcolor":  GREY,
        "legend.frameon":    False,
        "legend.fontsize":   8.5,
    })
    return plt.rcParams


# Apply on import so a bare `import figure_style_for_notebooks` is enough.
apply_style()
