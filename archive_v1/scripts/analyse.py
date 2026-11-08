# -*- coding: utf-8 -*-
"""Build every corrected table and figure for the revised review."""
import os, json, re, textwrap
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from collections import Counter
import geo

OUT = '/home/claude/work/out'
FIG = os.path.join(OUT, 'figures'); os.makedirs(FIG, exist_ok=True)
MASTER = '/mnt/user-data/uploads/vegiclimate_review/data/step5_master_clean_19_4_2026.xlsx'

# ---- design tokens (dataviz reference palette, light surface) ----
SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; MUTED = '#8a8880'
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
SEQ = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
       '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']
from matplotlib.colors import LinearSegmentedColormap
BLUES = LinearSegmentedColormap.from_list('blues', ['#f4f8fe'] + SEQ)

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9,
    'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
    'axes.edgecolor': '#d6d5d0', 'axes.linewidth': 0.8, 'axes.labelcolor': INK2,
    'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
    'axes.grid': True, 'grid.color': '#eceae5', 'grid.linewidth': 0.8,
    'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False,
})

def save(fig, name):
    p = os.path.join(FIG, name)
    fig.savefig(p, dpi=330, bbox_inches='tight'); plt.close(fig)
    print('  wrote', name)

# ---------------------------------------------------------------- load
d = pd.read_excel(MASTER, sheet_name='Master Clean')
e = pd.read_csv(os.path.join(OUT, 'fulltext_extraction.csv'))
N_ALL, N_FT = len(d), len(e)
d['ns'] = d.author_country.apply(lambda c: 'Global North' if c in geo.NORTH_M49 else 'Global South')
d['ns_hi'] = d.author_country.apply(
    lambda c: 'Global North' if c in (geo.NORTH_M49 | geo.HIGH_INCOME_EXTRA) else 'Global South')
e = e.merge(d[['doi', 'ns']], on='doi', how='left')

def tally(col, df=None, denom=None):
    df = e if df is None else df
    denom = denom or len(df)
    c = Counter()
    for s in df[col].fillna(''):
        for k in str(s).split(';'):
            if k: c[k] += 1
    t = pd.Series(c).sort_values(ascending=False).to_frame('n')
    t['pct'] = (100 * t.n / denom).round(1)
    return t

tables = {}

# ================================================================ TABLE: PRISMA
prisma = pd.DataFrame([
 ('Identification', 'Records retrieved from Scopus (TITLE-ABS-KEY query, 13 compound pairs)', '4,794'),
 ('Deduplication', 'Duplicate records removed (DOI-exact and fuzzy title matching)', '6'),
 ('After deduplication', 'Unique records', '4,788'),
 ('Document-type filter', 'Excluded - not a journal article or review', '844'),
 ('After doc-type filter', 'Records retained (articles and reviews only)', '3,944'),
 ('Title/abstract screening', 'Excluded at title/abstract stage', '2,462'),
 ('Reports sought for retrieval', 'Records forwarded for full-text eligibility assessment', '1,482'),
 ('  Full text retrieved', 'Open-access PDF retrieved and parsed', '572'),
 ('  Full text not retrieved', 'No open-access PDF retrievable from any source', '910'),
 ('Excluded after assessment', 'Total excluded at this stage', '725'),
 ('  - failed a stated criterion', 'Assessed against the eight eligibility criteria and excluded', '458'),
 ('  - could not be assessed', 'Excluded because no content was available to assess', '124'),
 ('  - no decision logged', 'Excluded by subtraction; includes 25 records with no DOI', '143'),
 ('Final included', 'Studies included in the synthesis', '757'),
 ('  - assessed on full text', 'Basis of Sections 3.4-3.11', '455'),
 ('  - assessed on title/abstract', 'Contribute to Sections 3.2-3.3 only', '302'),
], columns=['Stage', 'Description', 'n'])
tables['T3_PRISMA'] = prisma

# ================================================================ FIG 1 PRISMA
PR = dict(sought=1482, retrieved=572, ret_inc=455, ret_exc=117, notret=910,
          notret_inc=302, notret_exc=608, inc=757, exc=725,
          exc_criterion=458, exc_noassess=124, exc_nolog=143)

