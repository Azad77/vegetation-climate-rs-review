"""screen_v2_finalize.py - combines the title-and-abstract screening decisions (screening_v2/v2_dec_*.txt) with the
language criterion and builds the revised corpus: data_v2/master_v2.xlsx (sheet 'Master Clean', same columns the analysis
scripts use) and data_v2/pdf_link_v2.json (PDF text stem -> master row). Language: records in journals that publish
predominantly in a language other than English are excluded (Table 1), as in the original verification step."""
import os, re, json, glob, unicodedata, pandas as pd
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(REV)
W = os.path.join(REV, 'reviewer_response', 'screening_v2'); OUT = os.path.join(REV, 'data_v2'); os.makedirs(OUT, exist_ok=True)
norm = lambda s: re.sub(r'[\.,;:\)\]\}>]+$', '', str(s).strip().lower())
d = {}
for f in sorted(glob.glob(os.path.join(W, 'v2_dec_*.txt'))):
    for tok in open(f).read().strip().split(';'):
        k, v = tok.split(); d.setdefault(int(k), v)
s = pd.read_csv(os.path.join(REV, 'reviewer_response', 'Table_S1_PRISMA_record_log.csv'))
r = pd.read_csv(os.path.join(W, 'records_with_abstracts.csv')).fillna('')
s = s.merge(r[['row_id', 'full_title', 'abstract_source']], on='row_id')
bad = s.full_title.str.startswith('ERS-2, RADARSAT') & ~s.title.str.startswith('ERS-2')
s.loc[bad, 'full_title'] = s.loc[bad, 'title']                     # title lookup failed for some no-DOI records
s['screen_v2'] = s.row_id.map(d)
NONENG = re.compile(r"xuebao|kexue|acta .*sinica|sinica|chinese journal|guang pu|remote sensing technology and application|"
    r"arid land geography|arid zone research|plateau meteorology|progress in geography|water saving irrigation|"
    r"resources and environment in the yangtze|journal of chinese soil|journal of geo.?information science|"
    r"world regional studies|national remote sensing bulletin|journal of irrigation and drainage|journal of nanjing|"
    r"korean journal of remote sensing|journal of the korean society|iranian journal|sovremennye|revista brasileira|"
    r"ra e ga|investigaciones geograficas|boletin de la asociacion|ciencia florestal|^floresta$|geodezia|anuario|"
    r"revista de teledeteccion|turkish journal of remote sensing|revista colombiana", re.I)
s['non_english_journal'] = s.journal.fillna('').map(lambda j: bool(NONENG.search(j)))
def final(x):
    if x.screen_v2 != 'I': return {'E-R': 'Satellite remote sensing not the primary data source', 'E-V': 'No vegetation variable analysed',
        'E-C': 'No climate driver or climate-related vegetation response', 'U': 'Uncertain, conservatively excluded'}[x.screen_v2]
    if x.non_english_journal: return 'Non-English publication (journal language)'
    return 'Included'
s['status_v2'] = s.apply(final, axis=1)
print(s.status_v2.value_counts().to_string())
inc = s[s.status_v2 == 'Included'].copy()
# metadata from the Scopus export
raw = pd.read_csv(os.path.join(ROOT, 'data', 'step1_scopus_raw.csv')); raw['dn'] = raw.doi.map(norm)
old = pd.read_excel(os.path.join(ROOT, 'data', 'step5_master_clean_19_4_2026.xlsx'), sheet_name='Master Clean'); old['dn'] = old.doi.map(norm)
inc['dn'] = inc.doi.map(norm)
rawi = raw.drop_duplicates('dn').set_index('dn'); oldi = old.drop_duplicates('dn').set_index('dn')
t60 = raw.assign(k=raw.title.str[:60].str.lower()).drop_duplicates('k').set_index('k')
rows = []
for x in inc.itertuples():
    o = oldi.loc[x.dn] if x.dn in oldi.index and x.dn != 'nan' else None
    rw = rawi.loc[x.dn] if x.dn in rawi.index and x.dn != 'nan' else (t60.loc[str(x.title)[:60].lower()] if str(x.title)[:60].lower() in t60.index else None)
    rows.append(dict(doi=x.doi, title=x.full_title, authors=(o['authors'] if o is not None else (rw['authors'] if rw is not None else '')),
        year=int(x.year) if x.year == x.year else (int(rw['year']) if rw is not None and rw['year'] == rw['year'] else None), journal=x.journal, cited_by=(o['cited_by'] if o is not None else (rw['cited_by'] if rw is not None else None)),
        author_country=(o['author_country'] if o is not None else (rw['country'] if rw is not None else None)),
        row_id_S1=x.row_id, in_v1=o is not None))
