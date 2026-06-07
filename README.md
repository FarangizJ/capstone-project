---
title: Uzbekistan Power Sector Transition Tracker
emoji: 🇺🇿
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Uzbekistan — Power Sector Transition Tracker

Interactive Plotly Dash dashboard for the capstone project *Forecasting Uzbekistan's
Power-Sector Transition* (Farangiz Jurakhonova · CEU × ILF Consulting Engineers).

It surfaces the full analysis from notebooks 02–08 — the historical growth of the
generation fleet (animated), supply-side and demand-side drivers, the statistical
structure of demand, the Bayesian-Ridge demand forecast, scenario generation mix and
CO₂ paths, and the investment / supply-adequacy signals — with bilingual English +
Russian summaries throughout.

## Run locally

```bash
pip install -r dashboard/requirements.txt
cd dashboard && python app.py
# → http://127.0.0.1:8050
```

## Deploy on Hugging Face Spaces (free, persistent)

1. Create an account at <https://huggingface.co> and click **New Space**.
2. Owner = you, Space name = e.g. `uzbekistan-power-tracker`, **SDK = Docker**, visibility Public.
3. Push this repository to the Space's git remote:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/uzbekistan-power-tracker
   git push space main
   ```
   (Authenticate with a Hugging Face **write** access token when prompted.)
4. The Space builds from the root `Dockerfile` and serves on port 7860 (set by the
   `app_port` header above). First build takes a few minutes; the public URL is then live.

The `.dockerignore` keeps the image small: only `dashboard/` and `data/processed/*.csv`
are needed at runtime.

## Data sources

IEA, IRENA, World Bank Data360, StatSUZ (State Statistics Committee of Uzbekistan),
OWID, EDB. Forecasts from project notebooks 03–07. No figures are invented; every number
traces to a processed CSV in `data/processed/`.
