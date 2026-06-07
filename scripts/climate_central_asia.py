"""
Extend the climate dataset:
  1. Push Uzbekistan national HDD/CDD back to 1990 (master_dataset starts then).
  2. Build comparable HDD/CDD/Tmean series for each of the other 4 Central Asia
     countries, using population-weighted averages across their major cities.
  3. Output a long panel (country, year, tmean_c, hdd18, cdd24) that joins to
     central_asia_panel.csv on (iso_code, year).

Source: Open-Meteo Historical Weather API (https://open-meteo.com), ERA5
reanalysis underneath. Free, no API key, no rate limit at this volume.

City weights (per country) are population shares from UN World Urbanization
Prospects 2023 (rounded). For Uzbekistan the existing 13-oblast set in
climate_uzb_national_annual.csv is used as a reference.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import ssl
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from typing import Iterable

import certifi
import numpy as np
import pandas as pd

# Explicit CA bundle context — see scripts/central_asia_panel.py for rationale.
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'processed' / 'uzstat_clean'
OUT.mkdir(parents=True, exist_ok=True)

START_DATE = '1990-01-01'
END_DATE   = '2024-12-31'

# Population-weighted city sets per country.
# Weights are approximate shares of the country's urban population concentrated
# in each city; rounded so they sum to 1. Sources noted inline.
COUNTRY_CITIES = {
    'UZB': [  # mirrors climate_uzb_national_annual.csv (13 oblast capitals)
        ('Tashkent',      41.3111, 69.2406, 0.30),  # capital + Tashkent region
        ('Samarkand',     39.6542, 66.9597, 0.10),
        ('Bukhara',       39.7681, 64.4556, 0.06),
        ('Andijan',       40.7821, 72.3442, 0.10),
        ('Namangan',      40.9983, 71.6726, 0.08),
        ('Fergana',       40.3864, 71.7864, 0.10),
        ('Nukus',         42.4531, 59.6103, 0.05),
        ('Urgench',       41.5503, 60.6311, 0.04),
        ('Qarshi',        38.8606, 65.7889, 0.05),
        ('Termez',        37.2242, 67.2783, 0.03),
        ('Navoiy',        40.0844, 65.3792, 0.03),
        ('Jizzakh',       40.1158, 67.8422, 0.03),
        ('Guliston',      40.4897, 68.7842, 0.03),
    ],
    'KAZ': [  # 5 largest urban centres, ≈70% of urban population
        ('Almaty',        43.2389, 76.8897, 0.35),
        ('Astana',        51.1605, 71.4704, 0.20),
        ('Shymkent',      42.3000, 69.6000, 0.18),
        ('Karaganda',     49.8047, 73.1094, 0.15),
        ('Aktobe',        50.2839, 57.1670, 0.12),
    ],
    'KGZ': [
        ('Bishkek',       42.8746, 74.5698, 0.55),
        ('Osh',           40.5283, 72.7985, 0.30),
        ('Jalal-Abad',    40.9333, 73.0000, 0.15),
    ],
    'TJK': [
        ('Dushanbe',      38.5598, 68.7870, 0.50),
        ('Khujand',       40.2867, 69.6196, 0.25),
        ('Kulob',         37.9106, 69.7831, 0.15),
        ('Qurghonteppa',  37.8333, 68.7833, 0.10),
    ],
    'TKM': [
        ('Ashgabat',      37.9601, 58.3261, 0.55),
        ('Turkmenabat',   39.0728, 63.5694, 0.20),
        ('Dashoguz',      41.8358, 59.9667, 0.15),
        ('Mary',          37.6000, 61.8333, 0.10),
    ],
}


def fetch_daily_tmean(lat: float, lon: float,
                      start: str = START_DATE, end: str = END_DATE,
                      retries: int = 5) -> pd.DataFrame:
    """Fetch daily mean temperature in °C from the Open-Meteo archive.

    Open-Meteo throttles bursts (HTTP 429); the request is retried with
    exponential back-off.
    """
    url = ('https://archive-api.open-meteo.com/v1/archive'
           f'?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}'
           f'&daily=temperature_2m_mean&timezone=auto')
    last_err = None
    for attempt in range(retries):
        try:
            data = json.loads(urlopen(url, timeout=180, context=SSL_CTX).read())
            return pd.DataFrame({
                'date': pd.to_datetime(data['daily']['time']),
                'tmean_c': data['daily']['temperature_2m_mean'],
            })
        except (URLError, HTTPError, TimeoutError) as e:
            last_err = e
            # 429 → long backoff; other errors → exponential
            sleep_s = 30 if (isinstance(e, HTTPError) and getattr(e, 'code', 0) == 429) else 2 ** attempt
            time.sleep(sleep_s)
    raise RuntimeError(f'Open-Meteo fetch failed for ({lat},{lon}): {last_err}')


def city_annual(city_name: str, lat: float, lon: float) -> pd.DataFrame:
    df = fetch_daily_tmean(lat, lon)
    # Self-throttle between cities to stay polite with Open-Meteo.
    time.sleep(2.0)
    df['year'] = df['date'].dt.year
    df['hdd18'] = np.maximum(18.0 - df['tmean_c'], 0)
    df['cdd24'] = np.maximum(df['tmean_c'] - 24.0, 0)
    annual = (df.groupby('year')
                .agg(tmean_c=('tmean_c', 'mean'),
                     hdd18=('hdd18', 'sum'),
                     cdd24=('cdd24', 'sum'))
                .reset_index())
    annual['city'] = city_name
    return annual


def country_weighted(iso: str, city_list: Iterable[tuple]) -> pd.DataFrame:
    """Population-weighted national HDD/CDD/Tmean from city annuals."""
    pieces = []
    for city, lat, lon, weight in city_list:
        print(f'  [{iso}] {city} (weight={weight:.2f}) ', end='', flush=True)
        a = city_annual(city, lat, lon)
        a['weight'] = weight
        pieces.append(a)
        print(f'rows={len(a)}')
    long = pd.concat(pieces, ignore_index=True)
    # Pop-weighted mean (weights re-normalised per year in case any city is missing)
    out = (long.groupby('year')
                .apply(lambda g: pd.Series({
                    'tmean_c': np.average(g['tmean_c'], weights=g['weight']),
                    'hdd18':   np.average(g['hdd18'],   weights=g['weight']),
                    'cdd24':   np.average(g['cdd24'],   weights=g['weight']),
                }))
                .reset_index())
    out['iso_code'] = iso
    out['source']   = f'Open-Meteo / ERA5; pop-weighted across {len(list(city_list))} cities'
    return out


def main():
    print(f'Open-Meteo ERA5 fetch window: {START_DATE} .. {END_DATE}')
    pieces = []
    for iso, city_list in COUNTRY_CITIES.items():
        print(f'\n[{iso}] cities: {len(city_list)}')
        pieces.append(country_weighted(iso, city_list))
    panel = pd.concat(pieces, ignore_index=True)
    panel = panel[['iso_code', 'year', 'tmean_c', 'hdd18', 'cdd24', 'source']]
    out_path = OUT / 'climate_central_asia.csv'
    panel.to_csv(out_path, index=False)
    print(f'\n-> wrote {out_path}  shape={panel.shape}')

    # Quick sanity print: tmean and CDD for the last 3 years per country
    print('\nLast 3 years per country (tmean_c, CDD24):')
    print(panel.sort_values(['iso_code', 'year']).groupby('iso_code')
                .tail(3)[['iso_code', 'year', 'tmean_c', 'cdd24']].round(2).to_string(index=False))


if __name__ == '__main__':
    main()
