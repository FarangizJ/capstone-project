"""Uzbekistan Power Sector Transition Tracker — Plotly Dash app.

Run locally:
    cd dashboard && python app.py
    → http://127.0.0.1:8050

Deploy to Render / HF Spaces: requirements in dashboard/requirements.txt; entrypoint app.py exposes `server` for gunicorn.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paths ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'processed'

# ── Load data once ────────────────────────────────────────────────────
master       = pd.read_csv(DATA / 'master_dataset_core.csv')
df_c         = master[master['data_status'] == 'confirmed'].copy()
demand_fc    = pd.read_csv(DATA / 'forecast_demand.csv')
scenarios_fc = pd.read_csv(DATA / 'forecast_scenarios.csv')
co2_fc       = pd.read_csv(DATA / 'forecast_co2.csv')
invest_fc    = pd.read_csv(DATA / 'investment_signals.csv')
scoreboard   = pd.read_csv(DATA / 'forecast_scoreboard_advanced.csv')
oblasts      = pd.read_csv(DATA / 'oblast_atlas.csv')

WINNER       = demand_fc['winner_model'].iat[0]

COLORS = {
    'gas':'#d97706','coal':'#374151','hydro':'#0891b2','solar':'#facc15',
    'wind':'#10b981','nuclear':'#6b21a8',
    'BAU':'#9ca3af','Government':'#16a34a','Accelerated':'#0d9488',
    'history':'#1f2937','demand':'#1e3a8a',
}

# ── Helper: parametric nuclear overlay (Plan B) ───────────────────────
def apply_nuclear(scen_df, capacity_mw, commission_year, cf=0.85):
    if capacity_mw <= 0:
        out = scen_df.copy(); out['gen_nuclear_twh'] = 0.0
        return out
    out = scen_df.copy()
    nuc = []
    for yr in out['year']:
        if yr < commission_year:
            nuc.append(0.0)
        else:
            ramp = min(1.0, (yr - commission_year + 1) / 2)
            nuc.append(capacity_mw * 8760 * cf * ramp / 1e6)
    out['gen_nuclear_twh'] = nuc
    out['gen_thermal_twh'] = (out['gen_thermal_twh'] - out['gen_nuclear_twh']).clip(lower=0)
    out['gen_total_twh']   = (out['gen_thermal_twh'] + out['gen_hydro_twh']
                              + out['gen_solar_twh'] + out['gen_wind_twh']
                              + out['gen_nuclear_twh'])
    re_plus = out['gen_hydro_twh'] + out['gen_solar_twh'] + out['gen_wind_twh'] + out['gen_nuclear_twh']
    out['re_share_pct'] = ((out['gen_hydro_twh']+out['gen_solar_twh']+out['gen_wind_twh'])
                          / out['gen_total_twh'] * 100)
    out['re_plus_nuclear_share_pct'] = re_plus / out['gen_total_twh'] * 100
    return out

# ── Layout ────────────────────────────────────────────────────────────
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title='Uzbekistan Power Transition Tracker',
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1'}])
server = app.server   # for gunicorn

HEADER_STYLE = {'background':'linear-gradient(135deg,#0d4d7a 0%,#1e3a8a 100%)',
                'color':'white','padding':'24px 36px'}
CARD_STYLE = {'background':'white','border':'1px solid #e5e7eb','borderRadius':'10px',
              'padding':'18px','marginBottom':'14px','boxShadow':'0 1px 2px rgba(0,0,0,0.02)'}
LABEL = {'fontSize':'12px','color':'#6b7280','textTransform':'uppercase','letterSpacing':'0.5px',
         'margin':'10px 0 4px','fontWeight':600}

def graph(graph_id):
    """A chart wrapped in a navy loading spinner so slow callbacks show progress.
    responsive=True lets Plotly rescale to the container width on phones/tablets."""
    return dcc.Loading(type='circle', color='#0d4d7a',
                       children=dcc.Graph(id=graph_id, style={'width': '100%'},
                                          config={'displayModeBar': False, 'responsive': True}))

def static_graph(figure, height=None):
    """A non-interactive chart whose figure is fixed at load time (no callback).
    Used for the notebook deep-dive panels, which do not react to the sidebar."""
    style = {'width': '100%'}
    return dcc.Graph(figure=figure, style=style,
                     config={'displayModeBar': False, 'responsive': True})

# ── Narrative helpers (EN body + bilingual RU box) ────────────────────
def narr(*children):
    """Body paragraph for the deep-dive panels. Technical terms carry an inline
    plain-language gloss in parentheses, e.g. 'capacity factor (share of the year a
    plant actually runs)', so a non-specialist reader never loses the thread."""
    return html.P(list(children), style={'color':'#374151','fontSize':'14px','lineHeight':1.6,'margin':'0 0 10px'})

def takeaway(text):
    return html.Div(style={'background':'#eef4f9','borderLeft':'4px solid #0d4d7a','padding':'10px 14px',
                           'borderRadius':'6px','fontSize':'13px','color':'#0d4d7a','fontWeight':500,
                           'margin':'6px 0 12px'}, children=text)

def ru_box(bullets):
    """Bilingual Russian summary box (house-style EN+RU). Translates the panel's
    real findings — every number is identical to the English text above it."""
    return html.Div(style={'background':'#fffaf0','border':'1px solid #f0d9a8','borderRadius':'8px',
                           'padding':'14px 16px','marginTop':'12px'}, children=[
        html.Div('🇷🇺 Ключевые выводы (Russian summary)',
                 style={'fontWeight':700,'color':'#92580a','fontSize':'13px','marginBottom':'8px',
                        'textTransform':'uppercase','letterSpacing':'0.4px'}),
        html.Ul(style={'margin':0,'paddingLeft':'18px','color':'#5b4410','fontSize':'13px','lineHeight':1.6},
                children=[html.Li(b) for b in bullets]),
    ])

# ── Deep-dive figure builders (static, from the real processed CSVs) ──
GEN_SOURCES = [('gen_gas_twh','gas','Gas'),('gen_coal_twh','coal','Coal'),
               ('gen_hydro_twh','hydro','Hydro'),('gen_solar_twh','solar','Solar'),
               ('gen_wind_twh','wind','Wind')]

