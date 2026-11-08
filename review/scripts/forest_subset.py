"""forest_subset.py - Reviewer 2, comment 1: forest-primary vs other full-text studies (raw extraction counts, i.e. studies naming
a term at least twice; see Section 3.4 for the over-count of sensors). Output: ../reviewer_response/Table_S13_forest_subset.csv"""
import os, json, pandas as pd, numpy as np
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); R = os.path.join(REV, 'reviewer_response')
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
D = pd.read_csv(os.path.join(R, 'design', 'study_design_quality.csv'))[['doi', 'design', 'quality_score']]
e = e.merge(D, on='doi', how='left')
e['forest'] = e.biome_primary.fillna('').str.startswith('Forest')
has = lambda col, k: e[col].fillna('').str.split(';').apply(lambda L: k in L)
rows = []
def add(lab, mask):
    f, o = mask[e.forest], mask[~e.forest]
    p = stats.fisher_exact([[f.sum(), (~f).sum()], [o.sum(), (~o).sum()]])[1]
    rows.append(dict(Quantity=lab, Forest_n=int(f.sum()), Forest_pct=round(100*f.mean(), 1), Other_n=int(o.sum()), Other_pct=round(100*o.mean(), 1), Fisher_p=float(f'{p:.2g}')))
for k in ['Landsat', 'MODIS', 'Sentinel-2', 'AVHRR / GIMMS', 'GEDI']: add(f'Sensor: {k}', has('sensors', k))
add('Sensor: SAR (any)', e.uses_sar.astype(bool))
add('Sensor: LiDAR (generic)', has('sensors', 'Airborne / spaceborne LiDAR (generic)'))
for k in ['NDVI', 'EVI']: add(f'Index: {k}', has('indexs', k))
add('Product: SIF', has('products', 'SIF'))
for k in ['Random Forest', 'Linear / multiple regression', 'Mann-Kendall / Sen slope']: add(f'Method: {k}', has('methods', k))
add('Any machine learning', e.uses_any_ml.astype(bool)); add('Any deep learning', e.uses_deep_learning.astype(bool))
for k in ['Biomass & carbon stock', 'Phenology', 'Greening / browning trends', 'Wildfire & post-fire recovery', 'Drought stress & vegetation response', 'Land cover / land use change']:
    add(f'Primary domain: {k}', e.domain_primary == k)
add('Independent test described', e.design.isin(['Independent hold-out test', 'Spatially independent test']))
add('R2 reported', e.r2_n > 0)
T = pd.DataFrame(rows); T.to_csv(os.path.join(R, 'Table_S13_forest_subset.csv'), index=False, encoding='utf-8-sig')
T.to_excel(os.path.join(R, 'Table_S13_forest_subset.xlsx'), index=False)
pd.set_option('display.width', 200); print('forest n =', int(e.forest.sum()), ' other n =', int((~e.forest).sum())); print(T.to_string(index=False))
print(e[e.forest].biome_primary.value_counts().to_dict())
