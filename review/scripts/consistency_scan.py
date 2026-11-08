"""consistency_scan.py - Reviewer 1, minor comment 5: scans every 'count (pct%)' / 'pct% (n = count)' pair in the manuscript and
infers its denominator; flags pairs that match no plausible denominator, and pairs whose percentage implies the 757-study corpus
while the sentence speaks of full-text studies (or the reverse). Output: ../reviewer_response/consistency_flags.csv"""
import os, re, docx, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE)
d = docx.Document(os.path.join(REV, 'Rasul_VegeClimate Review_R1.docx'))
DEN = [811, 369, 442, 1482, 163, 337, 196, 40, 38, 600, 16, 762, 284, 478, 152, 330, 120, 27, 19, 17, 3944, 4788, 671, 352, 181, 188, 14, 33, 8, 71, 355, 1265, 422, 1415, 663, 286]
P1 = re.compile(r'(\d[\d,]*)\s*\(\s*(\d+(?:\.\d+)?)\s*%')                     # 1,234 (12.3%
P2 = re.compile(r'(\d+(?:\.\d+)?)\s*%[^()]{0,25}\(\s*n\s*=\s*(\d[\d,]*)\)')   # 12.3% (n = 123)
P3 = re.compile(r'\(\s*n\s*=\s*(\d[\d,]*)\s*,\s*(\d+(?:\.\d+)?)\s*%')         # (n = 123, 12.3%
rows = []
paras = [(i, p.text) for i, p in enumerate(d.paragraphs)]
for t in d.tables:
    for r in t.rows:
        paras.append(('T', ' | '.join(c.text for c in r.cells)))
for i, t in paras:
    for pat, order in [(P1, 'cp'), (P2, 'pc'), (P3, 'cp')]:
        for m in pat.finditer(t):
            a, b = m.group(1), m.group(2)
            c, p = (a, b) if order == 'cp' else (b, a)
            c = int(c.replace(',', '')); p = float(p)
            if c == 0 or p == 0 or p > 100: continue
            dec = len(str(p).split('.')[1]) if '.' in str(p) else 0
            fits = [n for n in DEN if n >= c and abs(round(100*c/n, dec) - p) <= (0.051 if dec else 0.51)]
            ctx = t[max(0, m.start()-160):m.end()+40].replace('\n', ' ')
            flag = ''
            if not fits: flag = 'NO DENOMINATOR'
            elif 811 in fits and 369 not in fits and re.search(r'full-text|full text|Tier 2', ctx): flag = 'pct of 811 but text says full-text'
            elif 369 in fits and 811 not in fits and re.search(r'(all|of the) 811|included studies|whole corpus|of the corpus', ctx) and not re.search(r'full-text|full text', ctx): flag = 'pct of 369 but text implies 811'
            rows.append(dict(para=i, count=c, pct=p, denominators=fits[:4], flag=flag, context=ctx))
R = pd.DataFrame(rows); R.to_csv(os.path.join(REV, 'reviewer_response', 'consistency_flags.csv'), index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 170)
print(len(R), 'pairs;', (R.flag != '').sum(), 'flagged'); print(R[R.flag != ''][['para', 'count', 'pct', 'flag', 'context']].to_string(index=False))
