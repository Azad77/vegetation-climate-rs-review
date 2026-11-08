"""verify_v2.py - computational checks for the revised manuscript (corpus v2): recomputes key reported numbers from the
archived outputs and checks that the manuscript states them. Writes Supplementary Table S12."""
import os, json, re, docx, pandas as pd, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import geo, corpus
REV = corpus.REV; RR = os.path.join(REV, 'reviewer_response')
m = pd.read_excel(corpus.MASTER); e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
doc = docx.Document(os.path.join(REV, 'Rasul_VegeClimate Review_R1.docx'))
TXT = ' '.join(p.text for p in doc.paragraphs) + ' ' + ' '.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
N, NF = len(m), len(e); p1 = lambda k, n: f'{100 * k / n:.1f}%'
x = pd.ExcelFile(os.path.join(REV, 'Revised_Results_Tables.xlsx'))
def tab(sh, key): t = x.parse(sh); r = t[t.iloc[:, 0] == key].iloc[0]; return int(r.iloc[1])
C = []
def chk(name, s): C.append((name, s, 'PASS' if s in TXT else 'FAIL'))
chk('included', f'{N} studies'); chk('full text', f'{NF} of the {N}'); chk('full-text share', p1(NF, N))
y = m.year.value_counts(); r2125 = int(sum(y.get(k, 0) for k in range(2021, 2026))); chk('2021-25', f'{r2125} studies ({p1(r2125, N)})')
for yr in (2021, 2022, 2024, 2025): chk(f'year {yr}', str(int(y[yr])))
reg = m.geographic_region.value_counts()
for r in ['East Asia', 'Europe', 'North America']: chk(r, f'n = {reg[r]}, {p1(reg[r], N)}')
gn = m.author_country.isin(geo.NORTH_M49).sum(); chk('GN', f'{gn} studies ({p1(gn, N)})')
ch = (m.author_country == 'China').sum(); chk('China', f'{ch} first-author studies ({p1(ch, N)}')
ex = json.load(open(os.path.join(RR, 'prisma_v2_counts.json')))['excluded']
for k, v in ex.items(): chk('excluded ' + k[:30], str(v))
for sh, keys in [('T6_sensors', ['MODIS', 'Landsat', 'Sentinel-2']),
                 ('T9_methods', ['Linear / multiple regression', 'Random Forest', 'SVM / SVR']), ('T11_domains', ['Phenology', 'Biomass & carbon stock'])]:
    for k in keys: n = tab(sh, k); chk(f'{sh} {k}', f'n = {n}, {p1(n, NF)}')
for k in ['NDVI', 'EVI']: n = tab('T7_indices', k); chk('index ' + k, f'{n} ({p1(n, NF)})')
n = tab('T6_sensors', 'AVHRR / GIMMS'); chk('AVHRR', f'{n} studies ({p1(n, NF)})')
ml = int(e.uses_any_ml.sum()); chk('any ML', f'{ml} full-text studies ({p1(ml, NF)})')
dl = int(e.uses_deep_learning.sum()); chk('DL', f'{dl} studies ({p1(dl, NF)}')
r2 = int((e.r2_n > 0).sum()); chk('R2', f'{r2} of the {NF} full-text studies ({p1(r2, NF)})')
rm = int((e.rmse_n > 0).sum()); chk('RMSE', f'{rm} studies ({p1(rm, NF)})')
cr = int((e.code_status == 'Repository link').sum()); chk('code repo', f'{cr} ({p1(cr, NF)})')
dr = int((e.data_status == 'Repository link').sum()); chk('data repo', f'{dr} ({p1(dr, NF)})')
D = pd.read_csv(os.path.join(RR, 'design', 'study_design_quality.csv')); chk('Q2', f'{100 * D.Q2_independent_test.mean():.1f}%')
S10 = pd.read_csv(os.path.join(RR, 'Table_S10_biome_representation.csv'))
for c in ['Savanna', 'Tundra / alpine']: chk('ratio ' + c, f"{S10[S10.Class == c].Ratio.iloc[0]:.2f}")
f13 = pd.read_csv(os.path.join(RR, 'Table_S13_forest_subset.csv')); chk('forest n', f'{int(e.biome_primary.str.contains("Forest").sum())} full-text studies')
T = pd.DataFrame(C, columns=['Check', 'Expected text', 'Result'])
T.to_csv(os.path.join(RR, 'Table_S12_computational_checks.csv'), index=False, encoding='utf-8-sig')
T.to_excel(os.path.join(RR, 'Table_S12_computational_checks.xlsx'), index=False)
print(len(T), 'checks,', (T.Result == 'FAIL').sum(), 'FAIL'); print(T[T.Result == 'FAIL'].to_string(index=False))