def fig_growth_animation():
    """NB02 — animated history of the generation fleet, 1990→latest confirmed year.
    Each frame is one year; bars are TWh generated by each source. The animation
    makes the 'two speeds' story visible: a flat gas-dominated plateau to ~2018,
    then the post-2018 solar/wind surge."""
    d = df_c[['year'] + [c for c,_,_ in GEN_SOURCES]].fillna(0).sort_values('year')
    years = d['year'].tolist()
    names = [n for _,_,n in GEN_SOURCES]
    cols  = [COLORS[c] for _,c,_ in GEN_SOURCES]
    ymax  = float(d[[c for c,_,_ in GEN_SOURCES]].sum(axis=1).max()) * 1.08

    def bars_for(yr):
        row = d[d['year']==yr].iloc[0]
        return [float(row[c]) for c,_,_ in GEN_SOURCES]

    first = bars_for(years[0])
    base = go.Bar(x=names, y=first, marker_color=cols,
                  text=[f'{v:.1f}' for v in first], textposition='outside')
    frames = []
    for yr in years:
        vals = bars_for(yr)
        frames.append(go.Frame(name=str(int(yr)),
            data=[go.Bar(x=names, y=vals, marker_color=cols,
                         text=[f'{v:.1f}' for v in vals], textposition='outside')],
            layout=go.Layout(title_text=f'Generation by source — {int(yr)} '
                                        f'(total {sum(vals):.1f} TWh)')))
    fig = go.Figure(data=[base], frames=frames)
    fig.update_layout(
        template='plotly_white', height=460, margin=dict(l=50,r=20,t=80,b=90),
        title=f'Generation by source — {int(years[0])} (total {sum(first):.1f} TWh)',
        yaxis_title='TWh generated', yaxis_range=[0, ymax], xaxis_title='',
        updatemenus=[dict(type='buttons', showactive=False, x=0.02, y=-0.18, xanchor='left',
            buttons=[
                dict(label='▶ Play', method='animate',
                     args=[None, dict(frame=dict(duration=380, redraw=True),
                                      fromcurrent=True, transition=dict(duration=160))]),
                dict(label='❚❚ Pause', method='animate',
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')]),
            ])],
        sliders=[dict(active=0, y=-0.06, x=0.14, len=0.84, currentvalue=dict(prefix='Year: ', font=dict(size=14)),
            steps=[dict(label=str(int(yr)), method='animate',
                        args=[[str(int(yr))], dict(mode='immediate',
                              frame=dict(duration=0, redraw=True), transition=dict(duration=0))])
                   for yr in years])],
    )
    return fig

def fig_capacity():
    d = df_c[['year','capacity_total_mw','capacity_thermal_mw','capacity_hydro_mw']].dropna(subset=['capacity_total_mw'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d['year'], y=d['capacity_thermal_mw']/1000, name='Thermal (gas/coal)',
                             stackgroup='one', mode='none', fillcolor=COLORS['gas']))
    fig.add_trace(go.Scatter(x=d['year'], y=d['capacity_hydro_mw']/1000, name='Hydro',
                             stackgroup='one', mode='none', fillcolor=COLORS['hydro']))
    fig.add_trace(go.Scatter(x=d['year'], y=d['capacity_total_mw']/1000, name='Total installed',
                             line=dict(color='#111827', width=2), mode='lines'))
    fig.update_layout(template='plotly_white', height=400, margin=dict(l=50,r=20,t=50,b=40),
                      title='Installed capacity (nameplate power), GW', yaxis_title='GW',
                      xaxis_title='Year', hovermode='x unified')
    return fig

def fig_gas_balance():
    d = df_c[['year','gas_self_sufficiency_pct']].dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d['year'], y=d['gas_self_sufficiency_pct'], mode='lines+markers',
                             line=dict(color=COLORS['gas'], width=2.5), name='Gas self-sufficiency'))
    fig.add_hline(y=100, line=dict(dash='dot', color='grey'),
                  annotation_text='100% = production meets demand', annotation_position='top right')
    fig.update_layout(template='plotly_white', height=380, margin=dict(l=50,r=20,t=50,b=40),
                      title='Gas self-sufficiency (domestic production ÷ consumption), %',
                      yaxis_title='%', xaxis_title='Year', hovermode='x unified')
    return fig

def fig_sectors_2024():
    s = pd.read_csv(DATA / 'uzstat_electricity_by_sector_2024.csv')
    rows = s[s['sector_en'].isin(['Industry — total','Households (residential)','Agriculture',
                                  'Commercial & government services','Transport — total',
                                  'Construction','Unspecified other'])].copy()
    rows = rows.sort_values('electricity_twh', ascending=True)
    fig = go.Figure(go.Bar(
        y=rows['sector_en'].str.replace('Industry — total','Industry').str.replace(' — total',''),
        x=rows['electricity_twh'], orientation='h', marker_color='#0d4d7a',
        text=[f'{v:.1f} TWh ({p:.1f}%)' for v,p in zip(rows['electricity_twh'], rows['share_of_total_pct'])],
        textposition='auto'))
    fig.update_layout(template='plotly_white', height=400, margin=dict(l=180,r=30,t=50,b=40),
                      title='Final electricity consumption by sector — 2024 (UzStat balance)',
                      xaxis_title='TWh', hovermode='y unified')
    return fig

def fig_tariffs():
    t = pd.read_csv(DATA / 'tariff_history_uzb.csv')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t['year'], y=t['residential_uzs_kwh'], name='Residential',
                             mode='lines+markers', line=dict(color='#0d9488', width=2.5)))
    fig.add_trace(go.Scatter(x=t['year'], y=t['industrial_uzs_kwh'], name='Industrial',
                             mode='lines+markers', line=dict(color='#dc2626', width=2.5)))
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=50,r=20,t=50,b=40),
                      title='Nominal end-user electricity tariffs, UZS/kWh',
                      yaxis_title='UZS/kWh', xaxis_title='Year', hovermode='x unified')
    return fig

def fig_climate():
    c = pd.read_csv(DATA / 'climate_uzb_national_annual.csv')
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(go.Scatter(x=c['year'], y=c['cdd24_natl'], name='Cooling degree-days (CDD)',
                             line=dict(color='#dc2626', width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=c['year'], y=c['hdd18_natl'], name='Heating degree-days (HDD)',
                             line=dict(color='#1e3a8a', width=2)), secondary_y=True)
    fig.update_yaxes(title_text='CDD (°C·days, base 24°C)', secondary_y=False)
    fig.update_yaxes(title_text='HDD (°C·days, base 18°C)', secondary_y=True)
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=50,r=50,t=50,b=40),
                      title='Climate stress on demand — degree-days', xaxis_title='Year',
                      hovermode='x unified')
    return fig

def fig_intensity():
    d = pd.read_csv(DATA / 'demand_drivers_panel_v2.csv')
    d = d.dropna(subset=['cons_twh','wb_gdp_const2015_bn_usd'])
    d = d[d['wb_gdp_const2015_bn_usd'] > 0]
    intensity = d['cons_twh'] * 1e9 / (d['wb_gdp_const2015_bn_usd'] * 1e9)  # kWh per constant-2015 USD
    fig = go.Figure(go.Scatter(x=d['year'], y=intensity, mode='lines+markers',
                               line=dict(color='#6b21a8', width=2.5), name='Electricity intensity'))
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=50,r=20,t=50,b=40),
                      title='Electricity intensity of GDP (kWh per constant-2015 US$)',
                      yaxis_title='kWh / 2015 US$', xaxis_title='Year', hovermode='x unified')
    return fig

def fig_corr():
    d = pd.read_csv(DATA / 'demand_drivers_panel_v2.csv')
    pairs = [('industry_va_const2015_usd','Industry value-added'),
             ('services_va_const2015_usd','Services value-added'),
             ('gdp_pc_const2015_usd','GDP per capita'),
             ('wb_population','Population'),
             ('cdd24_natl','Cooling degree-days')]
    target = d['elec_consumption_twh'].fillna(d['cons_twh'])
    rows = []
    for col, label in pairs:
        if col in d.columns:
            sub = pd.concat([target, d[col]], axis=1).dropna()
            if len(sub) > 5:
                rows.append((label, float(sub.iloc[:,0].corr(sub.iloc[:,1]))))
    rows.sort(key=lambda r: r[1])
    fig = go.Figure(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation='h',
                           marker_color='#0d4d7a', text=[f'{r[1]:.2f}' for r in rows], textposition='auto'))
    fig.update_layout(template='plotly_white', height=340, margin=dict(l=170,r=30,t=50,b=40),
                      title='Correlation of demand with each driver (Pearson r, levels)',
                      xaxis_title='Pearson r', xaxis_range=[0,1], hovermode='y unified')
    return fig

