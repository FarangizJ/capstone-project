"""
Rewrite notebooks/01_data_pipeline.ipynb so that it is the *complete* pipeline
spine of the project:

  - Every markdown cell is academic passive voice (no "we/our/us/I").
  - A FULL DATA INVENTORY appears at the top: every raw input file and every
    processed output is listed with the downstream notebook(s) that consume it.
  - Each section opens with a STORY paragraph (purpose → action → why).
  - Each section carries a VOCABULARY block defining every shortened code
    idiom (skiprows, index_col, errors='coerce', isin, idxmax, twinx, fillna,
    replace, min_count, RangeIndex, pivot_table, NaN, col_rename, value_name,
    snake_case prefixes iea_* / sc_* / irena_* / wb_*) AND every shortened
    domain term (GWh, TJ, MCM, LHV, TES, TFC, T&D, CCGT, AR5, gCO₂/kWh,
    IEA, IRENA, WB, EDB, WDI, BESS, IPP, BOOT, PPA, OWID, Ember, AICc, RMSE).
  - A REASONING paragraph after each transformation explains WHY the step is
    needed (not just what it does).
  - An INTERPRETATION block follows each results-producing cell.
  - A new §13 — Supplementary feeds — loads (or references-and-validates)
    every supplementary CSV downstream notebooks read so that running NB01
    end-to-end touches every dataset the project uses.

Run from project root. Overwrites notebooks/01_data_pipeline.ipynb in-place.
"""
import json, os, sys

NB_PATH = 'notebooks/01_data_pipeline.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)


def md_cell(src):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': src}


def code_cell(src):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None,
            'outputs': [], 'source': src}


# ─────────────────────────────────────────────────────────────────────────────
# REPLACED MARKDOWN BODIES — keyed by their original cell index
# ─────────────────────────────────────────────────────────────────────────────

