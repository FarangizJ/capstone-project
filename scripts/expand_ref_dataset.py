"""Expand REF JSON with 15 verified small/medium hydro plants, then regenerate the
CSV and the HTML map's embedded PROJECTS array so all three stay in sync.

Sources: Global Energy Monitor wiki entries (gem.wiki), individually fetched
2026-06-02. Coordinates from Wikipedia where available; otherwise district-level
approximation with exact=false.

Plants added (operating, 11):
  Chirchik HPP, Tavak HPP, Akkavak HPP, Khodzhikent HPP, Gazalkent HPP,
  Tuyamuyun HPP, Andijan-1 HPP, Andijan HPP, Gissarak HPP, Topalang HPP,
  Zarchob I HPP

Plants added (build, 1):
  Pskem HPP

Plants added (plan, 3):
  Akbulak HPP, Mullalak HPP, Karateren pumped storage

Excluded after verification:
  Yovon HPP — owned by OSHC Barki Tojik (Tajikistan), not a Uzbek asset
  Fandaryo — cross-border Tajikistan-Uzbekistan, ownership unclear; flagged
    in the spatial notebook rather than added to REF
"""
import json
import csv
import re
from pathlib import Path
from collections import Counter

RESEARCH = Path(__file__).resolve().parents[1] / 'research' / 'uzbekistan-energy'
JSON_PATH = RESEARCH / 'uzbekistan_energy_projects.json'
CSV_PATH  = RESEARCH / 'uzbekistan_energy_projects.csv'
HTML_PATH = RESEARCH / 'uzbekistan_energy_map.html'

GEM = 'Global Energy Monitor wiki (gem.wiki), fetched 2026-06-02'

