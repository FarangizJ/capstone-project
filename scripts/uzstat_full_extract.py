"""
Comprehensive scan of the messy data dump.

For each of the 618 sdmx_data_<id>.csv files the script extracts:
  - structural fingerprint (rows, time range, monthly/annual, country flags)
  - row classifier theme (countries / Uzbekistan + oblasts / sectoral / single UZB)
  - sample row entities (Klassifikator_en) — the *contents* describe the topic
  - statistical fingerprint of the values (magnitude order, integer-vs-float,
    trend direction, % missing)

Outputs (data/processed/uzstat_clean/):
  - uzstat_full_manifest.csv         one row per file with fingerprint + topic guess
  - uzb_single_row_panel.csv         WIDE: year × every single-Uzbekistan-row series
  - uzb_oblast_panel_full.csv        LONG: (region, year, series_id, value) for all UZB+regions files
  - uzb_sectoral_panel.csv           LONG: (sector_en, year, series_id, value) for all sectoral files
  - intl_panel.csv                   LONG: (country_en, year, series_id, value) cross-country
"""
from __future__ import annotations
import csv
import re
import os
from pathlib import Path
from collections import Counter
from statistics import mean, median

import pandas as pd

ROOT  = Path(__file__).resolve().parents[1]
MESSY = Path('/Users/feya/Downloads/My capstone project/messy data')
OUT   = ROOT / 'data' / 'processed' / 'uzstat_clean'
OUT.mkdir(parents=True, exist_ok=True)

UZB_LABEL = 'Republic of Uzbekistan'
UZB_REGIONS = {
    'Republic of Karakalpakstan', 'Andijan region', 'Bukhara region', 'Jizzakh region',
    'Kashkadarya region', 'Navoiy region', 'Namangan region', 'Samarkand region',
    'Surkhandarya region', 'Syrdarya region', 'Tashkent region', 'Fergana region',
    'Khorezm region', 'Tashkent city',
}

# Confirmed topic mapping from stat.uz registry (partial, May 2026)
KNOWN_TOPICS = {
    # Energy / industry
    376:  'Thermal power capacity (MW)',
    380:  'Hydroelectric capacity (MW)',
    440:  'Electricity production by region (mln kWh)',
    444:  'Thermal energy production by region (thsd Gcal)',
    446:  'Solar power output (mln kWh)',
    458:  'Wind power output (mln kWh)',
    474:  'Oil production (thsd tonnes)',
    510:  'Gas condensate production (thsd tonnes)',
    516:  'Gasoline (motor fuel) production (thsd tonnes)',
    588:  'Total installed power capacity (MW)',
    2676: 'Diesel fuel production (thsd tonnes)',
    2677: 'Aviation kerosene production (thsd tonnes)',
    2678: 'Aviation gasoline production (thsd tonnes)',
    2679: 'Fuel oil (mazut) production (thsd tonnes)',
    2680: 'Natural gas production (mln m3)',
    2681: 'Natural gas consumption (mln m3)',
    2682: 'Coal production (thsd tonnes)',
    2683: 'Coal consumption (thsd tonnes)',
    2684: 'Electricity consumption by subscribers, by region (mln kWh)',
    2685: 'Electricity supply to enterprises (mln kWh)',
    2686: 'Electricity supply to housing (mln kWh)',
    # National accounts
    544:  'GDP, production method, current prices (bln UZS)',
    548:  'GVA of industries, current prices (bln UZS)',
    575:  'GDP, production method, constant prices (bln UZS)',
    582:  'GDP growth rate, production method (% YoY)',
    587:  'GDP, expenditure method, current prices (bln UZS)',
    625:  'GDP, expenditure method, constant prices (bln UZS)',
    641:  'GDP growth rate, expenditure method (% YoY)',
    658:  'GRP growth rate (% YoY)',
    1209: 'GVA of industries, constant prices (bln UZS)',
    1582: 'Gross regional product (quarterly)',
    1583: 'GVA of industries (quarterly)',
    1585: 'GVA of industry including construction (quarterly)',
    1588: 'GVA of services (quarterly)',
    1589: 'GVA trade/accommodation/food (quarterly)',
    1775: 'GVA transport/storage/info-comm (quarterly)',
    # Demography
    223:  'Number of births',
    226:  'Number of deaths',
    236:  'Population density (per km2)',
    241:  'General fertility rate',
    246:  'Permanent population, total (thsd)',
    247:  'Permanent population, rural (thsd)',
    248:  'Permanent population, urban (thsd)',
    229:  'Mortality rate',
    241:  'General fertility rate',
    295:  'Life expectancy at birth, total',
    665:  'Total fertility rate, total',
    662:  'Maternal mortality ratio',
    586:  'Infant mortality rate, total',
    # Labour
    500:  'Average nominal wage, annual (UZS)',
    506:  'Avg monthly wage by economic activity (quarterly)',
    522:  'Average nominal wage, quarterly (UZS)',
    515:  'Number of labour resources',
    521:  'Working-age population',
    532:  'Economic activity level (%)',
    554:  'Economically active population',
    567:  'Number of employed population',
    566:  'Economically inactive population',
    1310: 'Officially registered unemployed',
    1311: 'Employment rate',
    1313: 'Number of unemployed',
    1315: 'Distribution of employed by economic activity',
    1872: 'Number employed in public sector',
    1873: 'Number employed in non-state sector',
    # Living standards
    321:  'Total income of population (bln UZS)',
    329:  'Total income per capita by region',
    334:  'Growth rate of total income (%)',
    410:  'Real total income volume',
    624:  'Gini coefficient',
    1737: 'Share of low-income population (%)',
    3495: 'Poverty rate (%)',
    1325: 'Average household size',
    1242: 'Apartments with sewage (share)',
    1243: 'Apartments with natural gas (share)',
    1244: 'Total area of housing stock',
    1245: 'Number of residential apartments',
    # Services growth
    1206: 'Growth of market services rendered (%)',
    1207: 'Volume of motor transport services',
    1208: 'Communication & info services volume',
    1210: 'Total service sector volume by region',
    1212: 'Financial services volume',
    1213: 'Transport services volume',
    1220: 'Education services volume',
    1222: 'Trade services volume',
    1223: 'Accommodation and food services',
    1263: 'Telecommunication services volume',
}


