"""
Build the pooled Central Asia panel for transfer learning / pooled-regression.

Outputs (data/processed/uzstat_clean/):
  - central_asia_panel.csv     long panel: country x year with electricity demand + drivers
  - central_asia_provenance.csv  source URLs per series

Data sources:
  - OWID Energy dataset (Ember + EI Statistical Review of World Energy compiled by Our World in Data)
    https://ourworldindata.org/grapher/electricity-consumption-per-capita
    raw CSV: https://github.com/owid/energy-data/raw/master/owid-energy-data.csv
  - World Bank WDI via wbdata (GDP, population, urbanisation, sectoral GVA)

Countries: UZB, KAZ, KGZ, TJK, TKM (full Central Asia "stans").
Time window: 1990..latest year available.

The choice of CA-5 as the donor pool follows Francesca's 2026-05-19 feedback:
"You stack all data from Uzbekistan and Kazakhstan (and also other Central Asia countries),
adding a column to say which country each row belongs to, and train Ridge."
"""
import os
import io
from pathlib import Path
import ssl
from urllib.request import urlopen
from urllib.error import URLError

import certifi
import pandas as pd

# Explicit CA bundle context. macOS Python.org installers ship without a
# system-wide CA bundle, so the default urlopen() handshake fails with
# SSLCertVerificationError on first run. Passing an explicit context backed
# by certifi makes the fetcher portable across machines.
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

try:
    import wbdata
    HAS_WBDATA = True
except Exception:
    HAS_WBDATA = False

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / 'data' / 'processed' / 'uzstat_clean'
OUT.mkdir(parents=True, exist_ok=True)

COUNTRIES = {
    'UZB': 'Uzbekistan',
    'KAZ': 'Kazakhstan',
    'KGZ': 'Kyrgyzstan',
    'TJK': 'Tajikistan',
    'TKM': 'Turkmenistan',
}

OWID_URL = 'https://github.com/owid/energy-data/raw/master/owid-energy-data.csv'

WB_INDICATORS = {
    'NY.GDP.MKTP.KD':    'gdp_const2015_usd',
    'NY.GDP.PCAP.KD':    'gdp_pc_const2015_usd',
    'NV.IND.TOTL.KD':    'industry_va_const2015_usd',
    'NV.IND.MANF.KD':    'mfg_va_const2015_usd',
    'NV.SRV.TOTL.KD':    'services_va_const2015_usd',
    'NV.AGR.TOTL.KD':    'agri_va_const2015_usd',
    'SP.POP.TOTL':       'population_total',
    'SP.URB.TOTL.IN.ZS': 'urban_pop_pct',
    'EG.ELC.LOSS.ZS':    'td_losses_pct',
    'EN.ATM.CO2E.KT':    'co2_kt',
}


def fetch_owid_energy() -> pd.DataFrame:
    print(f'[OWID] downloading {OWID_URL}')
    try:
        raw = urlopen(OWID_URL, timeout=120, context=SSL_CTX).read().decode('utf-8')
    except URLError as e:
        raise RuntimeError(f'OWID fetch failed: {e}')
    df = pd.read_csv(io.StringIO(raw))
    df = df[df['iso_code'].isin(COUNTRIES.keys())]
    keep = ['iso_code', 'country', 'year',
            'electricity_demand', 'electricity_generation',
            'electricity_demand_per_capita', 'fossil_electricity',
            'renewables_electricity', 'low_carbon_electricity',
            'coal_electricity', 'gas_electricity', 'hydro_electricity',
            'solar_electricity', 'wind_electricity',
            'primary_energy_consumption', 'energy_per_capita',
            'gas_consumption', 'coal_consumption', 'oil_consumption']
    keep = [c for c in keep if c in df.columns]
    df = df[keep].sort_values(['iso_code', 'year']).reset_index(drop=True)
    return df


def fetch_world_bank() -> pd.DataFrame:
    if not HAS_WBDATA:
        print('[WB] wbdata not installed — skipping')
        return pd.DataFrame()
    frames = []
    for iso in COUNTRIES.keys():
        print(f'[WB] {iso}')
        per_iso = None
        for code, col in WB_INDICATORS.items():
            try:
                d = wbdata.get_dataframe({code: col}, country=iso).sort_index()
            except Exception as e:
                print(f'   skip {code}: {str(e)[:80]}')
                continue
            d.index = d.index.astype(int); d.index.name = 'year'
            d = d.reset_index()
            per_iso = d if per_iso is None else per_iso.merge(d, on='year', how='outer')
        if per_iso is None:
            continue
        per_iso['iso_code'] = iso
        per_iso['country'] = COUNTRIES[iso]
        frames.append(per_iso)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main():
    owid = fetch_owid_energy()
    print(f'[OWID] rows: {len(owid)}, countries: {owid["iso_code"].nunique()}')
    wb = fetch_world_bank()
    print(f'[WB]   rows: {len(wb)}, countries: {wb["iso_code"].nunique() if not wb.empty else 0}')

    if not wb.empty:
        panel = owid.merge(wb, on=['iso_code', 'country', 'year'], how='outer')
    else:
        panel = owid

    # Per-country temperature: leave out for v1 (Open-Meteo is single-point only;
    # would need a country centroid fetch per country — flagged as next step).

    panel = panel.sort_values(['iso_code', 'year']).reset_index(drop=True)
    out_path = OUT / 'central_asia_panel.csv'
    panel.to_csv(out_path, index=False)
    print(f'-> wrote {out_path}  shape={panel.shape}')

    # Coverage report by country
    cov = (panel.assign(has_demand=panel['electricity_demand'].notna())
                 .groupby('iso_code')['has_demand']
                 .agg(['sum', 'count']))
    print('\nElectricity-demand coverage by country (years with value / years total):')
    print(cov)

    prov = pd.DataFrame([
        {'source': 'OWID energy dataset (Ember + EI compiled)',
         'url': OWID_URL,
         'variables': 'electricity_demand, electricity_generation, fossil/renewables/coal/gas/hydro/solar/wind, energy_per_capita'},
        {'source': 'World Bank WDI via wbdata',
         'url': 'https://databank.worldbank.org/source/world-development-indicators',
         'variables': ','.join(WB_INDICATORS.values())},
    ])
    prov.to_csv(OUT / 'central_asia_provenance.csv', index=False)


if __name__ == '__main__':
    main()
