"""
Build the curated shortlist of UzStat SDMX files needed for the
electricity-demand model.

Cross-references:
  - scripts/uzstat_registry.py    (267 ID→title mappings)
  - data/processed/uzstat_clean/uzstat_full_manifest.csv  (618-file fingerprint)

Output: data/processed/uzstat_clean/SHORTLIST_for_analysis.csv with one row per
file that is needed for the model. Categorised by relevance (PRIMARY / STRONG /
POSSIBLE) and grouped by analytical purpose. The user reviews this before any
of the files are merged into the modelling pipeline.
"""
from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from uzstat_registry import REGISTRY

OUT = ROOT / 'data' / 'processed' / 'uzstat_clean'
MANIFEST_PATH = OUT / 'uzstat_full_manifest.csv'
SHORTLIST_PATH = OUT / 'SHORTLIST_for_analysis.csv'


def main():
    manifest = pd.read_csv(MANIFEST_PATH)
    print(f'Loaded manifest with {len(manifest)} files')

    # Attach registry info
    reg = pd.DataFrame([
        {'id': fid, 'title_en': t, 'category': c, 'relevance': r}
        for fid, (t, c, r) in REGISTRY.items()
    ])
    short = manifest.merge(reg, on='id', how='inner')

    # Keep only PRIMARY + STRONG + POSSIBLE; drop UNRELATED
    short = short[short['relevance'].isin(['PRIMARY', 'STRONG', 'POSSIBLE'])].copy()

    # Add modelling-purpose flag
    def purpose(row):
        cat = row['category']; rel = row['relevance']
        if cat == 'energy':
            return 'TARGET or PRIMARY ENERGY DRIVER (model spine)'
        if cat == 'gdp':
            return 'MACRO DRIVER (sectoral GDP / GVA)'
        if cat == 'demography':
            return 'POPULATION DRIVER'
        if cat == 'labour':
            return 'LABOUR DRIVER'
        if cat in ('prices',):
            return 'PRICE / TARIFF DRIVER (for elasticity)'
        if cat == 'investment':
            return 'INVESTMENT DRIVER (capacity buildout proxy)'
        if cat == 'construction':
            return 'CONSTRUCTION DRIVER (load growth proxy)'
        if cat == 'services':
            return 'SECTORAL ACTIVITY DRIVER'
        if cat == 'industry':
            return 'INDUSTRIAL ACTIVITY DRIVER'
        if cat == 'trade':
            return 'HOUSEHOLD DEMAND PROXY'
        if cat == 'foreign_trade':
            return 'EXTERNAL DEMAND DRIVER (gas/oil exports = energy)'
        if cat == 'environment':
            return 'HOUSING / AC PENETRATION PROXY'
        if cat == 'ecology':
            return 'EMISSIONS TARGET (CO2)'
        if cat == 'transport':
            return 'TRANSPORT ENERGY / FREIGHT'
        if cat == 'business':
            return 'INDUSTRIAL CONNECTIONS PROXY'
        return cat

    short['purpose'] = short.apply(purpose, axis=1)

    # Sort: PRIMARY first, then STRONG, then POSSIBLE; within group by category
    rel_order = {'PRIMARY': 0, 'STRONG': 1, 'POSSIBLE': 2}
    short = short.sort_values(
        by=['relevance', 'category', 'id'],
        key=lambda s: s.map(rel_order) if s.name == 'relevance' else s
    ).reset_index(drop=True)

    keep = ['id', 'title_en', 'category', 'relevance', 'purpose',
            'theme', 'monthly', 'n_rows', 'n_time', 't_start', 't_end',
            'median', 'magnitude_order', 'top_entities']
    short[keep].to_csv(SHORTLIST_PATH, index=False)

    print(f'Wrote {SHORTLIST_PATH}')
    print(f'\nTotal shortlisted: {len(short)} / {len(manifest)} files')
    print('\nBy relevance:')
    print(short['relevance'].value_counts())
    print('\nBy category × relevance:')
    pivot = short.groupby(['category', 'relevance']).size().unstack(fill_value=0)
    print(pivot)

    # Also list the still-unknown UZB single-row files (in the manifest but not in registry)
    unknown = manifest[~manifest['id'].isin(REGISTRY.keys())].copy()
    print(f'\nStill unmapped files: {len(unknown)} / {len(manifest)}')
    print('Theme split of unmapped:')
    print(unknown['theme'].value_counts())
    unknown[['id','file','theme','monthly','n_rows','t_start','t_end','median','magnitude_order','top_entities']].to_csv(
        OUT / 'UNMAPPED_files.csv', index=False)
    print(f'-> wrote {OUT / "UNMAPPED_files.csv"}')


if __name__ == '__main__':
    main()
