"""
Clean and merge selected UzStat SDMX CSVs from the messy data dump.

Outputs (written to data/processed/uzstat_clean/):
  - uzb_energy_national.csv     national-level energy series, annual 2010-2024
  - uzb_electricity_oblast.csv  oblast x year long panel (electricity production + consumption)
  - uzb_macro_national.csv      population/wages/services indices, annual where available
  - uzstat_id_registry.csv      registry of which SDMX IDs were used and their source URL
  - data_coverage_report.csv    one row per (variable, year) with non-null flag

Topic mapping confirmed from https://stat.uz/en/official-statistics/industry (May 2026).
"""
import os
import re
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MESSY = Path('/Users/feya/Downloads/My capstone project/messy data')
OUT   = ROOT / 'data' / 'processed' / 'uzstat_clean'
OUT.mkdir(parents=True, exist_ok=True)

# --- Topic registry ----------------------------------------------------------
ENERGY_NATIONAL = {
    376:  ('thermal_capacity_mw',           'MW',  'Thermal power capacity'),
    380:  ('hydro_capacity_mw',             'MW',  'Hydroelectric capacity'),
    446:  ('solar_output_mln_kwh',          'mln kWh', 'Solar power output'),
    458:  ('wind_output_mln_kwh',           'mln kWh', 'Wind power output'),
    474:  ('oil_production_kt',             'thsd t',  'Oil production'),
    510:  ('gas_condensate_production_kt',  'thsd t',  'Gas condensate production'),
    516:  ('gasoline_production_kt',        'thsd t',  'Gasoline (motor fuel) production'),
    588:  ('total_power_capacity_mw',       'MW',  'Total installed power capacity'),
    2676: ('diesel_production_kt',          'thsd t',  'Diesel fuel production'),
    2677: ('aviakerosene_production_kt',    'thsd t',  'Aviation kerosene production'),
    2678: ('aviagasoline_production_kt',    'thsd t',  'Aviation gasoline production'),
    2679: ('fuel_oil_production_kt',        'thsd t',  'Fuel oil (mazut) production'),
    2680: ('nat_gas_production_mcm',        'mln m3',  'Natural gas production'),
    2681: ('nat_gas_consumption_mcm',       'mln m3',  'Natural gas consumption'),
    2682: ('coal_production_kt',            'thsd t',  'Coal production'),
    2683: ('coal_consumption_kt',           'thsd t',  'Coal consumption'),
    2685: ('elec_supply_enterprises_gwh',   'GWh',     'Electricity supply to enterprises'),
    2686: ('elec_supply_housing_gwh',       'GWh',     'Electricity supply to housing'),
}

# Series with both national and oblast rows
ENERGY_BY_REGION = {
    440:  ('elec_production_gwh',           'GWh', 'Electricity production'),
    444:  ('thermal_energy_production_kkcal','thsd Gcal', 'Thermal energy production'),
    2684: ('elec_consumption_subscribers_gwh','GWh', 'Electricity consumption by subscribers'),
}

# Macro / demography / labour (single-row UZB national)
MACRO_NATIONAL = {
    246:  ('population_total',              'persons',  'Permanent population (total)'),
    247:  ('population_rural',              'persons',  'Permanent population (rural)'),
    248:  ('population_urban',              'persons',  'Permanent population (urban)'),
    236:  ('population_density',            'per km2',  'Population density'),
    500:  ('avg_nominal_wage_uzs',          'UZS',      'Average nominal wage (annual)'),
    567:  ('employed_persons',              'persons',  'Number of employed population'),
    1206: ('services_growth_idx_pct',       '% YoY',    'Growth rates of market services rendered'),
    321:  ('total_income_population_uzs',   'bln UZS',  'Total income of the population'),
    624:  ('gini_coefficient',              'index',    'Income inequality (Gini coefficient)'),
    3495: ('poverty_rate_pct',              '%',        'Poverty rate'),
    1737: ('low_income_share_pct',          '%',        'Share of low-income population'),
}

UZB_LABEL = 'Republic of Uzbekistan'


def _load_sdmx(path: Path):
    """Return (header, body) lists, decoded UTF-8-sig."""
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
        rd = csv.reader(f)
        header = next(rd)
        body = [row for row in rd if row]
    return header, body


def _melt_long(header, body, var_name, time_cols=None):
    """Convert SDMX wide rows into a tidy long DataFrame."""
    if time_cols is None:
        time_cols = [c for c in header if re.match(r'^(19|20)\d{2}', c)]
    # Drop duplicate columns (e.g. some files repeat a period); keep first
    seen = set(); deduped = []
    for c in time_cols:
        if c in seen: continue
        seen.add(c); deduped.append(c)
    time_cols = deduped
    # Build dataframe, taking only the first occurrence of each header column
    keep_idx, kept_names = [], []
    for i, h in enumerate(header):
        if h == 'Klassifikator_en' and 'Klassifikator_en' not in kept_names:
            keep_idx.append(i); kept_names.append('Klassifikator_en')
        elif h in time_cols and h not in kept_names:
            keep_idx.append(i); kept_names.append(h)
    rows = [[r[i] if i < len(r) else '' for i in keep_idx] for r in body]
    df = pd.DataFrame(rows, columns=kept_names).rename(columns={'Klassifikator_en': 'region'})
    long = df.melt(id_vars='region', var_name='period', value_name=var_name)
    long[var_name] = pd.to_numeric(long[var_name].replace('', None), errors='coerce')
    # period parsing — handle 'YYYY', 'YYYY-MNN', 'YYYY-MN'
    period = long['period'].astype(str)
    is_monthly = period.str.contains('-M', regex=False).any()
    if is_monthly:
        ym = period.str.extract(r'^(\d{4})-M(\d{1,2})$')
        long['year']  = pd.to_numeric(ym[0], errors='coerce').astype('Int64')
        long['month'] = pd.to_numeric(ym[1], errors='coerce').astype('Int64')
    else:
        long['year']  = pd.to_numeric(period.str.extract(r'^(\d{4})')[0], errors='coerce').astype('Int64')
        long['month'] = pd.NA
    long = long.dropna(subset=['year']).copy()
    long['year'] = long['year'].astype(int)
    return long


