# -*- coding: utf-8 -*-
"""Cross-check every quantitative claim in the revised manuscript against the data."""
import re, json
import pandas as pd, numpy as np
from docx import Document
from docx.text.paragraph import Paragraph
from collections import Counter
import geo

DOC = '/home/claude/work/out/VegeClimate Review Paper WithCitations 25_04_2026.docx'
e = pd.read_csv('/home/claude/work/out/fulltext_extraction.csv')
d = pd.read_excel('/mnt/user-data/uploads/vegiclimate_review/data/step5_master_clean_19_4_2026.xlsx',
                  sheet_name='Master Clean')
d['ns'] = d.author_country.apply(lambda c: 'Global North' if c in geo.NORTH_M49 else 'Global South')
d['ns_hi'] = d.author_country.apply(
    lambda c: 'Global North' if c in (geo.NORTH_M49 | geo.HIGH_INCOME_EXTRA) else 'Global South')
N, NF = len(d), len(e)

def tally(col):
    c = Counter()
    for s in e[col].fillna(''):
        for k in str(s).split(';'):
            if k: c[k] += 1
    return c
S, I, P, M, C = tally('sensors'), tally('indexs'), tally('products'), tally('methods'), tally('climates')
PL = tally('platforms'); DOM = tally('domains'); BIO = tally('biomes')
dp = e.domain_primary.value_counts(); bp = e.biome_primary.value_counts()
pct = lambda n, den=NF: round(100 * n / den, 1)

checks = []
def chk(name, expected, got):
    ok = (abs(expected - got) < 1e-6) if isinstance(expected, float) else (expected == got)
    checks.append((name, expected, got, 'PASS' if ok else 'FAIL'))

# corpus
chk('included studies', 757, N)
chk('full-text studies', 455, NF)
chk('full-text share %', 60.1, round(100*NF/N, 1))
chk('journals', 208, d.journal.nunique())
# years
y = d.year.value_counts()
for yr, v in [(2019, 47), (2021, 62), (2022, 87), (2023, 74), (2024, 120), (2025, 137)]:
    chk(f'studies {yr}', v, int(y[yr]))
chk('2021-2025 total', 480, int(sum(y.get(k, 0) for k in range(2021, 2026))))
chk('2021-2025 %', 63.4, pct(sum(y.get(k, 0) for k in range(2021, 2026)), N))
chk('max annual 2000-2011', 11, int(max(y.get(k, 0) for k in range(2000, 2012))))
ft23 = d[d.year.between(2023, 2025)].doi.isin(e.doi).sum()
chk('full text 2023-25', 250, int(ft23)); chk('included 2023-25', 331, int((d.year.between(2023,2025)).sum()))
ft14 = d[d.year <= 2014].doi.isin(e.doi).sum()
chk('full text <=2014', 27, int(ft14)); chk('included <=2014', 98, int((d.year <= 2014).sum()))
# geography
reg = d.geographic_region.value_counts()
for r, v in [('East Asia', 244), ('Europe', 208), ('North America', 147), ('South Asia', 31),
             ('Middle East & N. Africa', 30), ('Latin America', 27), ('Sub-Saharan Africa', 21),
             ('Southeast Asia', 15), ('Oceania', 15), ('Other / Unknown', 19)]:
    chk(f'region {r}', v, int(reg[r]))
chk('top3 regions %', 79.1, pct(244 + 208 + 147, N))
chk('Global North M49', 397, int((d.ns == 'Global North').sum()))
chk('Global North M49 %', 52.4, pct((d.ns == 'Global North').sum(), N))
chk('Global South M49', 360, int((d.ns == 'Global South').sum()))
chk('Global South M49 %', 47.6, pct((d.ns == 'Global South').sum(), N))
chk('Global North +HI', 421, int((d.ns_hi == 'Global North').sum()))
chk('Global North +HI %', 55.6, pct((d.ns_hi == 'Global North').sum(), N))
chk('Global South +HI %', 44.4, pct((d.ns_hi == 'Global South').sum(), N))
chk('China first-author', 208, int((d.author_country == 'China').sum()))
chk('China %', 27.5, pct((d.author_country == 'China').sum(), N))
south_nc = int(((d.ns == 'Global South') & (d.author_country != 'China')).sum())
chk('Global South excl China', 152, south_nc); chk('Global South excl China %', 20.1, pct(south_nc, N))
chk('SSA+SEA+LatAm %', 8.3, pct(21 + 15 + 27, N))
sa = d.study_area_country.value_counts()
for k, v in [('China', 84), ('United States', 37), ('Canada', 18), ('India', 16), ('Brazil', 15)]:
    chk(f'study area {k}', v, int(sa[k]))
