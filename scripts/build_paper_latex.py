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

# ── DNV key-finding callouts, keyed to the subsection they open ──────────────
# Each box quotes a figure already stated in that chapter's prose; none is a new
# quantity. The four chosen are the stakes the brief flags: the demand
# trajectory, the BAU renewable-share reversal, the BAU-vs-Accelerated carbon
# gap, and the realized-vs-target loss gap. Keys avoid the EQ keys so no heading
# carries both an equation and a callout.
CALLOUT = {}
CALLOUT["5.2"] = r"""
\keystat{Demand to 2040}{74 $\rightarrow$ 86 $\rightarrow$ 124 TWh}%
{Electricity demand rises about 2.5\% a year to 2030, then climbs further on a
deliberately growth-optimistic terminal tail held flat from 2031 ($\S$5.2).}
"""
CALLOUT["5.5"] = r"""
\keystat{BAU renewable share}{43\% (2030) $\rightarrow$ 36\% (2040)}%
{A build-out that is not sustained does not merely stall the transition --- it
\emph{reverses} it, ceding the post-2030 demand increment back to gas ($\S$5.5).}
"""
CALLOUT["5.8"] = r"""
\keystat{2040 power-sector carbon intensity}{436 vs 90 gCO\textsubscript{2}/kWh}%
{The BAU-versus-Accelerated spread is nearly fivefold, and it is decided by
build-out policy, not by anything the demand forecast can settle ($\S$5.7).}
"""
CALLOUT["6.1"] = r"""
\keystat{T\&D losses: realized vs target}{$\sim$16\% vs $\sim$9\%}%
{About seven percentage points of throughput is lost above what a modernised
network would lose --- the single largest efficiency prize in the data ($\S$6.1).}
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
\usepackage[default]{lato}      % humanist sans (DNV idiom) for body + headings
\usepackage[english]{babel}

% Horizontal margins held at 0.85in (column width unchanged -> no text reflow);
% vertical margins tightened to 0.72in to add ~0.26in of body height per page,
% which both fits more lines and gives the full-width floats more room to settle
% -- the deterministic lever for the <=30-page budget after Step-4 additions.
\usepackage[letterpaper,top=0.72in,bottom=0.72in,left=0.85in,right=0.85in,%
            headheight=13pt,headsep=9pt,columnsep=0.28in]{geometry}
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
\usepackage[most]{tcolorbox}     % DNV-style tinted key-finding callout panels
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}                 % break long reference-list URLs anywhere (no overfull lines)

% ── DNV-style brand palette (matches figure_style_for_notebooks.py) ──────────
\definecolor{navy}{HTML}{003591}     % primary   — headings, rules, links
\definecolor{sky}{HTML}{9DC3E6}      % secondary — tinted callout/opener panels
\definecolor{skydeep}{HTML}{3E7CB1}  % legible mid-sky for rules on white
\definecolor{leaf}{HTML}{5C9A3C}     % accent/"good"
\definecolor{warmgrey}{HTML}{B4ADA3} % neutral
\definecolor{teal}{HTML}{3E7CB1}     % back-compat alias → mid-sky
\definecolor{amber}{HTML}{A85B00}    % action markers ONLY — deliberately unchanged
\definecolor{ink}{HTML}{1F2937}
\definecolor{rulegrey}{HTML}{B4ADA3}
\definecolor{metagrey}{HTML}{6B7280}   % calm grey for "reference complete" tags
\definecolor{panelgrey}{HTML}{EEF2F6} % very-pale panel tint for opener bands

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

% ── DNV-style key-finding callout ────────────────────────────────────────────
%   A pale-navy panel with a thick navy left bar carrying one headline number.
%   These quote figures already in the prose (no new quantity); they are a
%   design device that lifts the four results the brief flags as the stakes of
%   the report. \keystat{kicker}{big stat}{one-line gloss}.
\newtcolorbox{keystatbox}{
  enhanced, breakable=false, sharp corners,
  colback=panelgrey, colframe=panelgrey,
  borderline west={2.6pt}{0pt}{navy},
  boxrule=0pt, left=10pt, right=8pt, top=6pt, bottom=6pt,
  before skip=8pt, after skip=8pt,
}
\newcommand{\keystat}[3]{%
  \begin{keystatbox}%
  {\footnotesize\bfseries\color{skydeep}#1}\par\vspace{1pt}%
  {\Large\bfseries\color{navy}#2}\par\vspace{2pt}%
  {\footnotesize\color{ink}#3}%
  \end{keystatbox}}

% ── navy section headings, author's own numbering kept (unnumbered) ──────────
%   DNV chapter-opener idiom: the chapter (\section) head is set large in navy
%   with a thin sky rule drawn beneath it; subsections stay compact. The rule is
%   column-wide in the two-column body and page-wide on the front matter.
\titleformat{\section}{\normalfont\Large\bfseries\color{navy}}{}{0pt}{}
  [{\vspace{1pt}{\color{skydeep}\titlerule[1.1pt]}}]
\titleformat{\subsection}{\normalfont\normalsize\bfseries\color{navy}}{}{0pt}{}
\titlespacing*{\section}{0pt}{10pt}{5pt}
\titlespacing*{\subsection}{0pt}{6pt}{3pt}

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
% \dblfloatpagefraction is the dominant lever for the "gap between graphs"
% complaint. At the old 0.66 a pair of medium figures (~75% of the page) was
% allowed to form a half-empty FLOAT PAGE, and the kernel's double-float page
% glue then spreads them apart with infinite stretch that \@fpsep/\raggedbottom
% cannot reach. Raising it to 0.88 forbids a float page unless the floats nearly
% fill it, so such pairs are instead set at the TOP of ordinary text pages (one
% per page top, body text beneath, \raggedbottom pooling any slack at the foot) —
% no mid-page gap. A genuinely page-filling figure still gets its own float page,
% where >88% occupancy leaves too little slack to spread visibly.
\renewcommand{\floatpagefraction}{0.85}\renewcommand{\dblfloatpagefraction}{0.88}
% Float-page vertical spacing. Pin floats to the TOP (\@fptop=0pt, no top
% stretch); give STACKED floats a fixed separation (\@fpsep) with no infinite
% "fil" — the default \@fpsep carries 2fil of stretch, and that is exactly what
% was injecting large blank gaps BETWEEN the graphs on figure-only pages; and
% let all leftover space pool at the BOTTOM (\@fpbot). Net effect: graphs stack
% snugly under one another at the top and the empty space sits below them.
\makeatletter
\setlength{\@fptop}{0pt}
\setlength{\@fpsep}{14pt plus 0pt minus 3pt}
\setlength{\@fpbot}{0pt plus 1fil}
\makeatother

% ── tighter float moats (DNV idiom is densely set) — reclaims the page the
%    Step-4 callouts/openers added without reshuffling float placement. The
%    \dbltextfloatsep governs the gap around the many full-width figure* / table*
%    floats and is the dominant lever here. ────────────────────────────────────
\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{12pt plus 2pt minus 2pt}
\setlength{\floatsep}{9pt plus 2pt minus 2pt}
\setlength{\dblfloatsep}{9pt plus 2pt minus 2pt}
\setlength{\intextsep}{9pt plus 2pt minus 2pt}

% ── ragged bottom: the two-column class default is \flushbottom, which STRETCHES
%    the vertical glue on every page so the last line sits exactly on the bottom
%    margin. On a page that carries a figure at the top and text/another figure
%    below, that stretch is distributed as large blank GAPS between the graph and
%    whatever follows — the "unprofessional space between graphs" the author saw.
%    \raggedbottom turns the stretch off: floats and text pack together at their
%    natural separation (the \floatsep/\textfloatsep moats above) and ALL leftover
%    space collects as one clean block at the page bottom — i.e. "cut the gap and
%    align so there is no gap further after." Pairs with the \@fpbot=...1fil rule
%    that already pools slack at the bottom of pure float pages. ────────────────
\raggedbottom

% ── the LAST gap source: when two full-width figure* floats land together on a
%    figure-only page (no body text — e.g. a full-page map pair, or the terminal
%    appendix figures), the kernel assembles that page in \@combinedblfloats as a
%    "\vbox to\textheight" holding the stacked floats + \dbltextfloatsep + an
%    EMPTY body box. With no text, the only stretchable glue is the finite
%    \dblfloatsep, so the "to\textheight" target is met by spreading the shortfall
%    BETWEEN the two graphs — the residual mid-page gap that \@fpsep/\raggedbottom
%    cannot reach (that path is governed by \@combinedblfloats, not \@fptop/etc.).
%    The fix is one token: append \vfil inside that vbox so leftover height always
%    pools at the FOOT of the page and the figures stay flush at the top, whether
%    or not body text is present. The redefinition is the current LaTeX kernel
%    macro verbatim (ltoutput) with the trailing \vfil added. ───────────────────
\makeatletter
\def\@combinedblfloats{%
  \ifx\@dbltoplist\@empty
  \else
    \setbox\@tempboxa\vbox{}%
    \let\@elt\@comdblflelt
    \@dbltoplist
    \let\@elt\relax
    \xdef\@freelist{\@freelist\@dbltoplist}%
    \global\let\@dbltoplist\@empty
    \setbox\@outputbox\vbox to\textheight{%
       \unvbox\@tempboxa\vskip-\dblfloatsep
       \ifnum\@dbltopnum>\m@ne
         \dblfigrule
       \fi
       \vskip\dbltextfloatsep
       \unvbox\@outputbox
       \vfil}%
  \fi
}
\makeatother

\setlength{\parindent}{0pt}
\setlength{\parskip}{2pt}
\sloppy   % small column width: prefer loose spacing over overfull lines
\setlength{\emergencystretch}{3em}   % last-resort stretch so justified columns never overflow

% ── no end-of-line word-breaking: keep every word whole and never split it with
%    a trailing hyphen. hyphenpenalty/exhyphenpenalty=10000 forbid both
%    discretionary hyphenation and breaks at existing hyphens (so "single-country"
%    stays intact too); \sloppy + the larger \emergencystretch above take up the
%    slack so the justified columns still never overflow into the margin. The
%    proper-noun list below is now redundant but kept as belt-and-suspenders. ───
\hyphenpenalty=10000
\exhyphenpenalty=10000
\hyphenation{Uzbekistan Uzbekenergo Kazakhstan Kyrgyzstan Tajikistan
             Turkmenistan Karakalpakstan Jizzakh DataVolt}

% ── running header (grey title left / programme right, thin grey rule) +
%    footer (page X of Y). The header is suppressed on the cover and front
%    matter, which run under \pagestyle{empty}. ───────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize\itshape\color{metagrey}Uzbekistan's Power Sector to 2040}
\fancyhead[R]{\footnotesize\color{metagrey}CEU MSc Business Analytics}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{{\color{rulegrey}\hrule height\headrulewidth}}
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

INLINE_RE = re.compile(r"\*\*(.+?)\*\*|\*([^*]+?)\*|`([^`]+)`|(https?://[^\s)\]]+)")
MARKER_RE = re.compile(r"\[(?:CITE|VERIFY|TEMPLATE)[^\]]*\]")
FN_RE = re.compile(r"\[FN:\s*([^\]]*)\]")
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")

def highlight(s):
    # [FN: ...] is a RESOLVED self-citation: its source has been double-checked
    # against the repo's own data, so it becomes a real footnote — a small
    # superscript number in the text and the source line at the column bottom —
    # rather than an amber to-do. Only repo-traceable sources are ever promoted
    # to [FN:]; unresolved [CITE:]/[VERIFY:] stay amber for the author to fill.
    s = FN_RE.sub(lambda m: r"\footnote{" + m.group(1).strip() + "}", s)
    s = s.replace(r" \footnote{", r"\footnote{")   # mark hugs the preceding word

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
        elif m.group(3) is not None:
            out.append(code_span(m.group(3)))
        else:                                  # bare URL -> breakable navy link
            out.append(r"\url{" + m.group(4) + "}")
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
    # ── DNV-style cover: a navy/sky top band, a small-caps eyebrow, the navy
    #    title with a sky accent rule, the italic deck, the author block, and a
    #    matching band at the foot. Top-anchored, single page. ─────────────────
    L.append(r"\vspace*{0.5in}")
    L.append(r"\noindent{\color{navy}\rule{\textwidth}{2.4pt}}\\[3pt]")
    L.append(r"\noindent{\color{skydeep}\rule{\textwidth}{0.6pt}}\par")
    L.append(r"\vspace{0.5in}")
    L.append(r"\begin{center}")
    L.append(r"{\footnotesize\color{metagrey}\textsc{Central European University "
             r"\textperiodcentered\ MSc Business Analytics "
             r"\textperiodcentered\ Capstone Research Paper}\par}")
    L.append(r"\vspace{18pt}")
    L.append(r"{\color{navy}\Huge\bfseries Uzbekistan's Power Sector to 2040\par}")
    L.append(r"\vspace{12pt}{\color{skydeep}\rule{2.3in}{1.4pt}}\par")
    L.append(r"\vspace{12pt}{\large\itshape\color{ink} Forecasting Demand, Bounding "
             r"Uncertainty, and Locating Advisory Opportunity\par}")
    L.append(r"\vspace{0.5in}{\Large\textbf{Farangiz Jurakhonova}\par}")
    L.append(r"\vspace{5pt}{\color{metagrey}MSc in Business Analytics, "
             r"Central European University\par}")
    L.append(r"\vspace{0.45in}")
    L.append(r"\begin{tabular}{r@{\quad}l}")
    L.append(r"{\color{navy}\bfseries Supervisors:} & Eduardo Ari\~{n}o de la Rubia\\[1pt]")
    L.append(r" & Francesca Conselvan\\[3pt]")
    # client name on the metadata row; any descriptor after the em-dash in the
    # markdown client line renders as a discreet grey subline beneath the name.
    desc = client_verify.split("—", 1)[1].strip() if "—" in client_verify else ""
    client_cell = r"ILF Consulting Engineers Austria GmbH"
    if desc:
        client_cell += (r"\\[1pt] & {\footnotesize\itshape\color{metagrey}"
                        + latex_escape(desc) + r"}")
    L.append(r"{\color{navy}\bfseries Capstone client:} & " + client_cell + r"\\[3pt]")
    L.append(r"{\color{navy}\bfseries Sponsor:} & Ardak Akhatova, ILF Consulting Engineers Austria GmbH\\[3pt]")
    L.append(r"{\color{navy}\bfseries Date:} & June 2026\\")
    L.append(r"\end{tabular}\par")
    L.append(r"\end{center}")
    L.append(r"\vfill")
    L.append(r"\noindent{\color{skydeep}\rule{\textwidth}{0.6pt}}\\[3pt]")
    L.append(r"\noindent{\color{navy}\rule{\textwidth}{2.4pt}}")
    L.append(r"\vspace{6pt}")
    L.append(r"\begin{center}{\footnotesize\color{metagrey}"
             r"\textcopyright\ 2026 Farangiz Jurakhonova \textperiodcentered\ "
             r"Licensed under Creative Commons Attribution-NonCommercial 4.0 "
             r"International (CC BY-NC 4.0) \textperiodcentered\ Not for sale."
             r"}\end{center}")
    L.append(r"\vspace{0.3in}")
    L.append(r"\clearpage")
    # abstract / declarations / contents on one full-width column. Front-matter
    # section headings are set a touch tighter than body chapters so the whole
    # block (abstract + declarations + section-level ToC) lands on one page.
    L.append(r"\begingroup\titlespacing*{\section}{0pt}{4pt}{4pt}")
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
    L.append(r"{\renewcommand{\baselinestretch}{0.9}\small\setlength{\parskip}{0.3pt}"
             r"\titlecontents{section}[0em]{\vspace{0.5pt}}{}{}"
             r"{\titlerule*[0.6pc]{.}\contentspage}"
             r"\titlecontents{subsection}[1.6em]{}{}{}"
             r"{\titlerule*[0.6pc]{.}\contentspage}"
             r"\tableofcontents}")
    L.append(r"\endgroup")
    L.append(r"\clearpage\pagestyle{fancy}\twocolumn")
    return "\n".join(L)

# ── main parse loop ───────────────────────────────────────────────────────────
TOC_SUBSECTIONS = False   # False -> section-level ToC (saves a front-matter page)

def heading(level, text, toc_level):
    cmd = r"\section*" if level == 1 else r"\subsection*"
    t = inline(text)
    if toc_level == "subsection" and not TOC_SUBSECTIONS:
        return r"%s{%s}" % (cmd, t)        # heading only, no ToC entry
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
        if (s.startswith("**Use of generative AI") or s.startswith("**Authorship")
                or s.startswith("**Licensing")):
            decl_lines.append(s)

    body = [PREAMBLE,
            front_matter(abstract, keywords, decl_lines, client_verify)]

    pending_caption = None      # bold "Table 4.1." / "D.1 ..." lead-in
    table_index = -1
    in_list = False
    body_started = False
    stats = {"sections": 0, "subsections": 0, "figs": 0, "tables": 0,
             "bullets": 0, "paras": 0, "eqs": 0, "callouts": 0}

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
               ("**Author:**", "**Programme:**", "**Supervisors:**",
                "**Capstone client:**", "**Sponsor:**", "**Date:**",
                "**License:**")):
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
                if key in CALLOUT:
                    body.append(CALLOUT[key].strip())
                    stats["callouts"] += 1
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