def build_energy_national(messy_dir: Path) -> pd.DataFrame:
    out = None
    used_ids = []
    for fid, (col, unit, title) in ENERGY_NATIONAL.items():
        p = messy_dir / f'sdmx_data_{fid}.csv'
        if not p.exists():
            print(f'  [skip] {fid} {col}: file missing')
            continue
        header, body = _load_sdmx(p)
        long = _melt_long(header, body, col)
        nat = long[long['region'] == UZB_LABEL][['year', col]].dropna()
        if nat.empty:
            print(f'  [skip] {fid} {col}: no Uzbekistan row')
            continue
        nat = nat.sort_values('year').drop_duplicates('year', keep='first')
        out = nat if out is None else out.merge(nat, on='year', how='outer')
        used_ids.append({'id': fid, 'column': col, 'unit': unit, 'title': title,
                         'source': f'https://stat.uz/uz/sdmx/data/{fid}.csv'})
    out = out.sort_values('year').reset_index(drop=True) if out is not None else pd.DataFrame()
    return out, used_ids


def build_energy_oblast(messy_dir: Path) -> pd.DataFrame:
    pieces = []
    used = []
    for fid, (col, unit, title) in ENERGY_BY_REGION.items():
        p = messy_dir / f'sdmx_data_{fid}.csv'
        if not p.exists():
            print(f'  [skip] {fid} {col}: missing')
            continue
        header, body = _load_sdmx(p)
        long = _melt_long(header, body, col)
        long = long[long['region'] != UZB_LABEL].dropna(subset=[col])
        long = long[['region', 'year', col]]
        pieces.append(long)
        used.append({'id': fid, 'column': col, 'unit': unit, 'title': title,
                     'source': f'https://stat.uz/uz/sdmx/data/{fid}.csv'})
    if not pieces:
        return pd.DataFrame(), used
    # Outer-merge each variable on (region, year)
    merged = pieces[0]
    for nxt in pieces[1:]:
        merged = merged.merge(nxt, on=['region', 'year'], how='outer')
    merged = merged.sort_values(['region', 'year']).reset_index(drop=True)
    return merged, used


def build_macro_national(messy_dir: Path):
    out = None
    used = []
    for fid, (col, unit, title) in MACRO_NATIONAL.items():
        p = messy_dir / f'sdmx_data_{fid}.csv'
        if not p.exists():
            print(f'  [skip] {fid} {col}: missing')
            continue
        header, body = _load_sdmx(p)
        long = _melt_long(header, body, col)
        nat = long[long['region'] == UZB_LABEL][['year', col]].dropna()
        if nat.empty:
            continue
        nat = nat.sort_values('year').drop_duplicates('year', keep='first')
        out = nat if out is None else out.merge(nat, on='year', how='outer')
        used.append({'id': fid, 'column': col, 'unit': unit, 'title': title,
                     'source': f'https://stat.uz/uz/sdmx/data/{fid}.csv'})
    out = out.sort_values('year').reset_index(drop=True) if out is not None else pd.DataFrame()
    return out, used


def main():
    print(f'-> Reading from {MESSY}')
    print(f'-> Writing to   {OUT}')

    print('\n[1] National energy series')
    nat, ids_nat = build_energy_national(MESSY)
    print(f'   rows: {len(nat)}, cols: {len(nat.columns) - 1 if not nat.empty else 0}')
    nat.to_csv(OUT / 'uzb_energy_national.csv', index=False)

    print('\n[2] Oblast electricity production + consumption')
    obl, ids_obl = build_energy_oblast(MESSY)
    print(f'   rows: {len(obl)}, regions: {obl["region"].nunique() if not obl.empty else 0}')
    obl.to_csv(OUT / 'uzb_electricity_oblast.csv', index=False)

    print('\n[3] Macro / population / labour')
    mac, ids_mac = build_macro_national(MESSY)
    print(f'   rows: {len(mac)}, cols: {len(mac.columns) - 1 if not mac.empty else 0}')
    mac.to_csv(OUT / 'uzb_macro_national.csv', index=False)

    # Registry
    pd.DataFrame(ids_nat + ids_obl + ids_mac).to_csv(OUT / 'uzstat_id_registry.csv', index=False)

    # Coverage report
    rows = []
    for col in nat.columns:
        if col == 'year':
            continue
        for _, r in nat.iterrows():
            rows.append({'scope': 'national', 'variable': col, 'year': int(r['year']),
                         'has_value': int(pd.notna(r[col]))})
    cov = pd.DataFrame(rows)
    cov.to_csv(OUT / 'data_coverage_report.csv', index=False)

    print('\nDone.')
    print(f'  uzb_energy_national.csv   {nat.shape}')
    print(f'  uzb_electricity_oblast.csv {obl.shape}')
    print(f'  uzb_macro_national.csv     {mac.shape}')


if __name__ == '__main__':
    main()