def fig_planb():
    p = pd.read_csv(DATA / 'planb_nuclear_sensitivity.csv')
    p = p[p['commission_year']==2032].drop_duplicates('capacity_mw').sort_values('capacity_mw')
    fig = go.Figure(go.Bar(x=[f'{m/1000:.1f} GW' for m in p['capacity_mw']],
                           y=p['re_plus_nuclear_share_2040'], marker_color=COLORS['nuclear'],
                           text=[f'{v:.1f}%' for v in p['re_plus_nuclear_share_2040']], textposition='outside'))
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=50,r=20,t=50,b=40),
                      title='Plan B — low-carbon share in 2040 vs nuclear capacity (Govt scenario)',
                      yaxis_title='RE + nuclear share, %', xaxis_title='Nuclear capacity commissioned',
                      yaxis_range=[55,85])
    return fig

def fig_deficit():
    dd = pd.read_csv(DATA / 'investment_signal_deficit.csv')
    g = dd[dd['scenario']=='Government'].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g['year'], y=g['demand_w_losses_twh'], name='Demand + grid losses',
                             line=dict(color='#111827', width=2.5)))
    fig.add_trace(go.Scatter(x=g['year'], y=g['demand_w_losses_twh']+g['deficit_upper80'],
                             name='Upper-80% stress band', line=dict(width=0, color='#dc2626'),
                             mode='lines'))
    fig.add_trace(go.Scatter(x=g['year'], y=g['demand_w_losses_twh'], line=dict(width=0),
                             fill='tonexty', fillcolor='rgba(220,38,38,0.12)', showlegend=False))
    flagged = g[g['flag']=='DEFICIT']
    fig.add_trace(go.Scatter(x=flagged['year'], y=flagged['demand_w_losses_twh'], mode='markers',
                             name='Deficit-flagged year', marker=dict(symbol='x', size=10, color='#dc2626')))
    fig.update_layout(template='plotly_white', height=400, margin=dict(l=50,r=20,t=50,b=40),
                      title='Supply-adequacy stress — demand incl. losses + 80% uncertainty band',
                      yaxis_title='TWh', xaxis_title='Year', hovermode='x unified')
    return fig

def fig_capex():
    t = pd.read_csv(DATA / 'investment_opportunity_table.csv')
    t = t[t['Capex (USD bn)'].astype(str).str.match(r'^[0-9.]+$')].copy()
    t['capex'] = t['Capex (USD bn)'].astype(float)
    t = t.sort_values('capex')
    cat = t['ILF category'].str.replace(r'^\d+\.\s*','', regex=True)
    fig = go.Figure(go.Bar(y=cat, x=t['capex'], orientation='h', marker_color='#16a34a',
                           text=[f'${v:.1f} bn' for v in t['capex']], textposition='auto'))
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=200,r=40,t=50,b=40),
                      title='Capital requirement by programme, 2024–2040 (USD bn)',
                      xaxis_title='USD billion', hovermode='y unified')
    return fig