# sensors
chk('sensor families', 26, len(S))
for k, v in [('Landsat', 234), ('MODIS', 203), ('Sentinel-2', 198), ('SAR (generic / other)', 119),
             ('Sentinel-1', 90), ('Airborne / spaceborne LiDAR (generic)', 81), ('AVHRR / GIMMS', 62),
             ('ALOS PALSAR', 46), ('GEDI', 26), ('ICESat / ICESat-2', 14),
             ('Hyperion / EnMAP / PRISMA / DESIS', 23), ('RADARSAT', 6), ('TerraSAR-X / TanDEM-X', 10),
             ('OCO-2/3, GOSAT, GOME-2, TROPOMI', 8)]:
    chk(f'sensor {k}', v, S[k])
for k, v in [('Landsat', 51.4), ('MODIS', 44.6), ('Sentinel-2', 43.5), ('SAR (generic / other)', 26.2),
             ('Sentinel-1', 19.8), ('Airborne / spaceborne LiDAR (generic)', 17.8), ('AVHRR / GIMMS', 13.6),
             ('ALOS PALSAR', 10.1), ('GEDI', 5.7), ('ICESat / ICESat-2', 3.1),
             ('Hyperion / EnMAP / PRISMA / DESIS', 5.1), ('OCO-2/3, GOSAT, GOME-2, TROPOMI', 1.8)]:
    chk(f'sensor% {k}', v, pct(S[k]))
chk('SAR union', 136, int(e.uses_sar.sum())); chk('SAR union %', 29.9, pct(e.uses_sar.sum()))
chk('multi-sensor', 286, int(e.multi_sensor_fusion.sum())); chk('multi-sensor %', 62.9, pct(e.multi_sensor_fusion.sum()))
# indices
chk('any index', 386, int((e['indexs'].fillna('').str.len() > 0).sum()))
chk('any index %', 84.8, pct((e['indexs'].fillna('').str.len() > 0).sum()))
for k, v in [('NDVI', 350), ('EVI', 128), ('SAVI / MSAVI / OSAVI', 67), ('NDWI', 56),
             ('NDMI / LSWI', 31), ('NBR / dNBR', 29), ('EVI2', 21), ('VCI', 12), ('VHI', 8),
             ('TCI', 9), ('kNDVI', 5), ('NIRv', 6)]:
    chk(f'index {k}', v, I[k])
for k, v in [('NDVI', 76.9), ('EVI', 28.1), ('SAVI / MSAVI / OSAVI', 14.7), ('NDWI', 12.3),
             ('NDMI / LSWI', 6.8), ('NBR / dNBR', 6.4), ('EVI2', 4.6), ('VCI', 2.6)]:
    chk(f'index% {k}', v, pct(I[k]))
chk('drought index cluster studies', 14, int(e['indexs'].fillna('').str.contains('VCI|VHI|TCI').sum()))
# products
for k, v in [('AGB / biomass product', 99), ('LAI', 85), ('ET / evapotranspiration', 84),
             ('Soil moisture', 75), ('GPP', 39), ('NPP', 21), ('SIF', 18)]:
    chk(f'product {k}', v, P[k])
for k, v in [('AGB / biomass product', 21.8), ('LAI', 18.7), ('ET / evapotranspiration', 18.5),
             ('Soil moisture', 16.5), ('GPP', 8.6), ('NPP', 4.6), ('SIF', 4.0)]:
    chk(f'product% {k}', v, pct(P[k]))
