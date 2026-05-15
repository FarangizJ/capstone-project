# Uzbekistan Power Sector — ILF Advisory Summary

**Author:** Farangiz Jurakhonova | **Sponsor:** Ardak Akhatova (ILF Consulting Engineers) | **Date:** 15 May 2026

This summary distils the Power Sector Transition Tracker findings into an opportunity table aligned with ILF's five advisory lines. It is intended for ILF's BD/advisory teams as a quarterly-refreshable input, not as professional advice.

---

## 1. Executive headline

Uzbekistan is on a credible trajectory toward the **April 2025 official target of 54% renewable share by 2030**, but only if the announced 27 GW renewable pipeline is built on time. Our forecast — Prophet model, 8-fold time-series CV mean MAPE = 6.4% — projects electricity demand of **103 TWh in 2030 and 123 TWh in 2035** (80% CI ±13 TWh in 2030). Under the Government Target scenario, the demand level requires **~17 GW of new renewables, 6 GWh of storage, and ~9,000 km of new transmission** to be commissioned by 2030. **Plan B nuclear (1.2 GW SMR from 2032)** can close the gap if PV/wind slip — adds 6.7 percentage points to the 2030 low-carbon share.

---

## 2. Opportunity table — ILF's five advisory lines

| # | Line | Signal (data-derived) | Magnitude | Cumulative capex 2024–2035 | Implementation window | ILF advisory role |
|---|---|---|---|---|---|---|
| 1 | **Generation new-build** | Govt scenario requires ~25 GW new RE by 2035 (vs ~5.6 GW today). Demand forecast +50% by 2030 vs 2023. | 12 GW solar, 8 GW wind, 4.7 GW hydro, 18 GW gas refresh | **USD 28–47 bn** (Govt → Accel) | 2024–2030 peak | Owner's engineer · technical DD · plant design |
| 2 | **Grid modernization** | T&D losses persistent at 9–10%. Sequential capacity additions in Karakalpakstan (1,450 km new HV) and Samarkand. | ~6,000 km HV lines + ~3 GW substations | **USD 3.0 bn** | Continuous | Network planning · substation EPC supervision · HVDC studies |
| 3 | **Renewable integration / storage** | Solar+wind share crosses 30% by 2027 → balancing-load concerns. BESS already part of Masdar/ACWA deals. | ~5 GWh BESS (Govt), ~12 GWh (Accel) | **USD 2.0–4.8 bn** | 2025–2030 | BESS sizing · grid-code studies · ancillary-service market design |
| 4 | **Energy efficiency (NEEA-aligned)** | Tariff reform 2024+; full gas-price deregulation 2026. Industrial intensity falling slowly — ample EE potential. | Industrial: cement, fertiliser, steel. Residential: heating | **USD 1.5 bn** (programmatic) | 2024–2030 | Audits · M&V · EPC supervision · NEEA capacity-building |
| 5 | **PPP / IFI advisory** | EBRD, ADB, AIIB, IFC, World Bank all active. 2026 alone: ADB-Masdar Guzar; EBRD ACWA $230 M; ADB-ACWA Bash II $226 M. | Multiple ~$200–500 M PPPs/yr | Fee-based, not capex | Continuous | Lender's engineer · IPP transaction advisory · risk-allocation review |
| 6 | **Plan B — Nuclear** *(parametric)* | Jizzakh SMR construction commenced 2024 (Rosatom). No regional precedent. Used here as sensitivity only. | 1.2 GW @ 2032 → +8.9 TWh by 2035; 3.6 GW → +27 TWh | **USD 6–18 bn** | 2030+ | Independent expert review · balance-of-plant · safety / regulatory liaison |

> Total ILF-addressable capex 2024–2035: **USD 34–50 bn** across lines 1–4, plus fee-based lines 5–6.

---

## 3. Five key data-driven findings

1. **The 54% target requires ~17 GW more RE than is currently in financed PPPs.** At the end of 2025 ~5.6 GW solar+wind was commissioned; the official 2030 target is ~25 GW. The gap is the addressable pipeline.
2. **The Government Target scenario only reaches 49% RE share in 2030 — not 54%.** This is because our updated demand forecast (Prophet) is ~12 TWh higher than earlier published projections. To hit 54% Uzbekistan needs either *more renewables than the headline 27 GW target* or *nuclear from 2032* (or both). Plan B nuclear (1.2 GW) closes ~6.7 pp of the gap; the remaining ~–1.4 pp comes from additional solar or accelerated wind.
3. **Wind is the highest-leverage technology by 2030.** Capex sensitivity to scenario is ±$10 bn (BAU vs Accelerated) — largest of any technology. Karakalpakstan + Navoi + Bukhara hold 84% of national wind potential.
4. **Power CO₂ emissions plateau in BAU but drop ~50% under Accelerated.** From 47.7 Mt in 2023, BAU ends at ~49 Mt in 2030; Government at ~32 Mt; Accelerated at ~25 Mt. CO₂ intensity falls from 642 → 281 gCO₂/kWh (Govt 2030), crossing the world average (475).
5. **Demand growth is faster than published government projections.** Our point forecast for 2025 = 84 TWh (gen 92) vs the official 86.7 TWh actual — within 1%. Linear/ARIMA models underpredict by ~10%. The 2018+ regime shift (tariff reform + gas-shortage-driven electrification) is the binding fact.

---

## 4. Methodology one-liner

Eleven models tested on 8 expanding-window CV folds × 3-year horizon. Winner = **Prophet** (CV mean MAPE 6.4%, Lewis-1982 "highly accurate" band) with bootstrap residual 80%/95% CIs. Scenarios anchored to April 2025 policy targets; CO₂ uses calibrated gas-fleet emission factors (650 gCO₂/kWh now → 380 with CCGT modernisation). Investment signals derived from capacity-gap thresholds × IRENA/IEA unit costs.

---

## 5. Quarterly refresh checklist (for ILF)

When new data drops, update these four CSVs and re-run notebooks 03 → 04 → 05 → 06:

| Source | File | Cadence |
|---|---|---|
| IEA balances (annual) | `data/raw/iea_*.csv` → `master_dataset.csv` | Annual (Sep) |
| IRENA capacity statistics | same | Annual (Mar) |
| StatSUZ — quarterly bulletin | `data/raw/statsuz_*` | Quarterly |
| MoE / Enerdata news | curate news section of dashboard | Monthly |

After refresh, `forecast_scoreboard.csv` will re-rank models; if a different model wins, the dashboard auto-updates the winner label.

---

## 6. What this summary does **not** support

- **Project-level financial returns** — capex figures are unit-cost rule-of-thumb, not bid data.
- **Resource-adequacy hour-by-hour** — annual capacity factors used; intra-year wind/solar variability not modelled.
- **Geopolitical scenarios** beyond what 2025 official targets articulate (e.g., faster Rosatom withdrawal, faster gas import liberalisation).
- **Nuclear-specific safety / regulatory feasibility** — Plan B is parametric for sensitivity only.

For these, ILF's own engineering models and the EDB 2026 regional report should be consulted.

---

*Source notebooks (reproducible): `notebooks/01_data_pipeline` → `02_eda_analysis` → `03_forecasting` → `04_dashboard` → `05_investment_signals` → `06_spatial`. Interactive dashboard: `dashboard/app.py`. Static HTML tracker: `outputs/uzbekistan_power_tracker.html`. Regional map: `outputs/uzbekistan_renewable_map.html`.*