app.layout = html.Div(style={'fontFamily':'Inter,system-ui,sans-serif','background':'#fafafa','margin':0}, children=[
    html.Div(className='app-header', style=HEADER_STYLE, children=[
        html.H1('🇺🇿 Uzbekistan — Power Sector Transition Tracker', style={'margin':0,'fontSize':'24px'}),
        html.P(['Capstone Project · Farangiz Jurakhonova · CEU × ILF Consulting Engineers · ',
                html.Span(f'Forecast winner: {WINNER}', style={'fontWeight':600})],
               style={'margin':'6px 0 0','opacity':0.9,'fontSize':'13px'}),
    ]),
    html.Div(className='app-grid', children=[
        # Sidebar with scenario controls
        html.Div(className='sidebar', children=[
            html.Div(className='sidebar-controls', children=[
                html.Div(children=[
                    html.Div(style=LABEL, children='Scenario'),
                    dcc.RadioItems(id='scenario', value='Government',
                                   options=[{'label': s, 'value': s} for s in ['BAU','Government','Accelerated']],
                                   labelStyle={'display':'block','padding':'4px 0'}),
                ]),
                html.Div(children=[
                    html.Div(style=LABEL, children='Plan B — Nuclear toggle'),
                    dcc.Checklist(id='nuclear-on', options=[{'label':' Include nuclear','value':'on'}],
                                  value=[], labelStyle={'display':'block','padding':'4px 0'}),
                ]),
                html.Div(children=[
                    html.Div(style=LABEL, children='Nuclear capacity (MW)'),
                    dcc.Slider(id='nuc-cap', min=0, max=4000, step=400, value=1200,
                               marks={0:'0', 1200:'1.2 GW', 2400:'2.4 GW', 3600:'3.6 GW'}),
                ]),
                html.Div(children=[
                    html.Div(style=LABEL, children='Commission year'),
                    dcc.Slider(id='nuc-year', min=2030, max=2034, step=1, value=2032,
                               marks={2030:'30', 2032:'32', 2034:'34'}),
                ]),
            ]),
            html.Div(className='sidebar-nav', children=[
                html.Div(style={**LABEL,'marginTop':'24px'}, children='Sections'),
                html.Ul(style={'listStyle':'none','padding':0,'margin':0,'fontSize':'13px'}, children=[
                    html.Li(html.A('Country snapshot',        href='#snap', className='nav-link')),
                    html.Li(html.A('① Power-system landscape', href='#nb02', className='nav-link')),
                    html.Li(html.A('② Supply-side drivers',    href='#nb03', className='nav-link')),
                    html.Li(html.A('③ Demand drivers',         href='#nb04', className='nav-link')),
                    html.Li(html.A('④ Statistical structure',  href='#nb05', className='nav-link')),
                    html.Li(html.A('⑤ Demand forecast',        href='#demand', className='nav-link')),
                    html.Li(html.A('⑥ Generation mix',         href='#mix', className='nav-link')),
                    html.Li(html.A('⑦ CO₂ emissions',          href='#co2', className='nav-link')),
                    html.Li(html.A('⑧ Investment & deficits',  href='#invest', className='nav-link')),
                    html.Li(html.A('Regional map',            href='#map', className='nav-link')),
                    html.Li(html.A('Model scoreboard',        href='#methods', className='nav-link')),
                    html.Li(html.A('Glossary',                href='#glossary', className='nav-link')),
                ]),
            ]),
        ]),
        # Main
        html.Div(className='main', children=[
            html.Section(id='snap', children=[
                html.H2('Country snapshot'),
                html.Div(id='kpi-cards', style={'display':'grid','gridTemplateColumns':'repeat(auto-fit,minmax(200px,1fr))','gap':'12px','marginBottom':'18px'}),
            ]),

            # ── ① NB02 — Power-system landscape + ANIMATION ──────────────
            html.Section(id='nb02', children=[
                html.H2('① The historical growth of the power sector (animated)'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Press ', html.B('▶ Play'), ' to watch Uzbekistan’s generation fleet (the set of power '
                         'plants that actually produce electricity) grow year by year. Each bar is the energy '
                         '(measured in TWh — terawatt-hours, where 1 TWh powers roughly 100,000 homes for a year) '
                         'generated by one source.'),
                    static_graph(fig_growth_animation()),
                    takeaway('Two speeds of history: a flat, gas-dominated plateau from 1990 to ~2018, then a sharp '
                             'post-2018 surge as the 2018–2019 renewable-energy laws (PP-4422 and the foreign-investment '
                             'framework) took hold — solar rose roughly 6-fold and wind by two orders of magnitude into 2024.'),
                    narr('Through the whole period natural gas (methane burned in turbines) supplies the overwhelming '
                         'majority of power — about 78% of the 72.2 TWh generated in 2023, rising to roughly 82 TWh total '
                         'output in 2024 (a ~10% one-year jump). Hydro (electricity from falling water) is the historic '
                         'second source; solar (photovoltaic panels) and wind only become visible on the right edge of the '
                         'animation. Non-hydro renewables still reached only ~5.8% of generation in 2024, against the legislated '
                         'target of at least 25% renewables by 2030 (Presidential Decree PP-4422).'),
                    ru_box([
                        'Две скорости истории: застой 1990–2018 (генерация почти не растёт и держится на газе) и рывок '
                        'после законов 2018–2019 годов о возобновляемой энергетике.',
                        'Природный газ остаётся доминирующим источником — около 78% из 72,2 ТВт·ч в 2023 году; в 2024 году '
                        'выработка выросла примерно до 82 ТВт·ч (+10% за год).',
                        'Солнечная генерация выросла примерно в 6 раз, ветровая — на два порядка к 2024 году, однако доля '
                        'невозобновляемой гидрогенерации ВИЭ составила лишь около 5,8% при цели не менее 25% к 2030 году.',
                    ]),
                ]),
            ]),

            # ── ② NB03 — Supply-side drivers ─────────────────────────────
            html.Section(id='nb03', children=[
                html.H2('② Supply-side drivers — capacity, gas and carbon'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Installed capacity (nameplate power — the maximum a plant could deliver, in GW = gigawatts) '
                         'roughly doubled from ~12.5 GW around 2010 to ~21 GW in 2024. To hit the official 2030 target the '
                         'system must add about 2.89 GW of renewables every year for six years — a build rate the country '
                         'has never sustained.'),
                    static_graph(fig_capacity()),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    narr('Gas self-sufficiency (domestic production divided by domestic consumption) slipped below 100% '
                         'around 2018: Uzbekistan now imports gas, chiefly in winter. Net gas exports have been falling by '
                         'about 1.10 bcm (billion cubic metres) per year, while coal use has grown at roughly +10.5% a year '
                         'off a small base.'),
                    static_graph(fig_gas_balance()),
                    takeaway('Power-sector carbon intensity (CO₂ emitted per unit of electricity) fell from ~800 gCO₂/kWh '
                             'before 2018 to 668 gCO₂/kWh in 2023 as newer gas plants replaced older ones; economy-wide CO₂ '
                             'reached 148.5 Mt in 2024 (4.09 tonnes per person).'),
                    ru_box([
                        'Установленная мощность выросла примерно с 12,5 ГВт (2010) до около 21 ГВт (2024); для цели 2030 '
                        'требуется вводить около 2,89 ГВт ВИЭ ежегодно в течение шести лет.',
                        'Самообеспеченность газом опустилась ниже 100% около 2018 года — страна стала импортёром газа зимой; '
                        'чистый экспорт газа снижается примерно на 1,10 млрд м³ в год.',
                        'Углеродоёмкость электроэнергетики снизилась с ~800 до 668 гCO₂/кВт·ч (2023); выбросы экономики — '
                        '148,5 млн т в 2024 году, или 4,09 т на человека.',
                    ]),
                ]),
            ]),

            # ── ③ NB04 — Demand drivers ──────────────────────────────────
            html.Section(id='nb04', children=[
                html.H2('③ What drives electricity demand'),
                html.Div(style=CARD_STYLE, children=[
                    narr('In 2024 industry (factories, mining, metallurgy) took 40% of final electricity, households 24.9% '
                         'and agriculture 14.6%. Total demand grew from 48.9 TWh in 1990 to 73.4 TWh in 2024 (+50%, or +68% '
                         'on the bridged series that splices gaps between data sources).'),
                    static_graph(fig_sectors_2024()),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    narr('Income elasticity (how strongly demand responds to income) is β = 0.473 — a 1% rise in GDP per '
                         'capita lifts electricity use by about 0.47%. Per-capita consumption rose from 1,782 kWh (2018) to '
                         '2,059 kWh (2023). Heat matters too: each extra cooling degree-day (CDD — a measure of how hot and '
                         'for how long) adds about 0.027% to demand.'),
                    static_graph(fig_climate()),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    narr('Real (inflation-adjusted) tariffs actually fell from 201.7 to 115.4 UZS/kWh between 2017 and 2023 '
                         'before the April 2024 reform, which roughly doubled nominal prices (residential 450, industrial '
                         '1,000 UZS/kWh). Cheap power plus rapid growth made the economy steadily more efficient: electricity '
                         'intensity of GDP fell from ~18.9 to ~4.5 kWh per constant-2015 dollar since 2000.'),
                    static_graph(fig_tariffs()),
                    static_graph(fig_intensity()),
                    ru_box([
                        'Структура спроса 2024: промышленность 40%, домохозяйства 24,9%, сельское хозяйство 14,6%; общий '
                        'спрос вырос с 48,9 ТВт·ч (1990) до 73,4 ТВт·ч (2024).',
                        'Эластичность спроса по доходу β = 0,473; потребление на душу выросло с 1 782 до 2 059 кВт·ч '
                        '(2018→2023); каждый градусо-день охлаждения добавляет около 0,027% к спросу.',
                        'Реальные тарифы снижались (201,7→115,4 сум/кВт·ч, 2017–2023) до реформы апреля 2024 года; '
                        'электроёмкость ВВП упала с ~18,9 до ~4,5 кВт·ч на доллар (2015) с 2000 года.',
                    ]),
                ]),
            ]),

            # ── ④ NB05 — Statistical structure ───────────────────────────
            html.Section(id='nb05', children=[
                html.H2('④ Statistical structure of the demand series'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Before forecasting, the demand series is screened for statistical structure. In levels, demand '
                         'correlates most strongly with industrial output, services, GDP per capita and cooling demand '
                         '(Pearson r — a number from 0 to 1 measuring how tightly two series move together).'),
                    static_graph(fig_corr()),
                    takeaway('Log-demand is integrated of order one (I(1) — it has a trend and must be differenced before '
                             'modelling). The Engle–Granger cointegration test (−2.654, p = 0.403) finds no long-run '
                             'equilibrium link, and Granger causality is inconclusive — but with only ~30 annual points '
                             'these tests are statistically under-powered (too little data to detect an effect), so they '
                             'guide model choice rather than settle it.'),
                    ru_box([
                        'В уровнях спрос сильнее всего коррелирует с промышленностью, услугами, ВВП на душу и охлаждением; '
                        'логарифм спроса интегрирован первого порядка I(1).',
                        'Тест коинтеграции Энгла–Грейнджера (−2,654; p = 0,403) не выявил долгосрочной связи, причинность '
                        'по Грейнджеру неинформативна.',
                        'При выборке всего ~30 годовых наблюдений эти тесты обладают низкой мощностью — они направляют выбор '
                        'модели, но не являются окончательными.',
                    ]),
                ]),
            ]),

            html.Section(id='demand', children=[
                html.H2('⑤ Electricity demand forecast'),
                html.Div(style=CARD_STYLE, children=[
                    narr('The deployed forecaster is a Bayesian Ridge regression (a linear model with automatic '
                         'shrinkage — it pulls weak coefficients toward zero to avoid over-fitting a short series) '
                         'trained on a pooled four-country Central-Asia panel. On the honest 2019–2023 hold-out '
                         '(years hidden from the model) it scores ~6% MAPE (mean absolute percentage error — the '
                         'average size of its mistakes). It projects ~86 TWh in 2030 (range 76.7–95.3) and ~124 TWh by 2040.'),
                    graph('demand-chart'),
                    ru_box([
                        'Прогноз построен байесовской гребневой регрессией на объединённой панели четырёх стран '
                        'Центральной Азии; ошибка на контрольной выборке 2019–2023 — около 6% MAPE.',
                        'Центральный сценарий: около 86 ТВт·ч к 2030 году (диапазон 76,7–95,3) и около 124 ТВт·ч к 2040 году.',
                    ]),
                ]),
            ]),
            html.Section(id='mix', children=[
                html.H2('⑥ Generation mix by scenario'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Use the sidebar to switch scenario. Renewable share of generation in 2030 ranges from 43.1% '
                         '(Business-as-usual) through 58.4% (Government target) to 70.8% (Accelerated). The gap between '
                         'them is almost entirely how fast solar and wind are built.'),
                    graph('mix-chart')]),
                html.Div(style=CARD_STYLE, children=[graph('re-share-chart')]),
            ]),
            html.Section(id='co2', children=[
                html.H2('⑦ CO₂ emissions'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Power-sector CO₂ in 2030 depends sharply on the build path: 36.6 Mt (BAU), 22.9 Mt (Government) '
                         'or 16.1 Mt (Accelerated). The decisive lever is the gas emission factor (CO₂ per unit of gas '
                         'power), which falls from ~650 to ~380 gCO₂/kWh as efficient combined-cycle plants replace old turbines.'),
                    graph('co2-chart'),
                    ru_box([
                        'Выбросы CO₂ электроэнергетики в 2030 году: 36,6 млн т (инерционный сценарий), 22,9 (целевой), '
                        '16,1 (ускоренный).',
                        'Ключевой фактор — снижение удельных выбросов газовой генерации с ~650 до ~380 гCO₂/кВт·ч при '
                        'переходе на парогазовые установки.',
                    ]),
                ]),
            ]),
            html.Section(id='invest', children=[
                html.H2('⑧ Investment signals, deficits and Plan B'),
                html.Div(style=CARD_STYLE, children=[
                    narr('Crossing forecast demand (plus grid losses) against planned supply flags adequacy stress: '
                         'the model marks deficit risk in 2026, 2027, 2029, 2030, 2032, 2036, 2038 and 2040. The shaded '
                         'band is the upper-80% uncertainty (an eight-in-ten worst-case margin).'),
                    static_graph(fig_deficit()),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    narr('Meeting the targets implies large, staged capital across five programmes — generation build '
                         'dominates at $28.4 bn, with grid modernisation, storage, efficiency and advisory alongside.'),
                    static_graph(fig_capex()),
                    graph('invest-chart'),
                ]),
                html.Div(style=CARD_STYLE, children=[
                    narr('Plan B is a parametric nuclear sensitivity (a what-if, not a forecast): commissioning 1.2–3.6 GW '
                         'of reactors lifts the 2040 low-carbon share from 60% (no nuclear) to 66.6%, 73.3% or 79.9%. '
                         'Toggle it live in the sidebar to see the effect on the mix and CO₂ charts above.'),
                    static_graph(fig_planb()),
                    ru_box([
                        'Дефицит мощности прогнозируется в 2026, 2027, 2029, 2030, 2032, 2036, 2038 и 2040 годах; '
                        'самообеспеченность газом ниже 100% с ~2018 года, потери в сетях хронически высоки.',
                        'Капитальные затраты по пяти программам: генерация $28,4 млрд, модернизация сетей, накопители, '
                        'энергоэффективность и консультационное сопровождение.',
                        'План Б (параметрический сценарий АЭС): ввод 1,2–3,6 ГВт повышает долю низкоуглеродной генерации '
                        'в 2040 году с 60% до 66,6%, 73,3% или 79,9% соответственно.',
                    ]),
                ]),
            ]),
            html.Section(id='map', children=[
                html.H2('Regional renewable map'),
                html.Div(style=CARD_STYLE, children=[graph('oblast-map')]),
            ]),
            html.Section(id='methods', children=[
                html.H2('Methodology — model scoreboard'),
                html.Div(style=CARD_STYLE, children=[
                    html.P('Six forecasting specifications scored on one honest ex-ante out-of-sample test: drivers are forecast (not given), '
                           'the demand lag is fed recursively, and the 2019–2023 hold-out is predicted with no look-ahead — directly comparable to ARIMA. '
                           'The conditional (observed-driver) MAPE is shown only as a labelled reference. Headline finding: only the cross-country pooled '
                           'Central-Asia panels achieve positive ex-ante R² through the 2019–2023 structural break (pooled Ridge CV-α: 6.08% MAPE, R²≈+0.10); '
                           'every single-country specification has negative ex-ante R². Ridge α is CV-selected by expanding-window, train-only cross-validation, '
                           'never tuned on the hold-out.',
                           style={'color':'#374151','fontSize':'14px','lineHeight':1.5}),
                    dcc.Graph(id='scoreboard-chart', config={'displayModeBar': False}),
                ]),
            ]),
            html.Section(id='glossary', children=[
                html.H2('Glossary — terms used in this dashboard'),
                html.P('Quick reference for non-technical readers. Hover any KPI card for the same definitions inline.',
                       style={'color':'#6b7280','fontSize':'14px','marginBottom':'14px'}),
                html.Div(id='glossary-grid', style={'display':'grid','gridTemplateColumns':'repeat(auto-fit,minmax(360px,1fr))','gap':'14px'}),
            ]),
        ]),
    ]),
    html.Footer(style={'padding':'20px 36px','color':'#6b7280','fontSize':'12px','borderTop':'1px solid #e5e7eb'},
                children=['Data: IEA, IRENA, World Bank, StatSUZ, EDB 2026. Forecasts: notebooks 03–06. ',
                         html.Span('Use the sidebar to change scenario or toggle Plan B nuclear — all charts update.', style={'fontStyle':'italic'})]),
])

