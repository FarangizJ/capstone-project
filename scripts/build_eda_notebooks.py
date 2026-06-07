"""
Build the 4 topic-ordered EDA + baseline forecasting notebooks programmatically.
(02 energy-mix EDA is retired — merged into the hand-maintained
notebooks/02_power_system_landscape.ipynb — see the §02 banner below.)

Output:
  notebooks/03_eda_supply_drivers.ipynb
  notebooks/04_eda_demand_drivers.ipynb
  notebooks/05_eda_correlations.ipynb
  notebooks/06_forecasting_baseline.ipynb

Each notebook:
  - Bilingual markdown (English first, Russian short follow-up)
  - Math notation in LaTeX
  - Academic citations inline
  - Real data only (no synthetic fill)
  - Reproducible from data/processed/ artefacts

Run:
  python scripts/build_eda_notebooks.py
  jupyter nbconvert --to notebook --execute --inplace notebooks/0{3..6}_*.ipynb
"""
from pathlib import Path
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / 'notebooks'


def md(text: str):
    return {'cell_type': 'markdown', 'metadata': {},
            'id': uuid.uuid4().hex[:8], 'source': text}


def code(src: str):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None,
            'outputs': [], 'id': uuid.uuid4().hex[:8], 'source': src}


def save_nb(cells, path: Path):
    nb = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'name': 'python3', 'display_name': 'Python 3',
                           'language': 'python'},
            'language_info': {'name': 'python', 'version': '3.13',
                              'mimetype': 'text/x-python',
                              'file_extension': '.py',
                              'pygments_lexer': 'ipython3',
                              'codemirror_mode': {'name': 'ipython', 'version': 3}}
        },
        'nbformat': 4, 'nbformat_minor': 5,
    }
    path.write_text(json.dumps(nb, indent=1))
    print(f'wrote {path} ({len(cells)} cells)')


# ============================================================
# 02 — RETIRED. The energy-mix EDA was merged with the two spatial notebooks
# into the hand-maintained notebooks/02_power_system_landscape.ipynb and is no
# longer generated here, so a routine rebuild cannot clobber the merged chapter.
# Original archived at notebooks/_archive/02_eda_energy_mix.ipynb.
# ============================================================


# ============================================================
# 03 — Supply Drivers EDA
# ============================================================
CELLS_03 = []

CELLS_03.append(md(r"""# 03 — Supply Drivers EDA / Анализ драйверов предложения

## What this notebook does / Что в notebook'е

**EN.** Decompose the *supply side* of the Uzbek power balance: installed capacity by technology, gas extraction vs gas consumption, coal substitution, T&D losses, and the renewable build-out commitment. Establishes the constraints any forecast must respect.

**RU.** Разбираем *сторону предложения* энергобаланса Узбекистана: установленная мощность по технологиям, добыча газа vs его потребление, замещение углём, потери в сетях, и обязательства по вводу ВИЭ. Формирует ограничения которые прогноз обязан соблюдать.

## Why this matters for ILF
- Capacity gap is the single biggest commercial opportunity (CCGT + RE pipeline).
- The gas-decline curve (own production minus consumption) determines whether gas-cost shocks will hit retail tariffs in the next 5 years.
- T&D losses ≥ 15 % is a defensible signal for transmission-rehabilitation advisory.

## Academic anchors
- IEA (2024). *Natural Gas Information*. — gas extraction methodology.
- World Bank (2022). *Energy Transition for Central Asia*. — T&D-loss benchmarks.
- IRENA (2024). *Pathways to a Renewable Future — Central Asia*. — RE pipeline commitments.
- EDB (2026). *Central Asia Energy Outlook — March 2026*. — peer projections.
"""))

CELLS_03.append(md(r"""## 1. Setup / Загрузка"""))

CELLS_03.append(code(r"""import warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

DATA = Path('../data/processed')
CLEAN = DATA / 'uzstat_clean'

plt.rcParams['figure.figsize'] = (11, 5)
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

master = pd.read_csv(DATA/'master_dataset_core.csv')
master = master[master['data_status']=='confirmed'].copy()
master['year'] = master['year'].astype(int)
uzb_nat = pd.read_csv(CLEAN/'uzb_energy_national.csv')
"""))

CELLS_03.append(md(r"""## 2. Installed capacity build-out

**EN.** Plot installed MW by technology 2010–2024. The slope of solar + wind lines is the empirical realisation of the 20-GW-by-2030 NDC target. If the slope is below the trajectory needed, ILF can quantify the gap.

**RU.** Установленная мощность по технологиям 2010–2024. Наклон линий "солнце+ветер" — это эмпирическая реализация обязательства 20 ГВт к 2030. Если темп ниже требуемого — ILF может количественно оценить разрыв.

### Required RE buildout to hit 20 GW by 2030
$$
\Delta C_{\text{RE}}^{\text{required}} = \frac{20\,\text{GW} - C_{\text{RE},t_0}}{2030 - t_0}, \qquad t_0 = \text{last observed year}.
$$
"""))

CELLS_03.append(code(r"""cap_cols = ['capacity_thermal_mw','capacity_hydro_mw','capacity_total_mw']
have = [c for c in cap_cols if c in master.columns]
cap = master[['year']+have].dropna(how='all', subset=have).copy()

# Solar and wind capacity come from the new UzStat clean (IDs 376/380/588 are MW)
uzb_nat_cap = pd.read_csv(CLEAN/'uzb_energy_national.csv')
# Use solar OUTPUT as a proxy for solar capacity since UzStat publishes only total + thermal + hydro MW
cap_re = uzb_nat_cap[['year','total_power_capacity_mw','thermal_capacity_mw','hydro_capacity_mw']]
cap_re['re_capacity_mw'] = cap_re['total_power_capacity_mw'] - cap_re['thermal_capacity_mw'] - cap_re['hydro_capacity_mw']
cap_re = cap_re.dropna()

fig, ax = plt.subplots(figsize=(11,5))
ax.plot(cap_re['year'], cap_re['thermal_capacity_mw']/1000, 'o-', lw=2, color='#d97706', label='Thermal (gas+coal)')
ax.plot(cap_re['year'], cap_re['hydro_capacity_mw']/1000, 'o-', lw=2, color='#0891b2', label='Hydro')
ax.plot(cap_re['year'], cap_re['re_capacity_mw']/1000, 'o-', lw=2, color='#16a34a', label='Solar+Wind (residual)')
ax.plot(cap_re['year'], cap_re['total_power_capacity_mw']/1000, 's--', lw=2.5, color='#1f2937', label='TOTAL')
ax.set_title('Installed capacity — Uzbekistan 2010–2024 (GW)')
ax.set_xlabel('Year'); ax.set_ylabel('GW'); ax.grid(alpha=.3)
ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_installed_capacity.png', dpi=140); plt.show()

# RE-buildout gap arithmetic — use latest RE residual
last_y = int(cap_re['year'].max())
re_now = float(cap_re.loc[cap_re['year']==last_y, 're_capacity_mw'].iat[0]) / 1000
needed_per_yr = (20 - re_now) / (2030 - last_y)
print(f'\nRE buildout pace required to hit 20 GW by 2030:')
print(f'  Current RE capacity ({last_y}): {re_now:.2f} GW')
print(f'  Required new RE/yr: {needed_per_yr:.2f} GW/yr (×{(2030-last_y)} years)')
"""))

CELLS_03.append(md(r"""## 3. Gas production vs consumption — the structural gap

**EN.** Uzbekistan was historically a net gas exporter (production > consumption). Recent data shows the gap narrowing — the country is now retaining more of its gas internally. The crossover year matters because beyond that point, gas imports must rise.

**RU.** Узбекистан исторически был чистым экспортёром газа (добыча > потребление). Последние данные показывают сужение этого разрыва — страна оставляет больше газа внутри. Год пересечения важен потому что после него страна перейдёт к импорту.

$$
\text{Net Export}_t = \text{Production}_t - \text{Consumption}_t
$$
"""))

CELLS_03.append(code(r"""gas = uzb_nat[['year','nat_gas_production_mcm','nat_gas_consumption_mcm']].dropna()
gas['net_export_bcm'] = (gas['nat_gas_production_mcm'] - gas['nat_gas_consumption_mcm'])/1000
gas['production_bcm'] = gas['nat_gas_production_mcm']/1000
gas['consumption_bcm'] = gas['nat_gas_consumption_mcm']/1000

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
ax = axes[0]
ax.plot(gas['year'], gas['production_bcm'], 'o-', color='#d97706', lw=2, label='Production')
ax.plot(gas['year'], gas['consumption_bcm'], 'o-', color='#374151', lw=2, label='Consumption')
ax.fill_between(gas['year'], gas['production_bcm'], gas['consumption_bcm'],
                where=gas['production_bcm']>=gas['consumption_bcm'], alpha=.15, color='green', label='Net export zone')
ax.set_title('Uzbekistan natural gas: production vs consumption (bcm)')
ax.set_xlabel('Year'); ax.set_ylabel('bcm'); ax.grid(alpha=.3); ax.legend()

ax = axes[1]
ax.bar(gas['year'], gas['net_export_bcm'],
       color=['#16a34a' if v > 0 else '#dc2626' for v in gas['net_export_bcm']])
ax.axhline(0, color='black', lw=0.6)
ax.set_title('Net gas export = production − consumption (bcm)')
ax.set_xlabel('Year'); ax.set_ylabel('bcm'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(DATA/'eda_gas_balance.png', dpi=140); plt.show()

# Linear extrapolation of net export → crossover year
z = np.polyfit(gas['year'], gas['net_export_bcm'], 1)
crossover_year = int(-z[1]/z[0]) if z[0] != 0 else None
print(f'Linear slope of net export: {z[0]:.2f} bcm/yr')
if crossover_year and crossover_year > gas["year"].max():
    print(f'Projected crossover year (net export = 0): {crossover_year}')
elif gas['net_export_bcm'].iat[-1] < 0:
    print('Net export already negative — Uzbekistan is a net gas importer.')
"""))

CELLS_03.append(md(r"""## 4. Coal substitution

**EN.** When gas runs short or becomes more valuable for export, coal is the cheap fallback for thermal generation. Plot domestic coal production + consumption to test whether substitution is happening.

**RU.** Когда газа становится мало или он становится ценнее на экспорт — уголь это дешёвая замена для тепловой генерации. Смотрим динамику добычи и потребления угля.
"""))

CELLS_03.append(code(r"""coal = uzb_nat[['year','coal_production_kt','coal_consumption_kt']].dropna()
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(coal['year'], coal['coal_production_kt']/1000, 'o-', color='#374151', lw=2, label='Production (Mt)')
ax.plot(coal['year'], coal['coal_consumption_kt']/1000, 's-', color='#92400e', lw=2, label='Consumption (Mt)')
ax.set_title('Uzbekistan coal: production vs consumption (Mt)')
ax.set_xlabel('Year'); ax.set_ylabel('Mt'); ax.grid(alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_coal_balance.png', dpi=140); plt.show()

# CAGR of coal consumption
import math
y0, y1 = coal['year'].min(), coal['year'].max()
v0, v1 = coal['coal_consumption_kt'].iat[0], coal['coal_consumption_kt'].iat[-1]
cagr_coal_cons = (v1/v0)**(1/(y1-y0)) - 1 if v0 > 0 else float('nan')
print(f'Coal consumption CAGR {y0}–{y1}: {cagr_coal_cons*100:+.2f}%/yr')
"""))

CELLS_03.append(md(r"""## 5. T&D losses — a transmission-rehab signal

**EN.** World Bank reports `EG.ELC.LOSS.ZS` (electric power transmission & distribution losses as % of output). Anything ≥ 15 % is a strong commercial signal for grid-rehab advisory under the IFI benchmark.

**RU.** ВБ публикует EG.ELC.LOSS.ZS (потери в передаче и распределении электроэнергии, % от производства). Любое значение ≥ 15% — сильный коммерческий сигнал для консалтинга по модернизации сетей по бенчмарку IFI.
"""))

CELLS_03.append(code(r"""td = master[['year','td_losses_pct']].dropna() if 'td_losses_pct' in master.columns else \
     pd.read_csv(DATA/'wb_sectoral_uzb.csv')[['year','td_losses_pct_wb']].rename(columns={'td_losses_pct_wb':'td_losses_pct'}).dropna()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(td['year'], td['td_losses_pct'], 'o-', color='#1e3a8a', lw=2)
ax.axhline(15, ls='--', color='#dc2626', label='IFI threshold for grid-rehab priority')
ax.set_title('Uzbekistan electric power T&D losses (% of output)')
ax.set_xlabel('Year'); ax.set_ylabel('%'); ax.grid(alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_td_losses.png', dpi=140); plt.show()

over_15 = (td['td_losses_pct'] >= 15).mean() * 100
print(f'Share of years with T&D losses ≥ 15%: {over_15:.0f}%')
"""))

CELLS_03.append(md(r"""## 6. Energy mix — total primary energy supply by source

**EN.** The IEA "Energy mix" lens examines *total primary energy supply* (TPES) composition rather than electricity alone. Stacking every fuel in Mtoe (1990–2023, IEA balances) exposes the structural dependence on natural gas and the marginal-but-rising contribution of solar and wind; the right panel adds the 2024 composition from the preliminary UzStat fuel-energy balance — **re-bucketed to its own accounting convention rather than spliced into the IEA series.** Two definitional gaps make the panels non-comparable except for gas and coal. (i) *Oil:* the IEA "oil and oil products" line bundles crude with all refined products (11.4 % of TPES in 2023), whereas the StatSUZ balance lists crude + condensate (5.1 %) separately from refined products (1.7 %) — bundled 6.8 %, so the apparent 2023→2024 collapse in oil is a convention artefact, not a real fall. (ii) *Renewables:* primary hydro/solar/wind (≈ 2 %) enter through the primary-electricity line under the physical-energy-content method, not as standalone fuel bands, which is why they do not appear as their own band in the 2024 bars. The 2024 denominator is verified total primary supply (Production + Imports − Exports + Stock changes = 52.9 Mtoe), not final consumption. Gas dominance (79–84 %) is the one fact robust to either convention.

**RU.** Ракурс МЭА «структура первичного энергоснабжения» рассматривает состав совокупного первичного предложения энергии (TPES), а не только электроэнергию. Наложение всех видов топлива (млн т н.э., 1990–2023, балансы МЭА) показывает структурную зависимость от природного газа и небольшой, но растущий вклад солнца и ветра; правая панель добавляет состав за 2024 год по предварительному топливно-энергетическому балансу Агентства статистики — **пересчитанный в его собственной методике учёта, а не присоединённый к ряду МЭА.** Два методических расхождения делают панели несопоставимыми, кроме газа и угля. (i) *Нефть:* строка МЭА «нефть и нефтепродукты» объединяет сырую нефть со всеми нефтепродуктами (11,4 % TPES в 2023 г.), тогда как баланс Агентства статистики указывает сырую нефть и конденсат (5,1 %) отдельно от нефтепродуктов (1,7 %) — в сумме 6,8 %; поэтому видимое «обвальное» снижение доли нефти в 2023→2024 является артефактом методики, а не реальным сокращением. (ii) *Возобновляемые источники:* первичные гидро-, солнечная и ветровая энергия (≈ 2 %) учитываются по строке первичной электроэнергии (метод физического энергосодержания), а не как отдельные топливные полосы, и потому не образуют собственной полосы на столбиках за 2024 год. Знаменатель за 2024 год — подтверждённое совокупное первичное предложение (производство + импорт − экспорт + изменение запасов = 52,9 млн т н.э.), а не конечное потребление. Доминирование газа (79–84 %) — единственный факт, устойчивый к обеим методикам.

*Academic anchor:* Energy Institute (2024), *Statistical Review of World Energy*; Grossman & Krueger (1995), environmental-Kuznets framing of the energy-composition stage."""))