def load_sdmx(path: Path):
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
        rd = csv.reader(f)
        header = next(rd)
        body = [row for row in rd if any(c.strip() for c in row)]
    return header, body


def classify_file(header, body):
    """Return (theme, time_cols, en_idx, monthly_bool)."""
    time_cols = [c for c in header if re.match(r'^(19|20)\d{2}', c)]
    monthly = bool(time_cols) and '-M' in time_cols[0]
    en_idx = header.index('Klassifikator_en') if 'Klassifikator_en' in header else None
    if en_idx is None or not time_cols or not body:
        return 'malformed', time_cols, en_idx, monthly
    entities = [r[en_idx] if len(r) > en_idx else '' for r in body]
    # Theme
    if len(entities) == 1 and entities[0] == UZB_LABEL:
        return 'national_single', time_cols, en_idx, monthly
    if UZB_LABEL in entities and any(e in UZB_REGIONS for e in entities):
        return 'national_with_regions', time_cols, en_idx, monthly
    if UZB_LABEL in entities and len(entities) <= 5:
        return 'national_breakdown', time_cols, en_idx, monthly  # UZB + small split (e.g., total/rural/urban)
    if UZB_LABEL not in entities and not any(e in UZB_REGIONS for e in entities):
        # All non-UZB rows: international comparison
        return 'international', time_cols, en_idx, monthly
    return 'sectoral_or_other', time_cols, en_idx, monthly


def value_fingerprint(body, en_idx, time_cols, header):
    """Stats about the numeric values to help guess the unit/magnitude."""
    vals = []
    for r in body:
        for tc in time_cols:
            try:
                ci = header.index(tc)
                v = r[ci] if ci < len(r) else ''
                if v.strip() == '': continue
                vals.append(float(v))
            except (ValueError, IndexError):
                pass
    if not vals: return {}
    mag = max(abs(v) for v in vals)
    is_intish = all(float(v).is_integer() for v in vals[:50])
    return {
        'n_vals': len(vals),
        'min': min(vals),
        'max': max(vals),
        'median': median(vals),
        'magnitude_order': int(f'{mag:.0e}'.split('e')[-1]) if mag > 0 else 0,
        'looks_integer': is_intish,
    }