# ── Glossary data ─────────────────────────────────────────────────────
GLOSSARY = [
    ('Units', [
        ('TWh', 'Terawatt-hour. A unit of energy. 1 TWh = 1 billion kWh = enough to power ~100,000 average households for a year.'),
        ('GW / MW', 'Gigawatt / Megawatt. Units of *power* (capacity). 1 GW = 1,000 MW = 1 million kW. A typical gas plant is 200-800 MW; a wind turbine is 3-6 MW.'),
        ('bcm', 'Billion cubic metres — standard unit for natural gas volumes. Uzbekistan consumed ~52 bcm/yr in 2023; ~17 bcm of that went into electricity generation.'),
        ('gCO₂/kWh', 'Grams of CO₂ emitted per kilowatt-hour of electricity generated. World average ~475. Modern gas CCGT ~380; coal ~950; renewables ~0.'),
    ]),
    ('Scenarios used in this tracker', [
        ('BAU (Business-As-Usual)', 'Current build pace continues. Reaches ~60% of the official 2030 renewable target — what is most likely if no policy acceleration occurs.'),
        ('Government Target', 'Meets the official April 2025 targets exactly: 12 GW solar, 8 GW wind, 4.7 GW hydro by 2030 (≈27 GW total RE). 54% renewable share is the stated headline.'),
        ('Accelerated', 'Stretch case — exceeds government targets by ~25%. Reaches 60%+ RE share by 2030; implies a faster build than any country has historically achieved at this scale.'),
        ('Plan B (Nuclear overlay)', 'A *parametric* sensitivity scenario, NOT a baseline forecast. Lets you switch on a small modular reactor (SMR) and see how it would change the RE+nuclear share. Toggle in the left sidebar.'),
    ]),
    ('Power-sector concepts', [
        ('RE share / penetration', 'Share of total electricity generation that comes from renewables (hydro + solar + wind). Uzbekistan stands at ~10% in 2023; the legislated target is 40% by 2030, with 54% cited as a presidential aspiration.'),
        ('Capacity factor (CF)', 'How much of a plant\'s nameplate capacity it actually produces over a year. Assumed annual averages: solar 18%, wind 30%, hydro 36%, gas 55%, nuclear 85%.'),
        ('T&D losses', 'Transmission & Distribution losses — electricity lost between generation and the customer. Uzbekistan ~16% on a like-for-like post-2001 basis (17.8% in 2023; regional median ~8%); a chronic grid-investment signal. The 9% figure is the 2030 policy-reduction TARGET, not the realized rate.'),
        ('Gas self-sufficiency', 'Domestic gas production ÷ consumption. Below 100% means Uzbekistan must import (mainly winter); fell below 100% around 2018.'),
    ]),
    ('Forecasting terms', [
        ('MAPE', 'Mean Absolute Percentage Error. The average % error of a forecast. Lower is better. Lewis (1982) bands: <10% "highly accurate", 10-20% "good", 20-50% "reasonable".'),
        ('Cross-validation (CV)', 'A way to test model accuracy fairly by repeatedly fitting on past data and predicting the next chunk. We use 8 "expanding window" splits with a 3-year forecast horizon each.'),
        ('Bootstrap CI (80% / 95%)', 'Confidence interval from resampling the model\'s historical residuals 1,000 times. "80% CI" means we expect the true value to fall inside this band 80% of the time.'),
        ('Hold-out test', 'A single chunk of recent data (2019-2023 in our case) kept aside and not used for training. Scores on this hold-out are the headline accuracy metric.'),
    ]),
    ('Models in the bench', [
        ('Prophet', 'Facebook/Meta\'s time-series tool. Decomposes a series into trend + seasonality + holidays. A benchmark model only — NOT the deployed forecaster. Its flexible changepoints suit the post-2018 demand regime shift, but on the ex-ante hold-out it trailed the deployed Bayesian-ridge driver model (Notebook 07).'),
        ('ARIMA / SARIMAX', 'Classical statistical models — predict next year from past values (and past errors). SARIMAX adds external variables (e.g. GDP, population). Order chosen by AICc.'),
        ('Holt-Winters / ETS', 'Exponential smoothing — gives recent observations more weight. Simple and robust to small samples; one of the benchmark models, not the deployed forecaster.'),
        ('Theta method', 'Decomposes the series and recombines — a classic M3-competition method. One of the benchmark models, not the deployed forecaster.'),
        ('OLS first-difference', 'Linear regression on year-on-year changes (not levels). Avoids "spurious regression" on non-stationary series (Granger & Newbold 1974).'),
        ('Bayesian Ridge (deployed) / Gradient Boosting', 'Regularised linear regression on macro drivers (GDP, population, prior-year demand) with automatic shrinkage that guards against overfitting the short annual series. Bayesian Ridge is the DEPLOYED demand forecaster (Notebook 07): ex-ante hold-out ~9-10% MAPE single-country, ~6% on the pooled 4-country Central-Asia panel. Plain Ridge and Gradient Boosting were tested as benchmarks but tend to overfit short annual data.'),
    ]),
    ('Acronyms — institutions', [
        ('IEA', 'International Energy Agency (Paris). Publishes country profiles and energy balances; primary data source.'),
        ('IRENA', 'International Renewable Energy Agency (Abu Dhabi). Publishes annual renewable capacity statistics.'),
        ('WB (World Bank)', 'World Bank Data360 — used for GDP, population, CO₂, T&D losses.'),
        ('EBRD / ADB / AIIB / IFC', 'European Bank for Reconstruction & Development / Asian Development Bank / Asian Infrastructure Investment Bank / International Finance Corporation — the main multilateral financiers active in Uzbek power.'),
        ('NEEA', 'National Energy Efficiency Agency of Uzbekistan — ILF\'s key advisory counterpart.'),
        ('MoE / MEF', 'Ministry of Energy / Ministry of Economy & Finance.'),
        ('StatSUZ', 'State Statistics Committee of Uzbekistan.'),
    ]),
    ('Acronyms — technologies & projects', [
        ('CCGT / OCGT', 'Combined-Cycle / Open-Cycle Gas Turbine. CCGT is the modern efficient gas plant (~55-60% efficiency, ~380 gCO₂/kWh). OCGT is older, less efficient (~30-35%, ~650 gCO₂/kWh). Uzbekistan\'s fleet is mostly OCGT/CHP today.'),
        ('PV', 'Photovoltaic — solar electricity from semiconductor panels.'),
        ('BESS', 'Battery Energy Storage System — lithium-ion battery installations that smooth out the variability of solar/wind. 2030 storage requirement is ~5 GWh under the Government scenario.'),
        ('SMR', 'Small Modular Reactor — the nuclear technology Uzbekistan is exploring with Rosatom at Jizzakh. Plan B overlay assumes 1.2-3.6 GW commissioned 2030-2034.'),
        ('PPP / IPP', 'Public-Private Partnership / Independent Power Producer — the contract structures used for ACWA Power, Masdar, EDF, Total Eren projects.'),
        ('PPA', 'Power Purchase Agreement — the long-term contract under which the offtaker (state utility) commits to buy power at a fixed tariff.'),
    ]),
    ('Geography', [
        ('Oblast', 'Russian/Uzbek term for "region" or "province". Uzbekistan has 12 oblasts + 1 autonomous republic (Karakalpakstan) + Tashkent city.'),
        ('Karakalpakstan', 'Westernmost region — sparsely populated, highest wind technical potential (4.4 TWh/yr). Site of ACWA Power\'s 1.6 GW wind build (2026).'),
        ('Bukhara / Navoi / Kashkadarya', 'Western/southern provinces — highest solar irradiance (1,800-1,850 kWh/m²/yr). Most utility-scale solar PPAs sit here.'),
        ('Jizzakh', 'Central province — site of the SMR construction. Close to the Tashkent demand centre.'),
    ]),
]

