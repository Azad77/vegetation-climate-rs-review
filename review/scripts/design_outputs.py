"""design_outputs.py - Reviewer 1, comment 5: design-classifier check, Supplementary Table S9, Table 14 and Figure 9."""
import os, json, pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE); R = os.path.join(REV, 'reviewer_response')
D = pd.read_csv(os.path.join(R, 'design', 'study_design_quality.csv'))
L = json.load(open(os.path.join(R, 'design', 'design_reference_labels.json')))
ind = lambda s: s in ('Independent hold-out test', 'Spatially independent test', 'Independent reference data')
# reference-labelled studies no longer in the corpus are scored from the archived run of the same classifier
D1 = pd.read_csv(os.path.join(REV, 'archive_v1', 'reviewer_response', 'design', 'study_design_quality.csv'))
DC = pd.concat([D, D1[~D1.doi.isin(D.doi)]], ignore_index=True)
chk = DC[DC.doi.isin(L)][['doi', 'design']].copy()
chk['reference_kind'] = chk.doi.map(lambda d: L[d]['kind']); chk['reference_design'] = chk.doi.map(lambda d: L[d]['design'])
chk['agree_independent_test'] = [int(ind(a) == ind(b)) for a, b in zip(chk.design, chk.reference_design)]
chk['note'] = chk.doi.map(lambda d: L[d]['note'])
chk.to_csv(os.path.join(R, 'design', 'design_check.csv'), index=False, encoding='utf-8-sig')
D['period'] = pd.cut(D.year, [1999, 2014, 2019, 2022, 2025], labels=['2000-2014', '2015-2019', '2020-2022', '2023-2025'])
D.to_excel(os.path.join(R, 'Table_S9_validation_design_and_reporting_quality.xlsx'), index=False)
r2 = D[D.r2_n > 0]
order = ['Independent hold-out test', 'Spatially independent test', 'Cross-validation only', 'None detected']
T14 = pd.crosstab(r2.domain_primary, r2.design).reindex(columns=order, fill_value=0)
T14['Total'] = T14.sum(axis=1); T14 = T14.sort_values('Total', ascending=False)
T14.loc['All domains'] = T14.sum(); T14.to_csv(os.path.join(R, 'design', 'Table14_r2_by_domain_and_design.csv'), encoding='utf-8-sig')
# Figure 9
SURF, INK, INK2, MUTED = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8880'
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'figure.facecolor': SURF, 'axes.facecolor': SURF,
                     'savefig.facecolor': SURF, 'axes.edgecolor': '#d6d5d0', 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False})
fig, (a, b) = plt.subplots(1, 2, figsize=(8.6, 3.7), gridspec_kw={'width_ratios': [1, 1.25]})
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
mets = [('R²', 'r2_n'), ('RMSE', 'rmse_n'), ('Overall accuracy', 'oa_n'), ('MAE', 'mae_n'), ("Cohen's kappa", 'kappa_n'), ('F1 score', 'f1_n')]
v = [100 * (e[c] > 0).mean() for _, c in mets]
a.barh(range(len(v))[::-1], v, color=CAT[0], height=0.6, zorder=3)
a.set_yticks(range(len(v))[::-1]); a.set_yticklabels([m for m, _ in mets])
for i, x in zip(range(len(v))[::-1], v): a.text(x + 1, i, f'{x:.1f}%', va='center', fontsize=7.5, color=INK2)
a.set_xlim(0, 55); a.set_xlabel('% of full-text studies (n = 455)'); a.xaxis.grid(True, color='#eceae5', zorder=0)
a.set_title('a  Validation metrics reported', loc='left', fontsize=9.5, color=INK)
ct = (pd.crosstab(D.period, D.design, normalize='index') * 100).reindex(columns=order, fill_value=0)
n = D.period.value_counts().reindex(ct.index)
left = np.zeros(len(ct)); cols = [CAT[0], '#0d4f9e', CAT[3], '#cfcdc6']
for c, col in zip(order, cols):
    b.barh(range(len(ct))[::-1], ct[c].values, left=left, color=col, height=0.62, label=c, zorder=3); left += ct[c].values
b.set_yticks(range(len(ct))[::-1]); b.set_yticklabels([f'{p}\n(n = {n[p]})' for p in ct.index], fontsize=8)
b.set_xlim(0, 100); b.set_xlabel('% of full-text studies in period')
b.legend(fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
b.set_title('b  Validation design detected', loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); fig.savefig(os.path.join(REV, 'figures', 'Figure9_performance.png'), dpi=330, bbox_inches='tight')
print(chk[['design', 'reference_design', 'agree_independent_test']].to_string()); print('agree', chk.agree_independent_test.sum(), '/', len(chk))
print(chk.reference_kind.value_counts().to_dict()); print(T14)
