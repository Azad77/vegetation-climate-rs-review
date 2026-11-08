"""screen_v2_prep.py - prepares the title-and-abstract screening: (1) deterministic pre-screen on the abstract-assessable
criteria (tier1_sensitivity_rules), which excludes only clear failures (no satellite remote sensing term, satellite data
absent with UAV/airborne only, or no vegetation term); (2) a condensed reading sheet (title, aim and method sentences) for
the remaining records, which are screened individually against Table 1."""
import os, re, sys, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tier1_sensitivity_rules import check
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); W = os.path.join(REV, 'reviewer_response', 'screening_v2')
r = pd.read_csv(os.path.join(W, 'records_with_abstracts.csv')).fillna('')
AIM = re.compile(r"\b(this (study|paper|research|work|article)|we |our |here|aim|objective|purpose|investigat|analy[sz]|"
                 r"estimat|assess|examin|propos|develop|evaluat|quantif|map|monitor|review)", re.I)
def condense(a):
    ss = re.split(r'(?<=[.!?])\s+', a); keep = [s for s in ss if AIM.search(s)][:3] or ss[:2]
    return ' '.join(keep)[:300]
pre = []
for x in r.itertuples():
    c = check(x.full_title, x.abstract)
    fail = []
    if not c['satellite_rs']: fail.append('no satellite RS term')
    if c['uav_without_satellite']: fail.append('UAV/airborne without satellite')
    if not c['vegetation']: fail.append('no vegetation term')
    pre.append('; '.join(fail))
r['prescreen_fail'] = pre
r['has_abstract'] = r.abstract.str.len() > 100
# pre-screen exclusions only when an abstract is available (titles alone are too short to fail a record)
r['prescreen_exclude'] = r.has_abstract & r.prescreen_fail.ne('')
r['condensed'] = [condense(a) if h else '' for a, h in zip(r.abstract, r.has_abstract)]
r.to_csv(os.path.join(W, 'screening_sheet.csv'), index=False)
print('records', len(r), '| with abstract', r.has_abstract.sum(), '| pre-screen excluded', r.prescreen_exclude.sum())
print(r[r.prescreen_exclude].prescreen_fail.value_counts())
print('to read', (~r.prescreen_exclude).sum(), 'chars', r.loc[~r.prescreen_exclude, 'condensed'].str.len().sum() + r.loc[~r.prescreen_exclude,'full_title'].str.len().sum())