# ── Callbacks ─────────────────────────────────────────────────────────
@app.callback(Output('glossary-grid','children'), Input('scenario','value'))
def render_glossary(_):
    cards = []
    for cat_name, terms in GLOSSARY:
        items = []
        for term, defn in terms:
            items.append(html.Div(style={'marginBottom':'10px'}, children=[
                html.Span(term, style={'fontWeight':600, 'color':'#0d4d7a', 'fontSize':'13px'}),
                html.Span(' — ' + defn, style={'fontSize':'13px', 'color':'#374151', 'lineHeight':1.45}),
            ]))
        cards.append(html.Div(style=CARD_STYLE, children=[
            html.H3(cat_name, style={'fontSize':'15px','margin':'0 0 10px','color':'#111827'}),
            *items,
        ]))
    return cards


def apply_overlay(scenario_name, nuclear_on, nuc_cap, nuc_year):
    sd = scenarios_fc.copy()
    if nuclear_on and 'on' in nuclear_on:
        sd = apply_nuclear(sd, nuc_cap, nuc_year)
    else:
        sd['gen_nuclear_twh'] = 0.0
        sd['re_plus_nuclear_share_pct'] = sd['re_share_pct']
    return sd[sd['scenario'] == scenario_name]

@app.callback(
    Output('kpi-cards', 'children'),
    Input('scenario', 'value'), Input('nuclear-on', 'value'),
    Input('nuc-cap', 'value'), Input('nuc-year', 'value'),
)
def update_kpis(scen, nuc_on, nuc_cap, nuc_year):
    sd = apply_overlay(scen, nuc_on, nuc_cap, nuc_year)
    latest = df_c[df_c['year'] == df_c['year'].max()].iloc[0]
    sd_2030 = sd[sd['year'] == 2030].iloc[0]
    co2_row = co2_fc[(co2_fc['scenario'] == scen) & (co2_fc['year'] == 2030)].iloc[0]
    demand_2030 = demand_fc.loc[demand_fc['year'] == 2030, 'demand_twh'].iat[0]

    def card(label, value, sub, color='#0d4d7a'):
        return html.Div(className='kpi-card', style={**CARD_STYLE, 'display':'flex','flexDirection':'column','gap':'4px'}, children=[
            html.Span(label, style={'fontSize':'11px','color':'#6b7280','textTransform':'uppercase','letterSpacing':'0.5px'}),
            html.Span(value, style={'fontSize':'26px','fontWeight':600,'color':color}),
            html.Span(sub, style={'fontSize':'12px','color':'#6b7280'}),
        ])
    return [
        card(f"Demand {int(latest['year'])}", f"{latest['elec_consumption_twh_bridged']:.1f} TWh",
             f"→ {demand_2030:.1f} TWh in 2030"),
        card(f"RE share 2030 ({scen})", f"{sd_2030['re_plus_nuclear_share_pct']:.1f}%",
             f"(RE only: {sd_2030['re_share_pct']:.1f}%) target 54%"),
        card(f"Power CO₂ 2030 ({scen})", f"{co2_row['co2_power_mt']:.1f} Mt",
             f"intensity {co2_row['co2_intensity_gco2_per_kwh']:.0f} gCO₂/kWh"),
        card("Plan B nuclear", f"{(nuc_cap if 'on' in (nuc_on or []) else 0)/1000:.1f} GW",
             f"from {nuc_year} @ 85% CF" if 'on' in (nuc_on or []) else "off"),
    ]