def prisma_fig():
    fig, ax = plt.subplots(figsize=(7.8, 9.6)); ax.axis('off')
    ax.set_xlim(0, 10); ax.set_ylim(0, 13.2); ax.grid(False)
    main = [("Records identified from Scopus\n(n = 4,794)", 12.2),
            ("Records after duplicate removal\n(n = 4,788)", 10.9),
            ("Records screened by document type\n(n = 4,788)", 9.6),
            ("Records screened on title and abstract\n(n = 3,944)", 8.3),
            ("Reports sought for retrieval\n(n = 1,482)", 7.0),
            ("Reports assessed on full text\n(n = 572)", 5.0),
            ("Studies included in the review\n(n = 757)", 2.6),
            ("455 assessed on full text  +  302 assessed on\ntitle and abstract only (Section 2.4, Stage 5)", 1.1)]
    excl = [("Duplicates removed\n(n = 6)", 11.55),
            ("Excluded - not a journal\narticle or review (n = 844)", 8.95),
            ("Excluded at title/abstract\nscreening (n = 2,462)", 7.65),
            ("Full text not retrieved (n = 910)\n302 retained on title/abstract\n608 excluded", 6.0),
            ("Excluded after assessment (n = 725)\n458 failed a stated criterion\n124 could not be assessed\n143 no decision logged", 3.8)]
    for t, y in main:
        h = 0.30 + 0.16 * t.count('\n')
        fc, ec = ('#f3f6f4', '#6f8f7d') if y < 1.6 else ('#eef4fd', CAT[0])
        ax.add_patch(FancyBboxPatch((0.45, y - h), 5.1, 2 * h,
                                    boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=1.1))
        ax.text(3.0, y, t, ha='center', va='center', fontsize=8.4, color=INK)
    for t, y in excl:
        h = 0.30 + 0.17 * t.count('\n')
        ax.add_patch(FancyBboxPatch((6.25, y - h), 3.5, 2 * h,
                                    boxstyle='round,pad=0.02,rounding_size=0.12', fc='#fdf1ec', ec=CAT[1], lw=1.0))
        ax.text(8.0, y, t, ha='center', va='center', fontsize=7.5, color=INK2)
    for i in range(len(main) - 1):
        h0 = 0.30 + 0.16 * main[i][0].count('\n'); h1 = 0.30 + 0.16 * main[i + 1][0].count('\n')
        ax.add_patch(FancyArrowPatch((3.0, main[i][1] - h0), (3.0, main[i + 1][1] + h1),
                                     arrowstyle='-|>', mutation_scale=11, color=MUTED, lw=1.0))
    for (t, ye) in excl:
        ax.add_patch(FancyArrowPatch((5.55, ye), (6.25, ye), arrowstyle='-|>',
                                     mutation_scale=10, color=MUTED, lw=1.0))
    # the 302 title/abstract-only records rejoin the included box
    ax.plot([9.75, 9.95, 9.95, 5.95], [5.36, 5.36, 2.45, 2.45], color=MUTED, lw=1.0,
            ls=(0, (4, 2)), solid_capstyle='butt', zorder=1)
    ax.add_patch(FancyArrowPatch((6.1, 2.45), (5.55, 2.45), arrowstyle='-|>', mutation_scale=10,
                                 color=MUTED, lw=1.0))
    ax.text(7.9, 2.27, '302 records retained on title/abstract', ha='center', va='top',
            fontsize=6.8, color=MUTED)
    for lab, y0, y1 in [('Identification', 12.9, 11.4), ('Screening', 11.3, 4.3), ('Included', 4.2, 0.4)]:
        ax.text(0.12, (y0 + y1) / 2, lab, rotation=90, ha='center', va='center',
                fontsize=9, color=MUTED, fontweight='bold')
    save(fig, 'Figure1_PRISMA.png')
prisma_fig()

