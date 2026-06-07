# Uzbekistan power sector — research dataset and briefing

This folder is a research handoff containing a verified, name-level dataset of
Uzbekistan's electricity-generation and storage assets (Soviet era → 2040
horizon), an interactive map built from that dataset, a reconciliation report
against the project's own data, and this briefing.

## Files

| File | Content |
|---|---|
| `uzbekistan_energy_projects.json` | Canonical structured dataset (46 assets, one object each) |
| `uzbekistan_energy_projects.csv` | Same data as a flat table |
| `uzbekistan_energy_map.html` | Self-contained interactive map (timeline 1950 → 2040, click-for-detail). Its embedded `PROJECTS` array is the same data as the JSON. |
| `RECONCILIATION_REPORT.md` | Detailed reconciliation of REF against the project's own StatSUZ aggregates and World Bank GeoJSON |
| `BRIEFING.md` | This file |

The **JSON is the single source of truth**. The CSV and the map's embedded
array are generated from it; if the data is changed, all three must be
regenerated so they stay in sync. The script
`scripts/expand_ref_dataset.py` handles the regeneration.

## Data dictionary

| Field | Meaning |
|---|---|
| `name` | Asset name |
| `tech` | `thermal`, `hydro`, `solar`, `wind`, `nuclear`, `storage`, `gasfield` |
| `status` | `op` operational, `build` under construction or contracted, `plan` planned or target |
| `year` | Commissioning year or target year |
| `mw` | Nameplate capacity in MW (`null` for the gas field) |
| `region` | Host region or district |
| `lat`, `lng` | Coordinates (decimal degrees) |
| `exact` | `true` for published plant or site coordinates; `false` for district-level approximation |
| `retired` | Description of retired or idle units (where applicable) |
| `dev` | Developer / partners |
| `fin` | Financiers |
| `inv` | Investment (amount or "not disclosed") |
| `ret` | Contracted PPA tariff where known (NOT profit — see caveats) |
| `tax` | Tax and regulatory treatment |
| `src` | Source citation per asset |

## Capacity summary (REF dataset, as of 2026-06-02)

Total: 46 assets, 34 operating, 6 under construction, 6 planned.

| Technology | Operating | MW | Build | MW | Plan | MW |
|---|---:|---:|---:|---:|---:|---:|
| Thermal | 7 | 13 681 | 0 | 0 | 0 | 0 |
| Hydro | 13 | 1 897 | 1 | 400 | 3 | 700 |
| Solar | 9 | 2 047 | 1 | 1 000 | 0 | 0 |
| Wind | 3 | 1 500 | 3 | 700 | 1 | 1 500 |
| Nuclear | 0 | 0 | 1 | 2 100 | 0 | 0 |
| Storage | 1 | 200 | 0 | 0 | 2 | 450 |
| Gas field | 1 | n/a | 0 | 0 | 0 | 0 |

## Sectoral allocation of generation, 2024

| Destination | Share | Notes |
|---|---:|---|
| Residential | ~ 40 % | ≈ 1,800 kWh per capita per year |
| Industry | ~ 20 % | Utilities 72.5 %; Fergana textiles, Navoi/Zarafshan mining concentrating load |
| Transport | ~ 20 % | Electric rail and urban transit |
| Services / commercial | ~ 20 % | Lighting, cooling, datacentres |
| Transmission & distribution losses | ~ 12.5 % | Transformer loading > 80 % in 101 areas |

## Cross-border trade

| Direction | Counterparty | Volume | Year |
|---|---|---|---|
| Export | Afghanistan | 1.2 TWh (≈ US$72 M) | 2024 |
| Export | Kyrgyzstan | 1.6 TWh (2023); 1.7-2.0 TWh expected | 2021-2024 |
| Import | Turkmenistan | up to 4 TWh per year agreed | 2024 |
| Net winter imports | TKM 64.3 %, TJK 23.5 %, KAZ 12.2 % | ~ 4 % of supply | 2022 |

