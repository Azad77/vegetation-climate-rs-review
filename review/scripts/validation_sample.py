"""validation_sample.py - Reviewer 1, comment 4, step 1.
Draws a stratified random sample of 40 Tier 2 studies (seed 2026; proportional to publication period) and, for 15 main
classifications, writes every passage (keyword-in-context, +/-200 characters, tagged by section) in which the vocabulary
term OR a broader synonym occurs in the reference-stripped body text, so that 'applied in this study' can be judged
against 'only mentioned'. Pairs with no occurrence of the broad pattern are pre-labelled 'not used'.
Output: ../reviewer_response/validation/kwic_sample.json and validation_sheet.csv (one row per study x variable)."""
import os, re, json, pandas as pd, numpy as np
import extract as X, vocab as V
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE)
OUT = os.path.join(REV, 'reviewer_response', 'validation'); os.makedirs(OUT, exist_ok=True)
X.TXT = os.path.join(REV, 'pdf_text')
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
H = {c: e[c].apply(json.loads) for c in ['sensor_hits', 'index_hits', 'method_hits', 'platform_hits']}
def hits(i, keys, col): return sum(H[col].loc[i].get(k, 0) for k in keys)
DL = ['CNN (incl. ResNet, VGG, DeepLab)', 'U-Net', 'LSTM / GRU / RNN', 'Transformer / attention', 'GAN', 'Autoencoder', 'Deep learning (generic)']
SAR = ['Sentinel-1', 'ALOS PALSAR', 'RADARSAT', 'TerraSAR-X / TanDEM-X', 'SAR (generic / other)']
LID = ['Airborne / spaceborne LiDAR (generic)', 'GEDI', 'ICESat / ICESat-2']
# variable: (columns, keys, strict pattern = vocabulary, broad pattern used to find candidate passages incl. synonyms)
VARS = {
 'Landsat':        ('sensor_hits', ['Landsat'], V.SENSORS['Landsat'], r'Landsat|\bETM\+|\bOLI\b|\bTM\b|Thematic Mapper'),
 'MODIS':          ('sensor_hits', ['MODIS'], V.SENSORS['MODIS'], r'MODIS|\bMOD\d{2}|\bMYD\d{2}|\bMCD\d{2}|Moderate[- ]Resolution Imaging'),
 'Sentinel-2':     ('sensor_hits', ['Sentinel-2'], V.SENSORS['Sentinel-2'], r'Sentinel[- ]?2|\bS2\b|MultiSpectral Instrument|\bMSI\b'),
 'SAR (any)':      ('sensor_hits', SAR, '|'.join(V.SENSORS[k] for k in SAR), r'\bSAR\b|[Ss]ynthetic [Aa]perture|Sentinel[- ]?1|PALSAR|\bALOS\b|RADARSAT|TerraSAR|TanDEM|\bradar\b|backscatter|InSAR'),
 'LiDAR (any)':    ('sensor_hits', LID, '|'.join(V.SENSORS[k] for k in LID), r'LiDAR|LIDAR|[Ll]idar|GEDI|ICESat|\bGLAS\b|laser scann|\bALS\b|\bTLS\b'),
 'AVHRR / GIMMS':  ('sensor_hits', ['AVHRR / GIMMS'], V.SENSORS['AVHRR / GIMMS'], r'AVHRR|GIMMS|NOAA[- ]?\d'),
 'NDVI':           ('index_hits', ['NDVI'], V.INDICES['NDVI'], r'NDVI|[Nn]ormali[sz]ed [Dd]ifference [Vv]egetation'),
 'EVI':            ('index_hits', ['EVI'], V.INDICES['EVI'], r'\bEVI\b|[Ee]nhanced [Vv]egetation [Ii]ndex'),
 'Random Forest':  ('method_hits', ['Random Forest'], V.METHODS['Random Forest'], r'[Rr]andom [Ff]orest|\bRF\b|\bRFR\b'),
 'Linear / multiple regression': ('method_hits', ['Linear / multiple regression'], V.METHODS['Linear / multiple regression'], r'[Ll]inear regression|[Mm]ultiple regression|least squares|\bOLS\b|\bMLR\b|[Rr]egression model|[Rr]egression analysis'),
 'SVM / SVR':      ('method_hits', ['SVM / SVR'], V.METHODS['SVM / SVR'], r'[Ss]upport [Vv]ector|\bSVM\b|\bSVR\b'),
 'Gradient boosting': ('method_hits', ['Gradient boosting / XGBoost / LightGBM'], V.METHODS['Gradient boosting / XGBoost / LightGBM'], r'[Bb]oost|\bXGB\b|LightGBM|CatBoost|\bGBDT\b|\bGBM\b|\bBRT\b'),
 'Deep learning (any)': ('method_hits', DL, '|'.join(V.METHODS[k] for k in DL), r'[Dd]eep learning|[Nn]eural [Nn]etwork|\bCNN\b|U-?Net|LSTM|\bGRU\b|\bRNN\b|[Tt]ransformer|\bGAN\b|[Aa]uto-?encoder|ResNet|DeepLab|\bVGG'),
 'Mann-Kendall / Sen slope': ('method_hits', ['Mann-Kendall / Sen slope'], V.METHODS['Mann-Kendall / Sen slope'], r'Mann[- ]?Kendall|Theil|Sen\'?s slope|\bMK\b|[Tt]rend test'),
 'Google Earth Engine': ('platform_hits', ['Google Earth Engine'], V.PLATFORMS['Google Earth Engine'], r'Earth Engine|\bGEE\b'),
}
e['period'] = pd.cut(e.year, [1999, 2014, 2019, 2022, 2025], labels=['2000-2014', '2015-2019', '2020-2022', '2023-2025'])
S = e.groupby('period', group_keys=False, observed=True)[e.columns.tolist()].apply(
    lambda g: g.sample(n=max(2, round(40 * len(g) / len(e))), random_state=2026))