# ================================================================ FIG 2 trend
yr = d.year.value_counts().sort_index()
yr = yr.reindex(range(2000, 2026), fill_value=0)
ftyr = e.year.value_counts().sort_index().reindex(range(2000, 2026), fill_value=0)
fig, ax = plt.subplots(figsize=(7.2, 3.5))
ax.bar(yr.index, yr.values, color=CAT[0], width=0.72, zorder=3, label='All included studies (n = 757)')
ax.bar(ftyr.index, ftyr.values, color='#9ec5f4', width=0.72, zorder=4,
       label='of which full text re-extracted (n = %d)' % N_FT)
for x in [2015, 2019]:
    ax.axvline(x - 0.5, color=MUTED, ls=(0, (4, 3)), lw=0.9, zorder=2)
ax.annotate('Landsat archive opened (2008)\nGoogle Earth Engine launched (2010)', xy=(2006.6, 96),
            fontsize=7.2, color=INK2, ha='left')
ax.annotate('Sentinel-2\nfrom 2015', xy=(2014.7, 96), fontsize=7.2, color=INK2, ha='center')
ax.annotate('deep-learning\nuptake from 2019', xy=(2018.7, 96), fontsize=7.2, color=INK2, ha='center')
ax.set_ylim(0, 152)
for x in [2024, 2025]:
    ax.text(x, yr[x] + 3, str(yr[x]), ha='center', fontsize=8, color=INK)
ax.set_xlabel('Publication year'); ax.set_ylabel('Number of studies')
ax.set_xticks(range(2000, 2026, 2)); ax.tick_params(axis='x', rotation=0)
ax.legend(loc='upper left', fontsize=8)
ax.set_axisbelow(True); ax.xaxis.grid(False)
save(fig, 'Figure2_publication_trend.png')
tables['T4_year'] = pd.DataFrame({'Year': yr.index, 'All included (n)': yr.values,
                                  'Full text re-extracted (n)': ftyr.values})

# ================================================================ FIG 3 geography
reg = d.geographic_region.value_counts()
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={'width_ratios': [1.55, 1]})
ax = axes[0]
r = reg.sort_values()
ax.barh(range(len(r)), r.values, color=CAT[0], height=0.62, zorder=3)
ax.set_yticks(range(len(r))); ax.set_yticklabels(r.index, fontsize=8)
for i, v in enumerate(r.values):
    ax.text(v + 3, i, f'{v} ({100*v/N_ALL:.1f}%)', va='center', fontsize=7.5, color=INK2)
ax.set_xlabel('Studies (first-author affiliation)'); ax.set_xlim(0, max(r.values) * 1.28)
ax.yaxis.grid(False); ax.set_axisbelow(True)
ax.set_title('a  Regional distribution', loc='left', fontsize=9.5, color=INK)
ax = axes[1]
ns = d.ns.value_counts(); ns_hi = d.ns_hi.value_counts()
xs = np.arange(2); w = 0.36
ax.bar(xs - w/2, [ns.get('Global North', 0), ns.get('Global South', 0)], w, color=CAT[0],
       zorder=3, label='UN M49 developed regions')
ax.bar(xs + w/2, [ns_hi.get('Global North', 0), ns_hi.get('Global South', 0)], w, color=CAT[1],
       zorder=3, label='+ high-income E. Asian economies')
for i, (a, b) in enumerate(zip([ns.get('Global North', 0), ns.get('Global South', 0)],
                               [ns_hi.get('Global North', 0), ns_hi.get('Global South', 0)])):
    ax.text(i - w/2, a + 6, f'{a}\n{100*a/N_ALL:.1f}%', ha='center', fontsize=7.5, color=INK2)
    ax.text(i + w/2, b + 6, f'{b}\n{100*b/N_ALL:.1f}%', ha='center', fontsize=7.5, color=INK2)
