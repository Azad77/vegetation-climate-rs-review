"""geography_biome.py - Reviewer 1, comment 6.
(A) Biome representation: share of full-text studies by primary biome against the share of ice-free land in the matching
    RESOLVE Ecoregions 2017 biome (Dinerstein et al., 2017; areas computed in Mollweide equal-area projection), plus three
    non-biome land classes from published extents (drylands 41.3%, MEA 2005; peatlands 2.84%, Xu et al. 2018; cropland 12%,
    FAO 2023). Representation ratio = study share / land share, 95% CI from the Wilson interval of the study share.
(B) First-author affiliation vs study area (deterministic study-area country, study_area.py).
Outputs -> ../reviewer_response/: Table_S10_biome_representation.csv, Table_S11_author_vs_study_area.csv, geography/geo_summary.json"""
import os, json, numpy as np, pandas as pd
import geo
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); R = os.path.join(REV, 'reviewer_response'); G = os.path.join(R, 'geography')
def wilson(k, n, z=1.96):
    p = k/n; c = (p + z*z/(2*n))/(1 + z*z/n); h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/(1 + z*z/n); return c-h, c+h
# ---------------- (A) biomes
A = pd.read_csv(os.path.join(G, 'biome_areas.csv')); A = A[A.BIOME_NAME != 'N/A']; LAND = A.km2.sum()
area = lambda nums: A[A.BIOME_NUM.isin(nums)].km2.sum() / LAND * 100
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv')); N = len(e)
bp = e.biome_primary.fillna('Unclassified')
CL = [  # label in corpus, corpus primary-biome labels, land share (%), source of land share
 ('Forest (all types)', ['Forest (temperate)', 'Forest (boreal)', 'Forest (tropical)', 'Forest (unspecified)'], area([1, 2, 3, 4, 5, 6]), 'RESOLVE biomes 1-6'),
 ('Grassland / steppe', ['Grassland / steppe'], area([8]), 'RESOLVE biome 8 (temperate grasslands, savannas & shrublands)'),
 ('Savanna', ['Savanna'], area([7]), 'RESOLVE biome 7 (tropical & subtropical grasslands, savannas & shrublands)'),
 ('Shrubland (Mediterranean-type)', ['Shrubland'], area([12]), 'RESOLVE biome 12 (Mediterranean forests, woodlands & scrub)'),
 ('Desert / dryland (biome)', ['Desert / dryland'], area([13]), 'RESOLVE biome 13 (deserts & xeric shrublands)'),
 ('Tundra / alpine', ['Tundra / alpine'], area([10, 11]), 'RESOLVE biomes 10-11 (montane grasslands; tundra)'),
 ('Wetland (non-peat, incl. mangrove)', ['Wetland (non-peat)'], area([9, 14]), 'RESOLVE biomes 9 and 14 (flooded grasslands; mangroves)'),
 ('Cropland (land use)', ['Cropland / agriculture'], 12.0, 'FAO (2023): ~12% of land area, 2021'),
 ('Peatland (land cover)', ['Peatland'], 2.84, 'Xu et al. (2018): 2.84% of land area'),
]
rows = []
for lab, keys, land, src in CL:
    k = int(bp.isin(keys).sum()); lo, hi = wilson(k, N)
    rows.append(dict(Class=lab, Studies_primary=k, Study_share_pct=round(100*k/N, 1), Land_share_pct=round(land, 1),
                     Ratio=round(100*k/N/land, 2), Ratio_CI=f'{100*lo/land:.2f}-{100*hi/land:.2f}', Land_share_source=src))
# drylands by aridity (overlaps several biomes): any mention vs MEA 41.3%
anyd = int(e.biomes.fillna('').str.contains('Desert / dryland').sum()); lo, hi = wilson(anyd, N)
rows.append(dict(Class='Drylands, aridity-defined (any mention)', Studies_primary=anyd, Study_share_pct=round(100*anyd/N, 1), Land_share_pct=41.3,
                 Ratio=round(100*anyd/N/41.3, 2), Ratio_CI=f'{100*lo/41.3:.2f}-{100*hi/41.3:.2f}', Land_share_source='MEA (Safriel & Adeel 2005): 41.3%; classes overlap'))
anyp = int(e.biomes.fillna('').str.contains('Peatland').sum()); lo, hi = wilson(anyp, N)
rows.append(dict(Class='Peatland (any mention)', Studies_primary=anyp, Study_share_pct=round(100*anyp/N, 1), Land_share_pct=2.84,
                 Ratio=round(100*anyp/N/2.84, 2), Ratio_CI=f'{100*lo/2.84:.2f}-{100*hi/2.84:.2f}', Land_share_source='Xu et al. (2018)'))