@app.callback(Output('demand-chart','figure'),
              Input('scenario','value'))
def update_demand(_):
    fig = go.Figure()
    y_h = df_c[['year','elec_consumption_twh_bridged']].dropna()
    fig.add_trace(go.Scatter(x=y_h['year'], y=y_h['elec_consumption_twh_bridged'], name='History',
                              mode='lines+markers', line=dict(color='#111827', width=2)))
    fig.add_trace(go.Scatter(x=demand_fc['year'], y=demand_fc['ci_hi95'], mode='lines',
                              line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=demand_fc['year'], y=demand_fc['ci_lo95'], mode='lines',
                              line=dict(width=0), fill='tonexty',
                              fillcolor='rgba(30,58,138,0.08)', name='95% CI'))
    fig.add_trace(go.Scatter(x=demand_fc['year'], y=demand_fc['ci_hi80'], mode='lines',
                              line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=demand_fc['year'], y=demand_fc['ci_lo80'], mode='lines',
                              line=dict(width=0), fill='tonexty',
                              fillcolor='rgba(30,58,138,0.18)', name='80% CI'))
    fig.add_trace(go.Scatter(x=demand_fc['year'], y=demand_fc['demand_twh'], name=f'★ {WINNER}',
                              line=dict(color='#111827', width=3)))
    fig.add_trace(go.Scatter(x=[2025,2026], y=[86.7/1.09, 90.0/1.09], mode='markers',
                              name='News-reported', marker=dict(symbol='star', size=14, color='#dc2626')))
    fig.add_vline(x=2023.5, line=dict(dash='dot', color='grey'))
    fig.update_layout(template='plotly_white', height=420, margin=dict(l=50,r=20,t=40,b=40),
                      title=f'Electricity demand 1990–2035 — winner: {WINNER}',
                      yaxis_title='TWh', xaxis_title='Year', hovermode='x unified')
    return fig

@app.callback(Output('mix-chart','figure'),
              Input('scenario','value'), Input('nuclear-on','value'),
              Input('nuc-cap','value'), Input('nuc-year','value'))
def update_mix(scen, nuc_on, nuc_cap, nuc_year):
    sd = apply_overlay(scen, nuc_on, nuc_cap, nuc_year)
    hist = df_c[['year','gen_gas_twh','gen_coal_twh','gen_hydro_twh','gen_solar_twh','gen_wind_twh']].fillna(0)
    sd_plot = sd.copy()
    sd_plot['gen_gas_twh']  = sd_plot['gen_thermal_twh'] * 0.88
    sd_plot['gen_coal_twh'] = sd_plot['gen_thermal_twh'] * 0.12
    if 'gen_nuclear_twh' not in sd_plot.columns: sd_plot['gen_nuclear_twh'] = 0.0
    fig = go.Figure()
    for src, col, name in [('gen_gas_twh','gas','Gas'),('gen_coal_twh','coal','Coal'),
                            ('gen_hydro_twh','hydro','Hydro'),('gen_solar_twh','solar','Solar'),
                            ('gen_wind_twh','wind','Wind'),('gen_nuclear_twh','nuclear','Nuclear')]:
        if src not in hist.columns: hist[src] = 0
        y_vals = pd.concat([hist[src], sd_plot[src]])
        x_vals = pd.concat([hist['year'], sd_plot['year']])
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, name=name, stackgroup='one', mode='none',
                                  fillcolor=COLORS[col]))
    fig.add_vline(x=2023.5, line=dict(dash='dot', color='grey'),
                   annotation_text='forecast →', annotation_position='top right')
    fig.update_layout(template='plotly_white', height=460, margin=dict(l=50,r=20,t=40,b=40),
                      title=f'Generation mix — {scen} scenario',
                      yaxis_title='TWh', xaxis_title='Year', hovermode='x unified')
    return fig

@app.callback(Output('re-share-chart','figure'),
              Input('scenario','value'), Input('nuclear-on','value'),
              Input('nuc-cap','value'), Input('nuc-year','value'))