ax.set_xticks(xs); ax.set_xticklabels(['Global North', 'Global South'], fontsize=8.5)
ax.set_ylabel('Studies'); ax.set_ylim(0, 620); ax.xaxis.grid(False); ax.set_axisbelow(True)
ax.legend(fontsize=7.0, loc='upper center', ncol=1, bbox_to_anchor=(0.5, 1.02))
ax.set_title('b  Global North / South', loc='left', fontsize=9.5, color=INK)
fig.tight_layout()
save(fig, 'Figure3_geography.png')
g = reg.to_frame('n'); g['pct'] = (100 * g.n / N_ALL).round(1)
tables['T5_regions'] = g.reset_index().rename(columns={'index': 'Region'})
tables['T5b_countries'] = (d.author_country.value_counts().to_frame('n')
                           .assign(pct=lambda x: (100*x.n/N_ALL).round(1)).reset_index()
                           .rename(columns={'index': 'First-author country'}))

# ================================================================ TABLE/FIG sensors
sen = tally('sensors'); tables['T6_sensors'] = sen.reset_index().rename(columns={'index': 'Sensor / platform'})
fig, ax = plt.subplots(figsize=(7.0, 4.4))
s = sen.head(16).iloc[::-1]
lbl = [textwrap.fill(i, 34) for i in s.index]
ax.barh(range(len(s)), s.pct, color=CAT[0], height=0.62, zorder=3)
ax.set_yticks(range(len(s))); ax.set_yticklabels(lbl, fontsize=8)
for i, (n, p) in enumerate(zip(s.n, s.pct)):
    ax.text(p + 0.7, i, f'{n}  ({p:.1f}%)', va='center', fontsize=7.5, color=INK2)
ax.set_xlabel('Share of full-text studies (%, n = ' + str(N_FT) + ')'); ax.set_xlim(0, 62)
ax.yaxis.grid(False); ax.set_axisbelow(True)
save(fig, 'Figure4_sensors.png')

# ================================================================ indices & products
idx = tally('indexs'); prod = tally('products')
tables['T7_indices'] = idx.reset_index().rename(columns={'index': 'Spectral index'})
tables['T8_products'] = prod.reset_index().rename(columns={'index': 'Biophysical variable / product'})
fig, axes = plt.subplots(1, 2, figsize=(7.6, 4.2))
for ax, t, ttl, col in [(axes[0], idx.head(12), 'a  Spectral vegetation indices', CAT[0]),
                        (axes[1], prod.head(12), 'b  Biophysical variables and products', CAT[2])]:
    t = t.iloc[::-1]
    ax.barh(range(len(t)), t.pct, color=col, height=0.6, zorder=3)
    ax.set_yticks(range(len(t))); ax.set_yticklabels([textwrap.fill(i, 26) for i in t.index], fontsize=7.5)
    for i, (n, p) in enumerate(zip(t.n, t.pct)):
        ax.text(p + 1.2, i, f'{n}', va='center', fontsize=7, color=INK2)
    ax.set_xlabel('% of full-text studies'); ax.set_xlim(0, max(t.pct) * 1.22)
    ax.yaxis.grid(False); ax.set_axisbelow(True)
    ax.set_title(ttl, loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, 'Figure5_indices.png')

# ================================================================ methods + DL over time
met = tally('methods'); tables['T9_methods'] = met.reset_index().rename(columns={'index': 'Method'})
fig, axes = plt.subplots(1, 2, figsize=(7.8, 4.3), gridspec_kw={'width_ratios': [1.25, 1]})
ax = axes[0]; m = met.head(15).iloc[::-1]
CLASS = {'Random Forest': 0, 'SVM / SVR': 0, 'Gradient boosting / XGBoost / LightGBM': 0,
         'Decision tree / CART': 0, 'k-NN': 0, 'ANN / MLP': 0, 'Naive Bayes': 0,
         'Maximum likelihood classifier': 0,
         'CNN (incl. ResNet, VGG, DeepLab)': 1, 'U-Net': 1, 'LSTM / GRU / RNN': 1,
         'Transformer / attention': 1, 'GAN': 1, 'Autoencoder': 1, 'Deep learning (generic)': 1}
cols = [CAT[1] if CLASS.get(i, 2) == 1 else (CAT[0] if CLASS.get(i, 2) == 0 else CAT[2]) for i in m.index]
ax.barh(range(len(m)), m.pct, color=cols, height=0.62, zorder=3)
ax.set_yticks(range(len(m))); ax.set_yticklabels([textwrap.fill(i, 30) for i in m.index], fontsize=7.5)
for i, (n, p) in enumerate(zip(m.n, m.pct)):
    ax.text(p + 0.6, i, f'{n}', va='center', fontsize=7, color=INK2)