CELL0 = """# 01 — Data Pipeline
## Uzbekistan Power Sector Transition Tracker
**ILF Consulting Engineers Austria — Capstone Project**

---

### Purpose of this notebook

This notebook is the **pipeline spine** of the project. Four heterogeneous raw sources (IEA, StatSUZ Uzbekistan, IRENA, World Bank) are loaded, harmonised to a single unit system, joined onto a 1990–2026 spine, audited, and exported as two CSVs that every downstream notebook reads. Section 13 then loads every supplementary dataset downstream notebooks consume so that running this notebook end-to-end touches every file the project depends on.

No analysis can begin until this assembly is complete and validated, which is why the pipeline is isolated in its own notebook with explicit quality checks at every join.

### Pipeline diagram

```
   raw/                                                processed/
   ──────────────────────────────────────────             ──────────────────────────────
   IEA       ─┐                                       ┌─→ master_dataset.csv      (86 cols)
   StatSUZ   ─┼─→ §2–§5 loaders ─→ §6 unit harm. ─→  ─┤
   IRENA     ─┼─→             ─→ §7 assemble  ─→ §8  ─┼─→ master_dataset_core.csv (32 cols)
   World Bank ┘    ─→ §9 preliminary flag → §10 QC  ─→│
                                                       └─→ pipeline_provenance.csv
   Supplementary feeds (loaded in §13):
   Open-Meteo ERA5 ─→ climate_central_asia.csv        ┐
   OWID + WB       ─→ central_asia_panel.csv          │
   IMF DataMapper  ─→ imf_weo_uzb.csv                 ├─→ Read directly by NB02-NB10
   UzStat SDMX     ─→ uzb_energy_national.csv,        │
                       uzb_electricity_oblast.csv,    │
                       wb_sectoral_uzb.csv            │
   Compiled tariff ─→ tariff_history_uzb.csv          │
   REF research    ─→ uzbekistan_energy_projects.json │
   CAREC + Atlas   ─→ oblast_atlas.csv                ┘
```

### Complete data inventory — every file the project reads

#### Raw inputs (loaded in §2 – §5)

| Source | File | Native unit | Loaded in | Why it is included |
|---|---|---|---|---|
| IEA | `Electricity generation by source - Uzbekistan.csv` | GWh | §2.1 | Six fuel-specific generation columns — the only file that gives the technology split needed for the energy-mix narrative. |
| IEA | `Electricity consumption - Uzbekistan.csv` | GWh | §2.2 | National electricity demand on the TFC boundary; the dependent variable of every demand model. |
| IEA | `Electricity consumption by sector - Uzbekistan.csv` | TJ | §2.3 | Industry / transport / residential / commercial / agriculture breakdown — used in the sectoral demand decomposition. |
| IEA | `Electricity consumption per capita - Uzbekistan.csv` | MWh | §2.4 | Cross-country comparator series; surfaces the ~1 800 kWh/cap figure quoted in the paper. |
| IEA | `Natural gas production - Uzbekistan.csv` | TJ gross | §2.5 | Required for the gas self-sufficiency ratio. |
| IEA | `Natural gas final consumption - Uzbekistan.csv` | TJ gross | §2.6 | Denominator of the same ratio. |
| IEA | `Total energy supply (TES) by source - Uzbekistan.csv` | TJ | §2.7 | Whole-system balance; carries the residual that distinguishes power-sector gas from heating gas. |
| IEA | `Net energy imports - Uzbekistan.csv` | TJ | §2.8 | Energy-security indicator; flags the seasonal winter import pattern. |
| IEA | `CO2 emissions by sector - Uzbekistan.csv` | Mt CO₂ | §2.9 | Climate accounting; isolates the power-sector share of national emissions. |
| IEA | `CO2 intensity of power - Uzbekistan.csv` | gCO₂/kWh | §2.10 | The single number summarising decarbonisation progress in the power sector. |
| StatSUZ | `Volume of electricity production.csv` | mln kWh = GWh | §3.1 | The only series that extends generation to 2024. |
| StatSUZ | `Volume of electricity supply.csv` | mln kWh = GWh | §3.2 | Used as the bridge donor for IEA `elec_consumption_twh` in §8. |
| StatSUZ | `Total installed capacity of power plants.csv` | MW | §3.3 | Capacity headline; cross-checks against IRENA. |
| StatSUZ | `Total installed capacity of thermal power centers and thermal power plants.csv` | MW | §3.4 | Thermal capacity split. |
| StatSUZ | `Total installed capacity of hydroelectric power plants.csv` | MW | §3.5 | Hydro capacity split. |
| StatSUZ | `Volume of electricity produced by solar power plants.csv` | mln kWh = GWh | §3.6 | Renewable generation by tech — extends IRENA to 2024. |
| StatSUZ | `Volume of electricity produced by wind power farms.csv` | mln kWh = GWh | §3.7 | Same role for wind. |
| StatSUZ | `Volume of natural gas production.csv` | mln m³ | §3.8 | Gas balance, MCM-native. |
| StatSUZ | `Volume of natural gas consumption.csv` | mln m³ | §3.9 | Same. |
| StatSUZ | `Volume of coal production.csv` | thousand t | §3.10 | Marginal — included because the coal phase-out is part of the narrative. |
| StatSUZ | `Volume of electricity supply in the industrial sector.csv` | mln kWh | §3.11 | Sectoral cross-check against IEA. |
| StatSUZ | `Volume of electricity supply in agricultural sector.csv` | mln kWh | §3.11 | Same. |
| StatSUZ | `Volume of electricity supply in transport sector.csv` | mln kWh | §3.11 | Same. |
| StatSUZ | `Volume of electricity supply in housing sector.csv` | mln kWh | §3.11 | Same. |
| IRENA | `production data from IRENA_ELEC-C_20260305-091153.csv` | MW + GWh | §4.1–4.2 | Capacity *and* generation in one long table; pivoted twice in the loader. |
| IRENA | `renewable share data from IRENA_RESHARE_20260305-091356.csv` | % | §4.3 | RE-share indicator (both capacity- and generation-based). |
| World Bank | `P_Data_Extract_From_World_Development_Indicators.xlsx` | mixed | §5 | Macro covariates: real GDP, GDP growth, population, urbanisation, industrial value added, AR5 CO₂, per-capita kWh, T&D losses, RE share. |

#### Processed outputs (written by NB01)

| File | Columns | Year coverage | Read by |
|---|---:|---|---|
| `master_dataset.csv` | ~86 | 1990–2026 | NB01 QC, NB08, NB09 |
| `master_dataset_core.csv` | ~32 | 1990–2026 | NB02, NB03, NB04, NB05, NB06, NB07, NB08, NB10 (dashboard) |
| `pipeline_provenance.csv` | ~6 | row per column | NB07 (drops aliasing) |

#### Supplementary feeds (loaded or referenced in §13)

| File | Generator script | Source | Read by |
|---|---|---|---|
| `climate_central_asia.csv` | `scripts/climate_central_asia.py` | Open-Meteo ERA5 reanalysis | NB04, NB05, NB06 |
| `central_asia_panel.csv` | `scripts/central_asia_panel.py` | OWID Energy + World Bank WDI | NB02, NB07 |
| `imf_weo_uzb.csv` | external — IMF DataMapper API | IMF WEO Apr 2026 vintage | NB04, NB07 |
| `tariff_history_uzb.csv` | manually compiled | Decree PP / PF series + KUN.uz reporting | NB04 |
| `uzb_energy_national.csv` | `scripts/uzstat_clean.py` | UzStat SDMX dump (618 files) | NB03, NB04, NB07 |
| `uzb_electricity_oblast.csv` | `scripts/uzstat_clean.py` | UzStat SDMX dump (oblast rows) | NB07 |
| `wb_sectoral_uzb.csv` | World Bank fetch | WB WDI sectoral GVA | NB03 |
| `oblast_atlas.csv` | NB09 §6 (hand-coded atlas) | CAREC 2024 + Global Solar Atlas + IEA Solar Roadmap | NB09 |
| `uzbekistan_energy_projects.json` | REF research dataset | 46 verified plants — see `research/uzbekistan-energy/BRIEFING.md` | NB09 |

#### Forecasting / signals outputs (written by NB06–NB08, not by NB01)

| File | Written by | Read by |
|---|---|---|
| `forecast_scoreboard_baseline.csv` | NB06 | dashboard, paper |
| `forecast_scoreboard_advanced.csv` | NB07 | dashboard, paper |
| `forecast_demand_bayes_ridge.csv`, `forecast_demand_bayes_scenarios.csv` | NB07 | NB08 |
| `forecast_demand.csv`, `forecast_co2.csv`, `forecast_scenarios.csv`, `forecast_scenarios_with_nuclear.csv` | NB08 | dashboard |
| `investment_signal_*.csv`, `investment_opportunity_table.csv`, `planb_nuclear_sensitivity.csv` | NB08 | dashboard, paper |

### Folder layout

```
data/raw/
  emissions (source - IEA)/                ← CO₂ intensity, sectoral emissions
  energy consumption data (source - IEA)/  ← electricity demand by sector
  energy imports and exports (source - IEA)/ ← net energy imports
  energy production data (source - IEA)/   ← generation by fuel, TES, gas
  energy production data (source - IRENA)/ ← renewable capacity & generation
  socioeconomic macro indicators (source - World Bank)/ ← GDP, population, CO₂
  statsuz/                                 ← national stats, extends to 2024
  power plants (source - World Bank)/      ← GeoJSON files for the spatial layer
data/processed/
  master_dataset.csv, master_dataset_core.csv  ← written by NB01 §12
  climate_central_asia.csv, central_asia_panel.csv, imf_weo_uzb.csv,
  tariff_history_uzb.csv, uzb_energy_national.csv,
  uzb_electricity_oblast.csv, wb_sectoral_uzb.csv  ← supplementary feeds (§13)
  forecast_*.csv, investment_*.csv  ← written by NB06–NB08
research/uzbekistan-energy/
  uzbekistan_energy_projects.json  ← 46 verified plants, REF dataset
  uzbekistan_energy_map.html       ← embedded in NB09
```

### Vocabulary used throughout this notebook

> Every shortened term that appears in this notebook is defined here so that the
> reader can audit both the code and the underlying analysis without leaving
> the page. Code-level idioms (top half) and domain-level acronyms (bottom
> half) are kept separate for easy lookup.

**Code-level idioms (pandas / numpy / Python)**

| Term | Meaning | Reason it is used here |
|---|---|---|
| **DataFrame** | The pandas tabular object (rows × columns); the canonical in-memory representation of every series in this project. | All joins, slicing, and aggregation operate on DataFrames. |
| **`pd.read_csv(..., skiprows=3)`** | Skip the first three rows on read — used to bypass the IEA licence header. | The IEA distributes its CSVs with a three-line legal preamble before the data table; without `skiprows=3` the parser treats the licence text as data. |
| **`index_col=0`** | Use the first column as the row index. | IEA CSVs put years in the first column; setting it as the index makes year-based selection (`master.loc[2023]`) immediate. |
| **`pd.to_numeric(..., errors='coerce')`** | Convert to number; replace anything non-numeric with `NaN` instead of raising. | Published CSVs sometimes contain `..`, `c`, or blank cells; `coerce` turns those into `NaN` so the pipeline does not crash on a single bad cell. |
| **`apply(pd.to_numeric, errors='coerce')`** | Column-wise application of the same coercion. | Enforces numeric dtype across every column at once after `pd.read_csv` has dropped to `object`. |
| **`NaN`** (`np.nan`) | "Not a Number" — the IEEE-754 missing-value sentinel pandas uses for gaps. | Distinguishes "value not reported" from "zero". |
| **`encoding='utf-8-sig'`** | UTF-8 with byte-order-mark; what StatSUZ exports use. | Without it the first column name is prefixed with an invisible BOM character and column lookups silently fail. |
| **`encoding='cp1251'`** | Cyrillic Windows code page. | Fallback for older StatSUZ files exported from a Russian-locale system. |
| **`col_rename={...}`** | Dictionary passed to `df.rename(columns=...)` mapping source column names → project column names. | Centralises the schema-mapping rule inside the loader; the rest of the notebook references the clean `snake_case` names only. |
| **`value_name='sc_elec_prod_gwh'`** | The destination column name returned by `load_statsuz`. | Each StatSUZ file produces a single named Series; the prefix `sc_` is the StatSUZ marker. |
| **`pivot_table(index=..., columns=..., values=..., aggfunc='sum')`** | Reshape long → wide; sum on duplicates. | IRENA distributes data in long format with one row per (year × technology); the analysis needs wide format with years as index and technologies as columns. |
| **wide format** | Years are columns or the index; indicators are columns. | The canonical analytical shape. |
| **long format** | One column for the indicator name, one for the year, one for the value. | The shape IRENA and many SDMX exports arrive in. |
| **`pd.RangeIndex(YEAR_START, YEAR_END + 1)`** | Inclusive integer range used as the year spine. | Guarantees the master frame has every year, even years with zero source data. |
| **`master.join(series)`** | Left-join `series` onto the master frame by index. | The "spine" pattern: anything missing in `series` becomes `NaN`, never a missing row. |
| **`.isin([...])`** | Element-wise membership test. | Used to flag preliminary years and to filter IRENA's `Technology` column. |
| **`.idxmax()`** | Index label of the maximum value. | Used to report *which* year had the largest IEA / StatSUZ discrepancy. |
| **`fillna(0).sum(axis=1, min_count=1)`** | Sum across columns row-by-row, returning `NaN` if *all* inputs were `NaN`. | Without `min_count=1`, a row of all-`NaN` becomes 0 — a silent false zero. |
| **`replace(0, np.nan)`** | Replace zeros with `NaN`. | Prevents division-by-zero in share calculations like `re_penetration_pct`. |
| **`twinx()` / twin axes** | Two y-axes sharing one x-axis. | Used in sanity plots to show GDP and demand on different scales. |
| **`bbox_inches='tight'`** | Trim white space around saved figures. | Keeps the PNG outputs presentation-ready. |
| **`os.makedirs(path, exist_ok=True)`** | Create directory tree; do nothing if it already exists. | Idempotent setup — running the cell twice does not error. |
| **`os.path.isdir / isfile`** | Existence check that distinguishes directories from regular files. | The path-check loop uses `isdir`; the loaders use `isfile`. |
| **`snake_case`** | Naming convention: lower case with underscores (`elec_consumption_twh`). | The project's column-naming standard; collisions with IEA's `Title Case` are filtered through `col_rename`. |
| **`iea_*` / `sc_*` / `irena_*` / `wb_*` prefixes** | Source markers on column names. | Guarantees that two series with similar content but different definitions never overwrite each other. |
| **`assert / validation loop`** | Cell-end consistency check. | Catches a silently-empty load before downstream code uses the broken column. |

**Domain-level acronyms (energy and statistics)**

| Term | Meaning | Why it matters here |
|---|---|---|
| **IEA** | International Energy Agency. | The reference balance source; series cited here run to 2023. |
| **StatSUZ** | National Statistics Committee of Uzbekistan. | The only source publishing to 2024; carries the bridge load. |
| **IRENA** | International Renewable Energy Agency, Abu Dhabi. | Canonical renewable-capacity time series. |
| **WB** | World Bank, World Development Indicators (WDI). | Macro covariates (GDP, population, urbanisation, AR5 CO₂). |
| **OWID** | Our World in Data, Oxford. | Cross-source consolidator (Ember + EI Stat Review); used in NB02 and NB07 via the central-Asia panel. |
| **Ember** | Independent energy think tank that publishes the global electricity dataset OWID consumes. | Source for `electricity_demand` in the OWID Energy Dataset. |
| **EDB** | Eurasian Development Bank. | 2026 *Central Asia Energy Outlook* is the external cross-check used in §10. |
| **WDI** | World Development Indicators. | The WB series catalogue. |
| **TWh** | Terawatt-hour, 10¹² Wh. | Project's electricity unit. |
| **GWh** | Gigawatt-hour, 10⁹ Wh. | IEA + StatSUZ native unit; divided by 1 000 to get TWh. |
| **MWh** | Megawatt-hour, 10⁶ Wh. | Per-capita units (kWh × 1 000). |
| **kWh** | Kilowatt-hour, 10³ Wh. | WB per-capita and PPA tariffs. |
| **TJ** | Terajoule, 10¹² J. | IEA gas, oil, TES; 1 TWh = 3 600 TJ. |
| **MCM** | Million cubic metres of natural gas. | StatSUZ gas unit; converted to TJ gross with LHV = 38.1 MJ/m³. |
| **LHV** | Lower Heating Value — usable energy per unit fuel, net of latent water-vapour heat. | The convention used by IEA and Uzbekneftegaz; chosen here over Higher Heating Value (HHV) so figures match the public balances. |
| **TES** | Total Energy Supply. | IEA's whole-system aggregate: production + imports − exports − bunkers ± stock change. |
| **TFC** | Total Final Consumption. | Energy delivered to end users, *net* of transformation and own-use. |
| **T&D** | Transmission & Distribution. | The grid layer between generation and end user; losses here account for the IEA-vs-StatSUZ gap. |
| **CCGT** | Combined-Cycle Gas Turbine. | Modernisation pathway displacing old Soviet steam units. |
| **AR5** | IPCC Fifth Assessment Report. | The Global-Warming-Potential convention used in WB's `*.MT.CE.AR5` series; matters because pre-AR5 numbers under-state CH₄. |
| **gCO₂/kWh** | Grams of CO₂ per kilowatt-hour. | Power-sector carbon intensity; ~480 in Uzbekistan vs ~250 EU avg. |
| **BESS** | Battery Energy Storage System. | New asset class appearing 2024 onward (Zarafshan, Zangiata). |
| **IPP** | Independent Power Producer. | Privately-financed plant selling to NEGU under a long-term PPA. |
| **BOOT** | Build-Own-Operate-Transfer. | Contract structure used by ACWA Bash and Masdar Nur. |
| **PPA** | Power Purchase Agreement. | Long-dated take-or-pay contract underwriting IPP financing. |
| **NEGU** | National Electric Grid of Uzbekistan. | Single buyer for new IPP capacity (function transferred to Uzenergosotish JSC July 2024). |
| **preliminary year** | First-release published value that may be revised ±5 %. | Flagged with `is_preliminary = 1`; downstream models drop these from training folds. |
| **AICc** | Akaike Information Criterion, small-sample-corrected. | Used in NB06/NB07 baseline-vs-advanced comparison. |
| **RMSE / MAPE / R²** | Root Mean Squared Error / Mean Absolute Percentage Error / Coefficient of Determination. | Forecast scoreboard metrics."""

