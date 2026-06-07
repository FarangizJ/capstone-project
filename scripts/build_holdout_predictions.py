"""
build_holdout_predictions.py
----------------------------
Persist the PER-YEAR ex-ante hold-out predictions (2019-2023) for the four
single-country demand models in Table 4.1, so the §4.4 forecast-vs-actuals
figure can be drawn from a real artifact instead of being re-derived ad hoc.

The scoring functions and data preparation are copied VERBATIM from
notebooks/07_forecasting_advanced.ipynb (the notebook that produced
forecast_scoreboard_advanced.csv). Nothing is re-implemented or invented: this
script re-runs the notebook's own ex-ante machinery and, as a fidelity check,
asserts the recomputed summary MAPE/R^2 reproduce the published scoreboard to
three decimals. If they do not match, the script refuses to write.

Input  (read-only):  data/processed/master_dataset_core.csv
                     data/processed/demand_drivers_panel_v2.csv
                     data/processed/uzstat_clean/uzb_energy_national.csv
                     data/processed/forecast_scoreboard_advanced.csv  (for the check)
Output (new only):   data/processed/forecast_holdout_predictions.csv
"""
from pathlib import Path
import math
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, BayesianRidge
from sklearn.metrics import mean_absolute_percentage_error, r2_score

ROOT  = Path(__file__).resolve().parents[1]
DATA  = ROOT / "data" / "processed"
CLEAN = DATA / "uzstat_clean"
SEED  = 42
np.random.seed(SEED)

# ── scoring machinery, copied verbatim from NB07 ─────────────────────────────
def mape(y, p): return mean_absolute_percentage_error(y, p) * 100
def rmse(y, p): return math.sqrt(((np.asarray(y) - np.asarray(p)) ** 2).mean())

MACRO_DRIVERS = {'gdp_pc_const2015_usd', 'industry_va_const2015_usd', 'services_va_const2015_usd',
                 'urban_pop_pct_wb', 'urban_pop_pct', 'population_total'}
CLIM_DRIVERS  = {'cdd24', 'hdd18'}
LAG_DRIVERS   = {'cons_lag1', 'demand_lag1'}

def forecast_logdrift(years, vals, future_years):
    s = pd.Series(np.asarray(vals, float), index=np.asarray(years))
    dln = np.log(s).diff().dropna().mean()
    fy = np.asarray(future_years, float)
    return np.exp(np.log(s.iloc[-1]) + dln * (fy - np.asarray(years)[-1]))

