"""search_screening_eval.py - Reviewer 1, comment 3.
(1) Relative recall of the Scopus search against an independent benchmark: works cited in the reference lists of
    the 455 Tier 2 studies that are eligible on their OpenAlex abstract (same deterministic rules as
    tier1_sensitivity.py), overall and by sensor family and application domain; diagnosis of every miss by
    simulating the 13-pair Boolean query on the benchmark title+abstract.
(2) Screening accuracy: end-to-end fate of retrieved benchmark studies through each screening stage, and the
    share of title- and eligibility-stage exclusions that meet the abstract-assessable criteria.
Outputs -> ../reviewer_response/Table_S4_search_recall.csv, Table_S5_screening_accuracy.csv,
           Table_S6_benchmark_records.csv, search_screening_eval.json"""
import os, re, json, pandas as pd, numpy as np
from tier1_sensitivity_rules import check, verdict
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); ROOT = os.path.dirname(REV)
OUT = os.path.join(REV, 'reviewer_response')
norm = lambda s: re.sub(r'[\.,;:\)\]\}>]+$', '', str(s).strip().lower())
oa = json.load(open(os.path.join(OUT, 'openalex_cache.json')))
cites = json.load(open(os.path.join(OUT, 'reference_dois.json')))
raw = pd.read_csv(os.path.join(ROOT, 'data', 'step1_scopus_raw.csv'))
log = pd.read_csv(os.path.join(OUT, 'Table_S1_PRISMA_record_log.csv'))
ta = pd.read_csv(os.path.join(ROOT, 'data', 'step2_exclusion_log.csv'))
RET = {norm(d) for d in raw.doi.dropna()}
DOCX = {norm(d) for d in raw.loc[~raw.doc_type.isin(['Article', 'Review']), 'doi'].dropna()}
TAX = {norm(d) for d in ta.doi.dropna()}
STAT = {norm(d): s for d, s in zip(log.doi.fillna(''), log.final_status)}

def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; c = (p + z*z/(2*n)) / (1 + z*z/n); h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return round(100*(c-h), 1), round(100*(c+h), 1)

from query_sim import PAIRS, has, query_match

SENS = {'Landsat': r'landsat', 'MODIS': r'modis', 'Sentinel-2': r'sentinel[- ]?2', 'SAR / Sentinel-1': r'\bsar\b|synthetic aperture|sentinel[- ]?1|palsar|radarsat',
        'AVHRR / GIMMS': r'avhrr|gimms', 'LiDAR / GEDI / ICESat': r'lidar|gedi|icesat', 'Hyperspectral': r'hyperspectral|hyperion|enmap|prisma|desis',
        'SIF': r'\bsif\b|solar[- ]induced|chlorophyll fluorescence', 'VIIRS': r'viirs', 'SPOT-VGT / PROBA-V': r'spot[- ]?vgt|spot vegetation|proba[- ]?v',
        'Very-high-resolution': r'worldview|quickbird|planetscope|gaofen|\bgf[- ]?[12]\b|ikonos'}
DOMS = {'Phenology': r'phenolog|green[- ]?up|growing season|start of season', 'Greening / browning trend': r'greening|browning|ndvi trend|vegetation trend',
        'Drought response': r'drought', 'Fire / disturbance': r'fire|burn|disturbance|mortality|dieback',
        'Biomass / carbon stock': r'biomass|carbon stock|carbon density', 'Productivity / carbon flux': r'\bgpp\b|\bnpp\b|productivity|carbon (flux|uptake|sink)',
        'Land cover change': r'land[- ]?cover|land[- ]?use|lulc', 'Crops / agriculture': r'\bcrop|yield|agricultur|wheat|maize|rice',
        'Forest': r'forest', 'Grassland / dryland': r'grassland|steppe|savanna|dryland|rangeland|arid', 'Tundra / high latitude': r'tundra|arctic|boreal|permafrost|alpine'}
tags = lambda t, D: [k for k, p in D.items() if re.search(p, t)]

# ---- (1) benchmark and recall
rows = []
for d, citers in cites.items():
    w = oa.get(d, {});
    if w.get('missing') or not w: continue
    a = w.get('abstract') or ''
    if len(a) < 100 or w.get('type') != 'article' or w.get('language') not in ('en', None) or not (2000 <= (w.get('year') or 0) <= 2025): continue
    r = check(w['title'], a)
    if not verdict(r, True).startswith('Meets') or not r['original_research']: continue
    text = (w['title'] or '') + ' ' + a + ' ' + (w.get('keywords') or '')
    qm, cc = query_match(text)
    retrieved = d in RET
    if retrieved:
        fate = ('Excluded: document type' if d in DOCX else 'Excluded: title screening' if d in TAX else
                ('Included' if STAT.get(d) == 'Included' else 'Excluded: title-and-abstract screening' if d in STAT else 'Excluded: duplicate/other'))
    else: fate = 'Not retrieved'
    rows.append(dict(doi=d, year=w['year'], title=w['title'], source=w.get('source'), n_citing_included=len(citers),
                     retrieved=retrieved, query_logic_matches_title_abstract=qm, mentions_climate_change=cc, fate=fate,
                     sensors='; '.join(tags(text.lower(), SENS)), domains='; '.join(tags(text.lower(), DOMS))))