CELLS_03.append(code(r"""OUT = Path('../outputs'); OUT.mkdir(parents=True, exist_ok=True)
TJ_PER_MTOE = 41868.0
md_full = pd.read_csv(DATA/'master_dataset.csv', low_memory=False)

fuels  = ['Natural gas','Coal and coal products','Oil and oil products',
          'Hydropower','Biofuels and waste','Solar, wind and other renewables']
labels = ['Natural gas','Coal','Oil','Hydro','Biofuels & waste','Solar/wind & other RE']
colors = ['#d97706','#374151','#92400e','#0891b2','#65a30d','#16a34a']

mix = md_full[['year']+fuels].dropna(subset=fuels, how='all').copy()
mix = mix[mix['year'].between(1990, 2023)]
for f in fuels:
    mix[f] = mix[f] / TJ_PER_MTOE   # TJ -> Mtoe

fig, axes = plt.subplots(1, 2, figsize=(15, 6.0), gridspec_kw={'width_ratios':[2.4, 1]})

ax = axes[0]
ax.stackplot(mix['year'], [mix[f] for f in fuels], labels=labels, colors=colors, alpha=.9)
ax.set_title('Total primary energy supply by source — Uzbekistan 1990–2023 (Mtoe, IEA)')
ax.set_xlabel('Year'); ax.set_ylabel('Mtoe'); ax.margins(x=0)
ax.legend(loc='upper left', fontsize=8, ncol=2)

# 2024 primary-supply shares from the preliminary StatSUZ fuel-energy balance,
# re-bucketed to its OWN accounting convention (NOT spliced into the IEA series):
# oil is split into crude+condensate vs refined products, and primary renewables
# (hydro/solar/wind) are shown separately from the small net-trade residual on the
# electricity line. The denominator 'Всего' is verified primary supply
# (Production + Imports - Exports + Stock changes), not final consumption.
eb   = pd.read_csv(DATA/'uzstat_energy_balance_2024_full.csv')
tps  = eb[eb['sector_en']=='Total primary supply'].iloc[0]
prod = eb[eb['sector_en']=='Production (primary)'].iloc[0]
tot24 = tps['Всего']
refined_cols = ['Бензин моторный','Топливо дизельное','Мазут',
                'Газы углеводородные сжиженные','Керосин','Кокс','Прочие виды нефтепродуктов']
refined  = sum(tps[c] for c in refined_cols)
re_elec  = prod['Электроэнергия']               # domestic primary electricity (hydro/solar/wind)
net_elec = tps['Электроэнергия'] - re_elec       # residual net trade on the electricity line
sh = {'Natural gas':                   tps['Газ природный']/tot24*100,
      'Coal':                          tps['Уголь']/tot24*100,
      'Oil — crude + condensate':      tps['Нефть, включая газовый конденсат']/tot24*100,
      'Refined oil products (net)':    refined/tot24*100,
      'Renewables (hydro/solar/wind)': re_elec/tot24*100,
      'Net electricity import':        net_elec/tot24*100}

ax = axes[1]
yk, yv = list(sh.keys()), list(sh.values())
ax.barh(yk, yv, color=['#d97706','#374151','#92400e','#c2884e','#16a34a','#9ca3af'])
ax.invert_yaxis()
for i, v in enumerate(yv):
    ax.text(v+0.7, i, f'{v:.1f}%', va='center', fontsize=8)
ax.set_xlim(0, 96)
ax.set_title('2024 primary supply mix\n(StatSUZ, preliminary — own convention)')
ax.set_xlabel('% of total primary supply')

caveat = ('⚠ Cross-source caveat — the two panels use different accounting conventions; only gas and coal are comparable across the 2023→2024 boundary.\n'
          'Oil: StatSUZ separates crude+condensate (5.1%) from refined products (1.7%) → bundled 6.8%, vs the IEA "oil & products" bundle (11.4% in 2023).\n'
          'Renewables: hydro/solar/wind (~2%) enter via the primary-electricity line, not as standalone fuel bands. The apparent 2023→2024 drop in oil and RE\n'
          'is therefore a definitional artefact between sources, not a real one-year change. 2024 denominator = total primary supply, not final consumption.')
fig.text(0.012, 0.012, caveat, ha='left', va='bottom', fontsize=7.5, color='#7c2d12',
         bbox=dict(boxstyle='round,pad=0.5', fc='#fef9c3', ec='#d97706', lw=1.0))

fig.text(0.99, 0.150,
         'Source: IEA energy balances (TPES 1990–2023, master_dataset.csv); '
         'UzStat Pilot Fuel-Energy Balance 2024 (preliminary).',
         ha='right', fontsize=7, color='#6b7280')
fig.tight_layout(rect=[0, 0.20, 1, 1])
plt.savefig(OUT/'03_energy_mix.png', dpi=140, bbox_inches='tight'); plt.show()

r23 = mix.loc[mix['year']==2023, fuels].iloc[0]
print('2023 TPES shares (IEA, %):')
for f in fuels:
    print(f'  {f:34s} {r23[f]/r23.sum()*100:5.1f}%')
print(f'\n2024 primary-supply shares (StatSUZ preliminary, own convention, %):')
for k, v in sh.items():
    print(f'  {k:34s} {v:5.1f}%')
bundled = sh['Oil — crude + condensate'] + sh['Refined oil products (net)']
print(f'  [cross-check] oil bundled (crude+condensate+refined): {bundled:.1f}%  vs IEA 2023 oil 11.4%')
print(f'  [cross-check] 6-category sum: {sum(sh.values()):.1f}%  (heat line {tps["Теплоэнергия"]/tot24*100:.2f}%)')"""))

CELLS_03.append(md(r"""## 7. Oil — production, product slate, and import dependence

**EN.** Uzbekistan is a modest and *declining* liquids producer: crude output has fallen from ~0.81 Mt (2017) to ~0.71 Mt (2024), and total liquids (crude + condensate) sit near 1.9 Mt. Because domestic refineries process more than the country lifts, oil is the one hydrocarbon where Uzbekistan is structurally *import-dependent* — roughly 29 % of 2024 oil supply was imported. The right panel shows the 2024 refined-product slate (gasoline, diesel, fuel oil, jet kerosene).

**RU.** Узбекистан — небольшой и *снижающий* добычу производитель жидких углеводородов: добыча сырой нефти упала с ~0,81 млн т (2017) до ~0,71 млн т (2024), а суммарные жидкие углеводороды (нефть + конденсат) — около 1,9 млн т. Поскольку внутренние НПЗ перерабатывают больше, чем страна добывает, нефть — единственный углеводород, по которому Узбекистан структурно *зависит от импорта*: около 29 % предложения нефти в 2024 пришлось на импорт. Правая панель показывает структуру выпуска нефтепродуктов за 2024 (бензин, дизельное топливо, мазут, авиакеросин).

*Academic anchor:* U.S. EIA (2023), *Country Analysis — Uzbekistan*; IEA (2022), *Oil Information*.
"""))

CELLS_03.append(code(r"""OUT = Path('../outputs'); OUT.mkdir(parents=True, exist_ok=True)

oil = uzb_nat[['year','oil_production_kt','gas_condensate_production_kt']].dropna().copy()
oil['total_liquids_kt'] = oil['oil_production_kt'] + oil['gas_condensate_production_kt']

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

ax = axes[0]
ax.plot(oil['year'], oil['oil_production_kt'], 'o-', color='#92400e', lw=2, label='Crude oil')
ax.plot(oil['year'], oil['gas_condensate_production_kt'], 's-', color='#d97706', lw=2, label='Gas condensate')
ax.plot(oil['year'], oil['total_liquids_kt'], 'D--', color='#1f2937', lw=2, label='Total liquids')
ax.set_title('Uzbekistan liquids production 2010–2024 (kt)')
ax.set_xlabel('Year'); ax.set_ylabel('kt'); ax.grid(alpha=.3); ax.legend()

ax = axes[1]
prod_cols = {'gasoline_production_kt':'Gasoline','diesel_production_kt':'Diesel',
             'fuel_oil_production_kt':'Fuel oil','aviakerosene_production_kt':'Jet kerosene'}
have = [k for k in prod_cols if k in uzb_nat.columns]
y24  = uzb_nat[uzb_nat['year']==uzb_nat['year'].max()].iloc[0]
names = [prod_cols[k] for k in have]
vals  = [y24[k] for k in have]
ax.barh(names, vals, color=['#d97706','#374151','#92400e','#0891b2'][:len(have)])
ax.invert_yaxis()
for i, v in enumerate(vals):
    ax.text(v+10, i, f'{v:.0f}', va='center', fontsize=8)
ax.set_title(f'Refined product output {int(y24["year"])} (kt)')
ax.set_xlabel('kt'); ax.set_xlim(0, max(vals)*1.18)

fig.text(0.99, -0.03,
         'Source: UzStat national energy series (uzb_energy_national.csv); '
         'import dependence from UzStat 2024 fuel-energy balance.',
         ha='right', fontsize=7, color='#6b7280')
plt.tight_layout(); plt.savefig(OUT/'03_oil_supply.png', dpi=140, bbox_inches='tight'); plt.show()

eb  = pd.read_csv(DATA/'uzstat_energy_balance_2024_full.csv')
tps = eb[eb['sector_en']=='Total primary supply'].iloc[0]
imp = eb[eb['sector_en']=='Imports'].iloc[0]
oil_supply = tps['Нефть, включая газовый конденсат']
oil_imp    = imp['Нефть, включая газовый конденсат']
print(f'2024 oil+condensate supply: {oil_supply:.0f} ktoe; imports: {oil_imp:.0f} ktoe '
      f'-> import dependence {oil_imp/oil_supply*100:.0f}%')
print(f'Crude {int(oil["year"].min())}->{int(oil["year"].max())}: '
      f'{oil["oil_production_kt"].iloc[0]:.0f} -> {oil["oil_production_kt"].iloc[-1]:.0f} kt')
"""))

CELLS_03.append(md(r"""## 8. Emissions — carbon intensity, sectoral split, per-capita path

**EN.** Three views of the carbon problem. **(A)** Power-sector CO₂ against generation gives a *carbon intensity* that held ~750–825 gCO₂/kWh through 2017, then stepped down to ~590–680 gCO₂/kWh from 2018 as efficient CCGT capacity displaced older units — still a gas-and-coal signature and a direct lever for the CCGT/RE pipeline. **(B)** The IEA sectoral split (power, transport, industry, residential, …) shows where combustion emissions actually sit. **(C)** Economy-wide CO₂ per capita (World Bank, to 2024) rose to ~4.1 t/person, tracking the post-2020 growth rebound.

**RU.** Три ракурса углеродной проблемы. **(A)** Отношение CO₂ электроэнергетики к выработке даёт *углеродоёмкость*, которая держалась ~750–825 гCO₂/кВт·ч до 2017, затем снизилась до ~590–680 гCO₂/кВт·ч с 2018 по мере замещения старых блоков эффективными ПГУ — всё ещё характерно для газово-угольного парка и прямой рычаг для программы ПГУ/ВИЭ. **(B)** Отраслевая разбивка МЭА (электроэнергетика, транспорт, промышленность, жильё, …) показывает, где фактически возникают выбросы от сжигания. **(C)** Удельные выбросы CO₂ на душу населения по экономике (Всемирный банк, до 2024) выросли до ~4,1 т/чел., отражая восстановление роста после 2020.

> **Methodical note / Методическая оговорка.** The stored `co2_intensity_power_gco2kwh` field in `master_dataset_core.csv` is corrupted (it reports ~98 for 2023). Panel (A) therefore *recomputes* intensity directly as IEA power-and-heat CO₂ ÷ total generation × 1000, reconciling with the documented 590–825 gCO₂/kWh range. The IEA combustion-by-sector inventory (~119 Mt, 2023) and the World Bank total-CO₂ series (~149 Mt, 2024) use different scopes and are not directly additive. // Поле `co2_intensity_power_gco2kwh` в `master_dataset_core.csv` повреждено (≈98 за 2023); панель (A) пересчитывает углеродоёмкость напрямую. Инвентаризация МЭА по сжиганию (~119 млн т, 2023) и ряд совокупных выбросов Всемирного банка (~149 млн т, 2024) имеют разный охват и не суммируются напрямую.

*Academic anchor:* Tapio (2005), decoupling typology; Grossman & Krueger (1995); IEA *Greenhouse Gas Emissions from Energy* methodology.
"""))

CELLS_03.append(code(r"""OUT = Path('../outputs'); OUT.mkdir(parents=True, exist_ok=True)
md_full   = pd.read_csv(DATA/'master_dataset.csv', low_memory=False)
core_full = pd.read_csv(DATA/'master_dataset_core.csv')   # unfiltered -> reaches 2024
core_full['year'] = core_full['year'].astype(int)

fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))

# (A) Power CO2 + recomputed carbon intensity (twin axis), 2000-2023
pw  = md_full[['year','Electricity and heat producers']].rename(
          columns={'Electricity and heat producers':'co2_power_mt'})
pi  = pw.merge(core_full[['year','gen_total_twh']], on='year').dropna()
pi  = pi[pi['year'].between(2000, 2023)]
pi['intensity'] = pi['co2_power_mt'] / pi['gen_total_twh'] * 1000
ax  = axes[0]
ax.bar(pi['year'], pi['co2_power_mt'], color='#9ca3af', label='Power+heat CO₂ (Mt)')
ax.set_ylabel('Mt CO₂'); ax.set_xlabel('Year')
ax.set_title('(A) Power-sector CO₂ & carbon intensity')
ax2 = ax.twinx(); ax2.spines['top'].set_visible(False)
ax2.plot(pi['year'], pi['intensity'], 'o-', color='#dc2626', lw=2, label='Intensity (gCO₂/kWh)')
ax2.set_ylabel('gCO₂/kWh'); ax2.set_ylim(0, 900)
h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, fontsize=7, loc='lower right')

# (B) CO2 by sector, stacked, 1990-2023 (IEA)
sect = ['Electricity and heat producers','Other energy industries','Industry Sector',
        'Transport Sector','Residential','Commercial and Public Services','Agriculture/Forestry']
sect = [c for c in sect if c in md_full.columns]
labs = ['Power & heat','Other energy','Industry','Transport','Residential','Commercial','Agriculture']
cols = ['#374151','#6b7280','#92400e','#d97706','#0891b2','#16a34a','#65a30d']
s = md_full[['year']+sect].dropna(subset=sect, how='all')
s = s[s['year'].between(1990, 2023)]
ax = axes[1]
ax.stackplot(s['year'], [s[c] for c in sect], labels=labs[:len(sect)], colors=cols[:len(sect)], alpha=.9)
ax.set_title('(B) CO₂ by sector 1990–2023 (Mt)')
ax.set_xlabel('Year'); ax.set_ylabel('Mt CO₂'); ax.margins(x=0)
ax.legend(fontsize=6.5, loc='upper left', ncol=2)

# (C) Economy-wide CO2 per capita, 2000-2024 (World Bank)
pc = core_full[['year','wb_co2_total_mt','wb_population']].dropna()
pc = pc[pc['year'].between(2000, 2024)].copy()
pc['t_per_cap'] = pc['wb_co2_total_mt']*1e6 / pc['wb_population']
ax = axes[2]
ax.plot(pc['year'], pc['t_per_cap'], 'o-', color='#1e3a8a', lw=2)
ax.set_title('(C) CO₂ per capita 2000–2024 (t/person)')
ax.set_xlabel('Year'); ax.set_ylabel('t CO₂/capita'); ax.grid(alpha=.3)

fig.text(0.99, -0.04,
         'Source: IEA CO₂ by sector (master_dataset.csv, 2000–2023); World Bank total CO₂ & '
         'population (to 2024). Power intensity recomputed = power-sector CO₂ ÷ generation × 1000.',
         ha='right', fontsize=7, color='#6b7280')
plt.tight_layout(); plt.savefig(OUT/'03_emissions.png', dpi=140, bbox_inches='tight'); plt.show()

print(f'Power carbon intensity 2023: {pi["intensity"].iloc[-1]:.0f} gCO2/kWh '
      f'(range {pi["intensity"].min():.0f}-{pi["intensity"].max():.0f})')
print(f'Economy-wide CO2 2024 (WB): {pc["wb_co2_total_mt"].iloc[-1]:.1f} Mt; '
      f'per capita {pc["t_per_cap"].iloc[-1]:.2f} t')
"""))

