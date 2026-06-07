"""
export_data.py — Uzbekistan Power Sector Transition Tracker
============================================================
Builds verified, audit-ready JSON files for the report website.

DATA SOURCES (all from /data/raw/):
  - IEA  : electricity generation by source (2000–2023), CO2 emissions from power
  - IRENA: installed capacity (2000–2024), generation cross-check
  - StatSUZ: national statistics agency (2010–2024), extends IEA for 2024
  - World Bank: GDP, population, per-capita electricity (2000–2023)

DATA INTEGRITY RULES:
  1. No interpolation. No null-filling. Missing = null in output JSON.
  2. CO2 intensity is computed from actual MtCO2 / TWh (not the IEA index).
  3. 2024 uses StatSUZ only (IEA not yet published).
  4. Solar/wind pre-2017 are genuine zeros — treated as 0, not missing.
  5. Every value is traceable to a source column noted in DATA_SOURCES below.

Run:
  python scripts/export_data.py

Output:
  docs/data/historical.json   — annual time series 2000–2024
  docs/data/audit_log.json    — data sources and quality flags per column
"""

import os
import json
import math
import pandas as pd
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW       = os.path.join(ROOT, 'data', 'raw')
OUT       = os.path.join(ROOT, 'docs', 'data')
os.makedirs(OUT, exist_ok=True)

PATH_IEA_PROD   = os.path.join(RAW, 'energy production data (source - IEA)')
PATH_IEA_EMIT   = os.path.join(RAW, 'emissions (source - IEA)')
PATH_IRENA      = os.path.join(RAW, 'energy production data (source - IRENA)')
PATH_STATSUZ    = os.path.join(RAW, 'statsuz')
PATH_WB         = os.path.join(RAW, 'socioeconomic macro indicators (source - World Bank)')

YEAR_START = 2000
YEAR_END   = 2024


# ── Helpers ────────────────────────────────────────────────────────────────────
def load_iea(filename, folder=PATH_IEA_PROD, col_map=None):
    """Load an IEA CSV (3-row header, years as index, values in first data col or named cols)."""
    path = os.path.join(folder, filename)
    df = pd.read_csv(path, skiprows=3, index_col=0)
    if 'Units' in df.columns:
        df = df.drop(columns=['Units'])
    df.index = pd.to_numeric(df.index, errors='coerce')
    df = df.loc[df.index.notna()]
    df.index = df.index.astype(int)
    df = df.apply(pd.to_numeric, errors='coerce')
    if col_map:
        df = df.rename(columns=col_map)
    return df.loc[df.index.isin(range(YEAR_START, YEAR_END + 1))]


def load_statsuz(filename):
    """Load StatSUZ CSV, return national total row as a Series indexed by year."""
    path = os.path.join(PATH_STATSUZ, filename)
    df = pd.read_csv(path)
    # Row 0 is always the national total (code 1700, Republic of Uzbekistan)
    row = df.iloc[0]
    year_cols = {}
    for col in df.columns:
        try:
            yr = int(col)
            if YEAR_START <= yr <= YEAR_END:
                year_cols[yr] = pd.to_numeric(row[col], errors='coerce')
        except (ValueError, TypeError):
            pass
    return pd.Series(year_cols, name=filename)


def nan_to_none(val):
    """Convert NaN/inf to None for JSON serialisation."""
    if val is None:
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(float(val), 4)
    try:
        if math.isnan(val) or math.isinf(val):
            return None
    except TypeError:
        pass
    return val


# ══════════════════════════════════════════════════════════════════════════════
# 1. IEA — Electricity generation by source (GWh → TWh)
# ══════════════════════════════════════════════════════════════════════════════
print("1. Loading IEA electricity generation...")
iea_gen_raw = load_iea(
    'Electricity generation by source - Uzbekistan.csv',
    col_map={
        'Coal':        'coal_gwh',
        'Oil':         'oil_gwh',
        'Natural gas': 'gas_gwh',
        'Hydropower':  'hydro_gwh',
        'Solar PV':    'solar_gwh',
        'Wind':        'wind_gwh',
    }
)

GWH_TO_TWH = 1 / 1000

