"""abstracts_v2.py - title and abstract for every one of the 1,482 records assessed for eligibility, for the revised
title-and-abstract screening. Sources in order: OpenAlex caches already built for the revision, the Crossref abstract
cache, then live OpenAlex and Crossref queries (DOI, or title search for records without a DOI)."""
import os, re, json, time, html, requests, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); ROOT = os.path.dirname(REV)
OUT = os.path.join(REV, 'reviewer_response', 'screening_v2'); CACHE = os.path.join(OUT, 'abstracts.json')
norm = lambda s: re.sub(r'[\.,;:\)\]\}>]+$', '', str(s).strip().lower())
clean = lambda t: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(t or ''))).strip()
log = pd.read_csv(os.path.join(REV, 'reviewer_response', 'Table_S1_PRISMA_record_log.csv'))
raw = pd.read_csv(os.path.join(ROOT, 'data', 'step1_scopus_raw.csv')); raw['dn'] = raw.doi.map(norm)
full = dict(zip(raw.dn, raw.title)); t60 = dict(zip(raw.title.str[:60].str.lower(), raw.title))
log['dn'] = log.doi.map(norm)
log['full_title'] = [full.get(d) if isinstance(full.get(d), str) else t60.get(str(t)[:60].lower(), t) for d, t in zip(log.dn, log.title)]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def inv(ai):
    if not ai: return ''
    pos = sorted((i, w) for w, ii in ai.items() for i in ii); return ' '.join(w for _, w in pos)
# existing caches
for f in ['openalex_cache.json', 'openalex_included_cache.json']:
    p = os.path.join(REV, 'reviewer_response', f)
    if os.path.exists(p):
        for k, v in json.load(open(p)).items():
            a = v.get('abstract') if isinstance(v, dict) else None
            if a and len(a) > 100 and norm(k) not in cache: cache[norm(k)] = {'abstract': clean(a), 'src': 'OpenAlex'}
p = os.path.join(ROOT, 'data', 'step5_abstract_cache.json')
if os.path.exists(p):
    for k, v in json.load(open(p)).items():
        a = v if isinstance(v, str) else (v.get('abstract') if isinstance(v, dict) else None)
        if a and len(a) > 100 and norm(k) not in cache: cache[norm(k)] = {'abstract': clean(a), 'src': 'Crossref'}
S = requests.Session(); S.headers['User-Agent'] = 'vegclimate-review-screening/1.0'
def key(r): return r.dn if r.dn and r.dn != 'nan' else 'title:' + str(r.full_title)[:120].lower()
T0 = time.time(); BUDGET = float(os.environ.get('BUDGET', '150'))
todo = [r for r in log.itertuples() if key(r) not in cache]
print('to fetch', len(todo), flush=True)
# 1. OpenAlex in batches of 40 DOIs
dois = [r.dn for r in todo if not key(r).startswith('title:') and '|' not in r.dn and ',' not in r.dn]
for i in range(0, len(dois), 40):
    if time.time() - T0 > BUDGET: break
    ch = dois[i:i + 40]
    try:
        j = S.get('https://api.openalex.org/works', params={'filter': 'doi:' + '|'.join(ch), 'per-page': 50}, timeout=30)
        got = {norm(w['doi'].replace('https://doi.org/', '')): inv(w.get('abstract_inverted_index')) for w in j.json().get('results', []) if w.get('doi')}
    except Exception as ex: print('err', ex); continue
    for dd in ch:
        a = got.get(dd, '')
        cache[dd] = {'abstract': a, 'src': 'OpenAlex'} if len(a) > 100 else {'abstract': '', 'src': 'pending'}
json.dump(cache, open(CACHE, 'w'))
# 2. Crossref for DOIs OpenAlex lacked; OpenAlex title search for records without DOI
for r in log.itertuples():
    if time.time() - T0 > BUDGET: break
    k = key(r); c = cache.get(k)
    if c and c['src'] != 'pending': continue
    a, src = '', 'none'
    try:
        if not k.startswith('title:'):
            j = S.get(f'https://api.crossref.org/works/{r.dn}', timeout=20)
            if j.ok: a, src = clean(j.json()['message'].get('abstract', '')), 'Crossref'
        else:
            j = S.get('https://api.openalex.org/works', params={'search': str(r.full_title)[:200], 'per-page': 1}, timeout=20)
            if j.ok and j.json()['results']:
                w = j.json()['results'][0]
                if w.get('title') and w['title'].lower()[:50] == str(r.full_title).lower()[:50]:
                    a, src = inv(w.get('abstract_inverted_index')), 'OpenAlex (title match)'
    except Exception as ex: print('err', k, ex)
    cache[k] = {'abstract': a, 'src': src} if len(a) > 100 else {'abstract': '', 'src': 'none'}
json.dump(cache, open(CACHE, 'w'))
log['abstract'] = [cache.get(key(r), {}).get('abstract', '') for r in log.itertuples()]
log['abstract_source'] = [cache.get(key(r), {}).get('src', 'none') for r in log.itertuples()]
log[['row_id', 'doi', 'full_title', 'year', 'journal', 'doc_type', 'abstract', 'abstract_source']].to_csv(os.path.join(OUT, 'records_with_abstracts.csv'), index=False)
print('with abstract', (log.abstract.str.len() > 100).sum(), 'of', len(log)); print(log.abstract_source.value_counts())