def main():
    files = sorted([f for f in os.listdir(MESSY)
                    if f.startswith('sdmx_data_') and '(1)' not in f])
    manifest_rows = []
    single_series = {}   # series_id -> {year: value}  for UZB single-row files
    oblast_rows = []     # (region, year, series_id, value)
    sectoral_rows = []   # (sector_en, year, series_id, value)
    intl_rows = []       # (country_en, year, series_id, value)

    for fn in files:
        fid = int(re.search(r'(\d+)', fn).group(1))
        path = MESSY / fn
        try:
            header, body = load_sdmx(path)
        except Exception as e:
            manifest_rows.append({'id': fid, 'file': fn, 'error': str(e)})
            continue
        theme, time_cols, en_idx, monthly = classify_file(header, body)
        vfp = value_fingerprint(body, en_idx, time_cols, header) if en_idx is not None else {}

        # Per-theme extraction (annual only; monthly handled separately later if needed)
        if not monthly and en_idx is not None and time_cols:
            year_cols = time_cols
            year_idxs = [(yc, header.index(yc)) for yc in year_cols]
            if theme == 'national_single':
                d = {}
                row = body[0]
                for yc, ci in year_idxs:
                    v = row[ci] if ci < len(row) else ''
                    try:
                        d[int(yc[:4])] = float(v) if v.strip() else None
                    except ValueError:
                        d[int(yc[:4])] = None
                single_series[fid] = d
            elif theme == 'national_with_regions':
                for r in body:
                    if len(r) <= en_idx: continue
                    region = r[en_idx]
                    if region == UZB_LABEL: continue   # we'll reconstruct UZB total = sum of regions if needed
                    for yc, ci in year_idxs:
                        v = r[ci] if ci < len(r) else ''
                        try:
                            oblast_rows.append({
                                'region': region, 'year': int(yc[:4]),
                                'series_id': fid, 'value': float(v) if v.strip() else None
                            })
                        except ValueError:
                            pass
            elif theme == 'sectoral_or_other':
                for r in body:
                    if len(r) <= en_idx: continue
                    sec = r[en_idx]
                    for yc, ci in year_idxs:
                        v = r[ci] if ci < len(r) else ''
                        try:
                            sectoral_rows.append({
                                'sector_en': sec, 'year': int(yc[:4]),
                                'series_id': fid, 'value': float(v) if v.strip() else None
                            })
                        except ValueError:
                            pass
            elif theme == 'international':
                for r in body:
                    if len(r) <= en_idx: continue
                    cn = r[en_idx]
                    for yc, ci in year_idxs:
                        v = r[ci] if ci < len(r) else ''
                        try:
                            intl_rows.append({
                                'country_en': cn, 'year': int(yc[:4]),
                                'series_id': fid, 'value': float(v) if v.strip() else None
                            })
                        except ValueError:
                            pass

        # Capture top row labels as topic hint for files that cannot be auto-named
        en_labels_sample = []
        if en_idx is not None:
            for r in body[:5]:
                if len(r) > en_idx:
                    en_labels_sample.append(r[en_idx])

        manifest_rows.append({
            'id': fid, 'file': fn,
            'theme': theme,
            'monthly': int(monthly),
            'n_rows': len(body),
            'n_time': len(time_cols),
            't_start': time_cols[0] if time_cols else '',
            't_end':   time_cols[-1] if time_cols else '',
            'top_entities': ' | '.join(en_labels_sample[:5]),
            'known_topic': KNOWN_TOPICS.get(fid, ''),
            **vfp,
        })

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(OUT / 'uzstat_full_manifest.csv', index=False)
    print(f'-> manifest: {OUT/"uzstat_full_manifest.csv"} ({len(manifest)} files)')
    print('\nFiles by theme:')
    print(manifest['theme'].value_counts())

    # UZB single-row wide table
    if single_series:
        years = sorted({yr for d in single_series.values() for yr in d.keys()})
        wide = pd.DataFrame({'year': years})
        for fid in sorted(single_series.keys()):
            col = f'uzstat_{fid}'
            wide[col] = [single_series[fid].get(y) for y in years]
        wide.to_csv(OUT / 'uzb_single_row_panel.csv', index=False)
        print(f'-> single-row UZB panel: {wide.shape}, {len(single_series)} series')

    # Long panels
    if oblast_rows:
        df = pd.DataFrame(oblast_rows)
        df.to_csv(OUT / 'uzb_oblast_panel_full.csv', index=False)
        print(f'-> oblast panel (long): {df.shape}, {df["series_id"].nunique()} series, {df["region"].nunique()} regions')
    if sectoral_rows:
        df = pd.DataFrame(sectoral_rows)
        df.to_csv(OUT / 'uzb_sectoral_panel.csv', index=False)
        print(f'-> sectoral panel (long): {df.shape}, {df["series_id"].nunique()} series, {df["sector_en"].nunique()} sectors')
    if intl_rows:
        df = pd.DataFrame(intl_rows)
        df.to_csv(OUT / 'intl_panel.csv', index=False)
        print(f'-> intl panel (long): {df.shape}, {df["series_id"].nunique()} series, {df["country_en"].nunique()} countries')


if __name__ == '__main__':
    main()