def update_re(scen, nuc_on, nuc_cap, nuc_year):
    fig = go.Figure()
    re_h = df_c[['year','re_penetration_pct']].dropna()
    fig.add_trace(go.Scatter(x=re_h['year'], y=re_h['re_penetration_pct'], name='Historical',
                              line=dict(color='#111827', width=2), mode='lines+markers'))
    for sc in ['BAU','Government','Accelerated']:
        sd = apply_overlay(sc, nuc_on, nuc_cap, nuc_year)
        line_w = 3 if sc == scen else 1.5
        dash = None if sc == scen else 'dash'
        fig.add_trace(go.Scatter(x=sd['year'], y=sd['re_plus_nuclear_share_pct'],
                                  name=f'{sc} (RE+nuclear)', line=dict(color=COLORS[sc], width=line_w, dash=dash)))
        fig.add_trace(go.Scatter(x=sd['year'], y=sd['re_share_pct'],
                                  name=f'{sc} (RE only)', line=dict(color=COLORS[sc], width=1, dash='dot'),
                                  showlegend=(sc==scen)))
    fig.add_hline(y=54, line=dict(dash='dot', color='grey'),
                   annotation_text='2030 target 54%', annotation_position='top left')
    fig.add_vline(x=2023.5, line=dict(dash='dot', color='grey'))
    fig.update_layout(template='plotly_white', height=420, margin=dict(l=50,r=20,t=40,b=40),
                      title='Low-carbon share of generation — all scenarios',
                      yaxis_title='%', xaxis_title='Year', hovermode='x unified')
    return fig

@app.callback(Output('co2-chart','figure'), Input('scenario','value'))
def update_co2(_):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Power-sector CO₂ emissions','CO₂ intensity'))
    co2_h = df_c[['year','wb_co2_power_mt']].dropna()
    fig.add_trace(go.Scatter(x=co2_h['year'], y=co2_h['wb_co2_power_mt'], name='History',
                              line=dict(color='#111827', width=2), mode='lines+markers'), row=1, col=1)
    for sc in ['BAU','Government','Accelerated']:
        sd = co2_fc[co2_fc['scenario']==sc]
        fig.add_trace(go.Scatter(x=sd['year'], y=sd['co2_power_mt'], name=sc,
                                  line=dict(color=COLORS[sc], width=2, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=sd['year'], y=sd['co2_intensity_gco2_per_kwh'], name=f'{sc} int',
                                  line=dict(color=COLORS[sc], width=2, dash='dash'), showlegend=False), row=1, col=2)
    fig.update_yaxes(title_text='Mt CO₂/yr', row=1, col=1); fig.update_yaxes(title_text='gCO₂/kWh', row=1, col=2)
    fig.update_layout(template='plotly_white', height=420, margin=dict(l=50,r=20,t=60,b=40),
                      title='Power-sector carbon footprint', hovermode='x unified')
    return fig

@app.callback(Output('invest-chart','figure'), Input('scenario','value'))
def update_invest(scen):
    pivot = invest_fc.pivot(index='tech', columns='scenario', values='capex_bn_usd').fillna(0)
    pivot = pivot.reindex(['solar','wind','hydro','thermal','storage','transmission'])
    fig = go.Figure()
    for sc in ['BAU','Government','Accelerated']:
        if sc not in pivot.columns: continue
        opacity = 1.0 if sc == scen else 0.45
        fig.add_trace(go.Bar(name=sc, x=pivot.index, y=pivot[sc], marker_color=COLORS[sc],
                              opacity=opacity, text=[f'${v:.1f}bn' for v in pivot[sc]], textposition='outside'))
    fig.update_layout(template='plotly_white', barmode='group', height=440,
                      margin=dict(l=50,r=20,t=40,b=40),
                      title='Capex by technology & scenario (2024–2035, USD bn)',
                      yaxis_title='USD billion', xaxis_title='Technology', hovermode='x unified')
    return fig

@app.callback(Output('oblast-map','figure'), Input('scenario','value'))
def update_map(_):
    fig = go.Figure()
    tech_colors = {'solar':'#facc15','wind':'#10b981','hydro':'#0891b2'}
    for tech, color in tech_colors.items():
        sub = oblasts[oblasts['dominant']==tech]
        fig.add_trace(go.Scattergeo(
            lon=sub['lon'], lat=sub['lat'], text=sub['oblast']+'<br>'+sub['projects'],
            marker=dict(size=sub['total_re_mw']/40+8, color=color, line=dict(color='black',width=1)),
            name=tech.title(), hovertemplate='<b>%{text}</b><extra></extra>'))
    fig.update_layout(template='plotly_white', height=480, margin=dict(l=10,r=10,t=40,b=10),
                      title='Renewables by oblast — bubble size ∝ total RE capacity',
                      geo=dict(scope='asia', center=dict(lat=41.5, lon=64.5), projection_scale=4.5,
                               showland=True, landcolor='#fafafa', showcountries=True,
                               countrycolor='#cbd5e1', showsubunits=True))
    return fig

@app.callback(Output('scoreboard-chart','figure'), Input('scenario','value'))
def update_scoreboard(_):
    df = scoreboard.sort_values('exante_mape%').copy()
    # Hero = specs that beat a naive forecast (positive ex-ante R²) — only the pooled CA panels do
    bar_colors = ['#1d4ed8' if r2 > 0 else '#9ca3af' for r2 in df['exante_r2']]
    fig = go.Figure()
    # Headline metric: honest ex-ante MAPE (drivers forecast, demand lag recursive, no look-ahead)
    fig.add_trace(go.Bar(
        y=df['model'], x=df['exante_mape%'], orientation='h', marker_color=bar_colors,
        name='Ex-ante MAPE (out-of-sample)',
        text=[f'{v:.1f}%' for v in df['exante_mape%']], textposition='auto',
        customdata=df[['exante_r2', 'conditional_mape% [ref]', 'basis', 'n_train']].to_numpy(),
        hovertemplate=('<b>%{y}</b><br>Ex-ante MAPE: %{x:.2f}%<br>'
                       'Ex-ante R²: %{customdata[0]:.2f}<br>'
                       'Conditional MAPE (ref): %{customdata[1]:.2f}%<br>'
                       'Basis: %{customdata[2]} • n_train=%{customdata[3]}<extra></extra>'),
    ))
    # Reference only: conditional (observed-driver) MAPE — NOT comparable to ARIMA, shown for context
    fig.add_trace(go.Scatter(
        y=df['model'], x=df['conditional_mape% [ref]'], mode='markers',
        name='Conditional MAPE (ref — observed drivers)',
        marker=dict(symbol='diamond-open', size=11, color='#6b7280', line=dict(width=1.5)),
        hovertemplate='<b>%{y}</b><br>Conditional MAPE (reference): %{x:.2f}%<extra></extra>',
    ))
    fig.add_vline(x=10, line=dict(dash='dot', color='grey'),
                   annotation_text='Lewis 10% (MAPE only)', annotation_position='top right')
    fig.update_layout(template='plotly_white', height=max(440, 70*len(df)),
                      margin=dict(l=300, r=20, t=84, b=40),
                      title='Forecasting scoreboard — <b>ex-ante</b> MAPE on UZB 2019–2023 hold-out<br>'
                            '<sub>Bars = honest ex-ante (drivers forecast, lag recursive) • ◇ = conditional MAPE (reference only)<br>'
                            'Blue = positive ex-ante R² (pooled Central-Asia panels) • Grey = negative ex-ante R² (single-country)</sub>',
                      xaxis_title='MAPE (%)', yaxis_title='',
                      legend=dict(orientation='h', y=-0.08, x=0.0))
    return fig

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('DASH_DEBUG', '1') == '1'
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    app.run(debug=debug, host=host, port=port)