CELL1_SETUP = """---
## 0. Setup — libraries and folder paths

**Story.** Before any data are touched, the environment is fixed: the analytical libraries are imported, console-display options are set so that wide DataFrames are readable, and warnings are silenced so the audit log below is not polluted by deprecation chatter. The cell below loads only the foundational stack; specialist libraries (folium, statsmodels, sklearn) are loaded later in the notebooks that need them.

### Reasoning

Pinning the imports here, before any path is referenced, lets the next cell fail fast if a folder is missing — there is no risk of a partial setup where pandas exists but matplotlib does not.

### Vocabulary for cell 0

| Term | Meaning | Why it is set here |
|---|---|---|
| **pandas** | Python's tabular-data library. Every dataset in this project becomes a pandas `DataFrame`. | All loaders return DataFrames or Series. |
| **numpy** | Numerical-array foundation that pandas is built on; used here mainly through `np.nan` (the missing-value sentinel) and array arithmetic. | Needed for the share calculations and the bridge ratio. |
| **matplotlib** | Plotting library; `matplotlib.pyplot` is the imperative interface used for the sanity figures at the end of the notebook. | The §11 sanity plots use it. |
| **`warnings.filterwarnings('ignore')`** | Suppresses deprecation and FutureWarning messages. | Keeps the pipeline log diff-readable; warnings are re-enabled selectively in the EDA notebooks. |
| **`pd.set_option('display.float_format', ...)`** | Forces three-decimal thousand-separated rendering so cross-source comparisons line up by eye. | Makes the cross-check tables in §10 readable. |
| **`pd.set_option('display.max_columns', 60)`** | Show up to 60 columns in `print(df)` output. | The master frame has 80+ columns; the default 20 is too narrow for a quick sanity scan. |
| **`pd.set_option('display.max_rows', 40)`** | Show up to 40 rows. | 37-year frame fits without truncation. |"""

CELL_PATHS_NEW = """---
## 0.1 Paths and analytical year window

**Story.** The notebook lives inside `notebooks/`, so every data path is constructed with `..` to walk up one directory. Pinning the year window here (`YEAR_START = 1990`, `YEAR_END = 2026`) means downstream code never has to re-compute the bounds, and the `PRELIMINARY_YEARS = [2024, 2025, 2026]` constant becomes the single point of truth for what gets flagged as provisional.

### Reasoning

The earliest year is 1990 because Uzbekistan becomes a separate reporting entity in IEA / WB only from independence onward. The latest year is 2026 because StatSUZ publishes preliminary projections one year ahead of the IEA cut-off. Centralising both as named constants prevents the off-by-one bugs that surface when bounds are inlined in multiple loaders.

### Vocabulary for cell 0.1

| Term | Meaning | Why it is set here |
|---|---|---|
| **relative path** (`'../data/raw/...'`) | `..` resolves to the parent folder of `notebooks/`, i.e. the project root. | Keeps the pipeline portable across machines without an environment variable. |
| **`os.makedirs(DATA_PROCESSED, exist_ok=True)`** | Create the processed-output folder if it does not exist; remain silent if it already does. | Idempotent — re-running the cell never errors. |
| **YEAR_START** | First year in the analytical window. | 1990 = independence reporting baseline. |
| **YEAR_END** | Last year in the analytical window. | 2026 = StatSUZ forward projection. |
| **PRELIMINARY_YEARS** | Years stamped with `is_preliminary = 1`. | Allows downstream training samples to drop or down-weight provisional data. |
| **`PATH_IEA_*`, `PATH_STATSUZ`, `PATH_IRENA`, `PATH_WORLDBANK`** | Source-folder constants. | Each loader takes one of these as its `folder` argument; renaming a folder requires editing only this cell. |
| **path-check loop** | Iterates over `(name, path)` and prints `✓` if `os.path.isdir(path)` returns `True`, else `✗ MISSING`. | Fail-fast guard: if any source folder is missing, the loop visibly flags it before the loaders silently return empty frames. |

### Interpretation of the path check

The directory-existence loop at the bottom of the cell is a fail-fast guard. If any source folder is missing, the icon flips from `✓` to `✗ MISSING` and the rest of the notebook will visibly under-fill; this guarantees that a silently-empty pipeline cannot reach the export step."""

CELL4_HELPERS = """---
## 1. Helper functions — one loader per source

**Story.** Each external source uses a different on-disk format. Rather than inlining four sets of parsing rules, the parsing logic is encapsulated in four named loader functions — `load_iea`, `load_statsuz`, `load_irena`, and `load_worldbank` — so that the loading cells below read like declarative recipes rather than CSV mechanics.

### Reasoning

Centralising the per-source parsing rules inside the loaders ensures that any source-side schema change (a renamed column, an extra header row, an encoding change) is fixed in exactly one place. The §2–§5 cells therefore read like data declarations, not parsing code.

### Source-specific parsing rules

- **IEA** — CSV with a 3-row licence header (`skiprows=3`); years are the row index. The `Units` column is dropped because units are recorded in this notebook explicitly during the harmonisation step in §6.
- **StatSUZ** — CSV with human-readable headers in wide format. Year columns are detected by `str.isdigit()` and the first data row is treated as the national total. Some files are UTF-8 with BOM, others are CP1251 — the loader falls back automatically.
- **IRENA** — long-format CSV filtered for Uzbekistan and pivoted on `Technology`. The same loader serves both the *Installed Capacity (MW)* and *Generation (GWh)* tables, switched via `data_type_filter`.
- **World Bank** — XLSX with WDI series codes as rows and year columns formatted `1990 [YR1990]`. The loader splits on the first space to recover the integer year.

### Vocabulary for cell 1

| Term | Meaning | Why it is used here |
|---|---|---|
| **loader function** | A small Python function whose only responsibility is parsing one file format. | Centralises parsing logic. |
| **`skiprows=3`** | Skip the IEA licence header — three lines of legal text before the data table. | Without it the parser treats the licence as data. |
| **`index_col=0`** | Treat the first column as the row index. | Makes `df.loc[2023]` immediate. |
| **`pd.to_numeric(..., errors='coerce')`** | Convert to numeric; replace failures with `NaN`. | Stops a single `..` or `c` value in the source crashing the pipeline. |
| **`apply(pd.to_numeric, errors='coerce')`** | Column-wise coercion. | Promotes the whole frame to numeric dtype in one call. |
| **`encoding='utf-8-sig'` / `'cp1251'`** | UTF-8 with BOM / Cyrillic code page. | Two encodings StatSUZ files appear in; tried in order. |
| **wide format** | Years are columns, indicators are rows. | Source layout for StatSUZ and (after pivot) IRENA. |
| **long format** | One column for indicator, one for year, one for value. | IRENA's native shape. |
| **pivot** | Reshape long → wide. | Used inside `load_irena` to turn `Technology` rows into columns. |
| **WDI series code** (`NY.GDP.MKTP.KD`, `EG.ELC.LOSS.ZS`, …) | The WB's stable indicator identifier. | Centralised in `WB_SERIES` so renames are one-line edits. |
| **`col_rename`** | Dictionary passed by the §2 cell to remap IEA columns to `snake_case`. | Decouples the source schema from the project schema. |
| **`value_name`** | Destination column / Series name. | Lets `load_statsuz` return Series with the project's `sc_*` prefix already in place. |
| **`data_type_filter`** | Argument to `load_irena` that selects either *Installed Capacity (MW)* or *Generation (GWh)* from the same long table. | Avoids two near-duplicate loader functions. |
| **`technology_filter`** | List of IRENA `Technology` strings to keep. | Drops the technologies that are immaterial in Uzbekistan (biofuels, geothermal). |
| **fall-back encoding pattern** | `try utf-8-sig / except cp1251`. | Defensive — the StatSUZ export switched encodings between vintages. |"""