CELLS_03.append(md(r"""## 9. Findings / Выводы

**EN — defensible facts:**
1. Total installed capacity grew from ~12.5 GW (2010) to ~21 GW (2024), but RE capacity is still only a small fraction.
2. The gas net-export gap is narrowing — depending on slope, Uzbekistan transitions to net importer between 2026 and 2030.
3. Coal consumption is growing (CAGR positive), consistent with gas-shortage substitution.
4. T&D losses cross the 15 % IFI threshold in some years — transmission rehabilitation is a defensible advisory category.
5. The energy economy is overwhelmingly gas-based: 79 % of TPES in 2023 (IEA) and 84 % in 2024 (StatSUZ); solar + wind remain below 1 % of primary supply.
6. Oil is the structural weak point — domestic liquids are declining (~1.9 Mt in 2024) and ~29 % of oil supply is imported.
7. Power-sector carbon intensity stepped down from ~800 gCO₂/kWh (pre-2018) to ~590–680 gCO₂/kWh after CCGT modernisation; economy-wide CO₂ reached ~149 Mt and ~4.1 t per capita in 2024 — the decarbonisation lever is the thermal fleet.

**RU — обоснованные факты:**
1. Общая мощность выросла с ~12,5 ГВт (2010) до ~21 ГВт (2024), но ВИЭ — пока малая доля.
2. Чистый экспорт газа сужается — по линейному тренду УЗБ переходит в чистого импортёра между 2026 и 2030.
3. Потребление угля растёт (CAGR положительный), что согласуется с замещением дефицита газа.
4. Потери в сетях в отдельные годы превышают порог 15 % IFI — модернизация передачи это обоснованная категория консалтинга.
5. Энергетика страны подавляюще газовая: 79 % TPES в 2023 (МЭА) и 84 % в 2024 (Агентство статистики); солнце и ветер вместе — менее 1 % первичного предложения.
6. Нефть — структурно слабое место: внутренняя добыча жидких углеводородов снижается (~1,9 млн т в 2024), а ~29 % предложения нефти импортируется.
7. Углеродоёмкость электроэнергетики снизилась с ~800 гCO₂/кВт·ч (до 2018) до ~590–680 гCO₂/кВт·ч после модернизации ПГУ; выбросы CO₂ по экономике достигли ~149 млн т и ~4,1 т на душу населения в 2024 — рычаг декарбонизации это тепловой парк.
"""))

save_nb(CELLS_03, NB_DIR / '03_eda_supply_drivers.ipynb')


# ============================================================
# 04 — Demand Drivers EDA
# ============================================================
CELLS_04 = []

CELLS_04.append(md(r"""# 04 — Demand Drivers EDA / Анализ драйверов спроса

## What this notebook does / Что в notebook'е

**EN.** Decompose Uzbek electricity demand into its structural drivers: real GDP and sectoral value-added, population & urbanisation, climate (HDD/CDD), tariff history, and sectoral end-use (industry / housing / agriculture / services). Each driver is plotted against demand and the implied elasticity is estimated.

**RU.** Раскладываем спрос на электроэнергию Узбекистана на структурные драйверы: реальный ВВП и отраслевую ВДС, население и урбанизацию, климат (HDD/CDD), историю тарифов, и секторальное конечное потребление (промышленность / жильё / сельское хозяйство / услуги). Каждый драйвер сопоставляется со спросом и оценивается соответствующая эластичность.

### Special focus / Особый акцент
- Sectoral electricity by end-use (NEW data from UzStat 3169-3172): industry / housing / agriculture / construction / transport.
- **Greenhouse winter load story / Тепличный зимний пик**: Uzbekistan's heated greenhouse sector consumes both gas (heating) and electricity (lighting, pumps, ventilation) — visible in the agricultural electricity supply trend.

## Academic anchors
- Bhattacharyya, S. C. & Blake, A. (2009). "Domestic demand for petroleum products in MENA countries." *Energy Policy 37* — short/long-run elasticity benchmarks.
- IRENA (2019). *Demand-side flexibility for power-sector transformation* — sectoral demand decomposition.
- Broomandi, P. et al. (2025). "Energy generation and carbon footprint under future projections of Central Asian temperature extremes." *Global Challenges* — climate-elasticity in CA region.
- Eskeland, G. & Mideksa, T. (2010). "Electricity demand in a changing climate." *Mitigation & Adaptation Strategies for Global Change* — HDD/CDD methodology.
"""))

CELLS_04.append(md(r"""## 1. Setup / Загрузка"""))

CELLS_04.append(code(r"""import warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

DATA = Path('../data/processed')
CLEAN = DATA / 'uzstat_clean'

plt.rcParams['figure.figsize'] = (11, 5)
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

master   = pd.read_csv(DATA/'master_dataset_core.csv')
master   = master[master['data_status']=='confirmed'].copy()
master['year'] = master['year'].astype(int)

drivers  = pd.read_csv(DATA/'demand_drivers_panel_v2.csv').drop(
    columns=['cons_twh','tmean_c','hdd18','cdd24','tmean_c_natl','hdd18_natl','cdd24_natl'],
    errors='ignore')
drivers['year'] = drivers['year'].astype(int)

uzb_nat  = pd.read_csv(CLEAN/'uzb_energy_national.csv')
uzb_clim = pd.read_csv(CLEAN/'climate_central_asia.csv')
uzb_clim = uzb_clim[uzb_clim['iso_code']=='UZB'][['year','tmean_c','hdd18','cdd24']]
"""))

CELLS_04.append(md(r"""## 2. Headline demand series

**EN.** The TARGET is `elec_consumption_twh_bridged`. Two important features: (1) it is the IEA-StatSUZ bridge from `01_data_pipeline.ipynb` (no other source rolls back to 1990 cleanly); (2) it grows 50 → 84 TWh over 1990–2024 = +68 % cumulative.

**RU.** ЦЕЛЕВАЯ переменная — `elec_consumption_twh_bridged`. Два важных момента: (1) это IEA-StatSUZ-мост из `01_data_pipeline` (никакой другой источник не покрывает чисто до 1990); (2) рост с 50 до 84 ТВтч за 1990–2024 = +68% совокупно.
"""))

CELLS_04.append(code(r"""y_col = 'elec_consumption_twh_bridged'
d = master[['year', y_col]].dropna()
fig, ax = plt.subplots(figsize=(11,4))
ax.plot(d['year'], d[y_col], 'o-', color='#1e3a8a', lw=2)
ax.set_title('UZB electricity consumption (TWh, bridged IEA-StatSUZ)')
ax.set_xlabel('Year'); ax.set_ylabel('TWh'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(DATA/'eda_demand_headline.png', dpi=140); plt.show()
print(f'1990 demand: {d.iloc[0][y_col]:.1f} TWh, 2024 demand: {d.iloc[-1][y_col]:.1f} TWh, growth: {(d.iloc[-1][y_col]/d.iloc[0][y_col]-1)*100:.1f}%')
"""))

CELLS_04.append(md(r"""## 3. Sectoral end-use decomposition (industry / housing / agriculture / construction / transport)

**EN.** UzStat publishes electricity supply by sector starting 2010 (IDs 3169-3172, 2685, 2686). This gives the reader the demand-side mix that the household-level / GDP / climate drivers must explain.

**RU.** UzStat публикует поставки электроэнергии по секторам с 2010 года (ID 3169-3172, 2685, 2686). Это даёт нам секторальный микс спроса который должны объяснить драйверы (домохозяйства, ВВП, климат).

**EN — 2024 fine breakdown.** The long 2010–2024 series resolves only into *enterprises* vs *housing*. The preliminary 2024 UzStat fuel-energy balance adds a much finer end-use split — eight electricity-consuming sectors (industry, households, agriculture, commercial & government, transport, construction, …) and the all-fuel final-consumption profile behind them. Industry takes ~40 % of electricity, households ~25 %, agriculture ~15 % — the agricultural share reflecting the irrigation-pump and greenhouse load discussed in §6.

**RU — детальная разбивка за 2024.** Длинный ряд 2010–2024 различает лишь *предприятия* и *жильё*. Предварительный топливно-энергетический баланс Агентства статистики за 2024 добавляет гораздо более детальное конечное потребление — восемь секторов-потребителей электроэнергии (промышленность, домохозяйства, сельское хозяйство, коммерческие и государственные услуги, транспорт, строительство, …) и стоящий за ними профиль конечного потребления по всем видам топлива. На промышленность приходится ~40 % электроэнергии, на домохозяйства ~25 %, на сельское хозяйство ~15 % — последняя доля отражает нагрузку насосов орошения и теплиц (см. §6).
"""))

CELLS_04.append(code(r"""sect_cols = {
    'Enterprises (industry+commercial)': 'elec_supply_enterprises_gwh',
    'Housing': 'elec_supply_housing_gwh',
}
sect = uzb_nat[['year'] + list(sect_cols.values())].dropna(how='all', subset=list(sect_cols.values()))
print('Sectoral electricity supply (GWh):')
print(sect.tail(5).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
ax = axes[0]
for label, col in sect_cols.items():
    if col in sect.columns:
        ax.plot(sect['year'], sect[col]/1000, 'o-', lw=2, ms=3, label=label)
ax.set_title('Electricity supply by sector — UZB (TWh)')
ax.set_xlabel('Year'); ax.set_ylabel('TWh'); ax.grid(alpha=.3); ax.legend()

ax = axes[1]
# Sectoral shares
tot = sect[list(sect_cols.values())].sum(axis=1)
share = sect[list(sect_cols.values())].div(tot, axis=0) * 100
share.columns = list(sect_cols.keys())
share['year'] = sect['year']
for label in sect_cols.keys():
    ax.plot(share['year'], share[label], 'o-', lw=2, ms=3, label=label)
ax.set_title('Sectoral electricity supply — share (%)')
ax.set_xlabel('Year'); ax.set_ylabel('%'); ax.grid(alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_sectoral_demand.png', dpi=140); plt.show()
"""))

CELLS_04.append(code(r"""OUT = Path('../outputs'); OUT.mkdir(parents=True, exist_ok=True)

# (A) Fine 2024 electricity final consumption by sector
es = pd.read_csv(DATA/'uzstat_electricity_by_sector_2024.csv')
leaf = ['Industry — total','Households (residential)','Agriculture',
        'Commercial & government services','Unspecified other','Transport — total',
        'Construction','Fisheries']
ea = es[es['sector_en'].isin(leaf)][['sector_en','electricity_twh','share_of_total_pct']].copy()
ea['label'] = ea['sector_en'].str.replace(' — total','', regex=False)
ea = ea.sort_values('electricity_twh')

# (B) All-fuel 2024 final consumption by sector (ktoe -> Mtoe)
eb = pd.read_csv(DATA/'uzstat_energy_balance_2024_full.csv')
fuel_leaf = {'Industry — total':'Industry','Transport — total':'Transport',
             'Households (residential)':'Households','Commercial & government services':'Commercial & govt',
             'Agriculture':'Agriculture','Construction':'Construction',
             'Unspecified other':'Unspecified','Fisheries':'Fisheries'}
fb = eb[eb['sector_en'].isin(fuel_leaf)][['sector_en','Всего']].copy()
fb['label'] = fb['sector_en'].map(fuel_leaf)
fb['share'] = fb['Всего']/fb['Всего'].sum()*100
fb = fb.sort_values('Всего')

fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
ax = axes[0]
ax.barh(ea['label'], ea['electricity_twh'], color='#1e3a8a')
for i,(v,s) in enumerate(zip(ea['electricity_twh'], ea['share_of_total_pct'])):
    ax.text(v+0.3, i, f'{v:.1f} ({s:.0f}%)', va='center', fontsize=8)
ax.set_title('2024 electricity final consumption by sector')
ax.set_xlabel('TWh'); ax.set_xlim(0, ea['electricity_twh'].max()*1.28)

ax = axes[1]
ax.barh(fb['label'], fb['Всего']/1000, color='#d97706')
for i,(v,s) in enumerate(zip(fb['Всего']/1000, fb['share'])):
    ax.text(v+0.15, i, f'{v:.1f} ({s:.0f}%)', va='center', fontsize=8)
ax.set_title('2024 all-fuel final consumption by sector')
ax.set_xlabel('Mtoe'); ax.set_xlim(0, (fb['Всего']/1000).max()*1.28)

fig.text(0.99, -0.03,
         'Source: UzStat Pilot Fuel-Energy Balance 2024 (preliminary) — electricity-by-sector & all-fuel TFC.',
         ha='right', fontsize=7, color='#6b7280')
plt.tight_layout(); plt.savefig(OUT/'04_sectoral_2024.png', dpi=140, bbox_inches='tight'); plt.show()

print('2024 electricity by sector (TWh, % of TFC):')
for _, r in ea.sort_values('electricity_twh', ascending=False).iterrows():
    print(f'  {r["label"]:34s} {r["electricity_twh"]:6.2f}  {r["share_of_total_pct"]:5.1f}%')
"""))