Uzbekistan is a net annual exporter but a winter net importer. The system is
part of the Central Asia Power System (220 / 500 kV interconnections with
Kazakhstan, Kyrgyzstan, Tajikistan, Turkmenistan). Tajikistan rejoined the
synchronous system in June 2024.

## Decommissioning roadmap

No Soviet- or transition-era plant has fully closed; aging units inside them
are being progressively retired against a national target of approximately
6.4 GW of obsolete thermal units to be shut.

| Plant | Retired / idle units | Year |
|---|---|---|
| Tashkent TES | Approximately 430 MW (units 1-3) decommissioned, EBRD-supported | 2023 |
| Tahiatash TES | Units 1-3 (310 MW); units 7-8 backup only | 2020 → ongoing |
| Angren TES | Units 1-2 retired | 2025 |
| Novo-Angren TES | Unit 8 (300 MW) left unfinished and mothballed | ~ 2015 |
| Navoi TES | Oldest steam units retired as CCGT added | 2012 / 2019 / 2024 |
| Syrdarya TES | Old inefficient units to retire when Syrdarya-2 CCGT online | Planned |

## Government programme stack

Private renewable IPPs are bankable only because a five-layer framework was put
in place 2018-2024. Each layer removes one specific obstacle.

1. **Legal foundation** — Decrees PP-3981 (2018), PP-4422 (2019), Renewable
   Energy Law and PPP Law (May 2019), CoM Resolution 610 (Jul 2019).
2. **Unbundling** — Decree PP-4249 (Mar 2019) split Uzbekenergo into JSC
   Thermal Power Plants (generation), National Electric Grid (transmission)
   and Regional Electric Networks (distribution).
3. **Guaranteed single buyer** — NEGU as off-taker; Decree PF-166 (Sep 2023)
   moved purchase to Uzenergosotish JSC from 1 Jul 2024; existing PPAs
   transferred from 1 Jan 2025.
4. **Independent regulation + competitive procurement** — Agency for the
   Development and Regulation of the Energy Market; IFC Scaling Solar (Nur
   Navoi US$0.027/kWh); reverse-bid auction under Decree 60 (Jan 2024)
   reached US$0.0165/kWh at Samarkand.
5. **Solvent off-taker** — tariff reform Oct 2023 (business) and May 2024
   (households); social-consumption-norm structure; energy-intensity 50 %
   cut target by 2030.

## Tax incentives

- **Decree UP-220** (9 Sep 2022) — 50 % cut on corporate income and property
  tax for RES producers (3-year window).
- Property + land tax exemption for RES ≥ 0.1 MW (10 years).
- Small systems ≤ 100 kW exempt from property and land tax; 3-year profit-tax
  holiday on grid sales (from Apr 2023).
- Customs / VAT relief on imported technological equipment under the
  investment-agreement regime.
- Free Economic Zone profit-tax exemptions for solar-manufacturing investment.

## Caveats — carry these into any write-up

1. **Profit is not public.** No net-profit figures exist for any project. The
   `ret` field gives the contracted PPA tariff where known. Uzbek tariff
   regulation caps the allowed margin between 10 % and 20 %.
2. **Coordinate accuracy.** `exact:false` rows are placed at the host district
   town. Fine for regional patterns; not survey-grade.
3. **Soviet-era financials** did not exist in a market sense (state-planned).
   Those rows are intentionally "not disclosed".
4. **A few developer attributions are unconfirmed** (Karaulbazar, Nishan,
   Yukorichirchik solar) — flagged in the data, not guessed.
5. **2031-2040 is trajectory, not committed numbers.** Uzbekistan's hard
   targets currently extend to 2030 and 2035; the 2040 horizon is strategy
   direction.
6. **Carbon-neutrality date** — power sector 2050 (EBRD/Japan roadmap);
   economy-wide net-zero 2060 (World Bank framing).

## Sources

### Primary
- IEA *Uzbekistan Energy Profile* (market design, energy security,
  sustainable development): https://www.iea.org/reports/uzbekistan-energy-profile