CELL6_LOAD_IEA = """---
## 2. Load IEA Data

**Story.** Ten IEA tables are loaded in this cell — six on the supply / generation side, two on gas, and two on emissions. Each table has been pre-selected as actually needed by the downstream analyses; tables that are duplicative or out-of-scope (heat, biofuels, road-transport detail) are intentionally not loaded.

### Reasoning

The IEA balance is the project's reference for production, demand, gas flows, and emissions. Loading exactly the ten files that feed the analytical notebooks — and no others — keeps the master frame at a manageable ~80 columns. Each load uses an explicit `col_rename` so the IEA's verbose column names (e.g. `Commercial and public services`) are mapped to `snake_case` names with units suffixed (`elec_commercial_tj`).

### Files ingested in §2

| File | Variable | Native unit | Used in |
|---|---|---|---|
| Electricity generation by source | `gen_{coal,oil,gas,hydro,solar,wind}_gwh` | GWh | EDA energy-mix (NB02), supply drivers (NB03) |
| Electricity consumption | `elec_consumption_gwh` | GWh | Demand drivers (NB04), forecasting (NB06, NB07) |
| Electricity consumption by sector | `elec_{industry,transport,residential,commercial,agriculture}_tj` | TJ | Sectoral decomposition (NB04) |
| Electricity per capita | `elec_per_capita_mwh` | MWh | Cross-country comparison (NB02) |
| Natural gas production | `gas_production_tj` | TJ gross | Supply self-sufficiency (NB03) |
| Natural gas final consumption | `gas_consumption_tj` | TJ gross | Supply self-sufficiency (NB03) |
| Total energy supply (TES) | wide TES frame | TJ | Decarbonisation tracking (NB02) |
| Net energy imports | `net_energy_imports_tj` | TJ | Energy-security indicator (NB02, NB03) |
| CO₂ by sector | wide emissions frame | Mt CO₂ | Climate accounting (NB02, NB08) |
| CO₂ intensity of power | `co2_intensity_power_gco2kwh` | gCO₂/kWh | Decarbonisation tracking (NB02, NB08) |

### Printed column names — full meaning (IEA side)

The cell below loads ten IEA tables. The columns introduced are decoded here in full.

| Printed column | Full name | Unit |
|---|---|---|
| `gen_coal_gwh` | IEA — generation from coal | GWh |
| `gen_oil_gwh` | IEA — generation from oil | GWh |
| `gen_gas_gwh` | IEA — generation from natural gas | GWh |
| `gen_hydro_gwh` | IEA — generation from hydropower | GWh |
| `gen_solar_gwh` | IEA — generation from solar photovoltaic | GWh |
| `gen_wind_gwh` | IEA — generation from onshore wind | GWh |
| `elec_consumption_gwh` | IEA — total national electricity consumption | GWh |
| `elec_industry_tj` | IEA — electricity consumed by the industry sector | TJ |
| `elec_transport_tj` | IEA — electricity consumed by the transport sector | TJ |
| `elec_residential_tj` | IEA — electricity consumed by the residential sector | TJ |
| `elec_commercial_tj` | IEA — electricity consumed by commercial and public services | TJ |
| `elec_agriculture_tj` | IEA — electricity consumed by agriculture and forestry | TJ |
| `elec_per_capita_mwh` | IEA — electricity consumption per capita | MWh / person / year |
| `gas_production_tj` | IEA — natural gas production, gross calorific basis | TJ |
| `gas_consumption_tj` | IEA — natural gas final consumption | TJ |
| `net_energy_imports_tj` | IEA — net energy imports (imports − exports) | TJ |
| `co2_intensity_power_gco2kwh` | IEA — CO₂ intensity of power generation | g CO₂ / kWh |

### Vocabulary for cell 2

| Term | Meaning | Why it matters |
|---|---|---|
| **`col_rename={...}`** | Dictionary mapping IEA's verbose column names to the project's `snake_case` schema; applied inside `load_iea`. | Decouples source-side renames from the rest of the notebook. |
| **`min_count=1`** | Used on `sum(axis=1)` so that a row of all-`NaN` returns `NaN` rather than 0 — a key guard against false zeros in early years. | Stops 1990s renewable totals from misreporting as 0 TWh. |
| **fossil share** | Share of generation from coal + oil + gas; computed in the harmonisation cell (§6). | Headline narrative variable. |
| **TES** | Total Energy Supply — IEA balance-side total covering production + imports − exports − bunkers ± stock change. | Whole-system accounting; carries the gas residual. |
| **TFC** | Total Final Consumption — energy delivered to end users, net of transformation and own-use. | Boundary of `elec_consumption_*` columns. |
| **`gen_*_gwh` → `gen_*_twh`** | Column prefix `gen_` marks "generation by fuel"; the unit suffix moves from GWh to TWh in §6. | Single-source-of-truth naming. |
| **`elec_*_tj`** | Sectoral electricity in TJ. | TJ is the native unit for sector splits; converted to TWh implicitly in NB04. |
| **`gas_*_tj`** | Gas flows in TJ gross. | Gross-calorific basis chosen to match Uzbekneftegaz's published balance. |
| **per-capita unit** (`elec_per_capita_mwh`) | MWh per person per year. | Comparable directly with Eurostat / IEA cross-country tables. |
| **gCO₂/kWh** | Grams of CO₂ per kilowatt-hour of electricity. | Power-sector carbon-intensity metric. |"""

CELL8_LOAD_STATSUZ = """---
## 3. Load StatSUZ Data

**Story.** StatSUZ is the only source publishing 2024 values at the time of writing, so it carries the burden of extending every IEA series past 2023. Eleven national-aggregate tables are loaded here: total generation, total supply, three capacity tables (total / thermal / hydro), solar and wind production, gas production and consumption, coal production, and four sectoral electricity-supply tables (industry, agriculture, transport, housing). Each file's first data row is the national total; sub-national breakdowns inside the same files are ignored at this stage and revisited in NB09 — Spatial.

### Reasoning

Two practical pressures drive the choice to load StatSUZ alongside IEA:

1. **Vintage gap.** IEA closes its public series at 2023 (a one-year lag). StatSUZ publishes 2024 by Q1 2025. Without StatSUZ the master frame would lose the most recent year, which is precisely the year the dashboard most needs.
2. **Sub-technology granularity.** StatSUZ publishes installed capacity by technology and renewable production by technology that IEA does not. These series are essential for the NB07 advanced forecasting model's renewable-build covariates.

### Printed column names — full meaning (StatSUZ side)

The cell below loads eleven StatSUZ national-aggregate tables. The columns introduced are decoded here in full.

| Printed column | Full name | Unit |
|---|---|---|
| `sc_elec_prod_gwh` | StatSUZ — total volume of electricity production | GWh |
| `sc_elec_supply_gwh` | StatSUZ — total volume of electricity supply (= production + net imports − losses) | GWh |
| `capacity_total_mw` | StatSUZ — total installed capacity of all power plants | MW |
| `capacity_thermal_mw` | StatSUZ — installed capacity of thermal power plants | MW |
| `capacity_hydro_mw` | StatSUZ — installed capacity of hydroelectric power plants | MW |
| `sc_solar_gwh` | StatSUZ — volume of electricity produced by solar power plants | GWh |
| `sc_wind_gwh` | StatSUZ — volume of electricity produced by wind power farms | GWh |
| `sc_gas_prod_mcm` | StatSUZ — volume of natural gas production | million cubic metres |
| `sc_gas_cons_mcm` | StatSUZ — volume of natural gas consumption | million cubic metres |
| `sc_coal_prod` | StatSUZ — volume of coal production | thousand tonnes |
| `sc_elec_industry_gwh` | StatSUZ — electricity supplied to the industrial sector | GWh |
| `sc_elec_agriculture_gwh` | StatSUZ — electricity supplied to the agricultural sector | GWh |
| `sc_elec_transport_gwh` | StatSUZ — electricity supplied to the transport sector | GWh |
| `sc_elec_housing_gwh` | StatSUZ — electricity supplied to housing (≈ IEA "residential") | GWh |

### Vocabulary for cell 3

| Term | Meaning | Why it appears here |
|---|---|---|
| **mln kWh** | Million kWh = GWh — StatSUZ's native electricity unit. | Converted to TWh in §6. |
| **MCM** | Million Cubic Metres of natural gas. | StatSUZ gas unit; converted to TJ in §6. |
| **`value_name='sc_elec_prod_gwh'`** | Project-side column name; the `sc_` prefix marks the series as originating from StatSUZ. | Prevents collisions with IEA twins. |
| **`sc_` prefix** | StatSUZ-source marker. | Cross-source disambiguation. |
| **first data row = national total** | StatSUZ files are oblast-broken; row 0 is the country-wide total used here. | NB09 reads oblast rows from the same files. |
| **housing sector** | StatSUZ's term for the residential sector. | One-word note for the reader cross-checking against IEA's `residential`. |
| **validation loop** | Catches any series that arrived empty (filename typo or encoding mismatch) by checking `len(s) == 0 or s.isna().all()`. | The canary for the rest of the pipeline. |

### Interpretation of the StatSUZ load summary

Every series should arrive with 15 years of data (2010–2024) except solar and wind, which only start in 2014–2015. If any series prints `EMPTY`, the StatSUZ bridge in §8 will silently degrade — the validation loop is therefore the canary for the rest of the pipeline."""

CELL10_LOAD_IRENA = """---
## 4. Load IRENA Data

**Story.** IRENA provides two reference series the IEA does not: a renewable-share-of-capacity time series and a long-history of installed capacity by technology down to onshore-wind and solar-PV granularity. Three IRENA tables are ingested — capacity, generation, and renewable shares — and each is pivoted from long format on the `Technology` column so the rest of the pipeline sees them in the same wide shape as the IEA frames.

### Reasoning

IRENA is the canonical international cross-check for renewable-capacity claims. Including IRENA alongside IEA and StatSUZ allows §10 to triangulate three sources and surface any single-source bias. The `irena_` prefix on every column keeps the source visible end-to-end.

### Printed column names — full meaning (IRENA side)

The cell below loads three IRENA tables (capacity, generation, renewable shares). The columns introduced are decoded here in full.

| Printed column | Full name | Unit |
|---|---|---|
| `irena_cap_total_renewable` | IRENA — total renewable installed capacity | MW |
| `irena_cap_total_non-renewable` | IRENA — total non-renewable installed capacity | MW |
| `irena_cap_renewable_hydropower` | IRENA — installed capacity of renewable hydropower | MW |
| `irena_cap_solar_photovoltaic` | IRENA — installed capacity of solar photovoltaic | MW |
| `irena_cap_onshore_wind_energy` | IRENA — installed capacity of onshore wind | MW |
| `irena_cap_natural_gas` | IRENA — installed capacity fired on natural gas | MW |
| `irena_cap_coal_and_peat` | IRENA — installed capacity fired on coal and peat | MW |
| `irena_cap_oil` | IRENA — installed capacity fired on oil | MW |
| `irena_gen_total_renewable` | IRENA — total renewable electricity generation | GWh |
| `irena_gen_total_non-renewable` | IRENA — total non-renewable electricity generation | GWh |
| `irena_gen_renewable_hydropower` | IRENA — renewable hydropower generation | GWh |
| `irena_gen_solar_photovoltaic` | IRENA — solar photovoltaic generation | GWh |
| `irena_gen_onshore_wind_energy` | IRENA — onshore wind generation | GWh |
| `irena_gen_natural_gas` | IRENA — natural-gas-fired generation | GWh |
| `irena_gen_coal_and_peat` | IRENA — coal- and peat-fired generation | GWh |
| `irena_gen_oil` | IRENA — oil-fired generation | GWh |
| `irena_re_share_capacity_pct` | IRENA — renewable share of installed capacity | % |
| `irena_re_share_generation_pct` | IRENA — renewable share of generation | % |

### Vocabulary for cell 4

| Term | Meaning | Why it appears here |
|---|---|---|
| **IRENA** | International Renewable Energy Agency (Abu Dhabi). | Canonical renewable-capacity time series. |
| **PV** | Photovoltaic — semiconductor cells that convert sunlight directly to electricity. | The IRENA `Solar photovoltaic` technology. |
| **onshore wind** | Wind turbines sited on land (as opposed to offshore). | Uzbekistan has no offshore wind; the project carries only the onshore series. |
| **peat** | Partly-decayed plant matter burned as low-grade fuel; aggregated with coal in IRENA's `Coal and peat`. | Not relevant in Uzbekistan but retained because the IRENA column name preserves the pairing. |
| **`data_type_filter`** | Switches the same long table between *Installed Capacity (MW)* and *Generation (GWh)*. | Two complementary views of the same renewable fleet. |
| **`technology_filter`** | List of IRENA `Technology` strings to retain. | Drops technologies immaterial in Uzbekistan (biofuels, geothermal). |
| **renewable share** | IRENA's RESHARE indicator. | Published on both a capacity basis (`irena_re_share_capacity_pct`) and a generation basis (`irena_re_share_generation_pct`). |
| **`irena_cap_*` / `irena_gen_*` prefix** | Column markers for capacity vs generation IRENA series. | Allows the master frame to carry both without aliasing. |
| **`pivot_table(... aggfunc='sum')`** | Reshape long → wide; sum on ties. | Required because IRENA's long table can carry sub-segmentations that resolve to a single technology after filtering. |"""