def expanding_cv_alpha(tr_df, feats, target, alphas=(0.01, 0.1, 1, 10, 100), min_train=8, continuous=None):
    feats = list(feats)
    cont = list(continuous) if continuous is not None else feats
    d = tr_df.dropna(subset=feats + [target]).sort_values('year').reset_index(drop=True)
    uniq = sorted(d['year'].unique())
    start = min(min_train, max(3, len(uniq) // 2))
    rows = []; best = (None, np.inf)
    for a in alphas:
        errs = []
        for cut in uniq[start:]:
            trk = d[d['year'] < cut]; vak = d[d['year'] == cut]
            if len(trk) < max(3, len(cont)) or len(vak) == 0:
                continue
            sc = StandardScaler().fit(trk[cont])
            def _tf(df_):
                X = df_[feats].copy(); X[cont] = sc.transform(X[cont]); return X.values
            m = Ridge(alpha=a, random_state=SEED).fit(_tf(trk), trk[target].values)
            errs.append(mape(vak[target].values, m.predict(_tf(vak))))
        rows.append({'alpha': a, 'cv_mape%': float(np.mean(errs)) if errs else np.nan})
        if errs and np.mean(errs) < best[1]:
            best = (a, float(np.mean(errs)))
    return best[0], pd.DataFrame(rows)

def exante_holdout(tr_df, te_years, feats, target, transform, model, return_std=False):
    feats = list(feats)
    tr_df = tr_df.sort_values('year')
    te_years = np.asarray(te_years)
    paths = {}
    for c in feats:
        if c in LAG_DRIVERS:
            paths[c] = None
        elif c in CLIM_DRIVERS:
            paths[c] = np.full(len(te_years), tr_df[c].tail(5).mean())
        elif c in MACRO_DRIVERS:
            paths[c] = forecast_logdrift(tr_df['year'].values, tr_df[c].values, te_years)
        else:
            paths[c] = np.full(len(te_years), tr_df[c].iloc[-1])
    lag = float(tr_df[target].iloc[-1]); preds = []; stds = []
    for i in range(len(te_years)):
        row = {c: (lag if c in LAG_DRIVERS else paths[c][i]) for c in feats}
        X1 = pd.DataFrame([row])[feats].values
        if return_std:
            mu, sd = model.predict(transform(X1), return_std=True)
            preds.append(float(mu[0])); stds.append(float(sd[0])); lag = float(mu[0])
        else:
            yp = float(model.predict(transform(X1))[0]); preds.append(yp); lag = yp
    return (np.array(preds), np.array(stds)) if return_std else np.array(preds)

# ── data preparation, mirroring NB07 §2.1-§2.2 ───────────────────────────────
master = pd.read_csv(DATA / 'master_dataset_core.csv')
master = master[master['data_status'] == 'confirmed'].copy()
master['year'] = master['year'].astype(int)

drivers = pd.read_csv(DATA / 'demand_drivers_panel_v2.csv')
drivers['year'] = drivers['year'].astype(int)

uzb_energy_nat = pd.read_csv(CLEAN / 'uzb_energy_national.csv')

uzb_full = drivers.drop(columns=['cons_twh'], errors='ignore').copy()
uzb_full = uzb_full.rename(columns={'cdd24_natl': 'cdd24', 'hdd18_natl': 'hdd18',
                                    'tmean_c_natl': 'tmean_c'})
uzb_full = uzb_full.merge(uzb_energy_nat, on='year', how='left')
uzb_full = uzb_full.merge(master[['year', 'elec_consumption_twh_bridged']]
                          .rename(columns={'elec_consumption_twh_bridged': 'cons_twh'}),
                          on='year', how='left')
uzb_full = uzb_full.sort_values('year').reset_index(drop=True)
uzb_full = uzb_full.loc[:, ~uzb_full.columns.duplicated()]

needed = ['cons_twh', 'gdp_pc_const2015_usd', 'industry_va_const2015_usd',
          'services_va_const2015_usd', 'urban_pop_pct_wb', 'cdd24', 'hdd18']
core_window = uzb_full.dropna(subset=needed).copy()

TARGET = 'cons_twh'
core_window = core_window.sort_values('year').reset_index(drop=True)
core_window['cons_lag1'] = core_window[TARGET].shift(1)

FEATS_MIN = ['gdp_pc_const2015_usd', 'industry_va_const2015_usd', 'urban_pop_pct_wb', 'cons_lag1']
FEATS_EXT = FEATS_MIN + ['services_va_const2015_usd', 'cdd24', 'hdd18']
phys_candidates = ['nat_gas_consumption_mcm', 'total_power_capacity_mw', 'coal_consumption_kt',
                   'elec_supply_housing_gwh', 'elec_supply_enterprises_gwh']
for c in phys_candidates:
    if c in core_window.columns and core_window[c].notna().sum() >= len(core_window) / 2:
        FEATS_EXT.append(c)

TRAIN_END = 2018
TEST_START, TEST_END = 2019, 2023

def split_df(df, feats):
    d = df.dropna(subset=feats + [TARGET]).copy()
    tr = d[d['year'] <= TRAIN_END].copy()
    te = d[(d['year'] >= TEST_START) & (d['year'] <= TEST_END)].copy()
    return tr, te

trdf_min, tedf_min = split_df(core_window, FEATS_MIN)
trdf_ext, tedf_ext = split_df(core_window, FEATS_EXT)

alpha_min, _ = expanding_cv_alpha(trdf_min, FEATS_MIN, TARGET)
alpha_ext, _ = expanding_cv_alpha(trdf_ext, FEATS_EXT, TARGET)

def eval_model(name, model, feats, trdf, tedf):
    Xt = trdf[feats].values; yt = trdf[TARGET].values
    sc = StandardScaler().fit(Xt)
    model.fit(sc.transform(Xt), yt)
    yv = tedf[TARGET].values
    cond = model.predict(sc.transform(tedf[feats].values))
    exa = exante_holdout(trdf, tedf['year'].values, feats, TARGET, sc.transform, model)
    return {'name': name, 'years': tedf['year'].values, 'actual': yv, 'exante': exa,
            'exante_mape%': mape(yv, exa), 'exante_r2': r2_score(yv, exa),
            'cond_mape%': mape(yv, cond)}

models = [
    eval_model('Ridge CV-alpha (UZB, minimal)',           Ridge(alpha=alpha_min, random_state=SEED), FEATS_MIN, trdf_min, tedf_min),
    eval_model('Ridge CV-alpha (UZB, extended + UzStat)',  Ridge(alpha=alpha_ext, random_state=SEED), FEATS_EXT, trdf_ext, tedf_ext),
    eval_model('BayesianRidge (UZB, minimal)',             BayesianRidge(compute_score=True, fit_intercept=True), FEATS_MIN, trdf_min, tedf_min),
    eval_model('BayesianRidge (UZB, extended)',            BayesianRidge(compute_score=True, fit_intercept=True), FEATS_EXT, trdf_ext, tedf_ext),
]

# ── fidelity check against the published scoreboard ──────────────────────────
sb = pd.read_csv(DATA / 'forecast_scoreboard_advanced.csv').set_index('model')
print("Fidelity check (recomputed vs published forecast_scoreboard_advanced.csv):")
ok = True
for m in models:
    pub = sb.loc[m['name']]
    dm = abs(m['exante_mape%'] - pub['exante-mape%' if 'exante-mape%' in pub else 'exante_mape%'])
    dr = abs(m['exante_r2'] - pub['exante_r2'])
    match = (dm < 0.01) and (dr < 0.01)
    ok &= match
    print(f"  {m['name']:42s} exante {m['exante_mape%']:6.3f} (pub {pub['exante_mape%']:6.3f}) "
          f"R2 {m['exante_r2']:+.3f} (pub {pub['exante_r2']:+.3f})  {'OK' if match else 'MISMATCH'}")

if not ok:
    raise SystemExit("Recomputed metrics do NOT match the published scoreboard — refusing to write.")

# ── assemble + write the per-year predictions (new file only) ────────────────
years = models[0]['years']
assert all(np.array_equal(years, m['years']) for m in models), "hold-out years differ across models"
out = pd.DataFrame({'year': years, 'actual_cons_twh': models[0]['actual']})
SHORT = {
    'Ridge CV-alpha (UZB, minimal)':           'ridge_min',
    'Ridge CV-alpha (UZB, extended + UzStat)': 'ridge_ext',
    'BayesianRidge (UZB, minimal)':            'bayes_min',
    'BayesianRidge (UZB, extended)':           'bayes_ext',
}
for m in models:
    out[f"pred_{SHORT[m['name']]}"] = np.round(m['exante'], 4)
out['actual_cons_twh'] = np.round(out['actual_cons_twh'], 4)

dest = DATA / 'forecast_holdout_predictions.csv'
out.to_csv(dest, index=False)
print(f"\nsaved -> {dest}")
print(out.to_string(index=False))