chk('SIF earliest year', 2021, int(e[e['products'].fillna('').str.contains('SIF')].year.min()))
# methods
for k, v in [('Random Forest', 163), ('Linear / multiple regression', 134), ('SVM / SVR', 71),
             ('Gradient boosting / XGBoost / LightGBM', 35), ('ANN / MLP', 33),
             ('PLS / PLSR', 17), ('Mann-Kendall / Sen slope', 48),
             ('Time-series break detection (BFAST/LandTrendr/CCDC)', 16),
             ('CNN (incl. ResNet, VGG, DeepLab)', 24), ('U-Net', 10), ('LSTM / GRU / RNN', 10),
             ('Transformer / attention', 4), ('Deep learning (generic)', 45),
             ('Explainable AI (SHAP/LIME)', 10)]:
    chk(f'method {k}', v, M[k])
for k, v in [('Random Forest', 35.8), ('Linear / multiple regression', 29.5), ('SVM / SVR', 15.6),
             ('Gradient boosting / XGBoost / LightGBM', 7.7), ('ANN / MLP', 7.3), ('PLS / PLSR', 3.7),
             ('Mann-Kendall / Sen slope', 10.5), ('CNN (incl. ResNet, VGG, DeepLab)', 5.3),
             ('U-Net', 2.2), ('LSTM / GRU / RNN', 2.2), ('Transformer / attention', 0.9),
             ('Deep learning (generic)', 9.9), ('Explainable AI (SHAP/LIME)', 2.2)]:
    chk(f'method% {k}', v, pct(M[k]))
chk('GEE', 125, PL['Google Earth Engine']); chk('GEE %', 27.5, pct(PL['Google Earth Engine']))
chk('deep learning', 52, int(e.uses_deep_learning.sum())); chk('deep learning %', 11.4, pct(e.uses_deep_learning.sum()))
chk('any ML', 208, int(e.uses_any_ml.sum())); chk('any ML %', 45.7, pct(e.uses_any_ml.sum()))
chk('non-ML %', 54.3, round(100 - pct(e.uses_any_ml.sum()), 1))
chk('DL pre-2020', 0, int(e[e.year < 2020].uses_deep_learning.sum()))
s2022 = e[e.year.between(2020, 2022)]
chk('DL 2020-22 n', 7, int(s2022.uses_deep_learning.sum())); chk('2020-22 studies', 128, len(s2022))
chk('DL 2020-22 %', 5.5, round(100*s2022.uses_deep_learning.mean(), 1))
s2025 = e[e.year.between(2023, 2025)]
chk('DL 2023-25 n', 45, int(s2025.uses_deep_learning.sum())); chk('2023-25 studies', 250, len(s2025))
chk('DL 2023-25 %', 18.0, round(100*s2025.uses_deep_learning.mean(), 1))
chk('XAI earliest', 2022, int(e[e.methods.fillna('').str.contains('Explainable')].year.min()))
# climate
chk('any climate', 361, int((e['climates'].fillna('').str.len() > 0).sum()))
chk('any climate %', 79.3, pct((e['climates'].fillna('').str.len() > 0).sum()))
for k, v in [('Temperature', 283), ('Precipitation', 279), ('Drought (general)', 147),
             ('Drought index (SPI/SPEI/PDSI/scPDSI)', 25), ('Soil moisture', 73),
             ('Solar radiation / PAR', 48), ('Snow cover', 25), ('Permafrost', 27),
             ('Heatwave / extreme events', 31), ('Vapour pressure deficit', 11),
             ('Atmospheric CO2', 19)]:
    chk(f'climate {k}', v, C[k])
for k, v in [('Temperature', 62.2), ('Precipitation', 61.3), ('Drought (general)', 32.3),
             ('Drought index (SPI/SPEI/PDSI/scPDSI)', 5.5), ('Soil moisture', 16.0),
             ('Solar radiation / PAR', 10.5), ('Snow cover', 5.5), ('Permafrost', 5.9),
             ('Heatwave / extreme events', 6.8), ('Vapour pressure deficit', 2.4),
             ('Atmospheric CO2', 4.2)]:
    chk(f'climate% {k}', v, pct(C[k]))