ax.set_xlabel('% of full-text studies'); ax.set_xlim(0, 42)
ax.yaxis.grid(False); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=CAT[0], label='Classical / shallow ML'),
                   Patch(color=CAT[1], label='Deep learning'),
                   Patch(color=CAT[2], label='Statistical / time-series')],
          fontsize=7, loc='lower right')
ax.set_title('a  Methods across the corpus', loc='left', fontsize=9.5, color=INK)
ax = axes[1]
yy = range(2012, 2026)
sub = e[e.year.between(2012, 2025)]
tot = sub.groupby('year').size().reindex(yy, fill_value=0)
dl = sub[sub.uses_deep_learning].groupby('year').size().reindex(yy, fill_value=0)
ml = sub[sub.uses_shallow_ml].groupby('year').size().reindex(yy, fill_value=0)
den = tot.replace(0, np.nan)
ax.plot(list(yy), 100 * ml / den, color=CAT[0], lw=2, marker='o', ms=4, label='Classical / shallow ML')
ax.plot(list(yy), 100 * dl / den, color=CAT[1], lw=2, marker='s', ms=4, label='Deep learning')
ax.set_xlabel('Publication year'); ax.set_ylabel('% of full-text studies in year')
ax.set_ylim(0, 82); ax.legend(fontsize=7.5, loc='upper left')
ax.set_xticks(range(2013, 2026, 3))
ax.set_title('b  Adoption over time', loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, 'Figure6_methods.png')
tables['T10_ml_by_year'] = pd.DataFrame({'Year': list(yy), 'Full-text studies': tot.values,
                                         'Classical/shallow ML (n)': ml.values,
                                         'Deep learning (n)': dl.values})

# ================================================================ domains, biomes, gap map
dom = tally('domains'); bio = tally('biomes')
tables['T11_domains'] = dom.reset_index().rename(columns={'index': 'Application domain'})
tables['T12_biomes'] = bio.reset_index().rename(columns={'index': 'Biome'})
tables['T11b_domain_primary'] = (e.domain_primary.value_counts().to_frame('n')
    .assign(pct=lambda x: (100*x.n/N_FT).round(1)).reset_index().rename(columns={'index': 'Primary domain'}))
tables['T12b_biome_primary'] = (e.biome_primary.value_counts().to_frame('n')
    .assign(pct=lambda x: (100*x.n/N_FT).round(1)).reset_index().rename(columns={'index': 'Primary biome'}))

doms = list(dom.index); bios = [b for b in bio.index]
M = np.zeros((len(bios), len(doms)), int)
for _, r in e.iterrows():
    bs = [x for x in str(r.biomes).split(';') if x in bios]
    ds = [x for x in str(r.domains).split(';') if x in doms]
    for b in bs:
        for dd in ds: M[bios.index(b), doms.index(dd)] += 1
fig, ax = plt.subplots(figsize=(8.0, 4.8))
im = ax.imshow(M, cmap=BLUES, aspect='auto')
ax.set_xticks(range(len(doms))); ax.set_xticklabels([textwrap.fill(x, 16) for x in doms],
                                                    rotation=40, ha='right', fontsize=7.5)
ax.set_yticks(range(len(bios))); ax.set_yticklabels(bios, fontsize=7.5)
mx = M.max()
for i in range(len(bios)):
    for j in range(len(doms)):
        ax.text(j, i, M[i, j], ha='center', va='center', fontsize=6.8,
                color='#ffffff' if M[i, j] > 0.55 * mx else INK2)
ax.grid(False)
cb = fig.colorbar(im, ax=ax, shrink=0.82, pad=0.02); cb.set_label('Studies', fontsize=8)
cb.outline.set_visible(False)
ax.set_title('Evidence map: biome x application domain (full-text corpus, n = %d)' % N_FT,
             loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, 'Figure7_evidence_map.png')
tables['T13_gapmap'] = pd.DataFrame(M, index=bios, columns=doms).reset_index().rename(columns={'index': 'Biome'})

