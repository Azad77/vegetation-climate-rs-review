"""fetch_oa_pdfs_v2.py - tries to download open-access PDFs for included studies without full text, using the OpenAlex
open-access locations (no credentials). Saves to ../pdfs_v2/<doi>.pdf and converts with pdftotext -layout into pdf_text/."""
import os, re, json, time, subprocess, requests, pandas as pd
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PDF = os.path.join(os.path.dirname(REV), 'pdfs_v2')
LOG = os.path.join(REV, 'data_v2', 'oa_fetch_log.json'); log = json.load(open(LOG)) if os.path.exists(LOG) else {}
m = pd.read_excel(os.path.join(REV, 'data_v2', 'PDFs_needed_v2.xlsx'))
dois = [str(d).strip().lower() for d in m.doi if str(d) != 'nan']
S = requests.Session(); S.headers['User-Agent'] = 'Mozilla/5.0 (vegclimate-review)'
T0 = time.time(); B = float(os.environ.get('BUDGET', '160'))
# 1. OA locations from OpenAlex
if 'urls' not in log:
    urls = {}
    for i in range(0, len(dois), 40):
        ch = [d for d in dois[i:i + 40] if '|' not in d and ',' not in d]
        j = S.get('https://api.openalex.org/works', params={'filter': 'doi:' + '|'.join(ch), 'per-page': 50}, timeout=40).json()
        for w in j.get('results', []):
            d = w['doi'].replace('https://doi.org/', '').lower(); c = []
            for loc in [w.get('best_oa_location')] + (w.get('locations') or []):
                if loc and loc.get('pdf_url') and loc['pdf_url'] not in c: c.append(loc['pdf_url'])
            urls[d] = c
    log['urls'] = urls; json.dump(log, open(LOG, 'w'))
urls = log['urls']; done = log.setdefault('done', {})
print('with OA pdf url:', sum(bool(v) for v in urls.values()), 'of', len(dois), flush=True)
for d in dois:
    if time.time() - T0 > B: break
    if d in done or not urls.get(d): continue
    fn = os.path.join(PDF, re.sub(r'[^A-Za-z0-9._-]', '_', d) + '.pdf'); ok = False
    for u in urls[d][:3]:
        try:
            r = S.get(u, timeout=25, allow_redirects=True)
            if r.ok and r.content[:4] == b'%PDF':
                open(fn, 'wb').write(r.content); ok = True; break
        except Exception: pass
    done[d] = ok
    if ok:
        stem = re.sub(r'[^A-Za-z0-9._-]', '_', d)
        subprocess.run(['pdftotext', '-layout', fn, os.path.join(REV, 'pdf_text', 'v2_' + stem + '.txt')])
    json.dump(log, open(LOG, 'w'))
print('attempted', len(done), '| downloaded', sum(done.values()))