# domains
for k, v in [('Phenology', 148), ('Biomass & carbon stock', 109), ('Greening / browning trends', 103),
             ('Land cover / land use change', 101), ('Carbon & water flux', 87),
             ('Drought stress & vegetation response', 47), ('Wildfire & post-fire recovery', 47),
             ('Vegetation degradation & restoration', 38), ('Crop yield & agriculture', 32),
             ('Species distribution & biodiversity', 7)]:
    chk(f'domain {k}', v, DOM[k])
for k, v in [('Phenology', 32.5), ('Biomass & carbon stock', 24.0), ('Greening / browning trends', 22.6),
             ('Land cover / land use change', 22.2), ('Carbon & water flux', 19.1),
             ('Drought stress & vegetation response', 10.3), ('Wildfire & post-fire recovery', 10.3),
             ('Vegetation degradation & restoration', 8.4), ('Crop yield & agriculture', 7.0),
             ('Species distribution & biodiversity', 1.5)]:
    chk(f'domain% {k}', v, pct(DOM[k]))
chk('primary phenology', 111, int(dp['Phenology'])); chk('primary phenology %', 24.4, pct(dp['Phenology']))
chk('primary biomass', 94, int(dp['Biomass & carbon stock'])); chk('primary biomass %', 20.7, pct(dp['Biomass & carbon stock']))
chk('primary unclassified', 54, int(dp['Unclassified'])); chk('primary unclassified %', 11.9, pct(dp['Unclassified']))
# biomes
chk('biome assignable', 426, NF - int(bp['Unclassified']))
chk('biome assignable %', 93.6, pct(NF - bp['Unclassified']))
forest = int(bp[[k for k in bp.index if k.startswith('Forest')]].sum())
chk('forest primary', 206, forest); chk('forest primary %', 45.3, pct(forest))
chk('forest unspecified', 172, int(bp['Forest (unspecified)']))
chk('forest tropical', 19, int(bp['Forest (tropical)']))
chk('forest temperate', 10, int(bp['Forest (temperate)']))
chk('forest boreal', 5, int(bp['Forest (boreal)']))
for k, n, p in [('Cropland / agriculture', 52, 11.4), ('Wetland (non-peat)', 45, 9.9),
                ('Grassland / steppe', 43, 9.5), ('Tundra / alpine', 24, 5.3),
                ('Desert / dryland', 26, 5.7), ('Savanna', 11, 2.4), ('Shrubland', 8, 1.8),
                ('Peatland', 6, 1.3), ('Urban vegetation', 5, 1.1)]:
    chk(f'primary biome {k}', n, int(bp[k])); chk(f'primary biome% {k}', p, pct(bp[k]))
chk('dryland mentions', 78, BIO['Desert / dryland']); chk('dryland mentions %', 17.1, pct(BIO['Desert / dryland']))
chk('peatland mentions', 12, BIO['Peatland']); chk('peatland mentions %', 2.6, pct(BIO['Peatland']))
under = int(bp[['Desert / dryland', 'Savanna', 'Shrubland', 'Peatland']].sum())
chk('under-represented biomes', 51, under); chk('under-represented %', 11.2, pct(under))
# open science
cs = e.code_status.value_counts(); ds = e.data_status.value_counts()
chk('code repo', 40, int(cs['Repository link'])); chk('code repo %', 8.8, pct(cs['Repository link']))
chk('data repo', 34, int(ds['Repository link'])); chk('data repo %', 7.5, pct(ds['Repository link']))
chk('code on request', 94, int(cs['On request'])); chk('code on request %', 20.7, pct(cs['On request']))
chk('data on request', 97, int(ds['On request'])); chk('data on request %', 21.3, pct(ds['On request']))
chk('data stmt no link', 173, int(ds['Statement, no link'])); chk('data stmt no link %', 38.0, pct(ds['Statement, no link']))
chk('code not stated', 314, int(cs['Not stated'])); chk('code not stated %', 69.0, pct(cs['Not stated']))
chk('data not stated', 151, int(ds['Not stated'])); chk('data not stated %', 33.2, pct(ds['Not stated']))
chk('code unavailable', 5, int(cs['Explicitly unavailable'])); chk('code unavailable %', 1.1, pct(cs['Explicitly unavailable']))
per = {'2015-2019': e[e.year.between(2015, 2019)], '2020-2022': s2022, '2023-2025': s2025,
       'pre-2015': e[e.year < 2015]}
