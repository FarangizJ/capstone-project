#!/usr/bin/env python3
"""
build_paper_latex.py
====================
Typeset docs/Capstone_Report.md into a two-column research-paper LaTeX source at
paper/Uzbekistan_Power_Sector_2040.tex, embedding the 12 regenerated 300-DPI
navy-palette figures from paper/figures/.

DESIGN PRINCIPLE — typeset, do not rewrite.
The markdown is the author's content of record. This builder renders it; it does
not invent numbers, citations, or narrative. The ~102 [CITE]/[VERIFY]/[TEMPLATE]
markers are kept VISIBLE (highlighted in amber so the author can find all of them
to fill from her own library). The author's manual figure/section numbering
("Figure 2.1", "Table 4.1", "4.5 ...") is preserved via unnumbered \\section*/
\\caption* so the in-text references never desync from auto-numbering.

The only content ADDED is the formal mathematics the brief asks for (Step 4):
ridge / Bayesian-ridge / ARIMA / ex-ante recursion / MAPE-R2 / loss gross-up /
scenario-generation / carbon-intensity identities. These formalize methods the
text already describes in words; no new quantities are introduced.

No local LaTeX toolchain is assumed; the .tex is written to compile on Overleaf
(pdfLaTeX). Escaping is placeholder-based so every %, &, $, _, ~, #, and the
unicode set (CO2, m^2, minus, approx, times, arrows, Greek) survive intact.

Run:  python scripts/build_paper_latex.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "Capstone_Report.md"
OUT = ROOT / "paper" / "Uzbekistan_Power_Sector_2040.tex"
FIGDIR = ROOT / "paper" / "figures"

# ── markdown figure path  ->  regenerated paper/figures/ stem ─────────────────
# every reference in the md points at ../outputs/<stem>.png or
# ../data/processed/<stem>.png; both remap to figures/<stem>.png (same stem).
def remap_fig(rel):
    return "figures/" + Path(rel).name

# ── figure layout: which span both columns (figure*) vs single column ─────────
# multi-panel / wide-aspect figures span both columns; the one near-square,
# simple single-panel chart (the capital-envelope bars) stays single-column to
# demonstrate the mixed layout the brief asked for.
FIG_SINGLE = {"forecast_investment.png"}   # everything else -> figure*

# ── table layout: 0-based order of appearance -> span both columns? ───────────
#  0 Table 4.1 demand hold-out (5 col, long names)      -> table*
#  1 sec 6.5 advisory categories (5 col, long text)     -> table*
#  2 App A full scoreboard (5 col)                       -> table*
#  3 App B LOCO (3 col, compact)                         -> table
#  4 App C coefficients (4 col)                          -> table*
#  5 App D.1 capital envelope (4 col)                    -> table*
#  6 App D.2 nuclear sensitivity (3 col, wide headers)   -> table*
#  7 App D.3 scenario endpoints (4 col)                  -> table*
# D.2's three headers ("Nuclear capacity" / "Nuclear output (2040)" /
# "RE+nuclear share (2040)") overrun a single column by ~101pt, so it spans
# both columns like its D.1/D.3 neighbours instead of bleeding into the gutter.
TABLE_STAR = {0, 1, 2, 4, 5, 6, 7}

# ── Step-4 mathematics, keyed to the subsection it follows ───────────────────
EQ = {}

EQ["4.2"] = r"""
\noindent The exploratory screen leaves the demand drivers mutually collinear at
$r\approx0.99$, which inflates the ordinary-least-squares variance
$\operatorname{Var}(\hat{\boldsymbol\beta}_{\mathrm{OLS}})=\sigma^2(\mathbf{X}^\top\mathbf{X})^{-1}$
toward instability. Ridge regression restores it by penalising the coefficient
norm:
\begin{equation}
\begin{aligned}
\hat{\boldsymbol\beta}_{\mathrm{ridge}}
   &=\arg\min_{\boldsymbol\beta}\;
   \bigl\lVert\mathbf{y}-\mathbf{X}\boldsymbol\beta\bigr\rVert_2^{2}
   +\lambda\lVert\boldsymbol\beta\rVert_2^{2}\\
   &=(\mathbf{X}^\top\mathbf{X}+\lambda\mathbf{I})^{-1}\mathbf{X}^\top\mathbf{y}.