B = pd.DataFrame(rows); B.to_csv(os.path.join(OUT, 'Table_S6_benchmark_records.csv'), index=False, encoding='utf-8-sig')
n, k = len(B), int(B.retrieved.sum())
res = {'cited_dois': len(cites), 'with_metadata': sum(1 for d in cites if not oa.get(d, {}).get('missing')),
       'benchmark_n': n, 'retrieved': k, 'recall_pct': round(100*k/n, 1), 'recall_ci': wilson(k, n)}
nr = B[~B.retrieved]
res['miss_no_climate_change_phrase'] = int((~nr.mentions_climate_change).sum())
res['miss_query_logic_fails'] = int((~nr.query_logic_matches_title_abstract).sum())
res['miss_query_logic_matches'] = int(nr.query_logic_matches_title_abstract.sum())
cc = B[B.mentions_climate_change]; ncc = B[~B.mentions_climate_change]
res['recall_with_cc_phrase'] = [len(cc), int(cc.retrieved.sum()), round(100*cc.retrieved.mean(), 1), wilson(int(cc.retrieved.sum()), len(cc))]
res['recall_without_cc_phrase'] = [len(ncc), int(ncc.retrieved.sum()), round(100*ncc.retrieved.mean(), 1), wilson(int(ncc.retrieved.sum()), len(ncc))]
qm = B[B.query_logic_matches_title_abstract]
res['recall_when_query_logic_matches'] = [len(qm), int(qm.retrieved.sum()), round(100*qm.retrieved.mean(), 1)]
yb = pd.cut(B.year, [1999, 2009, 2014, 2019, 2025]).astype(str)
res['recall_by_period'] = {p: [int(g.retrieved.sum()), len(g), round(100*g.retrieved.mean(), 1)] for p, g in B.groupby(yb)}

T = [('All benchmark studies', n, k)]
for lab, D, col in [('Sensor', SENS, 'sensors'), ('Domain', DOMS, 'domains')]:
    for key in D:
        g = B[B[col].str.contains(re.escape(key), regex=True)]
        if len(g) >= 10: T.append((f'{lab}: {key}', len(g), int(g.retrieved.sum())))
T = pd.DataFrame(T, columns=['Subset', 'Benchmark n', 'Retrieved'])
T['Recall (%)'] = (100*T.Retrieved/T['Benchmark n']).round(1)
T['95% CI'] = [f'{a}-{b}' for a, b in (wilson(r, m) for r, m in zip(T.Retrieved, T['Benchmark n']))]
T['Recall if "climate change" in abstract (%)'] = [
    round(100*g.retrieved.mean(), 1) if len(g) else np.nan for g in
    [B[B.mentions_climate_change]] + [B[B.mentions_climate_change & B[('sensors' if s.startswith('Sensor') else 'domains')].str.contains(re.escape(s.split(': ', 1)[1]))] for s in T.Subset[1:]]]
T.to_csv(os.path.join(OUT, 'Table_S4_search_recall.csv'), index=False, encoding='utf-8-sig')

# ---- (2) screening accuracy
ret = B[B.retrieved]
res['benchmark_retrieved_fate'] = ret.fate.value_counts().to_dict()
art = ret[ret.fate != 'Excluded: document type']
res['screening_sensitivity'] = [int((art.fate == 'Included').sum()), len(art), round(100*(art.fate == 'Included').mean(), 1),
                                wilson(int((art.fate == 'Included').sum()), len(art))]
def abs_pass(dois):
    v = []
    for d in dois:
        w = oa.get(norm(d), {})
        a = w.get('abstract') or ''
        if w.get('missing') or len(a) < 100: continue
        r = check(w.get('title', ''), a); v.append(verdict(r, True).startswith('Meets') and r['original_research'])
    return len(v), int(sum(v))
S = []
for lab, dois in [('Excluded at title screening', ta.doi.dropna()),
                  ('  no remote sensing term in title', ta.loc[ta.screen_reason.str.startswith('No remote'), 'doi'].dropna()),
                  ('  no vegetation term in title', ta.loc[ta.screen_reason.str.startswith('No veg'), 'doi'].dropna()),
                  ('Excluded at title-and-abstract screening', log.loc[log.final_status != 'Included', 'doi'].dropna()),
                  ('Included, Tier 1 (reference)', log.loc[log.extraction_tier == 'Bibliographic only (Tier 1)', 'doi'].dropna()),
                  ('Included, Tier 2 (reference)', log.loc[log.extraction_tier == 'Full text (Tier 2)', 'doi'].dropna())]:
    m, p = abs_pass(dois); S.append((lab, len(dois), m, p, round(100*p/m, 1) if m else np.nan, '%s-%s' % wilson(p, m)))
S = pd.DataFrame(S, columns=['Group', 'Records (with DOI)', 'With OpenAlex abstract', 'Meet abstract-assessable criteria',
                             '% meeting', '95% CI'])
S.to_csv(os.path.join(OUT, 'Table_S5_screening_accuracy.csv'), index=False, encoding='utf-8-sig')
json.dump(res, open(os.path.join(OUT, 'search_screening_eval.json'), 'w'), indent=1, default=str)
pd.set_option('display.width', 250)
print(T.to_string(index=False)); print(S.to_string(index=False)); print(json.dumps(res, indent=1, default=str))