# ================================================================ climate variables
cli = tally('climates'); tables['T14_climate'] = cli.reset_index().rename(columns={'index': 'Climate variable'})

# ================================================================ open science
order = ['Repository link', 'Statement, no link', 'On request', 'Explicitly unavailable', 'Not stated']
cs = e.code_status.value_counts().reindex(order, fill_value=0)
ds = e.data_status.value_counts().reindex(order, fill_value=0)
fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.9), gridspec_kw={'width_ratios': [1, 1.05]})
ax = axes[0]
xs = np.arange(len(order)); w = 0.38
ax.bar(xs - w/2, cs.values, w, color=CAT[0], zorder=3, label='Analysis code')
ax.bar(xs + w/2, ds.values, w, color=CAT[1], zorder=3, label='Study data')
for i, (a, b) in enumerate(zip(cs.values, ds.values)):
    ax.text(i - w/2, a + 4, str(a), ha='center', fontsize=7, color=INK2)
    ax.text(i + w/2, b + 4, str(b), ha='center', fontsize=7, color=INK2)
ax.set_xticks(xs); ax.set_xticklabels([textwrap.fill(o, 11) for o in order], fontsize=7.5)
ax.set_ylabel('Studies (n = %d)' % N_FT); ax.legend(fontsize=7.5)
ax.xaxis.grid(False); ax.set_axisbelow(True)
ax.set_title('a  Availability statements', loc='left', fontsize=9.5, color=INK)
ax = axes[1]
per = e.groupby(pd.cut(e.year, [1999, 2009, 2014, 2019, 2022, 2025],
                       labels=['2000-09', '2010-14', '2015-19', '2020-22', '2023-25']), observed=False)
rate = per.apply(lambda g: pd.Series({
    'Code repository': 100 * (g.code_status == 'Repository link').mean() if len(g) else np.nan,
    'Data repository': 100 * (g.data_status == 'Repository link').mean() if len(g) else np.nan,
    'n': len(g)}))
xs = np.arange(len(rate))
ax.bar(xs - 0.19, rate['Code repository'], 0.38, color=CAT[0], zorder=3, label='Code repository link')
ax.bar(xs + 0.19, rate['Data repository'], 0.38, color=CAT[1], zorder=3, label='Data repository link')
for i in range(len(rate)):
    ax.text(i, max(rate['Code repository'].iloc[i], rate['Data repository'].iloc[i]) + 0.7,
            f"n={int(rate['n'].iloc[i])}", ha='center', fontsize=7, color=MUTED)
ax.set_xticks(xs); ax.set_xticklabels(rate.index, fontsize=7.5)
ax.set_ylim(0, max(rate['Code repository'].max(), rate['Data repository'].max()) * 1.35)
ax.set_ylabel('% of studies in period'); ax.legend(fontsize=7.5, loc='upper left')
ax.xaxis.grid(False); ax.set_axisbelow(True)
ax.set_title('b  Repository sharing over time', loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, 'Figure8_open_science.png')
os_t = pd.DataFrame({'Status': order, 'Code (n)': cs.values, 'Code (%)': (100*cs.values/N_FT).round(1),
                     'Data (n)': ds.values, 'Data (%)': (100*ds.values/N_FT).round(1)})
tables['T15_open_science'] = os_t
tables['T15b_os_by_period'] = rate.round(1).reset_index().rename(columns={'year': 'Period'})

# ================================================================ performance metrics
rep = pd.DataFrame({
 'Metric': ['R²', 'RMSE', 'MAE', 'Overall accuracy', 'Cohen’s kappa', 'F1 score'],
 'Studies reporting (n)': [(e[m + '_n'] > 0).sum() for m in ['r2', 'rmse', 'mae', 'oa', 'kappa', 'f1']],
})
rep['% of full-text corpus'] = (100 * rep['Studies reporting (n)'] / N_FT).round(1)
med = []
for m in ['r2_median', 'rmse_median', 'mae_median', 'oa_median', 'kappa_median', 'f1_median']:
    v = e[m].dropna(); med.append(f'{v.median():.2f} [{v.quantile(.25):.2f}-{v.quantile(.75):.2f}]' if len(v) else '-')