for k, v in [('pre-2015', 0.0), ('2015-2019', 2.0), ('2020-2022', 7.0), ('2023-2025', 12.0)]:
    chk(f'code repo % {k}', v, round(100 * (per[k].code_status == 'Repository link').mean(), 1))
for k, v in [('pre-2015', 3.7), ('2015-2019', 4.0), ('2020-2022', 5.5), ('2023-2025', 9.6)]:
    chk(f'data repo % {k}', v, round(100 * (per[k].data_status == 'Repository link').mean(), 1))
# metrics
for m, n, p in [('r2', 186, 40.9), ('rmse', 121, 26.6), ('mae', 27, 5.9), ('oa', 68, 14.9),
                ('kappa', 27, 5.9), ('f1', 12, 2.6)]:
    chk(f'{m} studies', n, int((e[m + '_n'] > 0).sum())); chk(f'{m} %', p, pct((e[m + '_n'] > 0).sum()))
chk('total R2 values', 1408, int(e.r2_n.sum()))
chk('median within-study R2', 0.71, round(e.r2_median.median(), 2))
chk('R2 Q1', 0.57, round(e.r2_median.quantile(.25), 2)); chk('R2 Q3', 0.82, round(e.r2_median.quantile(.75), 2))
chk('median study max R2', 0.85, round(e.r2_max.median(), 2))
chk('OA median', 88.0, round(e.oa_median.median(), 1))
chk('OA Q1', 78.0, round(e.oa_median.quantile(.25), 1)); chk('OA Q3', 92.8, round(e.oa_median.quantile(.75), 1))
chk('kappa median', 0.82, round(e.kappa_median.median(), 2))
r2d = e[e.r2_median.notna()].groupby('domain_primary').r2_median
for k, n, med in [('Crop yield & agriculture', 4, 0.88), ('Land cover / land use change', 8, 0.79),
                  ('Phenology', 39, 0.76), ('Carbon & water flux', 17, 0.72),
                  ('Biomass & carbon stock', 68, 0.71),
                  ('Drought stress & vegetation response', 9, 0.57)]:
    chk(f'R2 domain n {k}', n, int(r2d.count()[k])); chk(f'R2 domain med {k}', med, round(r2d.median()[k], 2))
rm = pd.read_excel('/home/claude/work/out/Revised_Results_Tables.xlsx', sheet_name='T18_rmse_biomass')
chk('biomass RMSE studies', 34, int(rm.doi.nunique())); chk('biomass RMSE values', 193, len(rm))
chk('biomass RMSE median', 27.2, round(rm.rmse.median(), 1))
chk('biomass RMSE Q1', 14.5, round(rm.rmse.quantile(.25), 1))
chk('biomass RMSE Q3', 45.5, round(rm.rmse.quantile(.75), 1))


# ---------------------------------------------------------------- PRISMA retrieval flow
import csv, json as _json
clean = lambda s: re.sub(r'\.(pdf|xml|html)$', '', str(s).strip().lower().rstrip('.,;)'))
DD = '/mnt/user-data/uploads/vegiclimate_review/data/'
rows = list(csv.DictReader(open(DD + 'step3_pdf_download_log.csv', encoding='latin-1')))
kk = list(rows[0].keys())[0]
sought = {clean(r[kk]) for r in rows if r[kk] and clean(r[kk]) not in ('nan', '')}
cache = {clean(a): b for a, b in _json.load(
    open(DD + 'step3_fulltext_cache.json', encoding='utf-8', errors='ignore')).items()}