CELL12_LOAD_WB = """---
## 5. Load World Bank Data

**Story.** The World Bank's *World Development Indicators* are the source of every macro covariate that drives the demand model: real GDP, population, urbanisation, industrial value added, and the AR5-consistent CO₂ series. Twelve series codes are pulled from a single XLSX export. The two derived columns at the bottom (GDP and industrial value added expressed in billion USD) make the modelling notebooks more readable.

### Reasoning

WB is the only source aligned to UN national-accounts conventions for the macro variables. Pulling them all from a single XLSX (rather than the live WB API) keeps the pipeline reproducible offline — no API key, no rate limits, exact vintage frozen on disk.

### Series codes pulled from the WDI

| Code | Series | Unit | Why it is included |
|---|---|---|---|
| `NY.GDP.MKTP.KD` | GDP, constant 2015 US$ | USD | Real-GDP regressor for the demand model. |
| `NY.GDP.MKTP.KD.ZG` | GDP growth | % | Forecast scenario driver. |
| `SP.POP.TOTL` | Population, total | persons | Per-capita normalisation. |
| `SP.URB.TOTL.IN.ZS` | Urban population | % of total | Residential-demand structural driver. |
| `NV.IND.TOTL.KD` | Industry value added | USD | Industrial-demand regressor. |
| `EN.GHG.CO2.MT.CE.AR5` | CO₂ emissions, AR5 | Mt CO₂ | National emissions baseline. |
| `EN.GHG.CO2.PI.MT.CE.AR5` | CO₂ emissions, power industry, AR5 | Mt CO₂ | Power-sector emissions split. |
| `EG.USE.ELEC.KH.PC` | Electricity use per capita | kWh | WB-side comparator for IEA per-capita. |
| `EG.ELC.LOSS.ZS` | T&D losses | % of output | Grid-loss variable; flagged unreliable 2018–2022 in §10. |
| `EG.ELC.RNEW.ZS` | Renewable electricity output | % | RE-share cross-check vs IRENA. |

### Printed column names — full meaning

The cell below prints 12 column names. Each is decoded in full here.

| Printed column | Full name | Unit | WDI source code |
|---|---|---|---|
| `wb_gdp_const2015_usd` | World Bank — Gross Domestic Product, constant 2015 US dollars | USD | `NY.GDP.MKTP.KD` |
| `wb_gdp_growth_pct` | World Bank — annual GDP growth | % | `NY.GDP.MKTP.KD.ZG` |
| `wb_population` | World Bank — total population | persons | `SP.POP.TOTL` |
| `wb_urban_pop_pct` | World Bank — urban population share of total population | % | `SP.URB.TOTL.IN.ZS` |
| `wb_industry_va_const_usd` | World Bank — industry value added, constant 2015 US dollars | USD | `NV.IND.TOTL.KD` |
| `wb_co2_total_mt` | World Bank — total CO₂ emissions, AR5 Global-Warming-Potential basis | million tonnes (Mt) | `EN.GHG.CO2.MT.CE.AR5` |
| `wb_co2_power_mt` | World Bank — power-industry CO₂ emissions, AR5 basis | million tonnes (Mt) | `EN.GHG.CO2.PI.MT.CE.AR5` |
| `wb_elec_pc_kwh` | World Bank — electric power consumption per capita | kilowatt-hours per person | `EG.USE.ELEC.KH.PC` |
| `wb_td_losses_pct` | World Bank — electric power transmission & distribution losses, share of national output | % | `EG.ELC.LOSS.ZS` |
| `wb_re_share_pct` | World Bank — renewable electricity output, share of total electricity output | % | `EG.ELC.RNEW.ZS` |
| `wb_gdp_const2015_bn_usd` | Derived — same as `wb_gdp_const2015_usd` divided by 10⁹ for readability | billion USD | derived |
| `wb_industry_va_const_bn_usd` | Derived — same as `wb_industry_va_const_usd` divided by 10⁹ | billion USD | derived |

### Column-name decoder rules (apply throughout NB01)

| Token | Meaning | Example |
|---|---|---|
| `wb_` | World Bank, WDI source | `wb_gdp_const2015_usd` |
| `iea_` | International Energy Agency source | `iea_elec_consumption_twh` |
| `sc_` | StatSUZ (National Statistics Committee of Uzbekistan) source | `sc_elec_supply_gwh` |
| `irena_` | IRENA source | `irena_cap_solar_photovoltaic` |
| `gen_` | Generation (electricity produced) | `gen_gas_twh` |
| `elec_` | Electricity flow | `elec_consumption_twh` |
| `gas_` | Natural gas flow | `gas_production_tj` |
| `co2_` | Carbon-dioxide emissions | `wb_co2_power_mt` |
| `cap_` | Installed capacity | `irena_cap_hydropower` |
| `va_` | Value Added (UN national-accounts) | `wb_industry_va_const_usd` |
| `pc_` | Per Capita | `wb_elec_pc_kwh` |
| `td_` | Transmission & Distribution | `wb_td_losses_pct` |
| `re_` | Renewable Energy | `wb_re_share_pct` |
| `_const2015_` | inflation-adjusted to 2015 prices | `wb_gdp_const2015_usd` |
| `_pct` | the value is a percentage | `wb_urban_pop_pct` |
| `_mt` | million tonnes | `wb_co2_total_mt` |
| `_kwh` / `_mwh` / `_gwh` / `_twh` | kilo / mega / giga / tera-watt-hours | `wb_elec_pc_kwh` |
| `_tj` | terajoule | `gas_production_tj` |
| `_mw` | megawatt (capacity) | `capacity_total_mw` |
| `_mcm` | million cubic metres of gas | `sc_gas_prod_mcm` |
| `_bn_usd` | billion United States dollars | `wb_gdp_const2015_bn_usd` |
| `_bridged` | gap-filled via the §8 ratio-scaling bridge | `elec_consumption_twh_bridged` |

### Vocabulary for cell 5

| Term | Meaning | Why it appears here |
|---|---|---|
| **WDI** | World Development Indicators — the canonical WB time-series database. | The source for every macro covariate in this notebook. |
| **`[YR1990]`** | The bracketed suffix the WDI export uses to mark year columns. | The loader splits on the first space to recover the integer year. |
| **constant 2015 US$** | Inflation-adjusted GDP using 2015 as the price base. | Required for real-growth modelling — avoids the spurious correlation a nominal series produces. |
| **AR5** | IPCC Fifth Assessment Report Global-Warming-Potential convention. | Ensures the CO₂ figures are comparable across years. |
| **GWP** | Global Warming Potential — the factor that converts non-CO₂ GHG masses into CO₂-equivalent. | Embedded in the AR5 series codes. |
| **`KD` vs `CD` suffix** | `KD` = constant local prices (real); `CD` = current US$ (nominal). | Only real series are used in modelling. |
| **`load_worldbank` returns a frame already indexed by year** | so it can be joined onto `master` without further alignment. | Pattern is consistent with the other loaders. |

### Interpretation of the load summary

A series with 35 non-null values out of 36 means one year is missing — almost always 2024 (WDI lags one calendar year for most macro indicators). The two non-null counts of 33 (`wb_elec_pc_kwh` and `wb_td_losses_pct`) and 32 (`wb_re_share_pct`) reflect a longer lag for the electricity-specific WDI indicators, which is the reason the project also pulls these series from StatSUZ in §3."""