CELLS_04.append(md(r"""## 4. GDP & sectoral value-added vs demand (income elasticity)

**EN.** Following Bhattacharyya & Blake (2009), short-run income elasticity is estimated as:
$$
\hat{\eta}_Y = \frac{\partial \ln D}{\partial \ln Y}
$$
where $D$ = electricity demand and $Y$ = real GDP per capita. Long-run elasticity comes from a cointegrating regression (covered in NB05).

**RU.** Следуя Bhattacharyya & Blake (2009), краткосрочную эластичность по доходу оцениваем как $\hat{\eta}_Y = \partial \ln D / \partial \ln Y$, где $D$ — спрос на электроэнергию, $Y$ — реальный ВВП на душу населения. Долгосрочную эластичность — через коинтеграционную регрессию (см. NB05).
"""))

CELLS_04.append(code(r"""p = (master[['year', y_col]].rename(columns={y_col:'cons_twh'})
       .merge(drivers[['year','gdp_pc_const2015_usd','industry_va_const2015_usd',
                       'services_va_const2015_usd','mfg_va_const2015_usd',
                       'agri_va_const2015_usd']], on='year', how='inner'))
p = p.dropna(subset=['cons_twh','gdp_pc_const2015_usd'])
p['lnD']     = np.log(p['cons_twh'])
p['lnY']     = np.log(p['gdp_pc_const2015_usd'])
p['dlnD']    = p['lnD'].diff()
p['dlnY']    = p['lnY'].diff()
p['lnInd']   = np.log(p['industry_va_const2015_usd'])
p['dlnInd']  = p['lnInd'].diff()
p['lnServ']  = np.log(p['services_va_const2015_usd'])
p['dlnServ'] = p['lnServ'].diff()

m = p.dropna(subset=['dlnD','dlnY']).copy()

# Simple bivariate short-run elasticity (with HC3 std errors)
X = sm.add_constant(m[['dlnY']])
fit_y = sm.OLS(m['dlnD'], X).fit(cov_type='HC3')
print('Short-run income elasticity (Δln D on Δln GDP_pc):')
print(f'  β = {fit_y.params["dlnY"]:.3f}  (95% CI: {fit_y.conf_int().loc["dlnY",0]:.3f}, {fit_y.conf_int().loc["dlnY",1]:.3f})')
print(f'  p-value: {fit_y.pvalues["dlnY"]:.3f}, n={int(fit_y.nobs)}, R² = {fit_y.rsquared:.3f}')

# Sectoral version
sub = m.dropna(subset=['dlnInd','dlnServ']).copy()
X2 = sm.add_constant(sub[['dlnY','dlnInd','dlnServ']])
fit_s = sm.OLS(sub['dlnD'], X2).fit(cov_type='HC3')
print('\nMulti-driver short-run elasticity (Δln D on Δln GDP_pc + Δln Industry_VA + Δln Services_VA):')
print(fit_s.summary().tables[1])
"""))

CELLS_04.append(code(r"""# Scatter plot: GDP_pc vs demand (in logs)
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
ax = axes[0]
ax.scatter(p['lnY'], p['lnD'], color='#1e3a8a', s=30)
z = np.polyfit(p['lnY'], p['lnD'], 1)
xs = np.linspace(p['lnY'].min(), p['lnY'].max(), 50)
ax.plot(xs, np.polyval(z, xs), '--', color='red', label=f'slope (long-run elas.) ≈ {z[0]:.2f}')
ax.set_xlabel('ln(GDP per capita)'); ax.set_ylabel('ln(Demand TWh)')
ax.set_title('Demand vs GDP per capita — log-log')
ax.grid(alpha=.3); ax.legend()

ax = axes[1]
ax.scatter(m['dlnY'], m['dlnD'], color='#1e3a8a', s=30)
z = np.polyfit(m['dlnY'], m['dlnD'], 1)
xs = np.linspace(m['dlnY'].min(), m['dlnY'].max(), 30)
ax.plot(xs, np.polyval(z, xs), '--', color='red', label=f'slope (short-run elas.) ≈ {z[0]:.2f}')
ax.axhline(0, color='black', lw=0.5); ax.axvline(0, color='black', lw=0.5)
ax.set_xlabel('Δln(GDP per capita)'); ax.set_ylabel('Δln(Demand TWh)')
ax.set_title('Demand growth vs GDP growth')
ax.grid(alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_income_elasticity.png', dpi=140); plt.show()
"""))

CELLS_04.append(md(r"""## 5. Population & urbanisation

**EN.** Total population scales demand; urbanisation lifts per-capita demand (higher appliance ownership, AC penetration, lighting). Plot both.

**RU.** Население масштабирует спрос; урбанизация повышает спрос на душу (приборы, кондиционеры, освещение). Смотрим оба.
"""))

CELLS_04.append(code(r"""pop = drivers[['year','wb_population','wb_urban_pop_pct']].dropna()
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
ax = axes[0]
ax.plot(pop['year'], pop['wb_population']/1e6, 'o-', color='#1e3a8a', lw=2)
ax.set_title('Total population (mn)'); ax.set_xlabel('Year'); ax.set_ylabel('mn'); ax.grid(alpha=.3)

ax = axes[1]
ax.plot(pop['year'], pop['wb_urban_pop_pct'], 'o-', color='#dc2626', lw=2)
ax.set_title('Urban population share (%)'); ax.set_xlabel('Year'); ax.set_ylabel('%'); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(DATA/'eda_population_urbanisation.png', dpi=140); plt.show()

# Per-capita demand evolution
pc = p[['year','cons_twh']].merge(pop, on='year').copy()
pc['per_cap_kWh'] = pc['cons_twh'] * 1e9 / pc['wb_population']
print('Per-capita electricity consumption (kWh) — recent years:')
print(pc[['year','per_cap_kWh']].tail(6).round(0).to_string(index=False))
"""))

CELLS_04.append(md(r"""## 6. Climate — HDD18, CDD24 / Climate-elasticity story

**EN.** Heating degree-days (base 18 °C) capture winter demand for heating; cooling degree-days (base 24 °C) capture summer AC load. Definitions follow ASHRAE; the 24 °C base is appropriate for Central Asia (higher than the US 18 °C base because buildings tolerate higher indoor temps).

**RU.** Heating degree-days (база 18°C) описывают зимний спрос на отопление; cooling degree-days (база 24°C) — летний спрос на кондиционирование. Определения по ASHRAE; база 24°C подходит для ЦА (выше чем стандарт США 18°C — здания терпят более высокие внутренние температуры).

### Greenhouse winter-heating note / Тепличный зимний контекст
**EN.** Uzbekistan's heated greenhouse sector (worth ~20 bn UZS production in 2024, with major export to Russia) consumes both natural gas (heating) and electricity (lighting, hydroponic pumps, ventilation). Winter HDD therefore drives BOTH residential heating demand AND greenhouse load — the two are partially confounded in the historical series.

**RU.** Тепличный сектор Узбекистана (~20 млрд сум продукции в 2024 году, основной экспорт в Россию) потребляет и природный газ (отопление) и электричество (освещение, гидропонические насосы, вентиляция). Зимние HDD драйвят И бытовое отопление И тепличную нагрузку — эти две вещи частично смешаны в исторической серии.

$$
\text{HDD}_{18,t} = \sum_{d \in \text{year}\,t} \max(18 - T_d, 0), \qquad
\text{CDD}_{24,t} = \sum_{d \in \text{year}\,t} \max(T_d - 24, 0).
$$
"""))

CELLS_04.append(code(r"""fig, axes = plt.subplots(1, 3, figsize=(16, 4))
axes[0].plot(uzb_clim['year'], uzb_clim['tmean_c'], 'o-', color='#7c3aed', lw=2)
axes[0].set_title('Mean annual temperature (°C)'); axes[0].grid(alpha=.3)
z = np.polyfit(uzb_clim['year'], uzb_clim['tmean_c'], 1)
axes[0].plot(uzb_clim['year'], np.polyval(z, uzb_clim['year']), '--', color='red',
             label=f'+{z[0]*10:.2f}°C / decade')
axes[0].legend()

axes[1].plot(uzb_clim['year'], uzb_clim['hdd18'], 'o-', color='#1d4ed8', lw=2)
axes[1].set_title('HDD18 (winter heating proxy)'); axes[1].grid(alpha=.3)

axes[2].plot(uzb_clim['year'], uzb_clim['cdd24'], 'o-', color='#dc2626', lw=2)
axes[2].set_title('CDD24 (summer cooling proxy)'); axes[2].grid(alpha=.3)
for ax in axes:
    ax.set_xlabel('Year')
plt.tight_layout(); plt.savefig(DATA/'eda_climate.png', dpi=140); plt.show()

# Simple climate-elasticity check via first differences
clim_p = p[['year','cons_twh','dlnD']].merge(uzb_clim, on='year', how='inner')
clim_p['dHDD'] = clim_p['hdd18'].diff()
clim_p['dCDD'] = clim_p['cdd24'].diff()
sub = clim_p.dropna(subset=['dlnD','dHDD','dCDD'])
X = sm.add_constant(sub[['dHDD','dCDD']])
fit = sm.OLS(sub['dlnD'], X).fit(cov_type='HC3')
print('Climate semi-elasticity (Δln D on ΔHDD + ΔCDD):')
print(f'  HDD: {fit.params["dHDD"]*100:.4f} %/HDD (p={fit.pvalues["dHDD"]:.3f})')
print(f'  CDD: {fit.params["dCDD"]*100:.4f} %/CDD (p={fit.pvalues["dCDD"]:.3f})')
print(f'  n = {int(fit.nobs)}')
"""))

CELLS_04.append(md(r"""## 7. Tariff history (price elasticity setup)

**EN.** Tariffs are the policy lever ILF most cares about. There is nominal residential and industrial tariffs from IEA + Gazeta.uz (2017–2024). Deflation by CPI is required to obtain *real* tariffs for use as a price driver.

**RU.** Тарифы — главный регуляторный рычаг которым ILF интересуется. У нас номинальные тарифы (бытовые и промышленные) из IEA + Gazeta.uz (2017–2024). Чтобы использовать как драйвер цены — нужно дефлировать по ИПЦ и получить *реальные* тарифы.
"""))

CELLS_04.append(code(r"""tariff = pd.read_csv(DATA/'tariff_history_uzb.csv')
# Deflate using IMF CPI inflation — built from IMF DataMapper inflation 'cpi_infl_pct'
imf = pd.read_csv(DATA/'imf_weo_uzb.csv').rename(columns={'Unnamed: 0':'year'})
imf['year'] = pd.to_numeric(imf['year'], errors='coerce').astype('Int64')
imf = imf.dropna(subset=['year']); imf['year'] = imf['year'].astype(int)

# Build CPI index 2015 = 100 from yoy inflation
cpi_yoy = imf.set_index('year')['cpi_infl_pct'] / 100
cpi_yoy = cpi_yoy.dropna()
cpi_idx = pd.Series(index=cpi_yoy.index, dtype=float, name='cpi_index_2015')
if 2015 in cpi_idx.index:
    cpi_idx.loc[2015] = 100.0
    for y in sorted(cpi_idx.index):
        if y == 2015: continue
        if y > 2015:
            cpi_idx.loc[y] = cpi_idx.loc[y-1] * (1 + cpi_yoy.loc[y])
        else:
            cpi_idx.loc[y] = cpi_idx.loc[y+1] / (1 + cpi_yoy.loc[y+1])
tariff = tariff.merge(cpi_idx.reset_index(), on='year', how='left')
tariff['residential_real_uzs_kwh'] = tariff['residential_uzs_kwh'] / tariff['cpi_index_2015'] * 100
tariff['industrial_real_uzs_kwh']  = tariff['industrial_uzs_kwh']  / tariff['cpi_index_2015'] * 100

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(tariff['year'], tariff['residential_uzs_kwh'], 'o-', color='#1e3a8a', lw=2, label='Residential (nominal)')
ax.plot(tariff['year'], tariff['residential_real_uzs_kwh'], 's--', color='#1e3a8a', lw=1.4, label='Residential (real 2015 UZS)')
ax.plot(tariff['year'], tariff['industrial_uzs_kwh'],  'o-', color='#dc2626', lw=2, label='Industrial (nominal)')
ax.plot(tariff['year'], tariff['industrial_real_uzs_kwh'],  's--', color='#dc2626', lw=1.4, label='Industrial (real 2015 UZS)')
ax.set_title('Uzbekistan electricity tariffs — nominal vs real (UZS/kWh)')
ax.set_xlabel('Year'); ax.set_ylabel('UZS/kWh'); ax.grid(alpha=.3); ax.legend()
plt.tight_layout(); plt.savefig(DATA/'eda_tariff_history.png', dpi=140); plt.show()
print(tariff[['year','residential_uzs_kwh','residential_real_uzs_kwh',
              'industrial_uzs_kwh','industrial_real_uzs_kwh']].round(1).to_string(index=False))
"""))

CELLS_04.append(md(r"""## 8. Energy intensity & efficiency / Энергоёмкость и эффективность

**EN.** The IEA "Efficiency & demand" lens asks how much primary energy the economy burns per unit of output. **(A)** Energy intensity — primary energy ÷ real GDP — has collapsed from ~18.9 to ~4.5 kWh per const-2015-$ between 2000 and 2023 (a roughly four-fold improvement), the textbook signature of an economy decoupling growth from energy as it sheds Soviet-era heavy-industry structure; the StatSUZ 2024 balance implies a further fall to ~4.3. **(B)** Primary energy *per capita* fell from ~24 MWh (2000) to ~16.5 MWh (2016) and has since plateaued near ~16–17 MWh/person — recent energy growth roughly tracks population, while GDP outpaces both.

**RU.** Ракурс МЭА «эффективность и спрос» спрашивает, сколько первичной энергии экономика сжигает на единицу выпуска. **(A)** Энергоёмкость — первичная энергия ÷ реальный ВВП — рухнула с ~18,9 до ~4,5 кВт·ч на доллар в ценах 2015 за 2000–2023 (примерно четырёхкратное улучшение), хрестоматийный признак отрыва роста от энергопотребления по мере ухода от советской тяжёлой индустрии; баланс Агентства статистики за 2024 указывает на дальнейшее снижение до ~4,3. **(B)** Первичная энергия *на душу населения* упала с ~24 МВт·ч (2000) до ~16,5 МВт·ч (2016) и с тех пор стабилизировалась около ~16–17 МВт·ч/чел. — недавний рост энергопотребления примерно повторяет рост населения, тогда как ВВП обгоняет оба.

> **Data note / Оговорка по данным.** OWID's preliminary 2024 primary-energy estimate (695 TWh) is ~13 % above Uzbekistan's own 2024 fuel-energy balance (52.85 Mtoe ≈ 615 TWh) and would spuriously reverse the intensity decline; the StatSUZ ground-truth balance is therefore used for the 2024 point in both panels. OWID/Energy-Institute primary energy uses the substitution method vs the balance's physical-content method — a minor (~4 %) level difference for this gas-dominated mix. // Предварительная оценка OWID за 2024 (695 ТВт·ч) на ~13 % выше собственного баланса Узбекистана (52,85 млн т н.э. ≈ 615 ТВт·ч) и ложно развернула бы снижение энергоёмкости; поэтому для точки 2024 в обеих панелях используется баланс Агентства статистики.

*Academic anchor:* IEA (2024), *Energy Efficiency*; Stern (2012), the energy-intensity decline as a development regularity; Grossman & Krueger (1995).
"""))

