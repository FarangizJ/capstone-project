# Reconciliation report — REF JSON vs project data

**Date**: 2026-06-02
**Reference dataset**: `uzbekistan_energy_projects.json` (31 named assets)
**Project data compared against**:
- `data/raw/power plants (source - World Bank)/existingpowerplant_2.geojson` (26 features, no names)
- `data/raw/power plants (source - World Bank)/futurepowerplant.geojson` (2 features, no names)
- `data/processed/master_dataset.csv` (StatSUZ + IEA + IRENA capacity columns)

Caveats applied per `BRIEFING.md` §Caveats: profit treated as non-public (PPA tariff used as the financial proxy); `exact:false` coordinates treated as district-level approximations (50 km proximity threshold); 2031–2040 entries treated as trajectory not committed; both values and both sources surfaced for every conflict — nothing overwritten.

---

## Section 1 — Agreements

12 of 31 REF assets match a nearby WB plant within 50 km. Strong technology-coincident match in only one case: **Charvak HPP** (REF hydro 700 MW ↔ WB "HPPs < 1,000 MW" at 25.1 km). The other 11 proximity matches are spurious because the WB GeoJSON carries only `Legend` (a generic "TPPs/HPPs ≷ 1,000 MW" tag) and no plant name — the proximity matcher hooks the wrong neighbour. See Section 2.

## Section 2 — Conflicts (9, both sources surfaced)

| REF asset | REF says | WB GeoJSON says | REF source |
|---|---|---|---|
| Tashkent TES | thermal, 2,230 MW | HPPs > 1,000 MW (36.9 km away) | EES EAEC energy profile |
| Navoi TES | thermal, 2,060 MW | HPPs > 1,000 MW (40.8 km away) | EES EAEC energy profile |
| Syrdarya TES | thermal, 3,215 MW | HPPs > 1,000 MW (41.1 km away) | Wikipedia / EES EAEC |
| Novo-Angren TES (coal) | thermal, 2,100 MW | HPPs < 1,000 MW (48.9 km away) | EES EAEC |
| Tahiatash TES | thermal, 1,190 MW | TPPs < 1,000 MW (40.3 km away) | EES EAEC |
| Angren TES | thermal, 286 MW | HPPs > 1,000 MW (33.6 km away) | Global Energy Monitor |
| Farhad HPP | hydro, 126 MW | HPPs > 1,000 MW (42.9 km away) | Eurasian Research Institute |
| Talimarjan TES | thermal, 2,600 MW | TPPs < 1,000 MW (39.6 km away) | Trend.az; ADB; EBRD project documents |
| Nur Navoi solar | solar, 100 MW | HPPs > 1,000 MW (44.5 km away) | IEA market design; Masdar |

These are **not real value conflicts**; they are matching errors. The WB GeoJSON cannot serve as a name-level reconciliation source because (a) it has no plant-name attribute, (b) `Legend` distinguishes only two size bands and two technologies, (c) coordinates are approximate. The REF JSON is the more reliable named-asset source.

## Section 3a — REF assets missing from WB GeoJSON

19 of 31 REF assets have no nearby WB plant. All are 2021-or-later commissioning; the WB GeoJSON is a ~2018-2019 snapshot.

- Solar (8): Nurabad, Sherabad, Gallaorol, Kattakurgan, Karaulbazar, Yukorichirchik, Nur Bukhara, Samarkand 1 & 2 BESS
- Wind (4): Zarafshan, Bash, Dzhankeldy, Kungrad
- Storage / BESS (3): Tashkent Riverside, Zangiata, Zarafshan BESS
- Nuclear (1): Jizzakh VVER + SMR
- Gas field (1): Gazli
- Wind in build (2): Bash 2, Beruniy

No conflict; these post-date the WB dataset.

## Section 3b — WB UZB plants without a REF entry

16 of 24 WB plants inside the Uzbekistan bounding box have no REF counterpart. All carry only the generic `Legend`. These are likely small thermal CHP units and small hydro plants (Khodjikent, Gazalkent, Tuyabuguz, Hisarak, Andijan, and similar) that StatSUZ counts in totals but REF excludes from its curation.

Specifically:
- 3 unnamed TPPs < 1,000 MW
- 12 unnamed HPPs (10 < 1,000 MW + 2 > 1,000 MW)
- 1 future TPP > 1,000 MW at (45.71°N, 73.23°E) — possibly bleed-over from the Kazakhstan side of the bounding box

## Section 4 — Aggregate capacity cross-check

REF operational capacity sum 2024 (status `op`, `year <= 2024`, non-null `mw`) = **16,804 MW**. StatSUZ `capacity_total_mw` 2024 = **21,501 MW**. Gap = **21.8 %**.

Per technology:

| Tech | REF op 2024 (MW) | IRENA 2023 (MW) | StatSUZ 2024 (MW) | Notes |
|---|---:|---:|---:|---|
| Thermal | 13,681 | — | 15,684 | ~2,000 MW gap; REF likely missing small CHP / CCGT add-ons |
| Hydro | 826 | 4,763 | 3,134 | **Large gap.** REF carries only Charvak (700) + Farhad (126); IRENA/StatSUZ include many small HPPs |
| Solar | 1,797 | 949 | — | REF higher because REF includes 2024-2025 additions IRENA has not yet refreshed |
| Wind | 500 | 1.5 | — | IRENA stops before the 2024-2025 wind commissioning wave |
| Nuclear | 0 | — | — | Not yet operational |
| Storage | 0 | — | — | StatSUZ does not yet track storage |

## Recommendations (awaiting sign-off — nothing has been overwritten)

1. Use the REF JSON as the asset-level reference for `notebooks/02_power_system_landscape.ipynb` (Parts B–E) and the dashboard map. The WB GeoJSON becomes a background layer only.
2. Expand the REF JSON to include the ~6–8 small hydro plants implied by the 2.3 GW gap against StatSUZ. Candidate plants to research per primary sources: Khodjikent, Gazalkent, Tuyabuguz, Andijan, Hisarak. Verification per plant required before insertion.
3. Cite both sources in the research paper § 3.1: REF for asset detail (names, financiers, tariffs), StatSUZ for sector-wide capacity totals.

Once corrections are agreed, the JSON will be updated and the CSV and the map's embedded `PROJECTS` array regenerated from it so all three remain in sync.