m = pd.DataFrame(rows)
# region and Global North/South: same lookup as the original corpus
reg = old.dropna(subset=['author_country']).drop_duplicates('author_country').set_index('author_country')[['geographic_region', 'global_north_south']]
m = m.join(reg, on='author_country')
print('countries without region:', sorted(m.loc[m.geographic_region.isna(), 'author_country'].dropna().unique()))
m.insert(0, 'No', range(1, len(m) + 1))
for c in ['code_url', 'data_url', 'sensors', 'r2', 'rmse', 'mae', 'biome', 'study_area_country']: m[c] = None
# PDF linking: old links via DOI, then DOI in file name / first page, then title match
TXT = os.path.join(REV, 'pdf_text'); stems = [os.path.basename(f)[:-4] for f in glob.glob(os.path.join(TXT, '*.txt'))]
oldlink = json.load(open(os.path.join(REV, 'scripts', 'pdf_link.json')))
stem_doi = {st: norm(old.loc[i, 'doi']) for st, i in oldlink.items() if i < len(old)}
DOIRE = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
def nt(t): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()).split())
oa = json.load(open(os.path.join(OUT, 'oa_fetch_log.json'))).get('done', {}) if os.path.exists(os.path.join(OUT, 'oa_fetch_log.json')) else {}
for dd, ok in oa.items():
    if ok: stem_doi['v2_' + re.sub(r'[^A-Za-z0-9._-]', '_', dd)] = norm(dd)
for st in stems:
    if st in stem_doi: continue
    mm = re.search(r'(10\.\d{4,9})[_/]([-._;()A-Za-z0-9]+)', st)
    if mm: stem_doi[st] = norm(mm.group(1) + '/' + mm.group(2)); continue
    txt = open(os.path.join(TXT, st + '.txt'), errors='ignore').read()[:6000]
    h = DOIRE.findall(txt)
    if h: stem_doi[st] = norm(h[0])
    else:
        head = nt(txt[:1500])
        for x in m.itertuples():
            if len(nt(x.title)) > 30 and nt(x.title)[:60] in head: stem_doi[st] = norm(x.doi) if str(x.doi) != 'nan' else 'title:' + str(x.No); break
m['dn'] = m.doi.map(norm); dn2row = {dn: i for i, dn in enumerate(m.dn)}
link = {}
for st, dn in stem_doi.items():
    i = dn2row.get(dn, int(dn[6:]) - 1 if dn.startswith('title:') else None)
    if i is not None:
        sz = os.path.getsize(os.path.join(TXT, st + '.txt'))
        if i not in link.values() or sz > max(os.path.getsize(os.path.join(TXT, k + '.txt')) for k, v in link.items() if v == i):
            for k in [k for k, v in link.items() if v == i]: del link[k]
            link[st] = i
m['pdf_filename'] = None
for st, i in link.items(): m.loc[i, 'pdf_filename'] = st + '.pdf'
m['tier'] = m.pdf_filename.notna().map({True: 'Full text (Tier 2)', False: 'Bibliographic only (Tier 1)'})
json.dump(link, open(os.path.join(OUT, 'pdf_link_v2.json'), 'w'))
m.drop(columns='dn').to_excel(os.path.join(OUT, 'master_v2.xlsx'), sheet_name='Master Clean', index=False)
s.to_csv(os.path.join(W, 'screening_v2_log.csv'), index=False)
print('included', len(m), '| full text', m.pdf_filename.notna().sum(), '| in old corpus', m.in_v1.sum(), '| old full text kept',
      (m.in_v1 & m.pdf_filename.notna()).sum())

# complete region lookup (the original lookup left some countries, e.g. Ireland and Viet Nam, as 'Other / Unknown')
REGION = {**{c: 'Europe' for c in ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czech Republic', 'Denmark', 'Finland', 'France',
    'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russian Federation',
    'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom']},
    **{c: 'East Asia' for c in ['China', 'Hong Kong', 'Japan', 'South Korea', 'Taiwan']},
    **{c: 'North America' for c in ['United States', 'Canada']},
    **{c: 'South Asia' for c in ['Bangladesh', 'India', 'Nepal', 'Pakistan']},
    **{c: 'Southeast Asia' for c in ['Indonesia', 'Malaysia', 'Singapore', 'Thailand', 'Viet Nam']},
    **{c: 'Middle East & N. Africa' for c in ['Algeria', 'Iran', 'Iraq', 'Israel', 'Jordan', 'Lebanon', 'Morocco', 'Oman', 'Saudi Arabia',
    'Turkey', 'United Arab Emirates']},
    **{c: 'Sub-Saharan Africa' for c in ['Cameroon', 'Ethiopia', 'Nigeria', 'South Africa', 'Tanzania', 'Uganda']},
    **{c: 'Latin America' for c in ['Argentina', 'Brazil', 'Chile', 'Ecuador', 'Mexico', 'Puerto Rico']},
    **{c: 'Oceania' for c in ['Australia', 'New Zealand']}, 'Kazakhstan': 'Central Asia'}
m = pd.read_excel(os.path.join(OUT, 'master_v2.xlsx'))
m['geographic_region'] = m.author_country.map(REGION).fillna('Other / Unknown')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geo
m['global_north_south'] = m.author_country.map(lambda c: 'Global North' if c in geo.NORTH_M49 else 'Global South')
m.to_excel(os.path.join(OUT, 'master_v2.xlsx'), sheet_name='Master Clean', index=False)
print(m.geographic_region.value_counts().to_string()); print(m.global_north_south.value_counts().to_string())