CELL15_UNITS = """---
## 6. Unit harmonisation

**Story.** Three distinct unit systems arrive from the four sources. Before any series can be merged or modelled, everything that represents electricity is converted to **TWh**, and everything that represents gas is converted to **TJ gross**. Conversion factors are written out explicitly as named constants so that any audit can trace the arithmetic without leaving the notebook.

### Reasoning

Without an explicit harmonisation step, the master frame would carry GWh and TWh side-by-side. Downstream analysts would have to remember which column is in which unit — exactly the kind of latent bug that contaminates results late in a project. Pinning the conversions as named constants (`GWH_TO_TWH`, `TJ_TO_TWH`, `MCM_GAS_TO_TJ`) means every conversion in the pipeline is auditable from a single grep.

| Original | Converted to | Factor | Justification |
|----------|--------------|--------|---------------|
| GWh | TWh | ÷ 1 000 | Decimal scaling. |
| TJ | TWh | ÷ 3 600 | 1 TWh = 3.6 × 10⁶ GJ = 3 600 TJ. |
| Million m³ gas | TJ gross | × 38.1 | LHV = 38.1 MJ/m³ — Uzbek-blend average reported by Uzbekneftegaz. |

### Printed column names — full meaning (derived in §6)

This cell renames every electricity column to TWh and creates seven derived columns. Each is decoded in full here.

| Printed column | Full name | Unit | Definition |
|---|---|---|---|
| `gen_coal_twh` | generation from coal | TWh | `gen_coal_gwh / 1 000` |
| `gen_oil_twh` | generation from oil | TWh | `gen_oil_gwh / 1 000` |
| `gen_gas_twh` | generation from natural gas | TWh | `gen_gas_gwh / 1 000` |
| `gen_hydro_twh` | generation from hydropower | TWh | `gen_hydro_gwh / 1 000` |
| `gen_solar_twh` | generation from solar photovoltaic | TWh | `gen_solar_gwh / 1 000` |
| `gen_wind_twh` | generation from onshore wind | TWh | `gen_wind_gwh / 1 000` |
| `gen_total_twh` | total electricity generation across all fuels | TWh | row sum of the six `gen_*_twh` columns |
| `gen_fossil_twh` | fossil-fuel generation | TWh | `gen_coal_twh + gen_oil_twh + gen_gas_twh` |
| `gen_renewable_twh` | renewable generation | TWh | `gen_hydro_twh + gen_solar_twh + gen_wind_twh` |
| `re_penetration_pct` | renewable-energy penetration | % | `gen_renewable_twh / gen_total_twh × 100` |
| `fossil_share_pct` | fossil share of generation | % | `gen_fossil_twh / gen_total_twh × 100` |
| `elec_consumption_twh` | total electricity consumption | TWh | `iea_elec_consumption / 1 000` |
| `sc_elec_prod_twh` | StatSUZ — electricity production | TWh | `sc_elec_prod_gwh / 1 000` |
| `sc_elec_supply_twh` | StatSUZ — electricity supply | TWh | `sc_elec_supply_gwh / 1 000` |
| `sc_solar_twh` | StatSUZ — solar generation | TWh | `sc_solar_gwh / 1 000` |
| `sc_wind_twh` | StatSUZ — wind generation | TWh | `sc_wind_gwh / 1 000` |
| `sc_gas_prod_tj` | StatSUZ — natural-gas production | TJ | `sc_gas_prod_mcm × 38.1` |
| `sc_gas_cons_tj` | StatSUZ — natural-gas consumption | TJ | `sc_gas_cons_mcm × 38.1` |
| `irena_gen_twh_<tech>` | IRENA generation by technology | TWh | IRENA generation column ÷ 1 000 |

### Vocabulary for cell 6

| Term | Meaning | Why it appears here |
|---|---|---|
| **`GWH_TO_TWH = 1/1000`** | Named conversion constant. | Makes the conversion auditable; replaces every inline `0.001` in older versions. |
| **`TJ_TO_TWH = 1/3600`** | TJ → TWh factor. | Single source of truth for sectoral electricity. |
| **`MCM_GAS_TO_TJ = 38.1`** | LHV (Lower Heating Value) for the Uzbek pipeline blend; AGA-style heating-value reporting. | Uses Uzbekneftegaz's published LHV — IRENA's generic 36 MJ/m³ would under-state by ~6 %. |
| **LHV** | Lower Heating Value — usable energy per unit fuel, net of latent water-vapour heat. | The convention used by IEA and Uzbekneftegaz. |
| **AGA** | American Gas Association — the standards body that defines the natural-gas heating-value reporting convention. | The MJ/m³ basis. |
| **`fillna(0).sum(...)`** | Defensive pattern when summing optional columns. | Protects against silent `NaN` propagation. |
| **`gen_total_twh`** | Sum across all six fuels. | Project's master generation figure. |
| **`gen_fossil_twh`** | coal + oil + gas. | Supply-driver decomposition. |
| **`gen_renewable_twh`** | hydro + solar + wind. | Not adjusted for biomass or geothermal because they are immaterial in Uzbekistan. |
| **`re_penetration_pct`** | `gen_renewable_twh / gen_total_twh × 100`. | Energy-mix headline. |
| **`fossil_share_pct`** | Complementary fossil share. | Explicitly carried because the two do not always sum to exactly 100 (rounding, definitional gaps). |
| **`replace(0, np.nan)` before division** | Replace zeros with `NaN` to avoid divide-by-zero. | The early-1990s renewable rows are zero; division would otherwise raise `RuntimeWarning`. |

### Interpretation of the harmonised columns

Once this cell completes, every electricity column in the master frame is in TWh and every gas column is in TJ. The two derived shares (`re_penetration_pct`, `fossil_share_pct`) become the canonical inputs to the energy-mix narrative in NB02 — they are computed once, here, so that no downstream notebook re-derives them inconsistently."""

CELL17_ASSEMBLE = """---
## 7. Assemble the master dataset

**Story.** The four parsed sources are now stitched onto a common annual index (1990–2026). A `RangeIndex` of years is built first; every series is then `left-joined` onto that spine so that gaps appear as `NaN` rather than as missing rows. The collision-detection block at the end catches the silent-rename pattern that pandas applies when two columns share a name (`_x`, `_y` suffixes) — any hit there is treated as a schema bug and must be fixed before continuing.

### Reasoning

Building the spine first and left-joining onto it (rather than concatenating arbitrary frames) guarantees that the master frame has *exactly one row per year* in the analytical window. Without this discipline, an IRENA series starting in 2000 would silently drop years 1990–1999. The collision detector closes the second-order risk: two source columns with the same name being silently renamed `*_x` and `*_y`.

### Vocabulary for cell 7

| Term | Meaning | Why it appears here |
|---|---|---|
| **`pd.RangeIndex(1990, 2027)`** | Inclusive integer range (stop is exclusive). | Builds the year spine in one line. |
| **left join** | Keep every row in the spine (every year), pull in matching values from each series, fill the rest with `NaN`. | Pattern used for every `.join()` call below. |
| **column collision** | When two source-side columns share a name, pandas appends `_x`/`_y` rather than overwriting. | The detector at the bottom flags this so it can be fixed at source. |
| **`master`** | The single in-memory frame holding every reconciled series. | All downstream notebooks read it back from disk. |
| **`master.join(series)`** | Left-join `series` onto `master` by index. | Used 27 times — once per source-side frame. |
| **`shape[0] × shape[1]`** | Rows × columns. | Reported at the end of the cell for fail-fast comparison against the expected ~37 × ~81. |

### Interpretation of the master-shape print

The expected shape after this cell is **37 years × ~81 columns**. The row count is fixed (1990–2026). The column count drifts as series are added — any large drop relative to a previous run indicates an upstream file was silently emptied."""

CELL19_BRIDGE = """---
## 8. StatSUZ bridge — extending key series to 2024

**Story.** IEA stops at 2023 and StatSUZ has 2024. A ratio-scaling bridge is applied so that the IEA series is mechanically extended rather than overwritten. For every IEA / StatSUZ pair, the rolling 5-year mean of `IEA / StatSUZ` over the overlap period is computed; that scale factor is then multiplied by the StatSUZ 2024 value to fill the IEA gap. This preserves the IEA definitional basis (net of grid losses, IEA-style boundary) while gaining a one-year extension.

### Reasoning

Two alternatives were rejected:

1. **Replace the IEA series with StatSUZ.** Rejected because StatSUZ uses the supply-side boundary (gross of T&D losses) while IEA uses the consumption-side boundary. Replacing would silently change the level of the demand series, contaminating every per-capita and intensity ratio downstream.
2. **Leave the IEA series ending at 2023.** Rejected because the dashboard and the forecasting train/validation splits both require 2024 to be present.

Ratio scaling threads the needle: the level basis stays IEA, but the latest observation is mechanically inferred from StatSUZ.

Two pairs are bridged:

| IEA series | StatSUZ series | Output |
|---|---|---|
| `elec_consumption_twh` | `sc_elec_supply_twh` | `elec_consumption_twh_bridged` |
| `gen_total_twh` | `sc_elec_prod_twh` | `gen_total_twh_bridged` |

### Printed column names — full meaning (bridge outputs)

| Printed column | Full name | Unit | Definition |
|---|---|---|---|
| `elec_consumption_twh_bridged` | electricity consumption, IEA basis, extended to 2024 | TWh | IEA where available; scale × StatSUZ supply for 2024 |
| `gen_total_twh_bridged` | total generation, IEA basis, extended to 2024 | TWh | IEA where available; scale × StatSUZ production for 2024 |
| `gas_self_sufficiency_pct` | domestic gas production ÷ domestic gas consumption | % | `sc_gas_prod_tj / sc_gas_cons_tj × 100` |

### Vocabulary for cell 8

| Term | Meaning | Why it appears here |
|---|---|---|
| **ratio scaling** | A bridging technique that preserves the donor series' level basis but inherits the recipient series' definitional boundary. | The chosen extension method. |
| **scale factor** | The mean of `IEA / StatSUZ` over the overlap window. | Empirically ≈ 0.92 for consumption and ≈ 0.99 for generation. |
| **overlap window** | 2010–2023 — the years both sources publish. | Picked as the longest joint coverage. |
| **5-year mean of the ratio** | `ratio_df.tail(5).mean()`. | Smooths year-to-year noise in the ratio. |
| **`missing_mask`** | Boolean index that is `True` where the IEA value is `NaN` *and* the StatSUZ value is not. | The only rows that get filled. |
| **`gas_self_sufficiency_pct`** | Domestic gas production as a share of domestic gas consumption. | Computed in the same cell so the gas-side bridge stays beside the electricity bridge. |

### Interpretation of the printed scale factors

A scale factor of **0.9232** for consumption tells the analyst that StatSUZ supply is on average ~8 % larger than IEA consumption over 2010–2023. That gap reflects two real things: T&D losses (StatSUZ "supply" includes them, IEA "consumption" excludes them) and own-use power-station consumption. A factor near **0.99** for generation, in contrast, says the two sources agree on production within 1 % — IEA is essentially adopting StatSUZ data here. The bridged columns should therefore be used for trend lines but **not** for absolute-level cross-source claims."""