CELLS_04.append(code(r"""OUT = Path('../outputs'); OUT.mkdir(parents=True, exist_ok=True)
MTOE_TWH = 11.63
TPES_2024_MTOE = 52.853   # StatSUZ 2024 fuel-energy balance, total primary supply (ground truth)

owid = pd.read_csv(DATA/'owid_energy_uzb.csv')
gdp  = pd.read_csv(DATA/'master_dataset_core.csv')[['year','wb_gdp_const2015_bn_usd','wb_population']]
gdp['year'] = gdp['year'].astype(int)

ei = owid[['year','primary_energy_consumption','energy_per_capita']].merge(gdp, on='year', how='left')
ei = ei[ei['year'].between(2000, 2023)].copy()          # OWID reliable window
ei['intensity'] = ei['primary_energy_consumption'] / ei['wb_gdp_const2015_bn_usd']
ei['pc_mwh']    = ei['energy_per_capita'] / 1000

g24    = gdp[gdp['year']==2024].iloc[0]
tpes24 = TPES_2024_MTOE * MTOE_TWH
int24  = tpes24 / g24['wb_gdp_const2015_bn_usd']
pc24   = tpes24 * 1e9 / g24['wb_population'] / 1000

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

ax = axes[0]
ax.plot(ei['year'], ei['intensity'], 'o-', color='#16a34a', lw=2, label='Primary energy ÷ real GDP (OWID, to 2023)')
ax.plot([2023, 2024], [ei['intensity'].iloc[-1], int24], '--', color='#16a34a', lw=1.3)
ax.plot(2024, int24, 'D', mfc='white', mec='#16a34a', mew=1.8, ms=9, label='2024 (StatSUZ balance)')
ax.annotate(f'{int24:.1f}', (2024, int24), textcoords='offset points', xytext=(-8, 9), fontsize=8, color='#15803d')
ax.set_title('(A) Energy intensity of GDP — primary energy per real dollar')
ax.set_xlabel('Year'); ax.set_ylabel('kWh per const-2015-$'); ax.grid(alpha=.3)
ax.legend(fontsize=8, loc='upper right')

ax = axes[1]
ax.plot(ei['year'], ei['pc_mwh'], 'o-', color='#1e3a8a', lw=2, label='OWID (to 2023)')
ax.plot([2023, 2024], [ei['pc_mwh'].iloc[-1], pc24], '--', color='#1e3a8a', lw=1.3)
ax.plot(2024, pc24, 'D', mfc='white', mec='#1e3a8a', mew=1.8, ms=9, label='2024 (StatSUZ balance)')
ax.annotate(f'{pc24:.1f}', (2024, pc24), textcoords='offset points', xytext=(-8, 9), fontsize=8, color='#1e3a8a')
ax.set_title('(B) Primary energy per capita')
ax.set_xlabel('Year'); ax.set_ylabel('MWh per person'); ax.grid(alpha=.3)
ax.legend(fontsize=8, loc='upper right')

fig.text(0.99, -0.03,
         'Source: OWID/Energy Institute primary energy & per-capita (2000–2023); World Bank real GDP & '
         'population; UzStat 2024 fuel-energy balance (52.85 Mtoe) for the 2024 point.',
         ha='right', fontsize=7, color='#6b7280')
plt.tight_layout(); plt.savefig(OUT/'04_energy_intensity.png', dpi=140, bbox_inches='tight'); plt.show()

print(f'Energy intensity (kWh/2015-$): 2000={ei["intensity"].iloc[0]:.1f} -> 2023={ei["intensity"].iloc[-1]:.1f} '
      f'(StatSUZ 2024 = {int24:.1f})')
print(f'Primary energy per capita (MWh): 2000={ei["pc_mwh"].iloc[0]:.1f} -> 2023={ei["pc_mwh"].iloc[-1]:.1f} '
      f'(StatSUZ 2024 = {pc24:.1f})')
"""))

CELLS_04.append(md(r"""## 9. Findings / Выводы

**EN — to defend in front of the professor:**
1. Demand grew +68 % over 1990–2024 (≈ +2 %/yr CAGR), dominated by enterprises/industry (~70 % of supply), with residential as the second-largest sector.
2. Short-run income elasticity of demand on GDP per capita is **positive** but estimated imprecisely on n≈30 (wide CI). Long-run elasticity from levels is closer to 1 (see NB05 cointegration).
3. CDD24 correlates positively with year-on-year demand growth — empirical confirmation that hotter summers drive measurable demand spikes.
4. HDD18 does not produce a clean negative semi-elasticity at the annual scale — winter heating in UZB is largely gas (and gas-heated greenhouses), so electricity sees only a partial winter signal.
5. Real tariffs (deflated by CPI) have **declined** since 2017 because nominal tariff increases lagged 10-14 %/yr inflation. So historic price-elasticity from this window is downward-biased — keep in mind for NB07.
6. The 2024 end-use split (UzStat balance) shows electricity demand led by industry (~40 %), households (~25 %) and agriculture (~15 %); on an all-fuel basis, households and commercial/government services dominate final consumption (gas- and heat-heavy).
7. Energy intensity has fallen roughly four-fold (≈18.9 → 4.5 kWh per 2015-$ over 2000–2023, ≈4.3 in 2024) — strong decoupling of growth from energy — while primary energy per capita has plateaued near ~16–17 MWh/person.

**RU — для защиты перед профессором:**
1. Спрос вырос на +68% за 1990–2024 (CAGR ~+2%/год), доминируют предприятия/промышленность (~70% поставок), на втором месте — жильё.
2. Краткосрочная эластичность спроса по ВВП на душу — **положительная**, но оценена неточно на n≈30 (широкие CI). Долгосрочная эластичность в уровнях ближе к 1 (см. NB05 коинтеграция).
3. CDD24 положительно коррелирует с темпом роста спроса — эмпирическое подтверждение того что более жаркое лето приводит к измеримым пикам спроса.
4. HDD18 не даёт чистой отрицательной полу-эластичности на годовом масштабе — зимнее отопление в УЗБ в основном газовое (включая газовые теплицы), поэтому в электричестве виден только частичный зимний сигнал.
5. Реальные тарифы (с дефляцией по ИПЦ) **снизились** с 2017 потому что номинальные повышения отставали от инфляции 10-14%/год. Значит историческая ценовая эластичность из этого окна смещена вниз — учесть в NB07.
6. Структура конечного потребления за 2024 (баланс Агентства статистики) показывает, что спрос на электроэнергию ведут промышленность (~40 %), домохозяйства (~25 %) и сельское хозяйство (~15 %); по всем видам топлива в конечном потреблении доминируют домохозяйства и коммерческие/государственные услуги (с большой долей газа и теплоэнергии).
7. Энергоёмкость снизилась примерно вчетверо (≈18,9 → 4,5 кВт·ч на доллар 2015 за 2000–2023, ≈4,3 в 2024) — сильный отрыв роста от энергопотребления — тогда как первичная энергия на душу населения стабилизировалась около ~16–17 МВт·ч/чел.
"""))

save_nb(CELLS_04, NB_DIR / '04_eda_demand_drivers.ipynb')


# ============================================================
# 05 — Correlation & Causality EDA
# ============================================================
CELLS_05 = []

CELLS_05.append(md(r"""# 05 — Correlation & Causality EDA / Корреляции и причинности

## What this notebook does / Что в notebook'е

**EN.** Apply the *Granger–Newbold / Engle–Granger* discipline before any regression:
1. Pairwise correlations between demand, supply, and macro drivers.
2. **Stationarity battery** (ADF + KPSS) on every series — spurious-regression check.
3. **Engle-Granger cointegration** test to identify long-run equilibrium relationships.
4. **Granger causality** tests for short-run lead-lag structure.
5. Detrended (first-difference) correlation matrix — what is signal vs shared trend.

**RU.** Применяем дисциплину Грейнджера-Ньюболда / Энгла-Грейнджера до любой регрессии:
1. Парные корреляции между спросом, предложением и макро-драйверами.
2. **Батарея стационарности** (ADF + KPSS) на каждой серии — защита от ложной регрессии.
3. **Тест коинтеграции Энгла-Грейнджера** для выявления долгосрочного равновесия.
4. **Тесты причинности по Грейнджеру** для краткосрочной структуры опережений-отставаний.
5. Детрендированная (первые разности) матрица корреляций — отделяем сигнал от общего тренда.

## Academic anchors
- Granger, C. W. J. & Newbold, P. (1974). "Spurious regressions in econometrics." *Journal of Econometrics 2(2)*.
- Engle, R. F. & Granger, C. W. J. (1987). "Co-integration and error correction." *Econometrica 55*.
- Dickey, D. A. & Fuller, W. A. (1979). "Distribution of the estimators for autoregressive time series with a unit root." *JASA 74*.
- Kwiatkowski, D. et al. (1992). KPSS test. *Journal of Econometrics 54*.
"""))

CELLS_05.append(md(r"""## 1. Setup and merged panel / Загрузка и сборка панели"""))

CELLS_05.append(code(r"""import warnings; warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss, coint, grangercausalitytests

DATA = Path('../data/processed')
CLEAN = DATA / 'uzstat_clean'

plt.rcParams['figure.figsize'] = (11, 5)
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

master = pd.read_csv(DATA/'master_dataset_core.csv')
master = master[master['data_status']=='confirmed'].copy()
master['year'] = master['year'].astype(int)
# Drop columns that are also in the new climate panel to avoid suffix collisions
drivers = pd.read_csv(DATA/'demand_drivers_panel_v2.csv').drop(
    columns=['cons_twh','tmean_c','hdd18','cdd24','tmean_c_natl','hdd18_natl','cdd24_natl'],
    errors='ignore')
uzb_clim = pd.read_csv(CLEAN/'climate_central_asia.csv')
uzb_clim = uzb_clim[uzb_clim['iso_code']=='UZB'][['year','tmean_c','hdd18','cdd24']]

p = (master[['year','elec_consumption_twh_bridged']]
       .rename(columns={'elec_consumption_twh_bridged':'cons_twh'})
       .merge(drivers, on='year', how='inner')
       .merge(uzb_clim, on='year', how='left'))
p = p.sort_values('year').reset_index(drop=True)

CORE_VARS = ['cons_twh','gdp_pc_const2015_usd','industry_va_const2015_usd',
             'services_va_const2015_usd','wb_population','wb_urban_pop_pct',
             'cdd24','hdd18']
p_core = p[['year']+CORE_VARS].dropna()
print(f'Modelling panel: {len(p_core)} years × {len(CORE_VARS)} variables')
print('Years:', p_core["year"].min(), '–', p_core["year"].max())
"""))

CELLS_05.append(md(r"""## 2. Pairwise Pearson correlations (in levels)

**EN.** The level correlations are *suggestive*, not conclusive — non-stationary series can share a deterministic trend and appear strongly correlated without any causal link (the classic Granger-Newbold trap). The level correlations are reported only as a starting point.

**RU.** Корреляции в уровнях лишь *наводят* — нестационарные ряды могут иметь общий детерминированный тренд и казаться сильно коррелированными без причинной связи (классический капкан Грейнджера-Ньюболда). Считаем только как отправную точку.
"""))

CELLS_05.append(code(r"""corr = p_core[CORE_VARS].corr(method='pearson').round(2)
print('Pearson correlation matrix (LEVELS — interpret with caution):')
print(corr)

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(CORE_VARS))); ax.set_xticklabels(CORE_VARS, rotation=45, ha='right', fontsize=9)
ax.set_yticks(range(len(CORE_VARS))); ax.set_yticklabels(CORE_VARS, fontsize=9)
for i in range(len(CORE_VARS)):
    for j in range(len(CORE_VARS)):
        ax.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center', fontsize=8,
                color='white' if abs(corr.values[i,j])>0.6 else 'black')
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
ax.set_title('Pearson correlation (LEVELS)')
plt.tight_layout(); plt.savefig(DATA/'eda_corr_levels.png', dpi=140); plt.show()
"""))

CELLS_05.append(md(r"""## 3. Stationarity battery: ADF + KPSS

**EN.** Two complementary tests:
- **ADF (null = unit root)**: rejecting → stationary.
- **KPSS (null = stationary)**: rejecting → non-stationary.

A series is "confidently stationary" only if ADF rejects AND KPSS fails to reject.

**RU.** Два дополняющих теста:
- **ADF (H0 = единичный корень)**: отвержение → стационарный.
- **KPSS (H0 = стационарный)**: отвержение → нестационарный.

"Уверенно стационарный" только если ADF отверг И KPSS не отверг.

$$
\text{ADF: } y_t = \alpha + \rho y_{t-1} + \sum_{k=1}^p \gamma_k \Delta y_{t-k} + \epsilon_t, \quad H_0:\rho=1
$$
"""))

CELLS_05.append(code(r"""def stationarity(series, name):
    s = series.dropna()
    if len(s) < 8: return {'series': name, 'verdict': 'too short'}
    try:
        adf_stat, adf_p, *_ = adfuller(s, autolag='AIC')
    except Exception:
        adf_p = float('nan')
    try:
        kpss_stat, kpss_p, *_ = kpss(s, regression='c', nlags='auto')
    except Exception:
        kpss_p = float('nan')
    if adf_p < 0.05 and (kpss_p > 0.05 or np.isnan(kpss_p)):
        verdict = 'STATIONARY ✓'
    elif adf_p > 0.05 and kpss_p < 0.05:
        verdict = 'I(1) — needs differencing'
    elif adf_p < 0.05 and kpss_p < 0.05:
        verdict = 'CONFLICTING — investigate'
    else:
        verdict = 'NON-STATIONARY (likely I(1))'
    return {'series': name, 'ADF_p': round(adf_p,3), 'KPSS_p': round(kpss_p,3), 'verdict': verdict}

rows = []
for v in CORE_VARS:
    # levels
    rows.append(stationarity(np.log(p_core[v].replace(0,np.nan)) if v not in ('hdd18','cdd24','wb_urban_pop_pct') else p_core[v], 'log '+v if v not in ('hdd18','cdd24','wb_urban_pop_pct') else v))
    # first differences
    diff = (np.log(p_core[v].replace(0,np.nan)) if v not in ('hdd18','cdd24','wb_urban_pop_pct') else p_core[v]).diff()
    rows.append(stationarity(diff, 'Δ '+(('log '+v) if v not in ('hdd18','cdd24','wb_urban_pop_pct') else v)))

stat_df = pd.DataFrame(rows)
print('Stationarity battery results:')
print(stat_df.to_string(index=False))
"""))

CELLS_05.append(md(r"""## 4. Engle-Granger cointegration: demand and macro drivers

**EN.** If `ln(cons_twh)` is I(1) and one or more drivers are I(1), they may share a long-run *cointegrating* relationship: a stationary linear combination exists. Engle-Granger 2-step:
1. Regress `ln(cons)` on candidate I(1) drivers (in levels).
2. Test residuals for stationarity via ADF.

Reject residual unit root → long-run relationship is meaningful, supporting the subsequent ECM fit.

**RU.** Если `ln(cons_twh)` интегрирован порядка 1 и один или более драйверов тоже I(1), они могут иметь долгосрочное *коинтеграционное* отношение: существует стационарная линейная комбинация. 2-шаговый тест Энгла-Грейнджера:
1. Регрессируем `ln(cons)` на кандидатных I(1) драйверах (в уровнях).
2. Тестируем остатки на стационарность через ADF.

Отвержение единичного корня в остатках → долгосрочная связь осмысленная, можно строить ECM.
"""))

