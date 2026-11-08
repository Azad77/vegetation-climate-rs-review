"""prisma_v2.py - PRISMA 2020 counts, record log (Supplementary Table S1) and Figure 1 for the revised title-and-abstract
screening. Inputs: reviewer_response/screening_v2/screening_v2_log.csv (screen_v2_finalize.py) and data_v2/master_v2.xlsx."""
import os, json, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(REV, 'reviewer_response'); FIG = os.path.join(REV, 'figures')
s = pd.read_csv(os.path.join(OUT, 'screening_v2', 'screening_v2_log.csv'))
m = pd.read_excel(os.path.join(REV, 'data_v2', 'master_v2.xlsx'))
N_ID, N_DUP, N_DOC, N_TI = 4794, 6, 844, 2462
n_abs = int((s.abstract_source != 'none').sum()); n_inc = len(m); n_t2 = int(m.pdf_filename.notna().sum())
ex = s[s.status_v2 != 'Included'].status_v2.value_counts()
assert n_inc == int((s.status_v2 == 'Included').sum())
log = s[['row_id', 'doi', 'full_title', 'year', 'journal', 'doc_type', 'abstract_source', 'screen_v2', 'status_v2']].rename(columns={
    'full_title': 'title', 'abstract_source': 'abstract_source_at_screening', 'screen_v2': 'decision_code', 'status_v2': 'final_status'})
tier = dict(zip(m.row_id_S1, m.tier)); log['extraction_tier'] = log.row_id.map(tier)
log.to_csv(os.path.join(OUT, 'Table_S1_PRISMA_record_log.csv'), index=False, encoding='utf-8-sig')
log.to_excel(os.path.join(OUT, 'Table_S1_PRISMA_record_log.xlsx'), index=False)
rows = [('Identification', 'Records retrieved from Scopus', N_ID), ('Identification', 'Duplicates removed', N_DUP),
        ('Screening', 'Records screened by document type', N_ID - N_DUP), ('Screening', 'Excluded: not a journal article or review', N_DOC),
        ('Screening', 'Records screened on title (keyword classifier)', N_ID - N_DUP - N_DOC), ('Screening', 'Excluded at title screening', N_TI),
        ('Eligibility', 'Records assessed on title and abstract', 1482), ('Eligibility', '  with abstract', n_abs),
        ('Eligibility', '  title and bibliographic metadata only', 1482 - n_abs)]
rows += [('Eligibility', 'Excluded: ' + k, int(v)) for k, v in ex.items()]
rows += [('Included', 'Studies included', n_inc), ('Included', '  full text obtained and extracted (Tier 2)', n_t2),
         ('Included', '  bibliographic record only (Tier 1)', n_inc - n_t2)]
T3 = pd.DataFrame(rows, columns=['Stage', 'Description', 'n'])
T3.to_csv(os.path.join(OUT, 'Table3_PRISMA_reconciled.csv'), index=False, encoding='utf-8-sig')
json.dump(dict(n_abs=n_abs, n_inc=n_inc, n_t2=n_t2, excluded={k: int(v) for k, v in ex.items()}),
          open(os.path.join(OUT, 'prisma_v2_counts.json'), 'w'), indent=1)
INK, INK2, MUTED, BLUE, ORANGE = '#0b0b0b', '#52514e', '#8a8880', '#2a78d6', '#eb6834'; f = lambda n: f'{n:,}'
fig, ax = plt.subplots(figsize=(8.4, 10.0)); ax.axis('off'); ax.set_xlim(0, 10.4); ax.set_ylim(1.6, 14)
main = [(f"Records identified from Scopus\n(n = {f(N_ID)})", 13.2), (f"Records screened by document type\n(n = {f(N_ID - N_DUP)})", 11.8),
        (f"Records screened on title\n(keyword classifier; n = {f(N_ID - N_DUP - N_DOC)})", 10.4),
        (f"Records assessed on title and abstract\n(n = 1,482; abstract available for {f(n_abs)})", 8.6),
        (f"Studies included in the review\n(n = {n_inc})", 4.2),
        (f"Tier 2: full text extracted (n = {n_t2})\nTier 1: bibliographic record only (n = {n_inc - n_t2})", 2.6)]
g = lambda k: int(ex.get(k, 0))
excl = [(f"Duplicates removed\n(n = {N_DUP})", 12.5), (f"Excluded: not a journal article\nor review (n = {N_DOC})", 11.1),
        (f"Excluded at title screening\n(n = {f(N_TI)})", 9.7),
        (f"Excluded at title-and-abstract screening (n = {int(ex.sum())})\n"
         f"No climate driver or climate-related response: {g('No climate driver or climate-related vegetation response')}\n"
         f"No vegetation variable analysed: {g('No vegetation variable analysed')}\n"
         f"Satellite RS not the primary data source: {g('Satellite remote sensing not the primary data source')}\n"
         f"Non-English publication: {g('Non-English publication (journal language)')}\n"
         f"Uncertain, conservatively excluded: {g('Uncertain, conservatively excluded')}", 6.2)]
hh = lambda t, k: 0.28 + k * t.count('\n')
for t, y in main:
    h = hh(t, 0.16); fc, ec = ('#f3f6f4', '#6f8f7d') if y < 3 else ('#eef4fd', BLUE)
    ax.add_patch(FancyBboxPatch((0.45, y - h), 5.0, 2 * h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=1.1))
    ax.text(2.95, y, t, ha='center', va='center', fontsize=8.2, color=INK)
for t, y in excl:
    h = hh(t, 0.15)
    ax.add_patch(FancyBboxPatch((6.05, y - h), 4.2, 2 * h, boxstyle='round,pad=0.02,rounding_size=0.12', fc='#fdf1ec', ec=ORANGE, lw=1.0))
    ax.text(8.15, y, t, ha='center', va='center', fontsize=7.2, color=INK2, linespacing=1.25)
    yy = y if y > 7 else 8.6 - 0.9
    ax.add_patch(FancyArrowPatch((2.95, y), (6.05, y), arrowstyle='-|>', mutation_scale=10, color=MUTED, lw=1.0, zorder=0))
for i in range(len(main) - 1):
    a = main[i][1] - hh(main[i][0], 0.16); b = main[i + 1][1] + hh(main[i + 1][0], 0.16)
    ax.add_patch(FancyArrowPatch((2.95, a), (2.95, b), arrowstyle='-|>', mutation_scale=11, color=MUTED, lw=1.0))
for lab, y0, y1 in [('Identification', 13.9, 12.8), ('Screening', 12.4, 5.0), ('Included', 4.8, 1.9)]:
    ax.text(0.12, (y0 + y1) / 2, lab, rotation=90, ha='center', va='center', fontsize=9, color=MUTED, fontweight='bold')
fig.savefig(os.path.join(FIG, 'Figure1_PRISMA.png'), dpi=600, bbox_inches='tight', facecolor='white')
print(T3.to_string(index=False))