\end{aligned}
\label{eq:ridge}
\end{equation}
The Bayesian ridge places a Gaussian prior $\boldsymbol\beta\sim\mathcal{N}(\mathbf{0},\lambda^{-1}\mathbf{I})$
on a likelihood of noise precision $\alpha$, giving the posterior and the
predictive law the Chapter~5 fan is read from:
\begin{equation}
\begin{aligned}
\boldsymbol\beta\mid\mathbf{y}\sim\mathcal{N}(\mathbf{m},\mathbf{S}),\quad
&\mathbf{S}=(\alpha\mathbf{X}^\top\mathbf{X}+\lambda\mathbf{I})^{-1},\\
&\mathbf{m}=\alpha\,\mathbf{S}\,\mathbf{X}^\top\mathbf{y},
\end{aligned}
\label{eq:bridge}
\end{equation}
\begin{equation}
\hat y_\ast\sim\mathcal{N}\!\bigl(\mathbf{x}_\ast^\top\mathbf{m},\,\sigma_\ast^{2}\bigr),
\quad
\sigma_\ast^{2}=\alpha^{-1}+\mathbf{x}_\ast^\top\mathbf{S}\,\mathbf{x}_\ast,
\label{eq:pred}
\end{equation}
with the reported band $\hat y_\ast\pm1.645\,\sigma_\ast$. Because $\sigma_\ast$
prices only coefficient and residual noise --- not driver-forecast or
structural-break error --- it is a \emph{lower} bound on true uncertainty
($\S5.3$).
"""

EQ["4.3"] = r"""
\noindent The order of integration is settled by an augmented Dickey--Fuller
regression on the levels,
\begin{equation}
\Delta y_t=c+\gamma\,y_{t-1}+\textstyle\sum_{j}\delta_j\,\Delta y_{t-j}+\varepsilon_t,
\label{eq:adf}
\end{equation}
whose unit-root null $\gamma=0$ cannot be rejected (statistic $\approx+1.15$,
$p\approx0.996$), so the series is differenced once. The selected baseline is an
$\mathrm{ARIMA}(1,1,0)$, i.e. an AR(1) on the first difference,
\begin{equation}
(1-\phi_1 L)(1-L)\,y_t=c+\varepsilon_t
\;\Longleftrightarrow\;
\Delta y_t=c+\phi_1\,\Delta y_{t-1}+\varepsilon_t .
\label{eq:arima}
\end{equation}
"""

EQ["4.4"] = r"""
\noindent \emph{Ex-ante} scoring forecasts each driver before the target and
feeds the demand lag from the model's own output, exactly as a live forecast
must:
\begin{equation}
\hat D_t=f\!\bigl(\hat{\mathbf{z}}_t,\ \hat D_{t-1}\bigr),\qquad t=T{+}1,\dots,T{+}h,
\label{eq:exante}
\end{equation}
where macro drivers follow a log random walk with drift,
$\ln\hat z_{t}=\ln z_{T}+(t-T)\,\hat g$, and climate is held at its recent
climatology. The conditional backcast instead substitutes the \emph{observed}
$\mathbf{z}_t$ and the \emph{true} $D_{t-1}$ --- the optimism the headline
declines. Models are scored by
\begin{equation}
\begin{aligned}
\mathrm{MAPE}&=\frac{100}{n}\sum_{i=1}^{n}\left|\frac{y_i-\hat y_i}{y_i}\right|,\\
R^{2}&=1-\frac{\sum_i (y_i-\hat y_i)^2}{\sum_i (y_i-\bar y)^2}.
\end{aligned}
\label{eq:scores}
\end{equation}
$R^{2}<0$ whenever the squared error exceeds the variance of the hold-out about
its own mean --- the model does worse than a flat line --- which is precisely
what the post-2018 break forces and what the table reports.
"""

EQ["5.4"] = r"""
\noindent Demand is grossed up to required generation at the forward
loss-reduction target $\ell\approx0.09$ ($\S6.1$),
\begin{equation}
G_t=D_t\,(1+\ell),
\label{eq:gross}
\end{equation}
giving the single generation path shared by all three scenarios
($80.6\rightarrow135.1$ TWh). Each renewable technology's output is its capacity
times an annualised capacity factor, and thermal is the residual that closes the
balance:
\begin{equation}
G_{k,t}=\mathrm{CF}_k\cdot \mathrm{Cap}_{k,t}\cdot 8760,\quad
G_{\mathrm{th},t}=G_t-\!\!\sum_{k\neq\mathrm{th}}\!\! G_{k,t},
\label{eq:mix}
\end{equation}
for $k\in\{\text{solar},\text{wind},\text{hydro}\}$, with the renewable share
$s_t=\bigl(\sum_{k\in\mathrm{RE}}G_{k,t}\bigr)/G_t$.
"""

EQ["5.7"] = r"""
\noindent Grid carbon intensity is the generation-weighted emission factor, and
annual power-sector emissions follow by multiplication:
\begin{equation}
I_t=\frac{\sum_k G_{k,t}\,\mathrm{EF}_k}{G_t}\;\bigl[\text{gCO}_2/\text{kWh}\bigr],
\qquad
\mathrm{CO}_{2,t}=I_t\,G_t,
\label{eq:carbon}
\end{equation}
with $\mathrm{EF}_{\mathrm{th}}$ the gas-weighted thermal factor
(88\% gas / 12\% coal) and $\mathrm{EF}_k=0$ for solar, wind and hydro.
"""

# ── LaTeX preamble (two-column article, navy headings, Overleaf-safe) ─────────
PREAMBLE = r"""% !TEX program = pdflatex
% ============================================================================
% Uzbekistan's Power Sector to 2040  --  two-column capstone research paper.
% Typeset by scripts/build_paper_latex.py from docs/Capstone_Report.md.
% Compiles with pdfLaTeX (Overleaf: default TeX Live). Run twice for the ToC.
% Figures live in ./figures/ (12 regenerated 300-DPI navy-palette PNGs).
% Author fills the amber [CITE]/[VERIFY]/[TEMPLATE] markers from her library.
% ============================================================================
\documentclass[10pt,twocolumn]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}     % source is ASCII after escaping; harmless to keep
\usepackage{lmodern}
\usepackage[english]{babel}