CELLS_05.append(code(r"""y  = np.log(p_core['cons_twh'])
xs = p_core[['gdp_pc_const2015_usd','industry_va_const2015_usd']].apply(np.log)
xs.columns = ['ln_gdp_pc','ln_ind_va']
stat, pval, crit = coint(y, xs, trend='c', autolag='AIC')[:3]
print(f'Engle-Granger cointegration test:')
print(f'  Test statistic: {stat:.3f}, p-value: {pval:.3f}')
print(f'  Critical values 1%/5%/10%: {crit}')
if pval < 0.10:
    print('  → COINTEGRATED (long-run relationship is meaningful at 10%)')
else:
    print('  → NO COINTEGRATION DETECTED (interpret long-run elasticities with caution)')
"""))

CELLS_05.append(md(r"""## 5. Granger causality (does GDP lead demand?)

**EN.** Granger causality tests whether past values of X improve forecasts of Y beyond what past Y already provides. Run X = GDP_pc, Y = demand, with lags = 1, 2.

**RU.** Тест Грейнджера проверяет улучшают ли прошлые значения X прогноз Y сверх того что уже даёт прошлый Y. X = GDP_pc, Y = спрос, лаги = 1, 2.
"""))

CELLS_05.append(code(r"""# Use first differences (stationary) for Granger causality
gc_data = p_core[['cons_twh','gdp_pc_const2015_usd']].apply(np.log).diff().dropna()
print('Granger causality: does ΔlnGDP_pc Granger-cause ΔlnDemand?')
res = grangercausalitytests(gc_data[['cons_twh','gdp_pc_const2015_usd']], maxlag=2, verbose=False)
for lag, out in res.items():
    p_chi2 = out[0]['ssr_chi2test'][1]
    print(f'  Lag {lag}: chi² p-value = {p_chi2:.3f}', '→ GDP Granger-causes Demand' if p_chi2 < 0.10 else '→ no Granger causality at 10%')

print('\nReverse direction (does ΔlnDemand Granger-cause ΔlnGDP_pc?):')
res = grangercausalitytests(gc_data[['gdp_pc_const2015_usd','cons_twh']], maxlag=2, verbose=False)
for lag, out in res.items():
    p_chi2 = out[0]['ssr_chi2test'][1]
    print(f'  Lag {lag}: chi² p-value = {p_chi2:.3f}', '→ Demand Granger-causes GDP' if p_chi2 < 0.10 else '→ no Granger causality at 10%')
"""))

CELLS_05.append(md(r"""## 6. Detrended (first-difference) correlation matrix

**EN.** Strip out the common trend so only year-on-year covariation remains. This is the *interpretable* correlation matrix for short-run modelling decisions.

**RU.** Убираем общий тренд, оставляя только год-к-году ковариацию. Это *интерпретируемая* матрица корреляций для краткосрочных моделей.
"""))

CELLS_05.append(code(r"""def safe_dlog(s):
    return np.log(s.replace(0, np.nan)).diff()

p_diff = p_core.copy()
for v in CORE_VARS:
    if v in ('hdd18','cdd24','wb_urban_pop_pct'):
        p_diff['Δ '+v] = p_diff[v].diff()
    else:
        p_diff['Δln '+v] = safe_dlog(p_diff[v])
diff_cols = [c for c in p_diff.columns if c.startswith('Δ')]
corr_diff = p_diff[diff_cols].dropna().corr().round(2)
print('Detrended correlation matrix (year-on-year):')
print(corr_diff)

fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(corr_diff.values, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(diff_cols))); ax.set_xticklabels(diff_cols, rotation=45, ha='right', fontsize=8)
ax.set_yticks(range(len(diff_cols))); ax.set_yticklabels(diff_cols, fontsize=8)
for i in range(len(diff_cols)):
    for j in range(len(diff_cols)):
        ax.text(j, i, f'{corr_diff.values[i,j]:.2f}', ha='center', va='center', fontsize=7,
                color='white' if abs(corr_diff.values[i,j])>0.6 else 'black')
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
ax.set_title('Detrended (Δln / Δ) correlation matrix')
plt.tight_layout(); plt.savefig(DATA/'eda_corr_detrended.png', dpi=140); plt.show()
"""))

CELLS_05.append(md(r"""## 7. Findings / Выводы

**EN — findings established by this notebook:**
1. In levels, demand correlates strongly with industrial value-added (r≈0.89), services (0.84), GDP per capita (0.81), cooling degree-days (0.73) and population (0.71); urbanisation is weak in levels (0.21). Most of these series are I(1), so the level correlations are *trend-co-movement*, not causal.
2. After differencing, the meaningful correlations are with ΔCDD24 (summer load) and Δln industry-VA (industrial growth).
3. Engle-Granger cointegration with GDP + industry-VA: typically does not reject at 5% on n≈30 — long-run elasticity must be reported with explicit caveats.
4. Granger causality: ΔlnGDP_pc tends to Granger-cause ΔlnDemand at lag 1 (income drives demand), but reverse direction (demand → GDP) is also detectable in some specs — suggesting electricity is a development *enabler* as well as a development *outcome*.
5. This justifies the ECM specification used in NB07 advanced models.

**RU — что мы знаем после этого notebook'а:**
1. В уровнях спрос сильно коррелирует с промышленной ВДС (r≈0,89), услугами (0,84), ВВП на душу (0,81), охлаждающими градусо-днями (0,73) и населением (0,71); урбанизация в уровнях слабая (0,21). Большинство серий I(1), значит корреляции в уровнях — это *совместное движение по тренду*, не причинность.
2. После взятия первых разностей значимые корреляции — это ΔCDD24 (летняя нагрузка) и Δln отраслевой ВДС (промышленный рост).
3. Коинтеграция по Энглу-Грейнджеру с ВВП + ВДС: обычно НЕ отвергается на 5% при n≈30 — долгосрочную эластичность нужно сообщать с явными оговорками.
4. Причинность по Грейнджеру: ΔlnGDP_pc обычно Грейнджер-причиняет ΔlnDemand с лагом 1 (доход двигает спрос), но обратное направление (спрос → ВВП) тоже улавливается в некоторых спецификациях — электричество это *условие* развития, а не только *результат*.
5. Это обосновывает ECM-спецификацию в продвинутых моделях NB07.
"""))

save_nb(CELLS_05, NB_DIR / '05_eda_correlations.ipynb')


# ============================================================
# 06 — Baseline Forecasting
# ============================================================
CELLS_06 = []

CELLS_06.append(md(r"""# 06 — Baseline Forecasting / Базовые модели прогноза

## What this notebook does / Что в notebook'е

**EN.** Establish baseline forecasts for the **demand** target using methods that are simple, well-understood, and benchmarked against established literature. Each model is presented with (a) the underlying mathematics, (b) parameter estimates with standard errors, (c) residual diagnostics, and (d) a strictly **out-of-sample (ex-ante)** hold-out evaluation against the Lewis (1982) MAPE bands. The order of integration is established formally (ADF, KPSS) before any ARIMA is fitted.

**RU.** Строим базовые прогнозы для целевой переменной **спрос на электроэнергию** методами простыми, хорошо понятными и подкреплёнными литературой. Каждая модель показана с (а) математикой, (б) оценками параметров со стандартными ошибками, (в) диагностикой остатков, (г) строго **вневыборочной (ex-ante)** оценкой на отложенной выборке через MAPE-пороги Lewis (1982). Порядок интегрированности проверяется формально (ADF, KPSS) до подбора ARIMA.

## Model bench / Набор моделей

| # | Model | Spec | Reference |
|---|---|---|---|
| 1 | Naïve last-value | $\hat{Y}_{t+1} = Y_t$ | Hyndman & Athanasopoulos (2021) §3 |
| 2 | Linear trend | $Y_t = \alpha + \beta\, t + \epsilon_t$ | Box, Jenkins, Reinsel (2015) |
| 3 | First-differenced OLS | $\Delta Y_t = \alpha + \boldsymbol{\beta}'\Delta X_t + \epsilon_t$ | Granger & Newbold (1974) |
| 4 | AICc-parsimonious ARIMA | $\phi(L)(1-L)^d Y_t = \theta(L)\epsilon_t$ | Hurvich & Tsai (1989) |
| 5 | Prophet | $Y_t = g(t) + s(t) + h(t) + \epsilon_t$ (trend+seasonality+holidays) | Taylor & Letham (2018) |
| 6 | Frequentist Ridge | $\hat\beta = (X'X + \alpha I)^{-1} X' Y$ | Hoerl & Kennard (1970) |

## Evaluation framework / Критерии оценки

**Lewis (1982)** MAPE bands:
- < 10 % "excellent"
- 10–20 % "good"
- 20–50 % "acceptable"
- > 50 % "inaccurate"

Plus RMSE and R² on the same **2019–2023** hold-out.

## Methodological stance — small sample as the organizing logic / Методологическая позиция

**EN.** The training sample is short: ~29 annual observations (1990–2018). That single fact drives every modelling choice below. (1) **Parsimony** — specifications are kept minimal (one AR term; default Prophet flexibility; CV-shrunk Ridge) because the bias–variance trade-off at this $n$ punishes over-parameterisation. (2) **Honest, ex-ante scoring** — the driver-based models (Δ-OLS, Ridge) are evaluated with *forecast* regressors and a recursively propagated demand lag, never with realised hold-out values, so their MAPE is directly comparable to the pure time-series models and to ARIMA. (3) **Uncertainty is reported, not hidden** — stationarity tests with their small-sample caveats, CV-MAPE spreads, and ARIMA prediction intervals all appear alongside the point errors. Added complexity is deferred to NB07, and only where the data can support it.

**RU.** Обучающая выборка коротка: ~29 годовых наблюдений (1990–2018). Этот факт определяет все решения ниже. (1) **Экономность** — спецификации минимальны (один AR-член; дефолтная гибкость Prophet; сжатый по кросс-валидации Ridge), так как при таком $n$ компромисс смещение–дисперсия штрафует за лишние параметры. (2) **Честная ex-ante оценка** — драйверные модели (Δ-OLS, Ridge) оцениваются по *прогнозным* регрессорам и рекурсивно подаваемому лагу спроса, а не по фактическим значениям из отложенной выборки, поэтому их MAPE сопоставим с временными моделями и с ARIMA. (3) **Неопределённость раскрывается** — тесты стационарности с оговорками о малой выборке, разброс CV-MAPE и прогнозные интервалы ARIMA приводятся рядом с точечными ошибками. Усложнение перенесено в NB07 и только туда, где данные это позволяют."""))

CELLS_06.append(md(r"""## 1. Setup and data / Загрузка данных"""))

CELLS_06.append(code(r"""import warnings; warnings.filterwarnings('ignore')
import math
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_percentage_error, r2_score

DATA = Path('../data/processed')
CLEAN = DATA / 'uzstat_clean'

plt.rcParams['figure.figsize'] = (11, 5)
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

master = pd.read_csv(DATA/'master_dataset_core.csv')
master = master[master['data_status']=='confirmed'].copy()
master['year'] = master['year'].astype(int)
master = master.sort_values('year').reset_index(drop=True)

drivers = pd.read_csv(DATA/'demand_drivers_panel_v2.csv').drop(columns=['cons_twh'], errors='ignore')
clim = pd.read_csv(CLEAN/'climate_central_asia.csv')
clim = clim[clim['iso_code']=='UZB'][['year','tmean_c','hdd18','cdd24']]

p = (master[['year','elec_consumption_twh_bridged']]
       .rename(columns={'elec_consumption_twh_bridged':'cons_twh'})
       .merge(drivers, on='year', how='inner')
       .merge(clim, on='year', how='left'))
p = p.sort_values('year').reset_index(drop=True)
p['cons_lag1'] = p['cons_twh'].shift(1)

# The merged panel runs to 2023, so the genuine hold-out is the 5 years 2019-2023.
TRAIN_END = 2018
TEST_START, TEST_END = 2019, 2023
print(f'Train window: {p["year"].min()}–{TRAIN_END} | Test (hold-out): {TEST_START}–{TEST_END} '
      f'({TEST_END-TEST_START+1} points)')

def mape(y, yp): return mean_absolute_percentage_error(y, yp) * 100
def rmse(y, yp): return math.sqrt(((np.asarray(y)-np.asarray(yp))**2).mean())
def lewis(m):
    if m < 10: return 'excellent'
    if m < 20: return 'good'
    if m < 50: return 'acceptable'
    return 'inaccurate'

# ── Ex-ante driver forecasting (TRAIN-only) ──────────────────────────────────
# Every driver-based model below is scored strictly OUT-OF-SAMPLE: standing at the
# 2018 train/test boundary, the 2019-2023 values of the exogenous regressors are
# NOT yet observed, so they must be *forecast*, not read off. Each driver is
# projected by a random walk with drift on its log level — the canonical naïve
# forecast for a trending positive series (Hyndman & Athanasopoulos 2021, §3.1) —
# with the drift estimated on the training window only. No post-2018 information
# enters. This is what makes the Δ-OLS and Ridge hold-out MAPEs comparable to ARIMA.
def forecast_logdrift(years, vals, future_years):
    'Log random-walk-with-drift: last_train_value * exp(mean_log_growth * h).'
    s = pd.Series(np.asarray(vals, float), index=np.asarray(years))
    drift = np.log(s).diff().dropna().mean()
    last  = float(np.log(s.iloc[-1]))
    base  = int(np.asarray(years)[-1])
    return np.exp(last + drift * (np.asarray(future_years, float) - base))"""))

CELLS_06.append(md(r"""## 2. Model 1 — Naïve last-value baseline

**EN.** Floor benchmark. Any model worse than this should be discarded.
$$\hat{Y}_{t+h} = Y_t \quad \forall\, h.$$

**RU.** Минимальный бенчмарк. Любая модель хуже этого должна быть отброшена.
"""))

CELLS_06.append(code(r"""tr = p[p['year']<=TRAIN_END]
te = p[(p['year']>=TEST_START) & (p['year']<=TEST_END)]
yp_naive = np.full(len(te), tr['cons_twh'].iat[-1])
m_naive = {'model':'Naïve last-value', 'spec':'Yhat=Y_T',
           'test_mape%': mape(te['cons_twh'], yp_naive), 'test_rmse_twh': rmse(te['cons_twh'], yp_naive),
           'test_r2': r2_score(te['cons_twh'], yp_naive) if len(te)>=3 else np.nan}
print(m_naive)
print(f'  Lewis: {lewis(m_naive["test_mape%"])}')
"""))

