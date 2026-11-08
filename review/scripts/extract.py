# -*- coding: utf-8 -*-
"""Deterministic re-extraction of review variables from PDF full text.

Every value produced here is traceable: for each study and each variable we keep
the number of regex hits in the reference-stripped body text.
"""
import os, re, json, sys
import pandas as pd, numpy as np
import vocab

_HERE = os.path.dirname(os.path.abspath(__file__)); _REV = os.path.dirname(_HERE)
TXT = os.path.join(_REV, 'pdf_text')      # plain text of the PDFs (pdftotext); not redistributed
OUT = _REV
from corpus import MASTER, PDF_LINK

MIN_HITS = 2          # a term must occur at least twice in the body to count as "used"
DOMAIN_MIN = 3        # domain / biome label threshold
BIOME_MIN = 4

# ---------------------------------------------------------------- text utils
REF_HEAD = re.compile(r'\n[ \t]*(?:R\s?E\s?F\s?E\s?R\s?E\s?N\s?C\s?E\s?S?|References?|Bibliography|Literature [Cc]ited|REFERENCE LIST)[ \t]*\n')

def strip_refs(t):
    """Remove the reference list (last plausible heading in the final 60% of text)."""
    n = len(t)
    best = None
    for m in REF_HEAD.finditer(t):
        if m.start() > 0.35 * n:
            best = m.start(); break
    return t[:best] if best else t

WS = re.compile(r'[ \t]+')
def load(stem):
    raw = open(os.path.join(TXT, stem + '.txt'), errors='ignore').read()
    raw = raw.replace('ﬁ','fi').replace('ﬂ','fl').replace('‐','-').replace('–','-').replace('—','-')
    body = strip_refs(raw)
    # de-hyphenate line breaks
    body = re.sub(r'(\w)-\n(\w)', r'\1\2', body)
    body = WS.sub(' ', body)
    return raw, body

def count(pat, txt):
    return len(re.findall(pat, txt))

# ---------------------------------------------------------------- metrics
NUM = r'([-+]?\d*\.?\d+)'
R2_PATS = [
    re.compile(r'(?:R2|R\^2|R²|r2|r²)\s*(?:value)?\s*(?:of|=|:|was|were|reached|is)\s*'+NUM),
    re.compile(r'coefficient of determination[^.]{0,40}?(?:of|=|:)\s*'+NUM),
]
UNIT = r'(%|Mg\s?[/·]?\s?ha[-⁻¹1]*|t\s?[/·]?\s?ha[-⁻¹1]*|kg\s?[/·]?\s?m[-⁻²2]*|g\s?[/·]?\s?m[-⁻²2]*|m3\s?[/·]?\s?ha[-⁻¹1]*|days?|mm|cm|m|K|°C|W\s?m[-⁻²2]*|gC\s?m[-⁻²2]*[\w-]*|µg\s?cm[-⁻²2]*)'
RMSE_PATS = [re.compile(r'\bRMSE\w{0,6}\s*(?:value)?\s*(?:of|=|:|was|were|is)\s*'+NUM+r'\s*'+UNIT+r'?')]
MAE_PATS  = [re.compile(r'\bMAE\w{0,4}\s*(?:value)?\s*(?:of|=|:|was|were|is)\s*'+NUM+r'\s*'+UNIT+r'?')]
OA_PATS   = [re.compile(r'(?:overall accuracy|\bOA\b)[^.]{0,25}?(?:of|=|:|was|were|reached)\s*'+NUM+r'\s*%?'),]
KAPPA_PATS= [re.compile(r'(?:kappa|Kappa|κ)\s*(?:coefficient|statistic|value)?\s*(?:of|=|:|was|were)\s*'+NUM)]
F1_PATS   = [re.compile(r'F1[- ]?(?:score|value)?\s*(?:of|=|:|was|were)\s*'+NUM)]