NEW_ENTRIES = [
    # ── Operating hydro plants ────────────────────────────────────────
    {"name": "Chirchik HPP", "tech": "hydro", "status": "op", "year": 1940, "mw": 80,
     "region": "Tashkent region (Chirchik, Qibray district)",
     "lat": 41.47, "lng": 69.58, "exact": False,
     "dev": "State (now JSC Uzbekenergo)", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Chirchik plant, 4 turbines, 1940"},

    {"name": "Tavak HPP", "tech": "hydro", "status": "op", "year": 1941, "mw": 70,
     "region": "Tashkent region (Bostanlik district)",
     "lat": 41.60, "lng": 70.00, "exact": False,
     "dev": "State (now JSC Uzbekenergo)", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Tavak plant, 4 x 18 MW turbines, 1941"},

    {"name": "Akkavak HPP", "tech": "hydro", "status": "op", "year": 1951, "mw": 39,
     "region": "Tashkent region (Chirchik, Kibray district)",
     "lat": 41.4471, "lng": 69.5578, "exact": True,
     "dev": "State (now JSC Uzbekenergo)", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Akkavak plant, 1 turbine run-of-river, 1951"},

    {"name": "Khodzhikent HPP", "tech": "hydro", "status": "op", "year": 1976, "mw": 165,
     "region": "Tashkent region (Bostanlik / Karankultugay)",
     "lat": 41.56, "lng": 69.95, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Khodzhikent plant on Chirchik River, 1976; pumped storage 200 MW extension pre-construction"},

    {"name": "Gazalkent HPP", "tech": "hydro", "status": "op", "year": 1981, "mw": 120,
     "region": "Tashkent region (Bostanlik district)",
     "lat": 41.5625, "lng": 69.775, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Gazalkent (Gʻazalkent) plant on Chirchik River; coordinates via Wikipedia town record"},

    {"name": "Tuyamuyun HPP", "tech": "hydro", "status": "op", "year": 1986, "mw": 150,
     "region": "Karakalpakstan (Tortkul district)",
     "lat": 41.78, "lng": 61.46, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Tuyamuyun plant on Amudarya River, 1986; cross-border facility with Turkmenistan"},

    {"name": "Andijan-1 HPP", "tech": "hydro", "status": "op", "year": 1985, "mw": 140,
     "region": "Andijan region (Xonobod city)",
     "lat": 40.81, "lng": 73.00, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "USSR state budget",
     "inv": "Not disclosed (state-planned)", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Andijan-1 plant on Karadarya River, 1985"},

    {"name": "Andijan HPP", "tech": "hydro", "status": "op", "year": 2010, "mw": 50,
     "region": "Andijan region (Andijan Reservoir)",
     "lat": 40.7747, "lng": 73.1219, "exact": True,
     "dev": "JSC Uzbekgidroenergo",
     "fin": "State / DFI (likely AFD-related per Tashkent–Andijan hydro programme)",
     "inv": "Not separately disclosed", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Andijan plant, 50 MW, 2010; reservoir coordinates from Wikipedia"},

    {"name": "Gissarak HPP", "tech": "hydro", "status": "op", "year": 2010, "mw": 45,
     "region": "Kashkadarya region",
     "lat": 38.85, "lng": 67.05, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "State",
     "inv": "Not separately disclosed", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Gissarak (Hisarak) plant on Aksu River, 2010"},

    {"name": "Topalang HPP", "tech": "hydro", "status": "op", "year": 2023, "mw": 175,
     "region": "Surxondaryo region (Sariosiyo district)",
     "lat": 38.40, "lng": 67.95, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "State / DFI co-financing",
     "inv": "Not publicly disclosed", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Topalang plant on Tupalangdarya River, 2023"},

    {"name": "Zarchob I HPP", "tech": "hydro", "status": "op", "year": 2021, "mw": 37,
     "region": "Surxondaryo region (Sariosiyo district)",
     "lat": 38.50, "lng": 67.95, "exact": False,
     "dev": "JSC Uzbekgidroenergo (Uzbekhydroenergo)", "fin": "State",
     "inv": "Not publicly disclosed", "ret": "Regulated state tariff",
     "tax": "State-owned",
     "src": f"{GEM} — Zarchob I run-of-river plant on Tupalang River, 2 turbines, 2021"},

    # ── Under construction ──────────────────────────────────────────────
    {"name": "Pskem HPP", "tech": "hydro", "status": "build", "year": 2026, "mw": 400,
     "region": "Tashkent region (Bostanlik district)",
     "lat": 41.85, "lng": 70.30, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "DFI co-financing (in part)",
     "inv": "Conventional storage hydropower, expected commissioning 2026",
     "ret": "Regulated state tariff", "tax": "State strategic project",
     "src": f"{GEM} — Pskem plant on Pskem River, under construction, 2026 target"},

    # ── Planned / announced ─────────────────────────────────────────────
    {"name": "Akbulak HPP", "tech": "hydro", "status": "plan", "year": 2028, "mw": 60,
     "region": "Tashkent region",
     "lat": 41.5382, "lng": 69.6948, "exact": True,
     "dev": "JSC Uzbekgidroenergo", "fin": "TBD",
     "inv": "Announced phase", "ret": "Regulated state tariff",
     "tax": "State strategic project",
     "src": f"{GEM} — Akbulak plant on Akbulak River, announced, 2028 target"},

    {"name": "Mullalak HPP", "tech": "hydro", "status": "plan", "year": 2028, "mw": 140,
     "region": "Tashkent region (Boʻstonliq district)",
     "lat": 41.80, "lng": 70.10, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "Bank of China",
     "inv": "Pre-construction; conventional storage",
     "ret": "Regulated state tariff", "tax": "State strategic project",
     "src": f"{GEM} — Mullalak plant on Pskem River; Bank of China financing"},

    {"name": "Karateren pumped storage", "tech": "hydro", "status": "plan", "year": 2030, "mw": 500,
     "region": "Tashkent region (Bostanlik district)",
     "lat": 41.70, "lng": 70.20, "exact": False,
     "dev": "JSC Uzbekgidroenergo", "fin": "TBD",
     "inv": "Announced pumped storage facility",
     "ret": "Regulated state tariff / ancillary services",
     "tax": "State strategic project",
     "src": f"{GEM} — Karateren pumped storage on Pskem River, announced, 2030 target"},
]


def write_csv(ref_sorted):
    csv_fields = [
        ('name', 'name'), ('tech', 'technology'), ('status', 'status'),
        ('year', 'year'), ('mw', 'capacity_mw'), ('region', 'region'),
        ('lat', 'lat'), ('lng', 'lng'), ('exact', 'coords_exact'),
        ('retired', 'retired_units'),
        ('dev', 'developer_partners'), ('fin', 'financiers'),
        ('inv', 'investment'), ('ret', 'returns_tariff'),
        ('tax', 'tax_regulation'), ('src', 'source'),
    ]
    with open(CSV_PATH, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([h for _, h in csv_fields])
        for a in ref_sorted:
            row = []
            for key, _ in csv_fields:
                v = a.get(key, '')
                if v is True:    v = 'true'
                elif v is False: v = 'false'
                elif v is None:  v = ''
                row.append(v)
            w.writerow(row)


def update_html(ref_sorted):
    html = HTML_PATH.read_text()
    pat = re.compile(r'const PROJECTS = \[.*?\];', re.DOTALL)
    m = pat.search(html)
    if not m:
        print('⚠ Could not find PROJECTS array in HTML; map not updated.')
        return

    lines = ['const PROJECTS = [']
    for asset in ref_sorted:
        parts = []
        for k in ['name', 'tech', 'status', 'year', 'mw', 'region', 'lat', 'lng', 'exact']:
            v = asset.get(k)
            if v is None:
                parts.append(f'{k}:null')
            elif isinstance(v, bool):
                parts.append(f'{k}:{"true" if v else "false"}')
            elif isinstance(v, str):
                s = v.replace('\\', '\\\\').replace('"', '\\"')
                parts.append(f'{k}:"{s}"')
            else:
                parts.append(f'{k}:{v}')
        if asset.get('retired'):
            s = asset['retired'].replace('\\', '\\\\').replace('"', '\\"')
            parts.append(f'retired:"{s}"')
        for k in ['dev', 'fin', 'inv', 'ret', 'tax', 'src']:
            v = asset.get(k, '')
            s = str(v).replace('\\', '\\\\').replace('"', '\\"')
            parts.append(f'{k}:"{s}"')
        lines.append('  {' + ', '.join(parts) + '},')
    lines[-1] = lines[-1].rstrip(',')
    lines.append('];')
    new_array = '\n'.join(lines)
    html_new = html[:m.start()] + new_array + html[m.end():]
    HTML_PATH.write_text(html_new)


def main():
    ref = json.loads(JSON_PATH.read_text())
    print(f'Loaded REF: {len(ref)} assets')

    existing_names = {a['name'] for a in ref}
    to_add = [e for e in NEW_ENTRIES if e['name'] not in existing_names]
    print(f'Adding {len(to_add)} verified entries (skipping {len(NEW_ENTRIES)-len(to_add)} duplicates)')
    ref.extend(to_add)

    status_order = {'op': 0, 'build': 1, 'plan': 2}
    ref_sorted = sorted(ref, key=lambda a: (a['tech'], status_order.get(a['status'], 99), a['year']))

    JSON_PATH.write_text(json.dumps(ref_sorted, indent=2))
    print(f'Wrote {JSON_PATH}  ({len(ref_sorted)} assets total)')

    write_csv(ref_sorted)
    print(f'Wrote {CSV_PATH}')

    update_html(ref_sorted)
    print(f'Wrote {HTML_PATH} (PROJECTS array refreshed)')

    print()
    print('--- Final REF summary ---')
    print(f'Total: {len(ref_sorted)} | by status: {dict(Counter(a["status"] for a in ref_sorted))}')
    for tech in sorted({a['tech'] for a in ref_sorted}):
        all_n = sum(1 for a in ref_sorted if a['tech'] == tech)
        op_n  = sum(1 for a in ref_sorted if a['tech'] == tech and a['status'] == 'op')
        op_mw = sum(a['mw'] or 0 for a in ref_sorted if a['tech'] == tech and a['status'] == 'op')
        print(f'  {tech:10s} {all_n:3d} total ({op_n:2d} op)  op MW: {op_mw:,}')


if __name__ == '__main__':
    main()
