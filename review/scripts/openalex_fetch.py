"""openalex_fetch.py - Reviewer 1, comment 3: fetch OpenAlex metadata (title, abstract, year, type, language,
source) for (a) DOIs cited in the reference lists of the 455 Tier 2 full texts, (b) the 2,462 title-screening
exclusions and (c) the 615 eligibility-screening exclusions. Cached in ../reviewer_response/openalex_cache.json."""
import os, re, json, time, requests, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); ROOT = os.path.dirname(REV)
OUT = os.path.join(REV, 'reviewer_response'); CACHE = os.path.join(OUT, 'openalex_cache.json')
norm = lambda s: re.sub(r'[\.,;:\)\]\}>]+$', '', str(s).strip().lower())

def ref_dois(txt):
    m = list(re.finditer(r'\n\s*(references|bibliography|literature cited)\s*\n', txt, re.I))
    body = txt[m[-1].end():] if m and m[-1].start() > len(txt) / 3 else txt[int(len(txt) * 0.7):]
    body = re.sub(r'-\n', '', body)
    return {norm(x) for x in re.findall(r'10\.\d{4,9}/[^\s"<>\]]+', body)}

e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
cites = {}
for _, x in e.iterrows():
    p = os.path.join(REV, 'pdf_text', f'{x.pdf_stem}.txt')
    if os.path.exists(p):
        for d in ref_dois(open(p, encoding='utf-8', errors='ignore').read()):
            if len(d) < 60: cites.setdefault(d, set()).add(norm(x.doi))
log = pd.read_csv(os.path.join(OUT, 'Table_S1_PRISMA_record_log.csv'))
ta = pd.read_csv(os.path.join(ROOT, 'data', 'step2_exclusion_log.csv'))
need = set(cites) | {norm(d) for d in ta.doi.dropna()} | {norm(d) for d in log.loc[log.final_status != 'Included', 'doi'].dropna()}
need.discard(''); need.discard('nan')
json.dump({k: sorted(v) for k, v in cites.items()}, open(os.path.join(OUT, 'reference_dois.json'), 'w'))

cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
todo = sorted(d for d in need if d not in cache)
print('cited DOIs', len(cites), '| to fetch', len(todo), 'of', len(need))
S = requests.Session()
def inv(ai):
    if not ai: return ''
    pos = sorted((i, w) for w, ii in ai.items() for i in ii); return ' '.join(w for _, w in pos)
for i in range(0, len(todo), 50):
    chunk = todo[i:i + 50]
    q = '|'.join('https://doi.org/' + d for d in chunk if '|' not in d and ',' not in d)
    for attempt in range(4):
        try:
            r = S.get('https://api.openalex.org/works', params={'filter': f'doi:{q}', 'per-page': 50,
                      'select': 'doi,title,abstract_inverted_index,publication_year,type,language,primary_location,keywords'}, timeout=60)
            r.raise_for_status(); break
        except Exception as ex:
            time.sleep(5 * (attempt + 1)); r = None
    found = {}
    if r is not None:
        for w in r.json().get('results', []):
            d = norm((w.get('doi') or '').replace('https://doi.org/', ''))
            src = ((w.get('primary_location') or {}).get('source') or {})
            found[d] = dict(title=w.get('title') or '', abstract=inv(w.get('abstract_inverted_index')),
                            year=w.get('publication_year'), type=w.get('type'), language=w.get('language'),
                            source=src.get('display_name'), keywords='; '.join(k.get('display_name', '') for k in (w.get('keywords') or [])))
    for d in chunk: cache[d] = found.get(d, {'missing': True})
    if (i // 50) % 20 == 0:
        json.dump(cache, open(CACHE, 'w')); print(i + len(chunk), 'done', flush=True)
    time.sleep(0.15)
json.dump(cache, open(CACHE, 'w'))
print('cached', len(cache), 'missing', sum(1 for v in cache.values() if v.get('missing')))