def grab(pats, txt, lo=None, hi=None, with_unit=False):
    out = []
    for p in pats:
        for m in p.finditer(txt):
            try: v = float(m.group(1))
            except Exception: continue
            if lo is not None and v < lo: continue
            if hi is not None and v > hi: continue
            u = (m.group(2).strip() if with_unit and m.lastindex and m.lastindex >= 2 and m.group(2) else '')
            out.append((v, u))
    return out

YEARLIKE = lambda v: (1900 <= v <= 2100) and float(v).is_integer()

def metrics(body):
    r2 = [v for v, _ in grab(R2_PATS, body, 0.0, 1.0)]
    r2_bad = len([v for v, _ in grab(R2_PATS, body) if v < 0 or v > 1])
    rm_all = grab(RMSE_PATS, body, with_unit=True)
    rm = [(v, u) for v, u in rm_all if not (YEARLIKE(v) and u == '')]
    rm_rej = len(rm_all) - len(rm)
    mae = [(v, u) for v, u in grab(MAE_PATS, body, with_unit=True) if not (YEARLIKE(v) and u == '')]
    oa = [v for v, _ in grab(OA_PATS, body, 0.0, 100.0)]
    oa = [v * 100 if v <= 1.0 else v for v in oa]
    oa = [v for v in oa if 20 <= v <= 100]
    ka = [v for v, _ in grab(KAPPA_PATS, body, 0.0, 1.0)]
    f1 = [v for v, _ in grab(F1_PATS, body, 0.0, 1.0)]
    return dict(r2=r2, r2_out_of_range=r2_bad, rmse=rm, rmse_rejected_yearlike=rm_rej,
                mae=mae, oa=oa, kappa=ka, f1=f1)

# ---------------------------------------------------------------- open science
CODE_REPO = re.compile(r'(github\.com/[\w.\-]+/[\w.\-]+|gitlab\.com/[\w.\-/]+|bitbucket\.org/[\w.\-/]+|zenodo\.org/(?:record|records|doi)[\w./\-]*|10\.5281/zenodo\.\d+|codeocean\.com/[\w.\-/]+|osf\.io/\w+|code\.earthengine\.google\.com/[\w?=.\-]+)', re.I)
DATA_REPO = re.compile(r'(figshare\.com/[\w.\-/]+|10\.6084/m9\.figshare\.\d+|datadryad\.org/[\w.\-/]+|10\.5061/dryad\.\w+|pangaea\.de/[\w.\-/]+|10\.1594/PANGAEA\.\d+|data\.mendeley\.com/[\w.\-/]+|10\.17632/[\w.]+|zenodo\.org/(?:record|records|doi)[\w./\-]*|10\.5281/zenodo\.\d+|osf\.io/\w+)', re.I)
CODE_STMT = re.compile(r'(code availability|source code (?:is|are|will be)? ?(?:publicly )?available|scripts? (?:are|is) available|analysis code)', re.I)
DATA_STMT = re.compile(r'(data availability|data (?:are|is) (?:publicly |freely |openly )?available|datasets? (?:generated|analy[sz]ed).{0,60}available)', re.I)
ON_REQUEST = re.compile(r'available (?:from|on|upon)[^.]{0,60}(?:corresponding author|request)', re.I)
NOT_AVAIL = re.compile(r'(not publicly available|cannot be shared|are confidential|restrictions apply)', re.I)

def openscience(raw):
    tail = raw  # search whole document incl. statements after references
    code_urls = sorted(set(CODE_REPO.findall(tail)))
    data_urls = sorted(set(DATA_REPO.findall(tail)))
    has_code_stmt = bool(CODE_STMT.search(tail))
    has_data_stmt = bool(DATA_STMT.search(tail))
    on_req = bool(ON_REQUEST.search(tail))
    not_av = bool(NOT_AVAIL.search(tail))
    if code_urls: code = 'Repository link'
    elif has_code_stmt and on_req: code = 'On request'
    elif has_code_stmt: code = 'Statement, no link'
    elif on_req: code = 'On request'
    elif not_av: code = 'Explicitly unavailable'
    else: code = 'Not stated'
    if data_urls: data = 'Repository link'
    elif has_data_stmt and on_req: data = 'On request'
    elif has_data_stmt: data = 'Statement, no link'
    elif on_req: data = 'On request'
    elif not_av: data = 'Explicitly unavailable'
    else: data = 'Not stated'
    return code, data, ';'.join(code_urls[:3]), ';'.join(data_urls[:3])