# Solar and wind: IEA shows NaN before solar/wind existed — those are true zeros
# IEA began reporting solar for Uzbekistan from 2017 (0.0 GWh), so pre-2017 = 0
for col in ['solar_gwh', 'wind_gwh']:
    if col in iea_gen_raw.columns:
        iea_gen_raw[col] = iea_gen_raw[col].fillna(0)

gen = iea_gen_raw.copy()
gen['gen_gas_twh']   = gen.get('gas_gwh',   0) * GWH_TO_TWH
gen['gen_coal_twh']  = gen.get('coal_gwh',  0) * GWH_TO_TWH
gen['gen_oil_twh']   = gen.get('oil_gwh',   0) * GWH_TO_TWH
gen['gen_hydro_twh'] = gen.get('hydro_gwh', 0) * GWH_TO_TWH
gen['gen_solar_twh'] = gen.get('solar_gwh', 0) * GWH_TO_TWH
gen['gen_wind_twh']  = gen.get('wind_gwh',  0) * GWH_TO_TWH

gen['gen_fossil_twh']    = gen['gen_gas_twh'] + gen['gen_coal_twh'] + gen['gen_oil_twh']
gen['gen_renewable_twh'] = gen['gen_hydro_twh'] + gen['gen_solar_twh'] + gen['gen_wind_twh']
gen['gen_total_twh_iea'] = gen['gen_fossil_twh'] + gen['gen_renewable_twh']
gen['re_penetration_pct'] = gen['gen_renewable_twh'] / gen['gen_total_twh_iea'] * 100
gen['fossil_share_pct']   = gen['gen_fossil_twh']    / gen['gen_total_twh_iea'] * 100

print(f"   IEA generation: {gen.index.min()}–{gen.index.max()}, {len(gen)} years")


# ══════════════════════════════════════════════════════════════════════════════
# 2. IEA — CO2 emissions from electricity and heat (MtCO2)
#    → compute real intensity = MtCO2 / TWh_gen * 1000  (gCO2/kWh)
#    NOTE: The IEA "CO2 intensity of power" file uses Index (2000=100) — NOT used here.
# ══════════════════════════════════════════════════════════════════════════════
print("2. Computing real CO2 intensity from IEA emissions + generation...")
co2_raw = load_iea(
    'CO2 emissions from electricity and heat by energy source - Uzbekistan.csv',
    folder=PATH_IEA_EMIT,
    col_map={'Coal': 'co2_coal', 'Oil': 'co2_oil', 'Natural gas': 'co2_gas', 'Other': 'co2_other'}
)
co2_raw['co2_total_MtCO2'] = co2_raw[['co2_coal', 'co2_oil', 'co2_gas']].sum(axis=1, min_count=1)