rep['Median of study medians [IQR]'] = med
rep.loc[rep.Metric == 'RMSE', 'Median of study medians [IQR]'] = 'unit-dependent; not pooled'
rep.loc[rep.Metric == 'MAE', 'Median of study medians [IQR]'] = 'unit-dependent; not pooled'
tables['T16_metric_reporting'] = rep

fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.8), gridspec_kw={'width_ratios': [1, 1.25]})
ax = axes[0]
r = rep.iloc[::-1]
ax.barh(range(len(r)), r['% of full-text corpus'], color=CAT[0], height=0.6, zorder=3)
ax.set_yticks(range(len(r))); ax.set_yticklabels(r['Metric'], fontsize=8)
for i, (n, p) in enumerate(zip(r['Studies reporting (n)'], r['% of full-text corpus'])):
    ax.text(p + 0.8, i, f'{n} ({p:.1f}%)', va='center', fontsize=7.5, color=INK2)
ax.set_xlabel('Share of full-text studies (%, n = ' + str(N_FT) + ')'); ax.set_xlim(0, 58)
ax.yaxis.grid(False); ax.set_axisbelow(True)
ax.set_title('a  Metric reporting rates', loc='left', fontsize=9.5, color=INK)
ax = axes[1]
sub = e[e.r2_median.notna()].copy()
keep = [k for k in sub.domain_primary.value_counts().index if sub.domain_primary.value_counts()[k] >= 8]
data = [sub.loc[sub.domain_primary == k, 'r2_median'].values for k in keep]
bp = ax.boxplot(data, vert=False, widths=0.58, patch_artist=True, showfliers=False)
for p in bp['boxes']: p.set(facecolor='#dce9fb', edgecolor=CAT[0], linewidth=1.1)
for p in bp['medians']: p.set(color=CAT[1], linewidth=1.8)
for k in ('whiskers', 'caps'):
    for p in bp[k]: p.set(color=CAT[0], linewidth=1.0)
for i, k in enumerate(keep):
    ax.scatter(sub.loc[sub.domain_primary == k, 'r2_median'],
               np.full((sub.domain_primary == k).sum(), i + 1) + np.random.uniform(-.13, .13,
               (sub.domain_primary == k).sum()), s=7, color=CAT[0], alpha=.35, zorder=4, linewidths=0)
ax.set_yticklabels([textwrap.fill(k, 22) + f'\n(n={int((sub.domain_primary==k).sum())})' for k in keep], fontsize=7)
ax.set_xlabel('Within-study median R²'); ax.set_xlim(0, 1.02)
ax.yaxis.grid(False); ax.set_axisbelow(True)
ax.set_title('b  Reported R² by primary domain', loc='left', fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, 'Figure9_performance.png')

r2dom = sub.groupby('domain_primary').r2_median.agg(['count', 'median',
        lambda s: s.quantile(.25), lambda s: s.quantile(.75)])
r2dom.columns = ['Studies (n)', 'Median R²', 'Q1', 'Q3']
tables['T17_r2_by_domain'] = r2dom.round(3).sort_values('Studies (n)', ascending=False).reset_index()

# RMSE for the biomass sub-corpus only (comparable units)
rm = []
for _, r in e.iterrows():
    try: vals = json.loads(r.rmse_values) if isinstance(r.rmse_values, str) else []
    except Exception: vals = []
    for v, u in vals:
        u2 = re.sub(r'\s+', '', str(u)).lower()
        if u2.startswith(('mgha', 'mg/ha', 't/ha', 'tha')) and 0 < v < 400:
            rm.append({'doi': r.doi, 'rmse': v, 'unit': 'Mg ha-1 (t ha-1)'})
rmdf = pd.DataFrame(rm)
tables['T18_rmse_biomass'] = rmdf
print('biomass RMSE obs', len(rmdf), 'studies', rmdf.doi.nunique() if len(rmdf) else 0)