retrieved_doi = set(_json.load(open('/home/claude/work/out/retrieved_dois.json')))
final = set(d.doi.apply(clean))
ftset = set(e.doi.apply(clean))
excluded = sought - final
exc_logged = {dd: v for dd, v in cache.items() if v.get('ft_decision') == 'EXCLUDE' and dd in sought}
rr = pd.Series({dd: str(v.get('ft_reason') or '') for dd, v in exc_logged.items()})
NOTEXT = rr.str.contains('title only|no content|No full record|not provided|no text|unable to assess'
                         '|cannot assess|no abstract|not retrieved|Unresolved|no full text|No full text',
                         case=False, regex=True)

chk('sought for retrieval (rows)', 1482, len(rows))
chk('records with no DOI', 25, len(rows) - len(sought))
chk('full text retrieved', 572, len(ftset) + len(excluded & retrieved_doi))
chk('  retrieved -> included', 455, len(ftset))
chk('  retrieved -> excluded', 117, len(excluded & retrieved_doi))
chk('full text NOT retrieved', 910, 1482 - (len(ftset) + len(excluded & retrieved_doi)))
chk('  not retrieved -> retained', 302, len(final) - len(ftset))
chk('  not retrieved -> excluded', 608, 725 - len(excluded & retrieved_doi))
chk('excluded total', 725, 757 + 725 - len(final))
chk('  failed a stated criterion', 458, int((~NOTEXT).sum()))
chk('  could not be assessed', 124, int(NOTEXT.sum()))
chk('  no decision logged', 143, 725 - len(exc_logged))
chk('retrieval rate %', 38.6, round(100 * 572 / 1482, 1))
chk('cached INCLUDE not in final corpus', 85,
    len({dd for dd, v in cache.items() if v.get('ft_decision') == 'INCLUDE'} & sought) - len(final))

# ---------------------------------------------------------------- review sensitivity
rs = _json.load(open('/home/claude/work/out/review_sensitivity.json'))
chk('review articles in full-text corpus', 20, rs['n_reviews'])
chk('review share %', 4.4, round(100 * rs['n_reviews'] / NF, 1))
chk('primary studies', 435, rs['n_primary'])
chk('max sensitivity shift (pp)', 1.9, rs['max_pp'])
sens = pd.read_excel('/home/claude/work/out/Revised_Results_Tables.xlsx',
                     sheet_name='T19_review_sensitivity').set_index('Quantity')
for q, a, b in [('Landsat', 51.4, 50.3), ('MODIS', 44.6, 44.1), ('Sentinel-2', 43.5, 42.5),
                ('NDVI', 76.9, 76.3), ('Random Forest', 35.8, 35.2), ('Any deep learning', 11.4, 10.6)]:
    chk(f'sens {q} all %', a, float(sens.loc[q, '% (all)']))
    chk(f'sens {q} primary %', b, float(sens.loc[q, '% (primary only)']))
raw2 = pd.read_csv(DD + 'step1_scopus_raw.csv', encoding='latin-1', low_memory=False)
raw2.columns = ['title','abstract','year','doi','authors','journal','doc_type','language','cited_by','country','source']
raw2['doi_n'] = raw2.doi.apply(clean)
e2 = e.copy(); e2['doi_n'] = e2.doi.apply(clean)
e2 = e2.merge(raw2[['doi_n','doc_type']].drop_duplicates('doi_n'), on='doi_n', how='left')
e2['nsens'] = e2.sensors.fillna('').apply(lambda s: len([q for q in s.split(';') if q]))
chk('mean sensor families, reviews', 6.6, round(e2.loc[e2.doc_type=='Review','nsens'].mean(), 1))
chk('mean sensor families, primary', 2.71, round(e2.loc[e2.doc_type!='Review','nsens'].mean(), 2))

res = pd.DataFrame(checks, columns=['Claim', 'Stated in manuscript', 'Recomputed from data', 'Result'])
res.to_csv('/home/claude/work/out/verification_checks.csv', index=False)
bad = res[res.Result == 'FAIL']
print(f'{len(res)} checks, {len(bad)} FAIL')
if len(bad): print(bad.to_string(index=False))