# ---------------------------------------------------------------- main
def main():
    link = json.load(open(PDF_LINK))
    d = pd.read_excel(MASTER, sheet_name='Master Clean')
    # one pdf per record: prefer the longest text
    byrow = {}
    for stem, idx in link.items():
        sz = os.path.getsize(os.path.join(TXT, stem + '.txt'))
        if idx not in byrow or sz > byrow[idx][1]:
            byrow[idx] = (stem, sz)

    groups = [('sensor', vocab.SENSORS), ('index', vocab.INDICES), ('product', vocab.PRODUCTS),
              ('method', vocab.METHODS), ('platform', vocab.PLATFORMS), ('climate', vocab.CLIMATE)]
    compiled = {g: {k: re.compile(v) for k, v in voc.items()} for g, voc in groups}
    dom_c = {k: re.compile(v, re.I) for k, v in vocab.DOMAINS.items()}
    bio_c = {k: re.compile(v, re.I) for k, v in vocab.BIOMES.items()}

    rows = []
    for i, (idx, (stem, _)) in enumerate(sorted(byrow.items())):
        raw, body = load(stem)
        rec = {'row': idx, 'doi': d.at[idx, 'doi'], 'year': d.at[idx, 'year'],
               'title': d.at[idx, 'title'], 'journal': d.at[idx, 'journal'],
               'author_country': d.at[idx, 'author_country'], 'pdf_stem': stem,
               'n_chars_body': len(body)}
        allhits = {}
        for g, cc in compiled.items():
            hits = {k: count(p.pattern, body) for k, p in cc.items()}
            allhits[g] = hits
            rec[g + '_hits'] = json.dumps(hits)
            rec[g + 's'] = ';'.join(sorted(k for k, v in hits.items() if v >= MIN_HITS))
        # --- post-hoc rules -------------------------------------------------
        mh = allhits['method']
        sel = set(k for k, v in mh.items() if v >= MIN_HITS)
        # a bare "decision tree" mention inside a Random-Forest paper is the RF
        # base learner, not a separately applied method
        if 'Decision tree / CART' in sel and 'Random Forest' in sel and not re.search(r'\bCART\b|\bC4\.5\b|\bC5\.0\b', body):
            sel.discard('Decision tree / CART')
        rec['methods'] = ';'.join(sorted(sel))
        DL = {'CNN (incl. ResNet, VGG, DeepLab)', 'U-Net', 'LSTM / GRU / RNN',
              'Transformer / attention', 'GAN', 'Autoencoder', 'Deep learning (generic)'}
        SHALLOW = {'Random Forest', 'SVM / SVR', 'Gradient boosting / XGBoost / LightGBM',
                   'Decision tree / CART', 'k-NN', 'Naive Bayes', 'ANN / MLP',
                   'Maximum likelihood classifier'}
        STAT = {'Linear / multiple regression', 'PLS / PLSR', 'Ridge / Lasso / Elastic net',
                'GAM / GLM', 'Geographically weighted regression', 'Mann-Kendall / Sen slope',
                'Correlation analysis', 'Structural equation model', 'Granger causality'}
        rec['uses_deep_learning'] = bool(sel & DL)
        rec['uses_shallow_ml'] = bool(sel & SHALLOW)
        rec['uses_any_ml'] = bool(sel & (DL | SHALLOW))
        rec['uses_statistical_only'] = bool(sel & STAT) and not (sel & (DL | SHALLOW))
        sh = allhits['sensor']
        SARFAM = ['Sentinel-1', 'ALOS PALSAR', 'RADARSAT', 'TerraSAR-X / TanDEM-X', 'SAR (generic / other)']
        rec['uses_sar'] = any(sh.get(k, 0) >= MIN_HITS for k in SARFAM)
        OPTICAL = ['MODIS', 'Landsat', 'Sentinel-2', 'Sentinel-3', 'AVHRR / GIMMS', 'VIIRS',
                   'SPOT / VEGETATION', 'PlanetScope / RapidEye',
                   'WorldView / QuickBird / IKONOS', 'ASTER', 'Gaofen / HJ / FY / CBERS',
                   'IRS / LISS / Resourcesat', 'Himawari / GOES / MSG-SEVIRI',
                   'Hyperion / EnMAP / PRISMA / DESIS']
        nopt = sum(1 for k in OPTICAL if sh.get(k, 0) >= MIN_HITS)
        rec['n_optical_sensors'] = nopt
        rec['multi_sensor_fusion'] = (nopt >= 2) or (nopt >= 1 and rec['uses_sar'])
        dh = {k: len(p.findall(body)) for k, p in dom_c.items()}
        bh = {k: len(p.findall(body)) for k, p in bio_c.items()}
        rec['domain_hits'] = json.dumps(dh); rec['biome_hits'] = json.dumps(bh)
        rec['domains'] = ';'.join(sorted(k for k, v in dh.items() if v >= DOMAIN_MIN))
        rec['domain_primary'] = max(dh, key=dh.get) if max(dh.values()) >= DOMAIN_MIN else 'Unclassified'
        # forest resolution
        bh2 = dict(bh)
        spec = {k: bh2[k] for k in ['Forest (temperate)', 'Forest (boreal)', 'Forest (tropical)']}
        if max(spec.values()) >= BIOME_MIN:
            bh2['Forest (unspecified)'] = 0
        else:
            for k in spec: bh2[k] = 0
        rec['biomes'] = ';'.join(sorted(k for k, v in bh2.items() if v >= BIOME_MIN))
        rec['biome_primary'] = max(bh2, key=bh2.get) if max(bh2.values()) >= BIOME_MIN else 'Unclassified'
        m = metrics(body)
        rec['r2_n'] = len(m['r2'])
        rec['r2_max'] = max(m['r2']) if m['r2'] else np.nan
        rec['r2_median'] = float(np.median(m['r2'])) if m['r2'] else np.nan
        rec['r2_values'] = ';'.join(f'{v:g}' for v in m['r2'][:60])
        rec['rmse_n'] = len(m['rmse'])
        rec['rmse_min'] = min(v for v, _ in m['rmse']) if m['rmse'] else np.nan
        rec['rmse_median'] = float(np.median([v for v, _ in m['rmse']])) if m['rmse'] else np.nan
        rec['rmse_units'] = ';'.join(sorted({u.strip() for _, u in m['rmse'] if u})[:5])
        rec['rmse_values'] = json.dumps([[v, (u or '').strip()] for v, u in m['rmse'][:60]])
        rec['mae_values'] = json.dumps([[v, (u or '').strip()] for v, u in m['mae'][:40]])
        rec['rmse_rejected_yearlike'] = m['rmse_rejected_yearlike']
        rec['mae_n'] = len(m['mae'])
        rec['mae_median'] = float(np.median([v for v, _ in m['mae']])) if m['mae'] else np.nan
        rec['oa_n'] = len(m['oa']); rec['oa_max'] = max(m['oa']) if m['oa'] else np.nan
        rec['oa_median'] = float(np.median(m['oa'])) if m['oa'] else np.nan
        rec['kappa_n'] = len(m['kappa']); rec['kappa_median'] = float(np.median(m['kappa'])) if m['kappa'] else np.nan
        rec['f1_n'] = len(m['f1']); rec['f1_median'] = float(np.median(m['f1'])) if m['f1'] else np.nan
        c, da, cu, du = openscience(raw)
        rec['code_status'] = c; rec['data_status'] = da; rec['code_url'] = cu; rec['data_url'] = du
        rows.append(rec)
        if (i + 1) % 100 == 0: print(i + 1, flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, 'fulltext_extraction.csv'), index=False)
    print('done', out.shape)

if __name__ == '__main__':
    main()