B = pd.DataFrame(rows); B.to_csv(os.path.join(R, 'Table_S10_biome_representation.csv'), index=False, encoding='utf-8-sig')
# biome-label check
K = json.load(open(os.path.join(R, 'validation', 'kwic_sample.json'))); BR = json.load(open(os.path.join(G, 'biome_reference.json')))
bok = [v[0] for k, v in BR.items() if k.startswith('S')]
# ---------------- (B) author vs study area
m = pd.read_excel(__import__('corpus').MASTER, sheet_name='Master Clean')
REG = m.groupby('author_country').geographic_region.agg(lambda x: x.mode()[0]).to_dict()
NORM = {'Korea, Republic of': 'South Korea', 'Iran, Islamic Republic of': 'Iran', 'Türkiye': 'Turkey', 'Syrian Arab Republic': 'Syria',
        'Tanzania, United Republic of': 'Tanzania', "Korea, Democratic People's Republic of": 'North Korea', 'Viet Nam': 'Vietnam',
        'Taiwan, Province of China': 'Taiwan', 'Bolivia, Plurinational State of': 'Bolivia', "Lao People's Democratic Republic": 'Laos'}
EXTRA = {'Kenya': 'Sub-Saharan Africa', 'Burkina Faso': 'Sub-Saharan Africa', 'Ghana': 'Sub-Saharan Africa', 'Madagascar': 'Sub-Saharan Africa',
         'Mali': 'Sub-Saharan Africa', 'Namibia': 'Sub-Saharan Africa', 'Niger': 'Sub-Saharan Africa', 'Senegal': 'Sub-Saharan Africa',
         'Tanzania': 'Sub-Saharan Africa', 'Cambodia': 'Southeast Asia', 'Cuba': 'Latin America', 'Paraguay': 'Latin America',
         'French Guiana': 'Latin America', 'Iran': 'Middle East & N. Africa', 'Syria': 'Middle East & N. Africa', 'Tunisia': 'Middle East & N. Africa',
         'Turkey': 'Middle East & N. Africa', 'Armenia': 'Europe', 'Azerbaijan': 'Europe', 'Mongolia': 'East Asia', 'South Korea': 'East Asia',
         'North Korea': 'East Asia', 'Greenland': 'North America', 'Antarctica': 'Other / Unknown'}
S = pd.read_csv(os.path.join(G, 'study_area.csv'))
S['sc'] = S.study_country.map(lambda c: NORM.get(c, c))
S['study_region'] = S.sc.map(lambda c: REG.get(c, EXTRA.get(c, c if c in ('MULTI', 'GLOBAL', 'UNDETERMINED') else 'Other / Unknown')))
S['author_region'] = S.author_country.map(REG)
NORTH = geo.NORTH_M49 | {'Greenland'}
S['study_NS'] = np.where(S.study_region.isin(['MULTI', 'GLOBAL', 'UNDETERMINED']), S.study_region, np.where(S.sc.isin(NORTH), 'Global North', 'Global South'))
S['author_NS'] = np.where(S.author_country.isin(geo.NORTH_M49), 'Global North', 'Global South')
S['same_country'] = S.sc == S.author_country
single = S[~S.study_region.isin(['MULTI', 'GLOBAL', 'UNDETERMINED'])]
T = (single.groupby('study_region').agg(Studies=('doi', 'size'), Same_country_first_author=('same_country', 'sum'),
        Global_North_first_author=('author_NS', lambda x: int((x == 'Global North').sum())))
     .sort_values('Studies', ascending=False))
T['Same_country_pct'] = (100*T.Same_country_first_author/T.Studies).round(1)
T['Global_North_first_author_pct'] = (100*T.Global_North_first_author/T.Studies).round(1)
T.to_csv(os.path.join(R, 'Table_S11_author_vs_study_area.csv'), encoding='utf-8-sig')
gs = single[single.study_NS == 'Global South']; gn = single[single.study_NS == 'Global North']
fa = S.author_region.value_counts(); sa = single.study_region.value_counts()
summ = dict(land_km2=float(LAND), biome_label_check=[int(sum(bok)), len(bok)],
            study_area_check=json.load(open(os.path.join(G, 'study_area_check_summary.json'))) if os.path.exists(os.path.join(G, 'study_area_check_summary.json')) else None,
            n_single=len(single), n_multi=int((S.study_region == 'MULTI').sum()), n_global=int((S.study_region == 'GLOBAL').sum()),
            n_undet=int((S.study_region == 'UNDETERMINED').sum()), same_country_pct=round(100*single.same_country.mean(), 1),
            gs_n=len(gs), gs_gn_author=int((gs.author_NS == 'Global North').sum()), gs_same_country=int(gs.same_country.sum()),
            gn_n=len(gn), gn_gs_author=int((gn.author_NS == 'Global South').sum()),
            china_study=int((single.sc == 'China').sum()), china_study_china_author=int(((single.sc == 'China') & single.same_country).sum()),
            author_vs_study_region=pd.DataFrame({'first_author_455': fa, 'study_area_single_country': sa}).fillna(0).astype(int).to_dict())
json.dump(summ, open(os.path.join(G, 'geo_summary.json'), 'w'), indent=1, default=str)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print(B.to_string(index=False)); print(T.to_string()); print(json.dumps({k: v for k, v in summ.items() if k != 'author_vs_study_region'}, indent=1)); print(pd.DataFrame(summ['author_vs_study_region']))