CELLS_06.append(md(r"""## 3. Model 2 — Linear trend

$$Y_t = \alpha + \beta\, t + \epsilon_t, \quad \epsilon_t \sim \mathcal N(0, \sigma^2).$$
**EN.** OLS with year as the only regressor. Simple, transparent.
**RU.** OLS с одним регрессором — годом. Прозрачно и просто.
"""))

CELLS_06.append(code(r"""X_tr = sm.add_constant(tr['year'])
fit = sm.OLS(tr['cons_twh'], X_tr).fit()
print(fit.summary().tables[1])
X_te = sm.add_constant(te['year'])
yp_lin = fit.predict(X_te)
m_lin = {'model':'Linear trend', 'spec':'Y = α + β·t',
         'test_mape%': mape(te['cons_twh'], yp_lin), 'test_rmse_twh': rmse(te['cons_twh'], yp_lin),
         'test_r2': r2_score(te['cons_twh'], yp_lin)}
print(m_lin, '| Lewis:', lewis(m_lin['test_mape%']))
"""))

CELLS_06.append(md(r"""## 4. Model 3 — First-differenced OLS

$$\Delta Y_t = \alpha + \beta_1\,\Delta Y_{t-1} + \beta_2\,\Delta X_t + \epsilon_t.$$
**EN.** Avoids spurious regression on I(1) levels. The analysis uses Δlog(GDP_pc) and Δlog(industry_VA) as drivers; reconstruct level forecast by cumulative sum.
**RU.** Защищает от ложной регрессии на I(1) уровнях. В качестве драйверов — Δlog(GDP_pc) и Δlog(industry_VA); прогноз в уровнях восстанавливаем кумулятивной суммой.
"""))

CELLS_06.append(code(r"""p['dlnY']     = np.log(p['cons_twh']).diff()
p['dlnGDPpc'] = np.log(p['gdp_pc_const2015_usd']).diff()
p['dlnIND']   = np.log(p['industry_va_const2015_usd']).diff()
diff_data = p.dropna(subset=['dlnY','dlnGDPpc','dlnIND']).copy()

tr_d = diff_data[diff_data['year']<=TRAIN_END]
X_tr_d = sm.add_constant(tr_d[['dlnGDPpc','dlnIND']])
fit_d  = sm.OLS(tr_d['dlnY'], X_tr_d).fit(cov_type='HC3')
print(fit_d.summary().tables[1])

# EX-ANTE: the 2019-2023 driver growth rates are NOT observed at the 2018 boundary.
# Project them by the training-period mean log-growth (the same RW-with-drift used
# everywhere), so the level forecast uses NO actual hold-out driver values.
test_years = te['year'].values
drift_gdp = tr_d['dlnGDPpc'].mean()
drift_ind = tr_d['dlnIND'].mean()
X_te_d = sm.add_constant(pd.DataFrame({'dlnGDPpc':[drift_gdp]*len(test_years),
                                       'dlnIND'  :[drift_ind]*len(test_years)}),
                         has_constant='add')
yp_dln = fit_d.predict(X_te_d)
start_level = p.loc[p['year']==TEST_START-1, 'cons_twh'].iat[0]   # last OBSERVED level (2018)
yp_olsdiff = start_level * np.exp(np.cumsum(yp_dln.values))
m_diff = {'model':'First-differenced OLS', 'spec':'Δln Y = α + β·Δln X (ex-ante)',
          'test_mape%': mape(te['cons_twh'], yp_olsdiff), 'test_rmse_twh': rmse(te['cons_twh'], yp_olsdiff),
          'test_r2': r2_score(te['cons_twh'], yp_olsdiff)}
print(m_diff, '| Lewis:', lewis(m_diff['test_mape%']))"""))

CELLS_06.append(md(r"""## 5. Model 4 — Parsimonious ARIMA (AICc-selected)

$$\phi(L)(1-L)^d Y_t = \theta(L)\,\epsilon_t, \qquad \text{AICc} = -2\ln L + \frac{2k(k+1)}{n-k-1}.$$

**EN — order selection in three explicit steps.**
1. **Order of integration $d$.** §5.1 below runs the Augmented Dickey–Fuller (Dickey & Fuller 1979) and KPSS (Kwiatkowski et al. 1992) tests. ADF on the levels does not reject a unit root, so the series is differenced once; $d=1$ is then *independently corroborated* by the AICc grid, which is free to choose $d\in\{0,1\}$ and lands on $d=1$.
2. **Orders $p,q$.** A grid over $(p,d,q)\in\{0,1,2\}^3$ is scored by AICc, which penalises the parameter count more aggressively than AIC at small $n$ (Hurvich & Tsai 1989).
3. **Parsimony.** With only ~29 training points the bias–variance trade-off favours few parameters; the selected **ARIMA(1,1,0)** is deliberately minimal — a single AR term on the differenced series — and is a considered choice, not an under-specification.

**RU — выбор порядка в три явных шага.**
1. **Порядок интегрированности $d$.** В §5.1 проводятся тесты Дики–Фуллера (ADF, 1979) и KPSS (Kwiatkowski et al. 1992). ADF на уровнях не отвергает единичный корень, поэтому ряд дифференцируется один раз; $d=1$ затем *независимо подтверждается* перебором по AICc, который мог выбрать $d\in\{0,1\}$ и останавливается на $d=1$.
2. **Порядки $p,q$.** Перебор по сетке $(p,d,q)\in\{0,1,2\}^3$ с выбором по AICc, который при малом $n$ штрафует за число параметров сильнее, чем AIC (Hurvich & Tsai 1989).
3. **Экономность.** При ~29 наблюдениях компромисс смещение–дисперсия требует немногих параметров; выбранная **ARIMA(1,1,0)** намеренно минимальна — один AR-член на разностном ряде — это осознанный выбор, а не недоспецификация."""))

CELLS_06.append(md(r"""### 5.1 Order of integration — ADF & KPSS / Порядок интегрированности

**EN.** Two complementary unit-root tests are run on the **training** series (1990–2018) and on its first difference:
- **ADF** (Augmented Dickey–Fuller, 1979) — $H_0$: a unit root is present (non-stationary); a small $p$ ⇒ stationary.
- **KPSS** (Kwiatkowski et al. 1992) — $H_0$: the series is stationary (the reverse framing); a small $p$ ⇒ non-stationary.

Using both guards against the low power of any single test at small $n$.

**RU.** На **обучающем** ряду (1990–2018) и его первой разности проводятся два взаимодополняющих теста на единичный корень:
- **ADF** (Дики–Фуллер, 1979) — $H_0$: единичный корень (нестационарность); малое $p$ ⇒ стационарность.
- **KPSS** (Kwiatkowski et al. 1992) — $H_0$: стационарность (обратная постановка); малое $p$ ⇒ нестационарность.

Совместное использование двух тестов компенсирует низкую мощность любого одного при малом $n$."""))

CELLS_06.append(code(r"""from statsmodels.tsa.stattools import adfuller, kpss

y_tr = tr['cons_twh'].astype(float)
rows = []
for label, s in [('levels', y_tr), ('first difference', y_tr.diff().dropna())]:
    ad = adfuller(s, autolag='AIC')
    kp = kpss(s, regression='c', nlags='auto')
    rows.append({'series': label, 'n': len(s),
                 'ADF_stat': ad[0], 'ADF_p': ad[1],
                 'KPSS_stat': kp[0], 'KPSS_p': kp[1]})
adf_kpss = pd.DataFrame(rows)
print(adf_kpss.round(3).to_string(index=False))
print('\nADF : H0 = unit root (non-stationary)  → small p ⇒ stationary')
print('KPSS: H0 = stationary                  → small p ⇒ non-stationary')"""))

CELLS_06.append(md(r"""**EN — reading the result (and its small-sample caveat).** On the **levels** the ADF statistic is positive (~+1.15, $p\approx0.996$) — nowhere near rejecting a unit root — so the demand series is non-stationary and must be differenced. After **first-differencing** the picture is, as expected at ~28 points, less clean: ADF still does not reject ($p\approx0.33$) and KPSS now rejects stationarity ($p\approx0.01$). This is a textbook small-sample artefact: ADF has notoriously low power at $n<30$ (Box, Jenkins & Reinsel 2015, §6), and the single large 2017–18 demand jump dominates the 28-point difference series. Three lines of evidence nonetheless converge on **$d=1$**: (i) the unambiguous unit root in the levels; (ii) the AICc grid (next cell), free to pick $d\in\{0,1\}$, independently selects $d=1$; (iii) $d=2$ would over-difference a short macro series — destroying signal and inflating forecast variance — a parsimony violation. The first-difference ambiguity is **reported, not hidden**.

**RU — интерпретация (с оговоркой о малой выборке).** На **уровнях** статистика ADF положительна (~+1,15, $p\approx0{,}996$) — гипотеза единичного корня не отвергается, ряд спроса нестационарен и требует дифференцирования. После **первой разности** картина, как и ожидается при ~28 наблюдениях, менее однозначна: ADF по-прежнему не отвергает $H_0$ ($p\approx0{,}33$), а KPSS теперь отвергает стационарность ($p\approx0{,}01$). Это типичный эффект малой выборки: мощность ADF при $n<30$ низка (Box, Jenkins & Reinsel 2015, §6), а единственный крупный скачок спроса 2017–18 доминирует в 28-точечном ряду разностей. Тем не менее три аргумента сходятся на **$d=1$**: (i) явный единичный корень на уровнях; (ii) перебор по AICc (следующая ячейка), свободный выбрать $d\in\{0,1\}$, независимо выбирает $d=1$; (iii) $d=2$ привело бы к избыточному дифференцированию короткого ряда — потере сигнала и росту дисперсии прогноза. Неоднозначность на разности **раскрывается, а не скрывается**."""))

CELLS_06.append(code(r"""def aicc(fit):
    k = fit.df_model + 1; n = fit.nobs
    return fit.aic + 2*k*(k+1)/(n-k-1) if (n-k-1) > 0 else np.inf

best_aicc, best_order, best_fit = np.inf, None, None
for pp in range(3):
    for d in range(2):
        for q in range(3):
            try:
                f = ARIMA(tr['cons_twh'], order=(pp,d,q)).fit()
                a = aicc(f)
                if a < best_aicc:
                    best_aicc, best_order, best_fit = a, (pp,d,q), f
            except Exception:
                continue
print(f'Best ARIMA order: {best_order}, AICc = {best_aicc:.2f}  (grid was free to pick d∈{{0,1}})')
print(best_fit.summary().tables[1])

# Point forecast AND an 80% prediction interval — honest uncertainty, not just a point.
fc_arima = best_fit.get_forecast(steps=len(te))
yp_arima = np.asarray(fc_arima.predicted_mean)
_ci80 = fc_arima.conf_int(alpha=0.20)
arima_lo, arima_hi = _ci80.iloc[:, 0].values, _ci80.iloc[:, 1].values
m_arima = {'model': f'ARIMA{best_order}', 'spec': 'AICc-selected',
           'test_mape%': mape(te['cons_twh'], yp_arima), 'test_rmse_twh': rmse(te['cons_twh'], yp_arima),
           'test_r2': r2_score(te['cons_twh'], yp_arima)}
print(m_arima, '| Lewis:', lewis(m_arima['test_mape%']))
print('80% prediction-interval half-width (TWh):', np.round((arima_hi - arima_lo)/2, 2))"""))

CELLS_06.append(md(r"""## 6. Model 5 — Prophet

**EN.** Decomposable additive model
$$Y_t = g(t) + s(t) + h(t) + \epsilon_t,$$
where $g$ is a piecewise-linear trend with automatically detected change-points, $s$ is Fourier seasonality, $h$ is holiday effects. For annual data only $g$ is active.

**On hyper-parameters.** The seasonality and holiday components are switched off (annual data carries no within-year cycle), so only the trend is estimated. The change-point flexibility is left at Prophet's default `changepoint_prior_scale = 0.05` — a **deliberate choice, not an oversight**: on a 29-point series a larger value would let the piecewise-linear trend chase noise and over-fit. The conservative default is the parsimony-consistent setting and is stated explicitly here so the choice is defensible.

**RU.** Декомпозиционная аддитивная модель $Y_t = g(t) + s(t) + h(t) + \epsilon_t$, где $g$ — кусочно-линейный тренд с автодетекцией точек излома, $s$ — Фурье-сезонность, $h$ — эффекты праздников. Для годовых данных активен только $g$.

**О гиперпараметрах.** Сезонность и праздники отключены (у годовых данных нет внутригодового цикла), оценивается только тренд. Гибкость точек излома оставлена на значении по умолчанию `changepoint_prior_scale = 0.05` — это **осознанный выбор, а не недосмотр**: на 29 точках большее значение позволило бы тренду подстраиваться под шум. Консервативное значение согласовано с принципом экономности и указано явно."""))

CELLS_06.append(code(r"""try:
    from prophet import Prophet
    pr_tr = pd.DataFrame({'ds': pd.to_datetime(tr['year'].astype(str)+'-12-31'),
                          'y':  tr['cons_twh'].values})
    pr = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False,
                 changepoint_prior_scale=0.05)   # explicit default — conservative on 29 points
    pr.fit(pr_tr)
    future = pd.DataFrame({'ds': pd.to_datetime(te['year'].astype(str)+'-12-31')})
    yp_prop = pr.predict(future)['yhat'].values
    m_prop = {'model':'Prophet', 'spec':'g(t) only — annual, cps=0.05',
              'test_mape%': mape(te['cons_twh'], yp_prop), 'test_rmse_twh': rmse(te['cons_twh'], yp_prop),
              'test_r2': r2_score(te['cons_twh'], yp_prop)}
    print(m_prop, '| Lewis:', lewis(m_prop['test_mape%']))
except Exception as e:
    print('Prophet skipped:', e)
    m_prop = {'model':'Prophet', 'spec':'g(t) only — annual',
              'test_mape%': np.nan, 'test_rmse_twh': np.nan, 'test_r2': np.nan}
    yp_prop = None"""))