# ================================================================ appendix tables
a1 = e[e.r2_n > 0][['title', 'year', 'doi', 'journal', 'domain_primary', 'biome_primary',
                    'sensors', 'methods', 'r2_n', 'r2_median', 'r2_max']].copy()
a1 = a1.sort_values('r2_median', ascending=False)
a1.columns = ['Title', 'Year', 'DOI', 'Journal', 'Primary domain', 'Primary biome',
              'Sensors', 'Methods', 'R² values reported (n)', 'Median R²', 'Max R²']
tables['A1_r2_studies'] = a1
a2 = e[e.code_status == 'Repository link'][['title', 'year', 'doi', 'journal', 'domain_primary',
                                            'code_url', 'data_status', 'data_url']]
a2.columns = ['Title', 'Year', 'DOI', 'Journal', 'Primary domain', 'Code repository',
              'Data status', 'Data repository']
tables['A2_code_studies'] = a2.sort_values('Year', ascending=False)

# ================================================================ review-article sensitivity
raw = pd.read_csv('/mnt/user-data/uploads/vegiclimate_review/data/step1_scopus_raw.csv',
                  encoding='latin-1', low_memory=False)
raw.columns = ['title', 'abstract', 'year', 'doi', 'authors', 'journal', 'doc_type',
               'language', 'cited_by', 'country', 'source']
key = lambda s: s.astype(str).str.strip().str.lower()
raw['doi_n'] = key(raw.doi)
e['doi_n'] = key(e.doi)
e2 = e.merge(raw[['doi_n', 'doc_type']].drop_duplicates('doi_n'), on='doi_n', how='left')
art = e2[e2.doc_type != 'Review']
N_ART = len(art); N_REV = int((e2.doc_type == 'Review').sum())
print('reviews in full-text corpus:', N_REV, 'primary studies:', N_ART)

def tal(df, col):
    c = Counter()
    for s in df[col].fillna(''):
        for k in str(s).split(';'):
            if k: c[k] += 1
    return c
sens = []
for col, keys in [('sensors', ['Landsat', 'MODIS', 'Sentinel-2', 'Sentinel-1',
                               'Airborne / spaceborne LiDAR (generic)', 'AVHRR / GIMMS']),
                  ('indexs', ['NDVI', 'EVI']),
                  ('methods', ['Random Forest', 'Linear / multiple regression',
                               'CNN (incl. ResNet, VGG, DeepLab)'])]:
    A, B = tal(e2, col), tal(art, col)
    for k in keys:
        sens.append((k, A[k], round(100 * A[k] / len(e2), 1), B[k], round(100 * B[k] / N_ART, 1),
                     round(100 * A[k] / len(e2) - 100 * B[k] / N_ART, 1)))
for f, lab in [('uses_deep_learning', 'Any deep learning'), ('uses_sar', 'Any SAR'),
               ('multi_sensor_fusion', 'Two or more sensor families')]:
    sens.append((lab, int(e2[f].sum()), round(100 * e2[f].mean(), 1), int(art[f].sum()),
                 round(100 * art[f].mean(), 1), round(100 * e2[f].mean() - 100 * art[f].mean(), 1)))
sens = pd.DataFrame(sens, columns=['Quantity', 'n (all, N=455)', '% (all)',
                                   'n (primary only, N=%d)' % N_ART, '% (primary only)',
                                   'Difference (pp)'])
tables['T19_review_sensitivity'] = sens
MAXPP = float(sens['Difference (pp)'].abs().max())
print('max sensitivity shift (pp):', MAXPP)
json.dump({'n_reviews': N_REV, 'n_primary': N_ART, 'max_pp': MAXPP},
          open(os.path.join(OUT, 'review_sensitivity.json'), 'w'))

# ================================================================ write workbook
with pd.ExcelWriter(os.path.join(OUT, 'Revised_Results_Tables.xlsx'), engine='openpyxl') as w:
    for k, v in tables.items():
        v.to_excel(w, sheet_name=k[:31], index=False)
json.dump({'N_ALL': int(N_ALL), 'N_FT': int(N_FT)}, open(os.path.join(OUT, 'ns.json'), 'w'))
print('tables written:', len(tables))