- EES EAEC *Energetic Profile of Uzbekistan*:
  https://www.eeseaec.org/energetika-evrazii/energeticeskij-profil-uzbekistana
- IRENA *Renewable Capacity Statistics* (2024 figures): https://www.irena.org
- Eurasian Development Bank *Central Asia Energy Outlook — March 2026*
- Global Energy Monitor wiki — per-plant pages (https://www.gem.wiki)

### Project-specific finance and tax
- ADB, EBRD, AIIB, IFC project documents (per-project URLs in `src` field)
- Masdar (https://masdar.ae) and ACWA Power (https://acwapower.com) project pages
- World Bank Navoi Scaling Solar project page (P170598)
- UNCTAD Investment Policy Monitor (Decree UP-220 details)
- PwC *Uzbekistan Tax Summaries*

### Policy and reform
- Azizov & Partners (Decree PF-166 commentary)
- Law.asia (revised Law on the Electric Energy Industry)
- Lexology (single-buyer / offtaker analysis)
- ESCAP *Concept for Ensuring Electricity Supply 2020-2030*
- Bourse & Bazaar *Uzbekistan's Transition Depends on Structural Reforms* (2025)
- Mordor Intelligence *Uzbekistan Power Market Report* (2025)
- OECD *Roadmap for Sustainable Investment Policy Reforms in Uzbekistan* (2025)

### Trade press
- ess-news (storage and BESS reporting)
- Times of Central Asia (renewable timelines)
- Renewable Watch (EBRD packages)
- Power Technology (Zarafshan BESS, Charvak HPP profiles)
- The Astana Times (Nur Bukhara inauguration)
- Caspian Post (Zangiata BESS)

### Long-range outlook
- Enerdata (carbon-neutrality 2050, 2030 mix)
- pv magazine (Concept Note 2020-2030, 29.3 GW by 2030)
- NucNet, World Nuclear News, Wikipedia (Uzbekistan Nuclear Plant)
- World Bank *Country and Climate Development Report* (net-zero 2060 framing)

## Reconciliation against project data (instructions for the maintainer)

1. Load `uzbekistan_energy_projects.json` as the reference dataset.
2. Compare against the project's own `data/processed/master_dataset.csv`
   (StatSUZ aggregates) and `data/raw/power plants (source - World Bank)/*.geojson`.
3. For each REF asset, match by name + region + technology; coordinates and
   capacity help disambiguate.
4. Compare per asset: capacity, year, status, developer, financier, investment,
   tariff, tax treatment.
5. Produce a reconciliation report with (a) agreements, (b) conflicts (both
   values and both sources shown), (c) coverage gaps.
6. **Do not silently overwrite.** Where a conflict exists, surface both values
   and cite both sources. The project's own primary data should be preferred
   where it is better-sourced; flag anything that requires a human decision.
7. If the dataset is updated, regenerate the CSV and the map's embedded
   PROJECTS array via `scripts/expand_ref_dataset.py` so all three stay
   consistent.

The current reconciliation against the project data is documented in
`RECONCILIATION_REPORT.md` in this folder.

## Suggested CLAUDE.md entry

```
## Uzbekistan energy research data
- Reference dataset: research/uzbekistan-energy/uzbekistan_energy_projects.json (46 assets, Soviet → 2040).
- It is the single source of truth; the CSV and the map HTML are generated from it.
- Profit figures are never public — use the PPA tariff in `ret`, not invented profit.
- Coordinates with `exact:false` are district-level approximations.
- When reconciling with the project's data, never overwrite silently: report conflicts with both sources.
- See research/uzbekistan-energy/BRIEFING.md for the full caveats, the tax / regulatory layer, and the source list.
- See research/uzbekistan-energy/RECONCILIATION_REPORT.md for the current reconciliation against StatSUZ and the World Bank GeoJSON.
- Notebook notebooks/02_power_system_landscape.ipynb (Parts B–E) consumes this dataset and embeds the interactive HTML map. (The former 09_spatial_research / 09_spatial notebooks were merged into it and archived under notebooks/_archive/.)
```