\usepackage[letterpaper,margin=0.85in,columnsep=0.28in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}  % wrapping, left-ragged
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{siunitx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{caption}
\usepackage{titlesec}
\usepackage{titletoc}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage[hidelinks]{hyperref}

% ── brand palette (matches figure_style_for_notebooks.py) ────────────────────
\definecolor{navy}{HTML}{0D4D7A}
\definecolor{teal}{HTML}{0E7C7B}
\definecolor{amber}{HTML}{A85B00}   % darkened for legible body-weight marker text
\definecolor{ink}{HTML}{1F2937}
\definecolor{rulegrey}{HTML}{AAAAAA}
\definecolor{metagrey}{HTML}{6B7280}   % calm grey for "reference complete" tags

\hypersetup{
  colorlinks=true, linkcolor=navy, urlcolor=navy, citecolor=navy,
  pdftitle={Uzbekistan's Power Sector to 2040},
  pdfauthor={Farangiz Jurakhonova}
}

% ── visible-but-distinct markers ─────────────────────────────────────────────
%   \mk      amber, action-needed: [CITE: ...] slots, [VERIFY: ...], [TEMPLATE]
%   \mkdone  calm grey, informational: [CITE-COMPLETE] (reference already filled)
\newcommand{\mk}[1]{{\color{amber}\small #1}}
\newcommand{\mkdone}[1]{{\color{metagrey}\footnotesize #1}}

% ── navy section headings, author's own numbering kept (unnumbered) ──────────
\titleformat{\section}{\normalfont\large\bfseries\color{navy}}{}{0pt}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries\color{navy}}{}{0pt}{}
\titlespacing*{\section}{0pt}{10pt}{5pt}
\titlespacing*{\subsection}{0pt}{7pt}{3pt}

% ── caption style: small, author's "Figure 2.1." text carries the number ─────
\captionsetup{font={small},labelformat=empty,justification=justified,
  singlelinecheck=false,skip=4pt}

% ── float placement: this is a float-heavy two-column paper (12 figures, 8
%    tables, most spanning both columns). Relax the default placement budget so
%    the starred (full-width) floats settle at page tops / float pages instead
%    of deferring and triggering "Too many unprocessed floats". Package-free. ──
\setcounter{topnumber}{3}\setcounter{dbltopnumber}{4}
\setcounter{bottomnumber}{2}\setcounter{totalnumber}{6}
\renewcommand{\topfraction}{0.92}\renewcommand{\dbltopfraction}{0.92}
\renewcommand{\bottomfraction}{0.5}\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.66}\renewcommand{\dblfloatpagefraction}{0.66}

\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\sloppy   % small column width: prefer loose spacing over overfull lines

% ── footer: page X of Y ──────────────────────────────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\small\color{ink} Page \thepage\ of \pageref{LastPage}}

\begin{document}
"""

# ── placeholder-based LaTeX escaping (specials + unicode), Overleaf-safe ──────
_SPECIAL = [
    ("\\", r"\textbackslash{}"),
    ("{", r"\{"), ("}", r"\}"),
    ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
    ("^", r"\textasciicircum{}"),
    ("~", r"$\sim$"),                 # every '~' in this document means "approx."
    ("<", r"\textless{}"), (">", r"\textgreater{}"),
    (" ", " "),                  # nbsp -> normal space
    ("§", r"\S{}"),              # section sign
    ("−", r"$-$"),               # minus
    ("—", r"---"), ("–", r"--"),
    ("≈", r"$\approx$"), ("×", r"$\times$"), ("±", r"$\pm$"),
    ("≥", r"$\ge$"), ("≤", r"$\le$"),
    ("→", r"$\rightarrow$"),
    ("·", r"$\cdot$"), ("…", r"\ldots{}"),
    ("“", r"``"), ("”", r"''"), ("‘", r"`"), ("’", r"'"),
    ("°", r"$^\circ$"),
    ("₂", r"\textsubscript{2}"),
    ("²", r"\textsuperscript{2}"), ("³", r"\textsuperscript{3}"),
    ("α", r"$\alpha$"), ("β", r"$\beta$"), ("γ", r"$\gamma$"),
    ("Δ", r"$\Delta$"), ("μ", r"$\mu$"), ("σ", r"$\sigma$"),
    ("≡", r"$\equiv$"),
]
_MAP = dict(_SPECIAL)
_KEYS = sorted(_MAP, key=len, reverse=True)
_PAT = re.compile("|".join(re.escape(k) for k in _KEYS))

def _smart_double_quotes(s):
    """Straight ASCII " -> curly “/” by the standard whitespace heuristic, so
    the existing _SPECIAL mappings turn them into LaTeX ``/''. An opening quote
    follows start-of-string, whitespace, or an opening bracket/dash; every other
    " closes. (Apostrophes ' are left as-is: LaTeX already renders them ’.)"""
    out, opener = [], " \t\n([{—–-/"
    for i, ch in enumerate(s):
        if ch == '"':
            prev = s[i - 1] if i > 0 else ""
            out.append("“" if prev == "" or prev in opener else "”")
        else:
            out.append(ch)
    return "".join(out)

def latex_escape(s):
    s = _smart_double_quotes(s)
    bucket = []
    def grab(m):
        bucket.append(m.group(0))
        return "\x00%d\x00" % (len(bucket) - 1)
    s = _PAT.sub(grab, s)
    return re.sub(r"\x00(\d+)\x00", lambda m: _MAP[bucket[int(m.group(1))]], s)

INLINE_RE = re.compile(r"\*\*(.+?)\*\*|\*([^*]+?)\*|`([^`]+)`")
MARKER_RE = re.compile(r"\[(?:CITE|VERIFY|TEMPLATE)[^\]]*\]")
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")

def highlight(s):
    def wrap(m):
        tok = m.group(0)
        # [CITE-COMPLETE] is a "done" status tag on a finished reference entry,
        # not a to-do slot -> calm grey, so the reference list does not read as
        # 26 unfinished items. Everything else stays action-amber.
        cmd = r"\mkdone" if tok.startswith("[CITE-COMPLETE") else r"\mk"
        return cmd + "{" + tok + "}"
    return MARKER_RE.sub(wrap, s)

def code_span(s):
    """markdown `inline code` -> \\texttt{}, with break opportunities after / and
    _ so a long file path can wrap inside the narrow two-column measure."""
    esc = latex_escape(s).replace("/", r"/\allowbreak{}") \
                         .replace(r"\_", r"\_\allowbreak{}")
    return r"\texttt{" + esc + "}"

def inline(text):
    out, pos = [], 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append(latex_escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(r"\textbf{" + latex_escape(m.group(1)) + "}")
        elif m.group(2) is not None:
            out.append(r"\textit{" + latex_escape(m.group(2)) + "}")
        else:
            out.append(code_span(m.group(3)))
        pos = m.end()
    if pos < len(text):
        out.append(latex_escape(text[pos:]))
    return highlight("".join(out))

# ── tables ───────────────────────────────────────────────────────────────────
def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]

def is_sep(line):
    s = line.strip()
    if not s.startswith("|"):
        return False
    cells = split_row(s)
    return len(cells) > 0 and all(re.match(r"^:?-{2,}:?$", c) for c in cells)

def col_align(sepcell):
    sc = sepcell.strip()
    if sc.startswith(":") and sc.endswith(":"):
        return "c"
    if sc.endswith(":"):
        return "r"
    return "l"

def emit_table(rows, star, caption, note):
    header = split_row(rows[0])
    aligns = [col_align(c) for c in split_row(rows[1])]
    body = [split_row(r) for r in rows[2:]]
    ncol = len(header)
    while len(aligns) < ncol:
        aligns.append("l")
    env = "table*" if star else "table"
    placement = "tp" if star else "tbp"   # starred floats: top or float-page only
    out = [r"\begin{%s}[%s]" % (env, placement), r"\centering"]
    if caption:
        out.append(r"\caption*{%s}" % caption)
    out.append(r"\renewcommand{\arraystretch}{1.18}\small")
    if star:                                   # tabularx -> long text wraps (L)
        # left columns become stretchy L so prose wraps; but a uniformly short
        # left column (e.g. a "#" index) stays fixed-width l so it does not claim
        # an equal share of the wrap space and squeeze the real text columns.
        def colmax(j):
            vals = [header[j]] + [r[j] for r in body if j < len(r)]
            return max((len(v) for v in vals), default=0)
        spec = "".join(("L" if colmax(j) > 3 else "l") if a == "l" else a
                       for j, a in enumerate(aligns))
        if "L" not in spec:                    # tabularx needs >=1 stretchy column
            spec = "L" + spec[1:]
        out.append(r"\begin{tabularx}{\textwidth}{%s}" % spec)
    else:                                      # compact -> plain tabular
        out.append(r"\begin{tabular}{%s}" % "".join(aligns))
    out.append(r"\toprule")
    out.append(" & ".join(r"\textbf{%s}" % inline(c) for c in header) + r" \\")
    out.append(r"\midrule")
    for row in body:
        cells = [inline(row[j]) if j < len(row) else "" for j in range(ncol)]
        out.append(" & ".join(cells) + r" \\")
    out.append(r"\bottomrule")
    out.append(r"\end{tabularx}" if star else r"\end{tabular}")
    if note:
        out.append(r"\par\smallskip{\footnotesize\itshape %s}" % note)
    out.append(r"\end{%s}" % env)
    return "\n".join(out)

# ── figures ──────────────────────────────────────────────────────────────────
def emit_figure(rel, caption):
    name = Path(rel).name
    single = name in FIG_SINGLE
    # starred (full-width) floats may only be [t]/[p]; allow both so LaTeX can
    # flush them to a float page rather than deferring. Single-col floats: [tbp].
    if name == "fleet_evolution_4panel.png":
        placement = "p"          # tall 4-panel -> its own float page
    elif single:
        placement = "tbp"
    else:
        placement = "tp"
    env = "figure" if single else "figure*"
    width = r"\columnwidth" if single else r"\textwidth"
    out = [r"\begin{%s}[%s]" % (env, placement), r"\centering",
           r"\includegraphics[width=%s]{%s}" % (width, remap_fig(rel))]
    if caption:
        out.append(r"\caption*{%s}" % caption)
    out.append(r"\end{%s}" % env)
    return "\n".join(out)

def strip_emph(s):
    """drop a single wrapping *...* (figure-caption / table-note italics)."""
    s = s.strip()
    if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
        return s[1:-1]
    return s

def caption_text(raw):
    """render a caption line italic-small; markers stay highlighted."""
    return r"\itshape " + inline(strip_emph(raw))

# ── front matter (title page + abstract + declarations + ToC) ────────────────
def front_matter(abstract, keywords, decl_lines, client_verify):
    L = []
    L.append(r"\pagestyle{empty}\onecolumn")
    L.append(r"\begin{center}\vspace*{0.9in}")
    L.append(r"{\color{navy}\Huge\bfseries Uzbekistan's Power Sector to 2040\par}")
    L.append(r"\vspace{12pt}{\large\itshape Forecasting Demand, Bounding "
             r"Uncertainty, and Locating Advisory Opportunity\par}")
    L.append(r"\vspace{0.45in}{\Large\textbf{Farangiz Jurakhonova}\par}")
    L.append(r"\vspace{5pt}MSc in Business Analytics, Central European University\par")
    L.append(r"\vspace{0.5in}")
    L.append(r"\begin{tabular}{r@{\quad}l}")
    L.append(r"\textbf{Supervisor:} & Francesca Conselvan\\[3pt]")
    L.append(r"\textbf{Capstone client:} & ILF Consulting Engineers Austria GmbH\\[3pt]")
    L.append(r"\textbf{Sponsor:} & Ardak Akhatova, ILF Consulting Engineers Austria GmbH\\[3pt]")
    L.append(r"\textbf{Date:} & June 2026\\")
    L.append(r"\end{tabular}\par")
    # the title-page client descriptor carries a [VERIFY] marker; render it small
    # and amber-highlighted beneath the metadata block. The \par above closes the
    # tabular's line so the marker drops below it rather than running off its right.
    L.append(r"\vspace{12pt}")
    mv = MARKER_RE.search(client_verify)
    if mv:
        L.append(r"{\footnotesize " + highlight(latex_escape(mv.group(0))) + r"\par}")
    L.append(r"\end{center}\clearpage")
    # abstract / declarations / contents on one full-width column
    L.append(r"\phantomsection\addcontentsline{toc}{section}{Abstract}"
             r"\section*{Abstract}")
    L.append(inline(abstract))
    L.append(r"\vspace{4pt}\noindent\textbf{Keywords:}~" + inline(keywords))
    L.append(r"\phantomsection\addcontentsline{toc}{section}{Declarations}"
             r"\section*{Declarations}")
    for dl in decl_lines:
        L.append(inline(dl))
    # Only register the ToC entry + hyperref anchor here; the heading itself is
    # printed by \tableofcontents below. Emitting \section*{Contents} as well
    # would double the "Contents" title on the page.
    L.append(r"\phantomsection\addcontentsline{toc}{section}{Contents}")
    # ToC entries are added numberless (\addcontentsline, no \numberline; the
    # author's "1 ---", "4.2" prefixes live in the title text), so style them via
    # the *numberless* slot and leave the numbered/\contentslabel slot empty.
    # Dotted leaders to the page number; subsections indented one level.
    L.append(r"{\small\setlength{\parskip}{1.5pt}\renewcommand{\baselinestretch}{0.98}"
             r"\titlecontents{section}[0em]{\smallskip}{}{}"
             r"{\titlerule*[0.6pc]{.}\contentspage}"
             r"\titlecontents{subsection}[1.6em]{}{}{}"
             r"{\titlerule*[0.6pc]{.}\contentspage}"
             r"\tableofcontents}")
    L.append(r"\clearpage\pagestyle{fancy}\twocolumn")
    return "\n".join(L)

# ── main parse loop ───────────────────────────────────────────────────────────
def heading(level, text, toc_level):
    cmd = r"\section*" if level == 1 else r"\subsection*"
    t = inline(text)
    return (r"\phantomsection\addcontentsline{toc}{%s}{%s}%s{%s}"
            % (toc_level, t, cmd, t))

def build():
    lines = MD.read_text(encoding="utf-8").split("\n")
    n = len(lines)

    # pull abstract, keywords, declarations, client VERIFY out of the front matter
    abstract = keywords = ""
    decl_lines, client_verify = [], ""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("**Capstone client:**"):
            client_verify = s
        if s == "## Abstract":
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            abstract = lines[j].strip()
        if s.startswith("**Keywords:**"):
            keywords = s.split("**Keywords:**", 1)[1].strip()
        if s.startswith("**Use of generative AI") or s.startswith("**Authorship"):
            decl_lines.append(s)

    body = [PREAMBLE,
            front_matter(abstract, keywords, decl_lines, client_verify)]

    pending_caption = None      # bold "Table 4.1." / "D.1 ..." lead-in
    table_index = -1
    in_list = False
    body_started = False
    stats = {"sections": 0, "subsections": 0, "figs": 0, "tables": 0,
             "bullets": 0, "paras": 0, "eqs": 0}

    def close_list():
        nonlocal in_list
        if in_list:
            body.append(r"\end{itemize}")
            in_list = False

    i = 0
    while i < n:
        raw = lines[i]
        s = raw.strip()

        # skip the leading HTML drafting-conventions comment
        if s.startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if s == "" or s == "---":
            i += 1
            continue

        # title-page metadata (Author/Programme/Client/Date) is rendered by
        # front_matter() on the cover; skip the source lines so they do not
        # reappear as body paragraphs after the title page.
        if any(s.startswith(lbl) for lbl in
               ("**Author:**", "**Programme:**",
                "**Capstone client:**", "**Date:**")):
            i += 1
            continue

        # headings
        if s.startswith("#"):
            close_list()
            lvl = len(s) - len(s.lstrip("#"))
            text = s[lvl:].strip()
            # front-matter headings handled in front_matter(); skip them here
            if text.startswith("Uzbekistan's Power Sector"):      # title
                i += 1; continue
            if lvl == 3 and text.startswith("Forecasting Demand"):  # subtitle
                i += 1; continue
            if text in ("Abstract", "Declarations", "Table of contents"):
                # consume Abstract paragraph / declarations / toc placeholder block
                i += 1
                while i < n and not lines[i].strip().startswith("#") \
                        and lines[i].strip() != "---":
                    i += 1
                continue
            # first numbered chapter -> switch into two columns + arabic pages
            if lvl == 1 and re.match(r"^\d", text) and not body_started:
                body.append(r"\pagenumbering{arabic}")
                body_started = True
            if lvl == 1:
                body.append(heading(1, text, "section"))
                stats["sections"] += 1
            elif lvl == 2:
                body.append(heading(2, text, "subsection"))
                stats["subsections"] += 1
                key = text.split()[0]                 # e.g. "4.2"
                if key in EQ:
                    body.append(EQ[key].strip())
                    stats["eqs"] += 1
            else:
                body.append(heading(2, text, "subsection"))
                stats["subsections"] += 1
            i += 1
            continue

        # standalone image -> figure float (consume the following caption)
        m = IMG_RE.match(s)
        if m:
            close_list()
            cap = None
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and lines[j].strip().startswith("*Figure"):
                cap = caption_text(lines[j].strip())
                i = j
            body.append(emit_figure(m.group(2), cap))
            stats["figs"] += 1
            i += 1
            continue

        # bold table caption lead-in ("**Table 4.1. ...**", "**D.1 ...**")
        if (s.startswith("**Table ") or re.match(r"^\*\*D\.\d", s)):
            close_list()
            pending_caption = inline(s)   # inline() renders the **bold** lead-in
            i += 1
            continue

        # table block
        if s.startswith("|") and (i + 1 < n) and is_sep(lines[i + 1]):
            close_list()
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            # optional italic note line after the table
            note = None
            j = i
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n and lines[j].strip().startswith("*") \
                    and lines[j].strip().endswith("*") \
                    and not lines[j].strip().startswith("**"):
                note = inline(strip_emph(lines[j].strip()))
                i = j + 1
            table_index += 1
            cap = pending_caption                       # bold lead-in if present
            if cap is None:                             # else fall back to subsection
                cap = None
            body.append(emit_table(block, table_index in TABLE_STAR, cap, note))
            pending_caption = None
            stats["tables"] += 1
            continue

        # bullet list
        if s.startswith("- "):
            if not in_list:
                body.append(r"\begin{itemize}[leftmargin=1.2em,itemsep=1pt,topsep=2pt]")
                in_list = True
            body.append(r"\item " + inline(s[2:].strip()))
            stats["bullets"] += 1
            i += 1
            continue

        # normal paragraph
        close_list()
        body.append(inline(s))
        stats["paras"] += 1
        i += 1

    close_list()
    body.append(r"\end{document}")
    OUT.write_text("\n\n".join(body), encoding="utf-8")
    return stats

if __name__ == "__main__":
    st = build()
    txt = OUT.read_text(encoding="utf-8")
    print("=== LaTeX BUILD COMPLETE ===")
    print("output :", OUT)
    print("bytes  :", len(txt.encode("utf-8")))
    print("lines  :", txt.count("\n") + 1)
    for k, v in st.items():
        print(f"  {k:11}: {v}")
    # quick guards
    action = txt.count(r"\mk{")
    done = txt.count(r"\mkdone{")
    print("  markers    :", action, "amber action ([CITE:]/[VERIFY]/[TEMPLATE])",
          "+", done, "grey done ([CITE-COMPLETE])")
    miss = [Path(p).name for p in re.findall(r"includegraphics\[[^]]*\]\{([^}]+)\}", txt)
            if not (FIGDIR / Path(p).name).exists()]
    print("  fig files  :", "all present" if not miss else "MISSING: " + ", ".join(miss))
