"""index_bias.py - Reviewer 2, comment 3: does the query predetermine the prominence of NDVI/EVI/LAI?
(1) Fetches OpenAlex abstracts for the 757 included studies (cached). (2) Simulates the 13 query pairs on title+abstract and
counts included studies whose retrieval depended on an index-term group (NDVI/EVI/LAI) - i.e. that match only pairs in which
the index group was satisfied and would fail every pair if index terms were removed. (3) Compares the share of abstracts naming
NDVI, EVI, LAI and SIF in the included corpus with the share in the independent citation benchmark (Section 2.9).
Output: ../reviewer_response/index_bias.json"""
import os, re, json, time, requests, pandas as pd
from query_sim import PAIRS, has   # same Boolean simulation as Section 2.9
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); R = os.path.join(REV, 'reviewer_response')
CACHE = os.path.join(R, 'openalex_included_cache.json')
m = pd.read_excel(__import__('corpus').MASTER, sheet_name='Master Clean')
norm = lambda s: str(s).strip().lower()
dois = [norm(x) for x in m.doi]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
todo = [x for x in dois if x not in cache]
for i in range(0, len(todo), 50):
    ch = todo[i:i+50]
    r = requests.get('https://api.openalex.org/works', params={'filter': 'doi:' + '|'.join('https://doi.org/' + x for x in ch if '|' not in x and ',' not in x),
                     'per-page': 50, 'select': 'doi,title,abstract_inverted_index'}, timeout=60).json()
    got = {}
    for w in r.get('results', []):
        ai = w.get('abstract_inverted_index') or {}
        got[norm((w.get('doi') or '').replace('https://doi.org/', ''))] = (w.get('title') or '') + ' ' + ' '.join(t for _, t in sorted((p, t) for t, pp in ai.items() for p in pp))
    for x in ch: cache[x] = got.get(x, '')
    time.sleep(0.2)
json.dump(cache, open(CACHE, 'w'))
IDX = {'ndvi', 'evi', 'lai'}
def match(t, drop_index=False):
    t = t.lower().replace('-', ' ')
    ok = []
    for pr in PAIRS:
        groups = [[w for w in g if not (drop_index and w in IDX)] for g in pr]
        ok.append(all(any(has(t, w.replace('-', ' ')) for w in g) for g in groups if g) and all(g for g in groups))
    return any(ok)
inc = [cache[x] for x in dois if len(cache.get(x, '')) > 200]
dep = sum(1 for t in inc if match(t) and not match(t, drop_index=True))
mt = sum(1 for t in inc if match(t))
share = lambda texts, pat: round(100 * sum(1 for t in texts if re.search(pat, t, re.I)) / len(texts), 1)
oa = json.load(open(os.path.join(R, 'openalex_cache.json'))); B = pd.read_csv(os.path.join(R, 'Table_S6_benchmark_records.csv'))
bt = [(oa.get(norm(x), {}).get('title') or '') + ' ' + (oa.get(norm(x), {}).get('abstract') or '') for x in B.doi]
bnr = [t for t, r in zip(bt, B.retrieved) if not r]
PAT = {'NDVI': r'\bNDVI\b|normali[sz]ed difference vegetation index', 'EVI': r'\bEVI\b|enhanced vegetation index',
       'LAI': r'\bLAI\b|leaf area index', 'SIF': r'\bSIF\b|solar[- ]induced (?:chlorophyll )?fluorescence|chlorophyll fluorescence'}
res = dict(included_with_abstract=len(inc), included_matching_query_on_abstract=mt, retrieval_dependent_on_index_terms=dep,
           dependent_pct=round(100 * dep / mt, 1), benchmark_n=len(bt), benchmark_not_retrieved_n=len(bnr),
           abstract_share={k: dict(included=share(inc, p), benchmark=share(bt, p), benchmark_not_retrieved=share(bnr, p)) for k, p in PAT.items()})
json.dump(res, open(os.path.join(R, 'index_bias.json'), 'w'), indent=1); print(json.dumps(res, indent=1))