CELL21_PRELIM = """---
## 9. Preliminary-year flag

**Story.** The forecasting and correlation notebooks must be able to distinguish *confirmed* from *preliminary* data — the latter are first-release values that may be revised by ±5 % when the next vintage publishes. A single integer flag (`is_preliminary`) and a human-readable label (`data_status`) are added so every downstream model can drop or weight these years deterministically.

### Reasoning

Without an explicit flag, a model trained on 2024 data risks fitting noise that the next StatSUZ vintage will revise away. The flag lets NB07 mask 2024–2026 from the training fold while still allowing the dashboard to display them as "preliminary" tooltips.

### Printed column names — full meaning (preliminary-flag outputs)

| Printed column | Full name | Type | Values |
|---|---|---|---|
| `is_preliminary` | preliminary-year indicator | int | `1` for 2024 / 2025 / 2026; `0` otherwise |
| `data_status` | human-readable companion of `is_preliminary` | str | `"preliminary"` or `"confirmed"` |

### Vocabulary for cell 9

| Term | Meaning | Why it appears here |
|---|---|---|
| **preliminary year** | First-release published value, expected to be revised. | 2024 (StatSUZ first release), 2025 / 2026 (forward placeholders). |
| **`isin([...])`** | Element-wise membership test against the list. | Returns `True` for every year in `PRELIMINARY_YEARS`. |
| **`astype(int)`** | Convert boolean `True/False` to `1/0`. | Lets the column be passed straight into a regression. |
| **`map({0: 'confirmed', 1: 'preliminary'})`** | Generate the human-readable companion column for the dashboard tooltip layer. | Keeps the dashboard contract simple. |
| **`data_status`** | Companion text column. | Source for the dashboard "as-of" badge. |"""

CELL23_QC = """---
## 10. Quality checks

**Story.** The pipeline is only as trustworthy as its audit trail. Three checks are run before export: (1) per-column completeness — how many cells are missing in each column; (2) cross-source consistency — does IEA agree with StatSUZ on the years they both cover; and (3) the EDB 2026 *Central Asia Energy Outlook* cross-check on the 2024 demand, generation, capacity, and T&D-loss values. All three checks are *reported, not failing* — the philosophy here is that the analyst should see anomalies and decide, not have them silently masked.

### Reasoning

Cross-source consistency is the single most important QC step in a multi-source pipeline. If IEA and StatSUZ disagreed on generation by 20 % the bridge in §8 would be meaningless; the fact that they agree to within 1 % is what makes the bridge defensible. The EDB cross-check adds a third independent source on the 2024 anchor year.

### Vocabulary for cell 10

| Term | Meaning | Why it appears here |
|---|---|---|
| **completeness** | `1 − missing/total`; 100 % means every cell is populated. | Headline pipeline-health score. |
| **mean / max diff** | Mean and max of the absolute percentage difference between two series across their overlap. | The two-source agreement metric. |
| **`idxmax()`** | Pandas index of the row containing the maximum value. | Reports *which* year had the largest IEA / StatSUZ gap. |
| **EDB 2026 cross-check** | Eurasian Development Bank, *Central Asia Energy Outlook* (March 2026), Table 4.1. | External anchor for the 2024 values; resolves which side of the IEA / StatSUZ range the reality sits on. |
| **`wb_td_losses_pct`** | WB grid-loss series (`EG.ELC.LOSS.ZS`). | Series stops at 2022 and shows suspicious 2018 / 2021 dips; masked here and refilled with the EDB 17.8 % figure for 2023. |
| **mask + refill pattern** | `master.loc[2018:2022, col] = np.nan; master.loc[2023, col] = 17.8`. | Surgical correction recorded inline so the audit trail is intact. |

### Interpretation of the quality-check output

Three specific results in this block deserve flagging in the methodology section of the paper:

1. **Consumption vs Supply mean diff ≈ 14 %** — large, but expected: IEA's `elec_consumption_twh` is on the TFC boundary (net of T&D losses) while StatSUZ's `sc_elec_supply_twh` is on the supply boundary (gross of T&D losses). The gap is therefore approximately the national T&D-loss rate, which is independently confirmed at ~13–17 % by World Bank `EG.ELC.LOSS.ZS` for the same period.
2. **Generation vs Production mean diff < 1 %** — IEA and StatSUZ agree on physical production within rounding, which is the necessary precondition for the ratio-scaling bridge in §8.
3. **EDB 2024 anchors** — Demand 82.4 vs 84.2 TWh, Generation 81.5 vs 82.7 TWh, Capacity 21 259 vs 21 501 MW. All three are within 2 % of the EDB number, which is the strongest possible external anchor for the StatSUZ-driven 2024 row."""

CELL30_PLOTS = """---
## 11. Quick sanity plots

**Story.** Three small plots provide a visual check that the master dataset is internally consistent: (1) generation by source, stacked; (2) GDP plotted against bridged electricity demand, on twin axes; (3) installed capacity by technology. None of these are presentation-grade — that is the job of NB02–NB05 — but each catches a different class of pipeline error.

### Reasoning

A picture surfaces a unit-conversion bug or a column-misnaming bug faster than any numeric QC table. Putting these three figures at the end of NB01 means the analyst sees the obvious problems before reading any downstream notebook.

### Vocabulary for cell 11

| Term | Meaning | Why it appears here |
|---|---|---|
| **stacked bar chart** | Bars are accumulated on the same x-position via a running `bottom` array. | Total height is generation; slices are technology shares. |
| **twin axes (`twinx`)** | Two y-axes share an x-axis. | GDP (left) and electricity demand (right) have incomparable scales. |
| **`bbox_inches='tight'`** | Trim white space around the saved figure. | Keeps the PNG presentation-ready. |
| **`dpi=150`** | Dots per inch for the saved PNG. | 150 is the resolution Word renders cleanly. |
| **`fontsize=7` for legends** | Compact legend text. | Three subplots side-by-side leave little room. |

### Interpretation of the sanity plots

- The **generation stack** should look monotonically gas-dominated from 1995 onward, with hydro stable around 6–7 TWh and solar and wind appearing only in 2019–2020. Any visible coal or oil after 2010 in this plot indicates a unit-conversion bug.
- The **GDP / demand** twin chart should display two roughly parallel upward trends after ~2005; a visible decoupling around 2018–2019 corresponds to the start of the IFC Scaling-Solar reform programme and the tariff-driven efficiency push.
- The **capacity** panel should show thermal flat at ~12 GW, hydro flat at ~1.8 GW, and a sharp upward step in 2022–2024 driven by Nur Navoi, Nur Bukhara, and the ACWA Bash wind cluster."""

CELL32_EXPORT = """---
## 12. Export master dataset

**Story.** The pipeline closes by writing two CSVs: the **full master frame** (~86 columns) for the modelling notebooks and a **core slice** (~32 columns) for the dashboard. The core slice is hand-curated and intentionally excludes IRENA's sub-technology breakdowns and the WB-specific code suffixes, which are not displayed in the dashboard view.

### Reasoning

Writing two files instead of one is a deliberate decoupling. NB02–NB07 read the full frame because they need every covariate the master assembly produced. The dashboard reads the core slice because it only needs the ~32 columns it plots; this keeps the in-browser memory footprint small and the load time fast.

### Vocabulary for cell 12

| Term | Meaning | Why it appears here |
|---|---|---|
| **`master_dataset.csv`** | Full reconciled time series. | NB01 QC, NB08, NB09 read this. |
| **`master_dataset_core.csv`** | Dashboard slice. | NB02-NB07, NB10 read this. |
| **`CORE_COLUMNS`** | Explicit allow-list of columns kept in the slice. | Keeps the dashboard contract stable even if new columns are added upstream. |
| **`to_csv(path)`** | Default-arguments CSV write — UTF-8, comma-separated, index included. | Index = year, so the next reader can `pd.read_csv(path, index_col='year')`. |

### Interpretation of the export step

The two files are versioned together. If a series is renamed in §6, both this export step and the downstream notebooks must be updated in the same commit — otherwise the dashboard reads stale schema and silently drops columns from the chart legend."""

# ─────────────────────────────────────────────────────────────────────────────
# NEW §13 — Supplementary feeds (inserted at the very end of the notebook)
# ─────────────────────────────────────────────────────────────────────────────

CELL_S13_HEADER = """---
## 13. Supplementary feeds — every dataset downstream notebooks consume

**Story.** Beyond the four core sources loaded above, the project draws on six supplementary feeds. Each is generated by its own script (or fetched from an external API) and read directly by one or more downstream notebooks. They are *not* re-built here — that would slow the pipeline run to minutes — but they are loaded, validated, and inventoried so that running this notebook end-to-end touches every dataset the project depends on.

### Why these feeds are kept separate from the master frame

Three reasons drive the separation:

1. **Different temporal grain.** The climate feed is built on daily ERA5 reanalysis aggregated to annual HDD18 / CDD24; the IMF WEO feed is a five-year forward outlook; the master frame is annual historical. Joining them all into one wide frame would force every downstream notebook to ignore most columns.
2. **Different country grain.** The central-Asia panel and climate feed are five-country long panels (UZB, KAZ, KGZ, TJK, TKM); the master frame is Uzbekistan-only. Pooling them would force a wide-long pivot inside the master frame that the modelling notebooks would then have to undo.
3. **Different update cadence.** The IMF WEO is published twice a year; UzStat oblast data once a year; the REF research dataset is maintained manually. Keeping them out of the auto-rebuild path means a stale master frame does not force a re-fetch of every external API.

### Vocabulary for §13

| Term | Meaning | Why it appears here |
|---|---|---|
| **HDD18 / CDD24** | Heating Degree Days (base 18 °C) / Cooling Degree Days (base 24 °C). | ASHRAE convention; built from daily ERA5 temperatures in `climate_central_asia.py`. |
| **ERA5** | ECMWF Reanalysis v5; 0.25° daily global temperature / humidity / wind grid. | The free, full-coverage source for Central Asia climate. |
| **Open-Meteo** | Public API exposing ERA5 without an API key or rate limit at this volume. | Why the climate feed can be regenerated on any laptop. |
| **IMF WEO** | International Monetary Fund, *World Economic Outlook*; the canonical macro-forecast vintage. | Source of the 2024–2030 GDP growth assumptions used in NB07 scenarios. |
| **IMF DataMapper** | The WEO's JSON-over-HTTP API endpoint (`http://www.imf.org/external/datamapper/api/v1`). | The fetcher script hits this directly. |
| **OWID Energy Dataset** | Our World in Data's consolidated electricity / energy panel. | Compiled by OWID from Ember + EI Statistical Review; used as the cross-check for the central-Asia panel. |
| **Ember** | London-based climate think tank. | The source dataset OWID re-publishes. |
| **EI Statistical Review of World Energy** | Energy Institute (formerly BP). | The second source OWID consolidates with Ember. |
| **UzStat SDMX** | National Statistics Committee's SDMX endpoint. | 982 series identified, 618 files downloaded, ~25 retained — see `scripts/uzstat_clean.py`. |
| **SDMX** | Statistical Data and Metadata eXchange — UN/OECD standard for statistical data interchange. | The format the UzStat exports use. |
| **CAREC** | Central Asia Regional Economic Cooperation. | Source for wind-technical-potential and the IPP pipeline used in the oblast atlas. |
| **REF dataset** | "Reference" dataset of 46 verified Uzbek power assets. | Single source of truth for the spatial layer; see `research/uzbekistan-energy/BRIEFING.md`. |"""