# Join with generation to compute intensity
co2_combined = co2_raw[['co2_total_MtCO2']].join(gen[['gen_total_twh_iea']], how='left')
# gCO2/kWh: (MtCO2 / TWh) * 1000   [1 Mt = 1e12 g; 1 TWh = 1e9 kWh; ratio = 1000]
co2_combined['co2_intensity_gco2_kwh'] = (
    co2_combined['co2_total_MtCO2'] / co2_combined['gen_total_twh_iea'] * 1000
)
print(f"   CO2 intensity range: {co2_combined['co2_intensity_gco2_kwh'].min():.0f}–"
      f"{co2_combined['co2_intensity_gco2_kwh'].max():.0f} gCO2/kWh "
      f"(correct for a gas-heavy grid; NOT an index)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. StatSUZ — Extends key series through 2024
# ══════════════════════════════════════════════════════════════════════════════
print("3. Loading StatSUZ data (2010–2024)...")
sc_prod     = load_statsuz('Volume of electricity production.csv')         # GWh
sc_supply   = load_statsuz('Volume of electricity supply.csv')             # GWh
sc_capacity = load_statsuz('Total installed capacity of power plants.csv') # MW
sc_solar    = load_statsuz('Volume of electricity produced by solar power plants.csv')  # GWh
sc_wind     = load_statsuz('Volume of electricity produced by wind power farms.csv')    # GWh

sc_gen_twh      = sc_prod   * GWH_TO_TWH
sc_supply_twh   = sc_supply * GWH_TO_TWH
sc_solar_twh    = sc_solar  * GWH_TO_TWH
sc_wind_twh     = sc_wind   * GWH_TO_TWH


# ══════════════════════════════════════════════════════════════════════════════
# 4. IRENA — Installed capacity (MW) and generation cross-check
# ══════════════════════════════════════════════════════════════════════════════
print("4. Loading IRENA capacity data...")
irena_raw = pd.read_csv(
    os.path.join(PATH_IRENA, 'production data from IRENA_ELEC-C_20260305-091153.csv'),
    skiprows=1, names=['country','technology','data_type','grid','year','value']
)
irena_uzb = irena_raw[
    (irena_raw['country'] == 'Uzbekistan') & (irena_raw['grid'] == 'All')
].copy()
irena_uzb['year']  = pd.to_numeric(irena_uzb['year'],  errors='coerce')
irena_uzb['value'] = pd.to_numeric(irena_uzb['value'], errors='coerce')

irena_cap = (
    irena_uzb[irena_uzb['data_type'] == 'Electricity Installed Capacity (MW)']
    .groupby(['year', 'technology'])['value'].sum().unstack()
)
irena_gen_check = (
    irena_uzb[irena_uzb['data_type'] == 'Electricity Generation (GWh)']
    .groupby(['year', 'technology'])['value'].sum().unstack()
)


# ══════════════════════════════════════════════════════════════════════════════
# 5. World Bank — GDP, population, per-capita electricity
# ══════════════════════════════════════════════════════════════════════════════
print("5. Loading World Bank data...")
wb_series = {
    'NY.GDP.MKTP.KD':     'wb_gdp_const2015_usd',
    'NY.GDP.MKTP.KD.ZG':  'wb_gdp_growth_pct',
    'SP.POP.TOTL':        'wb_population',
    'SP.URB.TOTL.IN.ZS':  'wb_urban_pop_pct',
    'EG.USE.ELEC.KH.PC':  'wb_elec_pc_kwh',
    'EG.ELC.LOSS.ZS':     'wb_td_losses_pct',
    'EG.ELC.RNEW.ZS':     'wb_re_share_pct',
}

wb_zip  = os.path.join(PATH_WB, 'P_Data_Extract_From_World_Development_Indicators.zip')
import zipfile
with zipfile.ZipFile(wb_zip) as z:
    data_file = [n for n in z.namelist() if '_Data.csv' in n][0]
    with z.open(data_file) as _f:
        wb_raw = pd.read_csv(_f, encoding='latin-1')

wb_frames = []
for code, col_name in wb_series.items():
    row = wb_raw[wb_raw['Series Code'] == code]
    if row.empty:
        print(f"   WARNING: {code} not found in World Bank file")
        continue
    year_data = {}
    for c in row.columns:
        # Columns look like "2000 [YR2000]"
        if '[YR' in str(c):
            yr = int(c.split('[YR')[1].replace(']', ''))
            if YEAR_START <= yr <= YEAR_END:
                val = row[c].values[0]
                year_data[yr] = pd.to_numeric(str(val).replace('..', ''), errors='coerce')
    s = pd.Series(year_data, name=col_name)
    wb_frames.append(s)

wb = pd.concat(wb_frames, axis=1) if wb_frames else pd.DataFrame()
wb.index.name = 'year'
print(f"   World Bank: {wb.index.min()}–{wb.index.max()}, series: {list(wb.columns)}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. Assemble master: 2000–2024
# ══════════════════════════════════════════════════════════════════════════════
print("6. Assembling master dataset...")

years = list(range(YEAR_START, YEAR_END + 1))
master = pd.DataFrame(index=pd.Index(years, name='year'))

# --- Generation columns (IEA primary, StatSUZ for 2024) ---
for col in ['gen_gas_twh','gen_coal_twh','gen_oil_twh','gen_hydro_twh',
            'gen_solar_twh','gen_wind_twh','gen_fossil_twh','gen_renewable_twh',
            'gen_total_twh_iea','re_penetration_pct','fossil_share_pct']:
    master[col] = gen.get(col)

# 2024: IEA not yet published → use StatSUZ totals
# For 2024 breakdown by source, IEA is not available.
# StatSUZ totals + solar + wind are available, but not the gas/coal/hydro breakdown.
# Store the available aggregates; mark the breakdown columns as null.
master.loc[2024, 'gen_total_twh_statsuz'] = sc_gen_twh.get(2024)
master.loc[2024, 'gen_solar_twh']         = sc_solar_twh.get(2024, master.get('gen_solar_twh', pd.Series()).get(2024))
master.loc[2024, 'gen_wind_twh']          = sc_wind_twh.get(2024,  master.get('gen_wind_twh', pd.Series()).get(2024))

# StatSUZ cross-check column (2010–2024)
master['gen_total_twh_statsuz'] = pd.Series(
    {yr: sc_gen_twh.get(yr) for yr in years if sc_gen_twh.get(yr) is not None}
)
master['elec_supply_twh_statsuz'] = pd.Series(
    {yr: sc_supply_twh.get(yr) for yr in years if sc_supply_twh.get(yr) is not None}
)

# --- CO2 intensity (REAL gCO2/kWh, not index) ---
master['co2_intensity_gco2_kwh'] = co2_combined['co2_intensity_gco2_kwh']
master['co2_total_MtCO2']        = co2_combined['co2_total_MtCO2']

# --- Installed capacity ---
# StatSUZ is authoritative (2010–2024)
master['capacity_total_mw'] = pd.Series(
    {yr: sc_capacity.get(yr) for yr in years if sc_capacity.get(yr) is not None}
)
# IRENA hydro capacity (2000–2024, fills gap pre-2010)
if 'Renewable hydropower' in irena_cap.columns:
    master['capacity_hydro_mw_irena'] = irena_cap['Renewable hydropower'].reindex(years)
if 'Solar photovoltaic' in irena_cap.columns:
    master['capacity_solar_mw_irena'] = irena_cap['Solar photovoltaic'].reindex(years)
if 'Onshore wind energy' in irena_cap.columns:
    master['capacity_wind_mw_irena'] = irena_cap['Onshore wind energy'].reindex(years)

# --- StatSUZ solar/wind generation (2015–2024, more granular than IEA) ---
master['gen_solar_twh_statsuz'] = pd.Series(
    {yr: sc_solar_twh.get(yr) for yr in years if sc_solar_twh.get(yr) is not None}
)
master['gen_wind_twh_statsuz'] = pd.Series(
    {yr: sc_wind_twh.get(yr) for yr in years if sc_wind_twh.get(yr) is not None}
)

# --- World Bank ---
if not wb.empty:
    for col in wb.columns:
        master[col] = wb[col].reindex(years)

# --- Data status flag ---
# 2024: StatSUZ only (IEA not published yet); 2023 and earlier: IEA confirmed
master['data_source_gen']  = 'IEA'
master.loc[2024, 'data_source_gen'] = 'StatSUZ (IEA pending)'
master['year_status'] = 'confirmed'
master.loc[2024, 'year_status'] = 'preliminary'


# ══════════════════════════════════════════════════════════════════════════════
# 7. Data quality audit
# ══════════════════════════════════════════════════════════════════════════════
print("7. Running data quality checks...")

COLUMN_AUDIT = {
    'gen_gas_twh':            {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': ''},
    'gen_coal_twh':           {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': ''},
    'gen_oil_twh':            {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': ''},
    'gen_hydro_twh':          {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': ''},
    'gen_solar_twh':          {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': 'Pre-2017: genuine zero (no solar capacity existed)'},
    'gen_wind_twh':           {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': 'Near-zero before 2019'},
    'gen_total_twh_iea':      {'source': 'IEA',     'unit': 'TWh',       'years': '2000–2023', 'note': ''},
    'gen_total_twh_statsuz':  {'source': 'StatSUZ', 'unit': 'TWh',       'years': '2010–2024', 'note': 'Cross-check; 2024 primary'},
    'gen_solar_twh_statsuz':  {'source': 'StatSUZ', 'unit': 'TWh',       'years': '2015–2024', 'note': '2024: 3.97 TWh (major ramp-up)'},
    'gen_wind_twh_statsuz':   {'source': 'StatSUZ', 'unit': 'TWh',       'years': '2015–2024', 'note': '2024: 0.79 TWh'},
    're_penetration_pct':     {'source': 'IEA',     'unit': '%',         'years': '2000–2023', 'note': 'Computed from IEA generation'},
    'fossil_share_pct':       {'source': 'IEA',     'unit': '%',         'years': '2000–2023', 'note': 'Computed from IEA generation'},
    'co2_intensity_gco2_kwh': {'source': 'IEA',     'unit': 'gCO2/kWh', 'years': '2000–2023', 'note': 'Computed: MtCO2_power / TWh_gen * 1000. NOT the IEA index file.'},
    'co2_total_MtCO2':        {'source': 'IEA',     'unit': 'MtCO2',    'years': '2000–2023', 'note': 'From electricity and heat emissions file'},
    'capacity_total_mw':      {'source': 'StatSUZ', 'unit': 'MW',        'years': '2010–2024', 'note': 'No data before 2010 in any source'},
    'capacity_hydro_mw_irena':{'source': 'IRENA',   'unit': 'MW',        'years': '2000–2024', 'note': ''},
    'capacity_solar_mw_irena':{'source': 'IRENA',   'unit': 'MW',        'years': '2000–2024', 'note': ''},
    'capacity_wind_mw_irena': {'source': 'IRENA',   'unit': 'MW',        'years': '2000–2024', 'note': ''},
    'wb_gdp_const2015_usd':   {'source': 'World Bank', 'unit': 'USD 2015 const', 'years': '2000–2022', 'note': ''},
    'wb_gdp_growth_pct':      {'source': 'World Bank', 'unit': '%',      'years': '2000–2023', 'note': ''},
    'wb_population':          {'source': 'World Bank', 'unit': 'persons', 'years': '2000–2023', 'note': ''},
    'wb_elec_pc_kwh':         {'source': 'World Bank', 'unit': 'kWh/person', 'years': '2000–2021', 'note': ''},
    'wb_td_losses_pct':       {'source': 'World Bank', 'unit': '%',      'years': '2000–2021', 'note': 'WB stops at 2021; suspicious 2018 dip noted in pipeline'},
}

audit = {}
for col, meta in COLUMN_AUDIT.items():
    if col in master.columns:
        s = master[col]
        n_real = int(s.notna().sum())
        audit[col] = {
            **meta,
            'n_real': n_real,
            'n_total': len(master),
            'completeness_pct': round(n_real / len(master) * 100, 1),
            'min': nan_to_none(s.min()),
            'max': nan_to_none(s.max()),
        }

print("\n=== AUDIT SUMMARY ===")
print(f"{'Column':<30} {'Complete':>8}  {'Source':<12} {'Note'}")
print("-" * 90)
for col, a in audit.items():
    flag = ' ⚠' if a['completeness_pct'] < 50 else ''
    print(f"{col:<30} {a['completeness_pct']:>7.0f}%  {a['source']:<12} {a['note'][:50]}{flag}")


# ══════════════════════════════════════════════════════════════════════════════
# 8. Export JSON
# ══════════════════════════════════════════════════════════════════════════════
print("\n8. Exporting JSON files...")

# historical.json — one record per year
records = []
for yr in years:
    row = master.loc[yr]
    record = {'year': yr}
    for col in master.columns:
        record[col] = nan_to_none(row[col])
    records.append(record)

hist_path = os.path.join(OUT, 'historical.json')
with open(hist_path, 'w') as f:
    json.dump(records, f, indent=2)
print(f"   ✓ {hist_path}  ({len(records)} records)")

# audit_log.json
audit_path = os.path.join(OUT, 'audit_log.json')
with open(audit_path, 'w') as f:
    json.dump(audit, f, indent=2)
print(f"   ✓ {audit_path}  ({len(audit)} columns audited)")

print("\nDone. All values are from primary sources — no interpolation, no null-filling.")
