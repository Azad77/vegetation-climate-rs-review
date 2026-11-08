"""study_area.py - Reviewer 1, comment 6: deterministic study-area country for the 455 Tier 2 studies.
Counts country names (and a few unambiguous sub-national/regional aliases) in the study-area / data-and-methods part of
the reference-stripped body text, skipping the title page and affiliations. Primary country = most frequent with >= 2
mentions; >= 3 countries each with >= 3 mentions -> MULTI; 'global' framing with no dominant country -> GLOBAL.
Checked against the reading of the 40 validation-sample studies. Output: ../reviewer_response/geography/study_area.csv"""
import os, re, json, pandas as pd, pycountry
import extract as X
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); OUT = os.path.join(REV, 'reviewer_response', 'geography')
X.TXT = os.path.join(REV, 'pdf_text')
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
names = {}
for c in pycountry.countries:
    for n in {c.name, getattr(c, 'common_name', c.name), getattr(c, 'official_name', c.name)}:
        names[n] = c.name
ALIAS = {'USA': 'United States', 'U.S.A.': 'United States', 'United States of America': 'United States', 'U.S.': 'United States',
         'UK': 'United Kingdom', 'England': 'United Kingdom', 'Scotland': 'United Kingdom', 'Wales': 'United Kingdom',
         'Russia': 'Russian Federation', 'South Korea': 'Korea, Republic of', 'Korea': 'Korea, Republic of', 'Iran': 'Iran, Islamic Republic of',
         'Vietnam': 'Viet Nam', 'Turkey': 'Türkiye', 'Tanzania': 'Tanzania, United Republic of', 'Bolivia': 'Bolivia, Plurinational State of',
         'Venezuela': 'Venezuela, Bolivarian Republic of', 'Laos': 'Lao People\'s Democratic Republic', 'Syria': 'Syrian Arab Republic',
         'Czech Republic': 'Czechia', 'Taiwan': 'Taiwan, Province of China', 'Tibetan Plateau': 'China', 'Qinghai': 'China',
         'Inner Mongolia': 'China', 'Loess Plateau': 'China', 'Yangtze': 'China', 'Yellow River': 'China', 'Xinjiang': 'China',
         'Yunnan': 'China', 'Sichuan': 'China', 'Kurdistan Region': 'Iraq', 'Amazonia': 'Brazil', 'Brazilian': 'Brazil',
         'Alaska': 'United States', 'California': 'United States', 'Texas': 'United States', 'Quebec': 'Canada', 'Ontario': 'Canada',
         'Bavaria': 'Germany', 'Thuringia': 'Germany', 'Siberia': 'Russian Federation', 'Sumatra': 'Indonesia', 'Borneo': 'Indonesia',
         'Kalimantan': 'Indonesia', 'Java': 'Indonesia', 'Tuscany': 'Italy', 'Sardinia': 'Italy', 'Sicily': 'Italy', 'Andalusia': 'Spain',
         'Catalonia': 'Spain', 'Queensland': 'Australia', 'New South Wales': 'Australia', 'Victoria, Australia': 'Australia'}
names.update(ALIAS)
names = {k: v for k, v in names.items() if len(k) > 3 or k in ('USA', 'UK', 'U.S.')}
PAT = re.compile(r'\b(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')\b')
START = re.compile(r'(?:\d\.?\d?\.?\s*)?(?:Study [Aa]rea|Study [Ss]ite|Materials? and [Mm]ethods|Data and [Mm]ethods|Methodology|Methods)\b')
END = re.compile(r'(?:\d\.?\s*)?(?:Results|Discussion)\b')
MAKER = re.compile(r'\([^()]{0,80},\s*(?:USA|U\.S\.A\.|United States|Germany|Japan|Switzerland|UK|United Kingdom|Canada|France|Italy|Netherlands)\)')
def study_country(body, title=''):
    intro = body.find('Introduction'); s = body[max(intro, 0):]
    m = START.search(s, 1500 if intro >= 0 else 0); s = s[m.start():] if m else s[len(s)//5:]
    m2 = END.search(s, 3000); s = s[:m2.start()] if m2 else s[:15000]
    s = MAKER.sub(' ', s)
    hits = [names[x] for x in PAT.findall(s)] + [names[x] for x in PAT.findall(str(title))] * 3
    if not hits:   # fall back to the abstract / introduction
        hits = [names[x] for x in PAT.findall(MAKER.sub(' ', body[max(intro, 0):max(intro, 0) + 6000]))]
    cnt = pd.Series(hits, dtype=object).value_counts()
    glob = len(re.findall(r'\bglobal(?:ly)?\b', s, re.I))
    if len(cnt) == 0: return ('GLOBAL' if glob >= 5 else 'UNDETERMINED'), {}
    if (cnt >= 3).sum() >= 3: return 'MULTI', cnt.head(4).to_dict()
    if glob >= 8 and cnt.iloc[0] < 3: return 'GLOBAL', cnt.head(3).to_dict()
    return cnt.index[0], cnt.head(3).to_dict()
rows = []
for _, x in e.iterrows():
    raw, body = X.load(x.pdf_stem); c, top = study_country(body, x.title)
    rows.append(dict(doi=x.doi, year=x.year, author_country=x.author_country, study_country=c, top_counts=json.dumps(top, ensure_ascii=False)))
S = pd.DataFrame(rows); S.to_csv(os.path.join(OUT, 'study_area.csv'), index=False, encoding='utf-8-sig')
K = json.load(open(os.path.join(REV, 'reviewer_response', 'validation', 'kwic_sample.json')))
ref = json.load(open(os.path.join(OUT, 'study_area_reference.json')))
norm = {'Korea, Republic of': 'South Korea'}
# the validation sample was drawn from the original full-text set; sample studies no longer in the corpus are still
# scored, because the check validates the method, not corpus membership
e1 = pd.read_csv(os.path.join(REV, 'archive_v1', 'fulltext_extraction.csv'))
extra = []
for d in K:
    if d not in set(S.doi):
        x = e1[e1.doi == d].iloc[0]; raw, body = X.load(x.pdf_stem); c, top = study_country(body, x.title)
        extra.append(dict(doi=d, study_country=c, top_counts=json.dumps(top, ensure_ascii=False)))
Sv = pd.concat([S, pd.DataFrame(extra)], ignore_index=True)
chk = []
for i, d in enumerate(K, 1):
    r = ref[f'S{i:02d}']
    if r == 'NA': continue
    p = Sv.loc[Sv.doi == d, 'study_country'].iloc[0]; p2 = norm.get(p, p)
    chk.append(dict(S=f'S{i:02d}', reference=r, predicted=p2, agree=int(p2 == r), top=Sv.loc[Sv.doi == d, 'top_counts'].iloc[0]))
C = pd.DataFrame(chk); C.to_csv(os.path.join(OUT, 'study_area_check.csv'), index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90)
print(C.to_string(index=False)); print('agree', C.agree.sum(), '/', len(C)); print(S.study_country.value_counts().head(12).to_dict())
