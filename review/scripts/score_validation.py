"""score_validation.py - Reviewer 1, comment 4, step 2: scores the regex extraction against the reference labels.
Outputs -> ../reviewer_response/validation/validation_sheet_scored.csv, ../reviewer_response/Table_S7_extraction_validation.csv,
           validation_summary.json"""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(os.path.dirname(HERE), 'reviewer_response', 'validation')
K = json.load(open(os.path.join(V, 'kwic_sample.json'))); L = json.load(open(os.path.join(V, 'reference_labels.json')))
sheet = pd.read_csv(os.path.join(V, 'validation_sheet.csv'))
sid = {d: f'S{i:02d}' for i, d in enumerate(K, 1)}
sheet['study'] = sheet.doi.map(sid)
var = sheet.variable != 'Primary domain'
sheet.loc[var, 'reference_used'] = [int(v in L[s]['used']) for s, v in zip(sheet.study[var], sheet.variable[var])]
sheet.loc[~var, 'reference_used'] = [L[s]['domain_ok'] for s in sheet.study[~var]]
sheet['note'] = sheet.study.map(lambda s: L[s].get('note', ''))
sheet.to_csv(os.path.join(V, 'validation_sheet_scored.csv'), index=False, encoding='utf-8-sig')
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k/n; c = (p + z*z/(2*n))/(1 + z*z/n); h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/(1 + z*z/n); return (round(100*(c-h), 1), round(100*(c+h), 1))
def stats_(g):
    p = g.predicted_used.astype(int); r = g.reference_used.astype(int)
    tp, fp, fn, tn = int(((p == 1) & (r == 1)).sum()), int(((p == 1) & (r == 0)).sum()), int(((p == 0) & (r == 1)).sum()), int(((p == 0) & (r == 0)).sum())
    n = tp + fp + fn + tn; acc = (tp + tn)/n; pe = ((tp+fp)*(tp+fn) + (fn+tn)*(fp+tn))/n**2
    kap = (acc - pe)/(1 - pe) if pe < 1 else np.nan
    return dict(TP=tp, FP=fp, FN=fn, TN=tn, Accuracy=round(100*acc, 1), Precision=round(100*tp/(tp+fp), 1) if tp+fp else np.nan,
                Recall=round(100*tp/(tp+fn), 1) if tp+fn else np.nan, Kappa=round(kap, 2),
                Extracted_pct=round(100*(tp+fp)/n, 1), Reference_pct=round(100*(tp+fn)/n, 1))
VS = sheet[var].copy()
rows = [dict(Classification=v, **stats_(g)) for v, g in VS.groupby('variable', sort=False)]
groups = {'Sensors (6)': ['Landsat','MODIS','Sentinel-2','SAR (any)','LiDAR (any)','AVHRR / GIMMS'], 'Indices (2)': ['NDVI','EVI'],
          'Methods and platform (7)': ['Random Forest','Linear / multiple regression','SVM / SVR','Gradient boosting','Deep learning (any)','Mann-Kendall / Sen slope','Google Earth Engine']}
for gname, vs in groups.items(): rows.append(dict(Classification='Pooled: ' + gname, **stats_(VS[VS.variable.isin(vs)])))
rows.append(dict(Classification='Pooled: all 15 classifications', **stats_(VS)))
rows.append(dict(Classification='Pooled: all 15, excluding the review article', **stats_(VS[VS.study != 'S11'])))
T = pd.DataFrame(rows); T['Bias (pp)'] = (T.Extracted_pct - T.Reference_pct).round(1)
dm = sheet[~var].reference_used.astype(int)
T.to_csv(os.path.join(os.path.dirname(V), 'Table_S7_extraction_validation.csv'), index=False, encoding='utf-8-sig')
summ = {'n_studies': len(K), 'n_decisions': int(len(VS)), 'n_judged_from_text': int(VS.broad_hits.gt(0).sum()),
        'domain_correct': int(dm.sum()), 'domain_pct': round(100*dm.mean(), 1), 'domain_ci': wilson(int(dm.sum()), len(dm)),
        'pooled': rows[-2], 'pooled_excl_review': rows[-1],
        'fp_review': int(((VS.study == 'S11') & (VS.predicted_used.astype(int) == 1) & (VS.reference_used.astype(int) == 0)).sum()),
        'pdf_linkage_errors': [s for s in L if s.startswith('S') and 'LINKAGE' in L[s].get('note', '')]}