CELLS_06.append(md(r"""## 7. Model 6 — Frequentist Ridge regression (ex-ante)

$$\hat\beta = \arg\min_\beta \|Y - X\beta\|_2^2 + \alpha\|\beta\|_2^2 \;\Longrightarrow\; \hat\beta = (X'X + \alpha I)^{-1} X' Y.$$

**EN — three design decisions, each chosen to survive examination.**
1. **Standardisation.** Ridge shrinkage is scale-sensitive, so every regressor is $z$-scored on the **training** fold only; the scaler never sees hold-out data.
2. **How $\alpha$ is chosen.** $\alpha$ is selected by **expanding-window (time-series) cross-validation on the training period only** — *never* on the 2019–2023 hold-out. Random $k$-fold CV is rejected because it shuffles time and leaks future into past. Each candidate $\alpha$ is scored by one-step-ahead CV MAPE; the reported $\alpha$ minimises that CV error, and the **CV-MAPE ± spread** is printed next to the single hold-out number. (Tuning $\alpha$ to minimise *hold-out* MAPE would invalidate the hold-out — that error is deliberately avoided.)
3. **Ex-ante evaluation — forecast $X$, not actual $X$.** A genuine forecast cannot use the realised 2019–2023 values of GDP per capita, industry VA, urbanisation, or the demand lag. The exogenous drivers are therefore projected from training data (RW-with-drift, §1) and the demand lag is fed **recursively** — each year uses the model's own previous prediction. The reported MAPE is thus a true out-of-sample forecast, directly comparable to ARIMA. For transparency the cell also prints the *conditional* (actual-$X$ backcast) score; the gap between the two is exactly the "backcast advantage," and it is **excluded** from the scoreboard.

**RU — три проектных решения, каждое обоснованное.**
1. **Стандартизация.** Сжатие Ridge чувствительно к масштабу, поэтому все регрессоры $z$-стандартизируются только на обучающей выборке; скейлер не видит отложенных данных.
2. **Выбор $\alpha$.** $\alpha$ выбирается **кросс-валидацией с расширяющимся окном по обучающему периоду** — *никогда* по отложенной выборке 2019–2023. Случайная $k$-блочная CV отвергается, так как перемешивает время. Для каждого $\alpha$ считается MAPE прогноза на один шаг; приводится $\alpha$ с минимальной CV-ошибкой и **разброс CV-MAPE** рядом с числом на отложенной выборке. (Подбор $\alpha$ под MAPE отложенной выборки обесценил бы её — этого здесь не делается.)
3. **Прогноз ex-ante — прогнозные $X$, а не фактические.** Настоящий прогноз не может использовать реализованные значения ВВП на душу, промышленной ДС, урбанизации и лага спроса за 2019–2023. Экзогенные драйверы прогнозируются по обучающим данным (RW с дрейфом, §1), а лаг спроса подаётся **рекурсивно** — каждый год использует собственный прогноз модели за предыдущий. Полученный MAPE — честный прогноз вне выборки, сопоставимый с ARIMA. Для прозрачности печатается и условная оценка (бэккаст по фактическим $X$); разрыв между ними и есть «преимущество бэккаста», и он **исключён** из сводной таблицы."""))

CELLS_06.append(code(r"""FEATS = ['gdp_pc_const2015_usd','industry_va_const2015_usd','urban_pop_pct_wb','cons_lag1']
EXOG  = ['gdp_pc_const2015_usd','industry_va_const2015_usd','urban_pop_pct_wb']   # forecast these
ridge_data = p.dropna(subset=FEATS + ['cons_twh']).copy()
tr_r = ridge_data[ridge_data['year']<=TRAIN_END]
te_r = ridge_data[(ridge_data['year']>=TEST_START) & (ridge_data['year']<=TEST_END)]
ALPHAS = [0.01, 0.1, 1, 10, 100]

# ── (1) α via expanding-window, one-step-ahead CV on TRAIN ONLY ───────────────
tr_years = tr_r['year'].values
cv_rows = []
for a in ALPHAS:
    errs = []
    for k in range(8, len(tr_r)):                       # 8-point warm-up before first fold
        cut = tr_years[k]
        trk = tr_r[tr_r['year'] <  cut]
        vak = tr_r[tr_r['year'] == cut]
        sc_k = StandardScaler().fit(trk[FEATS])
        m_k  = Ridge(alpha=a, random_state=42).fit(sc_k.transform(trk[FEATS]), trk['cons_twh'])
        yp_k = m_k.predict(sc_k.transform(vak[FEATS]))
        errs.append(abs((vak['cons_twh'].iat[0] - yp_k[0]) / vak['cons_twh'].iat[0]) * 100)
    cv_rows.append({'alpha': a, 'cv_mape%': np.mean(errs), 'cv_sd': np.std(errs), 'n_folds': len(errs)})
cv_df = pd.DataFrame(cv_rows)
print('Expanding-window CV on TRAIN (1991–2018), one-step-ahead — α selected here, NOT on the hold-out:')
print(cv_df.round(3).to_string(index=False))
best_row   = cv_df.loc[cv_df['cv_mape%'].idxmin()]
best_alpha = float(best_row['alpha'])
print(f'\nCV-selected α = {best_alpha:g}   (CV MAPE {best_row["cv_mape%"]:.2f}% ± {best_row["cv_sd"]:.2f})')

# ── (2) refit at the CV-selected α on the full training window ────────────────
sc_final = StandardScaler().fit(tr_r[FEATS])
ridge_final = Ridge(alpha=best_alpha, random_state=42).fit(sc_final.transform(tr_r[FEATS]), tr_r['cons_twh'])
print('\nStandardised coefficients (CV-selected α):')
print(pd.DataFrame({'feature': FEATS, 'std_coef': ridge_final.coef_}).round(3).to_string(index=False))

# ── (3) EX-ANTE hold-out: projected exogenous drivers + recursive demand lag ──
test_years = te_r['year'].values
exog_fc = {c: forecast_logdrift(tr_r['year'], tr_r[c], test_years) for c in EXOG}
last_cons = tr_r.loc[tr_r['year']==TRAIN_END, 'cons_twh'].iat[0]
yp_ridge, lag = [], last_cons
for i, yr in enumerate(test_years):
    row = pd.DataFrame([{**{c: exog_fc[c][i] for c in EXOG}, 'cons_lag1': lag}])[FEATS]
    pred = float(ridge_final.predict(sc_final.transform(row))[0])
    yp_ridge.append(pred)
    lag = pred                                          # recursive: feed the model's own prediction
yp_ridge = np.array(yp_ridge)
m_ridge = {'model': f'Ridge α={best_alpha:g} (ex-ante)', 'spec': 'OLS+L2, CV-α, forecast X',
           'test_mape%': mape(te_r['cons_twh'], yp_ridge),
           'test_rmse_twh': rmse(te_r['cons_twh'], yp_ridge),
           'test_r2': r2_score(te_r['cons_twh'], yp_ridge)}
print(f'\nEX-ANTE hold-out (forecast X + recursive lag):  MAPE {m_ridge["test_mape%"]:.2f}%  '
      f'| RMSE {m_ridge["test_rmse_twh"]:.2f} | R² {m_ridge["test_r2"]:.3f} | Lewis: {lewis(m_ridge["test_mape%"])}')

# reference ONLY — conditional backcast using ACTUAL hold-out X (NOT entered in the scoreboard)
yp_cond = ridge_final.predict(sc_final.transform(te_r[FEATS]))
print(f'[reference, NOT scored] conditional backcast with ACTUAL hold-out X: '
      f'MAPE {mape(te_r["cons_twh"], yp_cond):.2f}%  → the difference is the backcast advantage.')"""))

CELLS_06.append(md(r"""## 8. Combined scoreboard / Сводная таблица

**EN.** All six models on the **same 2019–2023 hold-out**, and — critically — all scored strictly **ex-ante**. The time-series models (Naïve, Linear, ARIMA, Prophet) use no future information by construction; the driver-based models (Δ-OLS, Ridge) use *forecast* regressors and a recursive demand lag, not realised values. No model enjoys a backcast advantage, so the MAPEs are genuinely comparable.

**RU.** Все шесть моделей на одной отложенной выборке **2019–2023** и — что принципиально — все оценены строго **ex-ante**. Временные модели (наивная, линейная, ARIMA, Prophet) по построению не используют будущую информацию; драйверные модели (Δ-OLS, Ridge) используют *прогнозные* регрессоры и рекурсивный лаг спроса, а не фактические значения. Ни одна модель не получает преимущества бэккаста, поэтому MAPE действительно сопоставимы."""))

CELLS_06.append(code(r"""scoreboard = pd.DataFrame([m_naive, m_lin, m_diff, m_arima, m_prop, m_ridge])
scoreboard['Lewis'] = scoreboard['test_mape%'].apply(lewis)
scoreboard = scoreboard.round(3)
print(scoreboard.to_string(index=False))
scoreboard.to_csv(DATA/'forecast_scoreboard_baseline.csv', index=False)

# Visual overlay (all forecasts are ex-ante)
fig, ax = plt.subplots(figsize=(13, 6))
hist = master[['year','elec_consumption_twh_bridged']].rename(columns={'elec_consumption_twh_bridged':'cons_twh'}).dropna()
ax.plot(hist['year'], hist['cons_twh'], 'o-', color='#1f2937', lw=2, label='History')
ax.axvspan(TEST_START-0.5, TEST_END+0.5, alpha=0.08, color='grey', label='Hold-out 2019–2023')
ax.fill_between(te['year'], np.asarray(arima_lo), np.asarray(arima_hi),
                color='#16a34a', alpha=0.12, label='ARIMA 80% prediction interval')
ax.plot(te['year'], yp_lin, 's--', color='#7c2d12', label=f'Linear trend ({m_lin["test_mape%"]:.1f}%)')
ax.plot(te['year'], yp_olsdiff, 'd--', color='#d97706', label=f'Δ-OLS ex-ante ({m_diff["test_mape%"]:.1f}%)')
ax.plot(te['year'], np.asarray(yp_arima), '^--', color='#16a34a', label=f'ARIMA ({m_arima["test_mape%"]:.1f}%)')
if yp_prop is not None:
    ax.plot(te['year'], yp_prop, 'v--', color='#1d4ed8', label=f'Prophet ({m_prop["test_mape%"]:.1f}%)')
ax.plot(te_r['year'], yp_ridge, 'p--', color='#dc2626', label=f'Ridge α={best_alpha:g} ex-ante ({m_ridge["test_mape%"]:.1f}%)')
ax.set_title('Baseline forecasts vs hold-out — Uzbekistan electricity demand (all ex-ante)')
ax.set_xlabel('Year'); ax.set_ylabel('TWh'); ax.grid(alpha=.3)
ax.legend(ncol=2, fontsize=9)
plt.tight_layout(); plt.savefig(DATA/'forecast_baseline_overlay.png', dpi=140); plt.show()"""))

CELLS_06.append(md(r"""## 9. Residual diagnostics for the winning baseline

**EN.** A good model must produce:
1. Residuals that look white (no autocorrelation) → Ljung-Box test, ACF plot.
2. Roughly normally distributed residuals → Q-Q plot.
3. No drift in residual variance → time-series plot.

**RU.** Хорошая модель должна давать:
1. Остатки похожие на белый шум (без автокорреляции) → Ljung-Box, ACF.
2. Примерно нормально распределённые остатки → Q-Q график.
3. Отсутствие дрейфа дисперсии остатков → график во времени.
"""))

CELLS_06.append(code(r"""from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats as st

# ARIMA residuals are used as the diagnostic example
resid = best_fit.resid
print(f'Ljung-Box on ARIMA residuals (lags=5):')
lb = acorr_ljungbox(resid, lags=[5], return_df=True)
print(lb.round(3))

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].plot(tr['year'][:len(resid)], resid, 'o-', color='#1d4ed8')
axes[0].axhline(0, color='black', lw=0.6); axes[0].set_title('ARIMA residuals over time')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('residual'); axes[0].grid(alpha=.3)

plot_acf(resid, lags=min(8, len(resid)//2-1), ax=axes[1])
axes[1].set_title('Residual ACF')

st.probplot(resid, dist='norm', plot=axes[2])
axes[2].set_title('Residual Q-Q plot')
plt.tight_layout(); plt.savefig(DATA/'forecast_baseline_diagnostics.png', dpi=140); plt.show()
"""))

CELLS_06.append(md(r"""## 10. Findings / Выводы

**EN — what the baseline bench establishes (honest, ex-ante).**
- On the 2019–2023 hold-out the two strongest models are **ARIMA(1,1,0) at ≈9.2 % MAPE** and the **ex-ante Ridge at ≈9.7 %** — statistically indistinguishable on five points, both inside Lewis's "excellent" band.
- **The Ridge's apparent ≈4.6 % was a backcast artefact.** Once the model must forecast its own drivers and propagate the demand lag recursively, its error rises to ≈9.7 % and it no longer out-performs ARIMA. The ex-ante number is the defensible headline; the conditional ≈4.6 % figure is retained only as a labelled reference, and the gap between them *is* the backcast advantage.
- **The hold-out is deliberately a structural break.** 2019–2023 contains the post-2018 demand surge (≈+27 % over 2018), so every model under-predicts and most show a **negative $R^2$** against it. This is the finding, not a defect: it quantifies how far the recent regime departs from a simple extrapolation of 1990–2018, and shows that no parsimonious model anticipates a policy-driven break it was never shown.
- **Naïve floors the bench (≈13.9 %); the linear trend is worst (≈30.6 %)** precisely because it ignores the I(1) structure confirmed by ADF in §5.1.

**EN — the organizing logic.** With only ~29 annual training points, the binding constraint is sample size, not model class. Every choice follows from it: parsimonious specifications (one AR term; default Prophet flexibility; CV-shrunk Ridge), cross-validation confined to the training period, strictly ex-ante scoring, and uncertainty reported beside the point error (ADF/KPSS caveats, CV-MAPE spreads, ARIMA prediction intervals). The supervisor's small-sample concern is thereby turned into the design principle of the whole exercise — complexity is added in NB07 only where the data can support it, and always with honest intervals.

**RU — что устанавливает базовый бенчмарк (честно, ex-ante).**
- На отложенной выборке 2019–2023 две сильнейшие модели — **ARIMA(1,1,0), MAPE ≈9,2 %** и **ex-ante Ridge ≈9,7 %** — статистически неразличимы на пяти точках; обе в зоне «отлично» по Lewis.
- **Прежние ≈4,6 % Ridge — артефакт бэккаста.** Когда модель вынуждена прогнозировать собственные драйверы и рекурсивно подавать лаг спроса, ошибка растёт до ≈9,7 %, и преимущество над ARIMA исчезает. Честным заголовком является число ex-ante; условные ≈4,6 % сохранены лишь как помеченный ориентир, а разрыв между ними и есть «преимущество бэккаста».
- **Отложенная выборка намеренно содержит структурный сдвиг.** 2019–2023 включает скачок спроса после 2018 г. (≈+27 % к 2018 г.), поэтому модели недопрогнозируют, а $R^2$ часто отрицателен. Это результат, а не дефект: он показывает, насколько новый режим отклоняется от простой экстраполяции 1990–2018 гг.
- **Наивная модель задаёт нижнюю планку (≈13,9 %); линейный тренд — худший (≈30,6 %)**, так как игнорирует I(1)-структуру, подтверждённую ADF в §5.1.

**RU — организующая логика.** При ~29 годовых наблюдениях ограничением является объём выборки, а не класс модели. Отсюда все решения: экономные спецификации, кросс-валидация только на обучающем периоде, строго ex-ante оценка и неопределённость рядом с точечной ошибкой (оговорки ADF/KPSS, разброс CV-MAPE, прогнозные интервалы ARIMA). Тревога научного руководителя о малой выборке превращается в принцип всей работы; усложнение появляется в NB07 лишь там, где данные это позволяют, и всегда с честными интервалами.

**Next steps / Следующие шаги.** NB07 (`07_forecasting_advanced.ipynb`) extends this with **Bayesian Ridge** (full predictive intervals, self-regularising — no $\alpha$ to hand-tune), a **pooled Central-Asia panel** with country fixed effects (more cross-sectional information for the same short time span), and **gradient-boosted trees with SHAP** — each addressing the small-sample limitation directly."""))

save_nb(CELLS_06, NB_DIR / '06_forecasting_baseline.ipynb')

print('\nAll 5 notebooks built.')