CELL_S13_LOADER = """# ── §13 Supplementary-feed loader + validator ───────────────────────────────
# Loads every supplementary CSV/JSON downstream notebooks consume; prints the
# shape and the first two columns so the pipeline run validates every input.
# Files that are missing are reported, not raised — running this cell on a
# clean clone surfaces every external feed that needs (re-)fetching.

import json as _json

SUPP_FEEDS = [
    # (relative path under DATA_PROCESSED, generator,                     consumed by)
    ('uzstat_clean/climate_central_asia.csv',     'scripts/climate_central_asia.py', 'NB04, NB05, NB06'),
    ('uzstat_clean/central_asia_panel.csv',       'scripts/central_asia_panel.py',   'NB02, NB07'),
    ('imf_weo_uzb.csv',                            'external — IMF DataMapper',       'NB04, NB07'),
    ('tariff_history_uzb.csv',                     'manually compiled',               'NB04'),
    ('uzstat_clean/uzb_energy_national.csv',      'scripts/uzstat_clean.py',         'NB03, NB04, NB07'),
    ('uzstat_clean/uzb_electricity_oblast.csv',   'scripts/uzstat_clean.py',         'NB07'),
    ('wb_sectoral_uzb.csv',                        'WB WDI sectoral GVA fetch',       'NB03'),
    ('oblast_atlas.csv',                           'NB09 §6 (hand-coded atlas)',      'NB09'),
]

SUPP_JSON = [
    ('uzbekistan_energy_projects.json',   'REF research — research/uzbekistan-energy/', 'NB09'),
]

print('Supplementary-feed inventory')
print('=' * 78)
print(f'{"file":<40} {"shape":>12}   read by')
print('-' * 78)
for fname, _gen, consumers in SUPP_FEEDS:
    path = os.path.join(DATA_PROCESSED, fname)
    if not os.path.isfile(path):
        print(f'{fname:<40} {"MISSING":>12}   {consumers}   ← regen via {_gen}')
        continue
    try:
        df = pd.read_csv(path)
        shape = f'{df.shape[0]}×{df.shape[1]}'
        print(f'{fname:<40} {shape:>12}   {consumers}')
    except Exception as e:
        print(f'{fname:<40} {"READ ERROR":>12}   {consumers}   ← {e}')

# REF research dataset — JSON
for fname, _gen, consumers in SUPP_JSON:
    path = os.path.join('..', 'research', 'uzbekistan-energy', fname)
    if not os.path.isfile(path):
        print(f'{fname:<40} {"MISSING":>12}   {consumers}   ← {_gen}')
        continue
    with open(path) as f:
        records = _json.load(f)
    print(f'{fname:<40} {len(records):>8} assets   {consumers}')

print('=' * 78)
print('✓ Supplementary-feed inventory complete.')"""

CELL_S13_INTERP = """### Interpretation of the supplementary-feed inventory

If every line above prints a shape rather than `MISSING`, the project is fully primed: every notebook can run end-to-end without re-fetching anything. If any line prints `MISSING`, the second column tells the analyst which generator script (or external source) is needed to repopulate it. The most expensive feed to regenerate is `climate_central_asia.csv` (~5 minutes of Open-Meteo API calls); the others rebuild in under a minute each.

### What the §13 inventory tells the reader

- The pipeline reads from **29 raw files** and writes **two processed CSVs** (master + core). NB02–NB10 then add **eight supplementary CSVs and one JSON** to those two outputs.
- Every downstream notebook can be traced back to one of these eleven files; the *Read by* column in the table at the top of this notebook is the directed-dependency graph of the project.
- The two files marked *external* (IMF WEO) and *manually compiled* (tariff history) are the only links in the chain that are not script-regeneratable; both are version-controlled inside `data/processed/` so the project is fully reproducible from a clean clone."""


# Detect schema: a 34-cell first-pass layout vs the 35-cell post-paths-insert layout.
def _md_idx_for(header_substr):
    """Return the markdown cell index whose source begins with `header_substr`."""
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] != 'markdown':
            continue
        src = c['source'] if isinstance(c['source'], str) else ''.join(c.get('source', []))
        if header_substr in src[:200]:
            return i
    return None

REPLACE = {}
for header, body in [
    ('# 01 — Data Pipeline',                       CELL0),
    ('## 0. Setup',                                CELL1_SETUP),
    ('## 0.1 Paths',                               CELL_PATHS_NEW),
    ('## 1. Helper',                               CELL4_HELPERS),
    ('## 2. Load IEA',                             CELL6_LOAD_IEA),
    ('## 3. Load StatSUZ',                         CELL8_LOAD_STATSUZ),
    ('## 4. Load IRENA',                           CELL10_LOAD_IRENA),
    ('## 5. Load World Bank',                      CELL12_LOAD_WB),
    ('## 6. Unit',                                 CELL15_UNITS),
    ('## 7. Assemble',                             CELL17_ASSEMBLE),
    ('## 8. StatSUZ bridge',                       CELL19_BRIDGE),
    ('## 9. Preliminary',                          CELL21_PRELIM),
    ('## 10. Quality',                             CELL23_QC),
    ('## 11. Quick sanity',                        CELL30_PLOTS),
    ('## 12. Export',                              CELL32_EXPORT),
]:
    idx = _md_idx_for(header)
    if idx is None:
        print(f'WARN: no markdown cell found for header "{header}"')
        continue
    REPLACE[idx] = body

# Validate indices match expected markdown positions
for idx, body in REPLACE.items():
    if idx >= len(nb['cells']):
        sys.exit(f'ERROR: index {idx} beyond notebook length {len(nb["cells"])}')
    if nb['cells'][idx]['cell_type'] != 'markdown':
        sys.exit(f'ERROR: cell {idx} is {nb["cells"][idx]["cell_type"]}, expected markdown')
    nb['cells'][idx]['source'] = body
    nb['cells'][idx].pop('outputs', None)
    nb['cells'][idx].pop('execution_count', None)

# §0.1 paths-explainer: insert between imports-code and paths-code if not already
# present (first-pass layout). The REPLACE pass above already updates the cell
# if it already exists (second-pass layout).
paths_already = any(
    '0.1 Paths' in (c['source'] if isinstance(c['source'], str)
                    else ''.join(c.get('source', [])))
    for c in nb['cells'] if c['cell_type'] == 'markdown'
)
if not paths_already:
    paths_md_cell = md_cell(CELL_PATHS_NEW)
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code' and 'PATH_IEA_EMISSIONS' in (
                c['source'] if isinstance(c['source'], str)
                else ''.join(c.get('source', []))):
            nb['cells'].insert(i, paths_md_cell)
            break

# Ensure `def load_irena` exists in the helpers code cell (the worktree NB01
# does not have it; the project NB01 does).
for c in nb['cells']:
    if c['cell_type'] != 'code': continue
    src = c['source'] if isinstance(c['source'], str) else ''.join(c['source'])
    if 'def load_iea' in src and 'def load_irena' not in src:
        new_func = '''

def load_irena(filename, data_type_filter, technology_filter):
    """Load IRENA long-format CSV, filter UZB + technology, pivot to year×tech wide."""
    filepath = os.path.join(PATH_IRENA, filename)
    if not os.path.isfile(filepath):
        print(f'  ✗ NOT FOUND: {filepath}')
        return pd.DataFrame()
    df = pd.read_csv(filepath, skiprows=2)
    df.columns = [c.strip() for c in df.columns]
    df = df[df['Country/area'] == 'Uzbekistan']
    df = df[df['Data Type'] == data_type_filter]
    df = df[df['Technology'].isin(technology_filter)]
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Electricity statistics'] = pd.to_numeric(df['Electricity statistics'], errors='coerce')
    df = df.dropna(subset=['Year','Electricity statistics'])
    df['Year'] = df['Year'].astype(int)
    wide = df.pivot_table(index='Year', columns='Technology', values='Electricity statistics', aggfunc='sum')
    wide.index.name = 'year'
    wide = wide.loc[(wide.index >= YEAR_START) & (wide.index <= YEAR_END)]
    return wide

'''
        marker = "print('✓ Helper functions ready.')"
        if marker in src:
            c['source'] = src.replace(marker, new_func.strip() + '\n\n\n' + marker)
        else:
            c['source'] = src + new_func
        break

# §13 — supplementary feeds — idempotent insert OR refresh.
def _src(c):
    return c['source'] if isinstance(c['source'], str) else ''.join(c.get('source', []))

s13_header_idx = next((i for i, c in enumerate(nb['cells'])
                       if c['cell_type'] == 'markdown'
                       and '## 13. Supplementary feeds' in _src(c)), None)

if s13_header_idx is None:
    nb['cells'].append(md_cell(CELL_S13_HEADER))
    nb['cells'].append(code_cell(CELL_S13_LOADER))
    nb['cells'].append(md_cell(CELL_S13_INTERP))
else:
    # Refresh the existing three §13 cells in place.
    nb['cells'][s13_header_idx]['source'] = CELL_S13_HEADER
    nb['cells'][s13_header_idx + 1] = code_cell(CELL_S13_LOADER)
    if s13_header_idx + 2 < len(nb['cells']):
        nb['cells'][s13_header_idx + 2]['source'] = CELL_S13_INTERP
    else:
        nb['cells'].append(md_cell(CELL_S13_INTERP))

nb['metadata'] = nb.get('metadata', {})

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'✓ Rewrote NB01 ({NB_PATH}) — {len(nb["cells"])} cells, full inventory + §13 added.')