json.dump(summ, open(os.path.join(V, 'validation_summary.json'), 'w'), indent=1, default=str)
pd.set_option('display.width', 250); print(T.to_string(index=False)); print(json.dumps(summ, indent=1, default=str))

# ---- misclassification-corrected corpus prevalence: p_true = p_ext*PPV + (1-p_ext)*FOR, 95% CI by bootstrapping studies
e = pd.read_csv(os.path.join(os.path.dirname(HERE), 'fulltext_extraction.csv'))
H = {c: e[c].apply(json.loads) for c in ['sensor_hits', 'index_hits', 'method_hits', 'platform_hits']}
MAP = {'Landsat': ('sensor_hits', ['Landsat']), 'MODIS': ('sensor_hits', ['MODIS']), 'Sentinel-2': ('sensor_hits', ['Sentinel-2']),
       'SAR (any)': ('sensor_hits', ['Sentinel-1', 'ALOS PALSAR', 'RADARSAT', 'TerraSAR-X / TanDEM-X', 'SAR (generic / other)']),
       'LiDAR (any)': ('sensor_hits', ['Airborne / spaceborne LiDAR (generic)', 'GEDI', 'ICESat / ICESat-2']),
       'AVHRR / GIMMS': ('sensor_hits', ['AVHRR / GIMMS']), 'NDVI': ('index_hits', ['NDVI']), 'EVI': ('index_hits', ['EVI']),
       'Random Forest': ('method_hits', ['Random Forest']), 'Linear / multiple regression': ('method_hits', ['Linear / multiple regression']),
       'SVM / SVR': ('method_hits', ['SVM / SVR']), 'Gradient boosting': ('method_hits', ['Gradient boosting / XGBoost / LightGBM']),
       'Deep learning (any)': ('method_hits', ['CNN (incl. ResNet, VGG, DeepLab)', 'U-Net', 'LSTM / GRU / RNN', 'Transformer / attention', 'GAN', 'Autoencoder', 'Deep learning (generic)']),
       'Mann-Kendall / Sen slope': ('method_hits', ['Mann-Kendall / Sen slope']), 'Google Earth Engine': ('platform_hits', ['Google Earth Engine'])}
rng = np.random.default_rng(2026); studies = sorted(VS.study.unique()); out = []
for v, (col, keys) in MAP.items():
    pext = float(np.mean([max(h.get(k, 0) for k in keys) >= 2 if v not in ('SAR (any)', 'LiDAR (any)', 'Deep learning (any)') else any(h.get(k, 0) >= 2 for k in keys) for h in H[col]]))
    g = VS[VS.variable == v]
    def corr(gg):
        p = gg.predicted_used.astype(int); r = gg.reference_used.astype(int)
        ppv = r[p == 1].mean() if (p == 1).any() else 1.0; fo = r[p == 0].mean() if (p == 0).any() else 0.0
        return pext*ppv + (1-pext)*fo
    bs = []; G = {k: x for k, x in g.groupby('study')}
    for _ in range(2000):
        ss = rng.choice(studies, len(studies)); bs.append(corr(pd.concat([G[s] for s in ss if s in G])))
    out.append(dict(Classification=v, Extracted_in_corpus_pct=round(100*pext, 1), Corrected_pct=round(100*corr(g), 1),
                    CI_low=round(100*np.percentile(bs, 2.5), 1), CI_high=round(100*np.percentile(bs, 97.5), 1)))
C = pd.DataFrame(out); C.to_csv(os.path.join(os.path.dirname(V), 'Table_S8_corrected_prevalence.csv'), index=False, encoding='utf-8-sig')
print(C.to_string(index=False))
