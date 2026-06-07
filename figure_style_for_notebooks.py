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

# ── DNV-style brand palette ───────────────────────────────────────────────────
#   Four core colours, after the DNV Energy Transition Outlook: a deep navy
#   primary, a sky-blue secondary, a leaf-green "good"/upside accent, and a warm
#   neutral grey. Solar-gold, nuclear-purple and a fossil brown are kept as the
#   categorical extensions DNV itself uses on its fuel/technology charts.
NAVY     = "#003591"   # primary   — central/official series, hydro, "Government"
SKY      = "#9DC3E6"   # secondary — predictive bands, area fills, secondary bars
SKY_DEEP = "#3E7CB1"   # legible mid-sky for secondary *lines/bars* on white
LEAF     = "#5C9A3C"   # accent/"good" — upside, "Accelerated", positive bands
WARMGREY = "#B4ADA3"   # neutral   — baseline ("BAU"), residual mass, low-emphasis

# categorical extensions (DNV uses these on its own fuel/technology charts)
GOLD   = "#D98A1E"     # solar PV / highlight
PURPLE = "#7A4FB0"     # nuclear
BROWN  = "#8C6D46"     # gas & thermal (fossil)

# back-compat aliases — older figure code imports these names directly
TEAL  = SKY_DEEP       # was the secondary; now the legible mid-sky
AMBER = GOLD           # solar / highlight gold

# ── neutrals / semantic signals ──────────────────────────────────────────────
INK    = "#1F2937"   # near-black for history lines & headings
GREY   = "#6B7280"   # axis labels, secondary text
LGREY  = "#9CA3AF"   # captions
PALE   = "#E7E9EC"   # gridlines (very light, DNV idiom)
RED    = "#B91C1C"   # negative R², loss/over-threshold markers
GREEN  = LEAF        # positive R², "good" bands → DNV leaf green
NAVY_FILL = "#E3ECF7"  # pale sky-navy fill for shaded header cells / bands

# ── locked supply-scenario colours (used identically in §5 and §6) ───────────
SCEN = {
    "BAU":         WARMGREY,   # business-as-usual — neutral, lets the action paths pop
    "Government":  NAVY,       # central legislated path
    "Accelerated": LEAF,       # stretch / upside path ("good")
}

# ── technology palette for the asset & oblast maps (stay distinguishable) ─────
#   hydro → navy, solar → gold, wind → sky, nuclear → purple are DNV-idiom; the
#   rest are deliberately distinct so 7 techs never collide.
TECH = {
    "thermal":  {"color": BROWN,    "label": "Gas & thermal"},
    "hydro":    {"color": NAVY,      "label": "Hydropower"},
    "solar":    {"color": GOLD,      "label": "Solar PV"},
    "wind":     {"color": SKY_DEEP,  "label": "Wind"},
    "nuclear":  {"color": PURPLE,    "label": "Nuclear"},
    "storage":  {"color": LEAF,      "label": "Storage (BESS)"},
    "gasfield": {"color": WARMGREY,  "label": "Gas field"},
}

# ── fuel palette for the generation-mix bars ─────────────────────────────────
FUEL = {
    "solar":   GOLD,
    "wind":    SKY_DEEP,
    "hydro":   NAVY,
    "thermal": BROWN,
    "residual": WARMGREY,      # thermal+hydro mass (2024 split pending)
}

# ── data-source palette for the coverage/provenance matrix ───────────────────
SOURCE = {
    "IEA":           NAVY,
    "StatSUZ":       GOLD,
    "IRENA":         LEAF,
    "World Bank":    WARMGREY,
    "Supplementary": PURPLE,
}

# ── single/pooled family palette for the model scoreboard ────────────────────
FAMILY = {
    "single": GOLD,    # single-country (deployed family)
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