if len(S) < 40: S = pd.concat([S, e.drop(S.index).sample(n=40 - len(S), random_state=2026)])
S = S.sort_values('year')
SEC = re.compile(r'(?:^|\s)(?:\d(?:\.\d)?\.?\s+)?(Introduction|Materials? and [Mm]ethods|Methods?|Methodology|Data and [Mm]ethods|'
                 r'Study [Aa]rea|Data|Results?|Discussion|Conclusions?)\s', re.M)
def sections(body):
    marks = [(m.start(), m.group(1).split()[0].capitalize()) for m in SEC.finditer(body)]
    def at(pos):
        lab = 'Front'
        for s, l in marks:
            if s <= pos: lab = l
            else: break
        return {'Material': 'Methods', 'Methodology': 'Methods', 'Method': 'Methods', 'Study': 'Methods', 'Data': 'Methods',
                'Result': 'Results', 'Conclusion': 'Conclusions'}.get(lab, lab)
    return at
out, rows = {}, []
for i, x in S.iterrows():
    raw, body = X.load(x.pdf_stem); at = sections(body); rec = {'title': x.title, 'year': int(x.year),
          'domain_primary': x.domain_primary, 'abstract_head': body[:1400], 'vars': {}}
    for v, (col, keys, strict, broad) in VARS.items():
        n = hits(i, keys, col); pred = int(n >= X.MIN_HITS)
        ms = list(re.finditer(broad, body)); kw = []
        if ms:
            idx = np.unique(np.linspace(0, len(ms) - 1, min(len(ms), 5)).round().astype(int))
            for j in idx:
                m = ms[j]; kw.append(f"[{at(m.start())}] ...{body[max(0, m.start()-200):m.end()+200]}...")
        rec['vars'][v] = {'strict_hits': n, 'predicted': pred, 'broad_hits': len(ms), 'kwic': kw}
        rows.append(dict(doi=x.doi, year=int(x.year), title=x.title, variable=v, strict_hits=n, predicted_used=pred,
                         broad_hits=len(ms), reference_used=(0 if not ms else None), note=''))
    rows.append(dict(doi=x.doi, year=int(x.year), title=x.title, variable='Primary domain', strict_hits=None,
                     predicted_used=x.domain_primary, broad_hits=None, reference_used=None, note=''))
    out[x.doi] = rec
json.dump(out, open(os.path.join(OUT, 'kwic_sample.json'), 'w'), indent=1)
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'validation_sheet.csv'), index=False, encoding='utf-8-sig')
print(len(S), S.period.value_counts().to_dict(), 'pairs to judge:', sum(1 for r in rows if r['reference_used'] is None))
