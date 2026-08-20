# -*- coding: utf-8 -*-
"""Apply the corrected numbers, tables and figures to the manuscript."""
import copy, os, json, re
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import newtext as T

SRC = '/home/claude/work/ms.docx'
DST = '/home/claude/work/out/VegeClimate Review Paper WithCitations 25_04_2026.docx'
FIG = '/home/claude/work/out/figures'
XL = '/home/claude/work/out/Revised_Results_Tables.xlsx'
xl = pd.ExcelFile(XL)

doc = Document(SRC)
body = doc.element.body

# ---------------------------------------------------------------- helpers
def find(prefix):
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise KeyError(prefix)

def set_text(p, text, plain=True):
    """Replace a paragraph's text, keeping the formatting of its first run."""
    runs = p.runs
    if not runs:
        r = p.add_run(text)
        if plain: r.bold = False; r.italic = False
        return p
    runs[0].text = text
    if plain:
        runs[0].bold = False; runs[0].italic = False
    for r in runs[1:]:
        r._element.getparent().remove(r._element)
    return p

def clone_after(p, text, style=None):
    new = copy.deepcopy(p._p)
    p._p.addnext(new)
    from docx.text.paragraph import Paragraph
    np_ = Paragraph(new, p._parent)
    set_text(np_, text)
    if style: np_.style = doc.styles[style]
    return np_

from docx.text.paragraph import Paragraph as _P

# a clean Normal paragraph to clone from
_TEMPLATE = None
for _p in doc.paragraphs:
    if _p.style.name == 'Normal' and _p.text.strip().startswith('Vegetation covers approximately'):
        _TEMPLATE = _p._p
        break
assert _TEMPLATE is not None

def after(el, newel):
    el.addnext(newel); return newel

def mk_para(text, italic=False, bold=False, size=None, center=False):
    el = copy.deepcopy(_TEMPLATE)
    p = _P(el, doc)
    set_text(p, text)
    for r in p.runs:
        r.italic = italic; r.bold = bold
        if size: r.font.size = Pt(size)
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return el

def mk_img_para(path, width=6.3):
    el = copy.deepcopy(_TEMPLATE)
    p = _P(el, doc)
    for r in list(p.runs): r._element.getparent().remove(r._element)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width))
    return el

def mk_table(df, fontsize=8.5, widths=None):
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = doc.styles['Table Grid']
    hdr = t.rows[0].cells
    for j, c in enumerate(df.columns):
        hdr[j].text = str(c)
        for pp in hdr[j].paragraphs:
            for r in pp.runs: r.bold = True; r.font.size = Pt(fontsize)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = '' if pd.isna(v) else (f'{v:g}' if isinstance(v, float) else str(v))
            for pp in cells[j].paragraphs:
                for r in pp.runs: r.font.size = Pt(fontsize)
    if widths:
        from docx.oxml import OxmlElement
        t.autofit = False
        tblPr = t._tbl.tblPr
        for tag in ('w:tblLayout', 'w:tblW'):
            for e in tblPr.findall(qn(tag)): tblPr.remove(e)
        lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
        tw = OxmlElement('w:tblW')
        tw.set(qn('w:w'), str(int(sum(widths) * 1440))); tw.set(qn('w:type'), 'dxa')
        tblPr.append(tw)
        grid = t._tbl.find(qn('w:tblGrid'))
        if grid is not None:
            for gc in list(grid): grid.remove(gc)
            for w in widths:
                gc = OxmlElement('w:gridCol'); gc.set(qn('w:w'), str(int(w * 1440))); grid.append(gc)
        for row in t.rows:
            for j, w in enumerate(widths):
                row.cells[j].width = Inches(w)
    el = t._tbl
    el.getparent().remove(el)
    return el

def replace_table_after(caption_prefix, df, fontsize=8.5, widths=None):
    """Replace the first <w:tbl> that follows the paragraph starting with caption_prefix."""
    cap = find(caption_prefix)
    el = cap._p.getnext()
    while el is not None and not el.tag.endswith('}tbl'):
        el = el.getnext()
    assert el is not None, caption_prefix
    el.addnext(mk_table(df, fontsize, widths))
    el.getparent().remove(el)

def put_figure(p, path, width=6.3):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width))

def figure_block(el, img, caption, width=6.3):
    el = after(el, mk_img_para(os.path.join(FIG, img), width))
    el = after(el, mk_para(caption))
    return el

def table_block(el, caption, df, note=None, fontsize=8.5):
    el = after(el, mk_para(caption, italic=True, bold=True, size=10, center=True))
    el = after(el, mk_table(df, fontsize))
    if note:
        el = after(el, mk_para(note, italic=True, size=9))
    el = after(el, mk_para(''))
    return el

# ================================================================ 1. text swaps
SWAPS = [
 ("This study presents a comprehensive PRISMA 2020-compliant systematic review", T.ABSTRACT),
 ("Structured data extraction was performed for all 757", T.M25_1),
 ("Performance metrics (R², RMSE, MAE, overall accuracy, F1 score", T.M25_2),
 ("The systematic search of Scopus retrieved 4,794 records", T.R31_V2),
 ("The review protocol was designed and documented prior to data collection", T.M21_FIX),
 ("Vegetation covers approximately 71% of the ice-free land surface", T.INTRO_VEG),
 ("The annual distribution of included studies revealed", T.R32),
 ("First-author institutional affiliation was used as a proxy", T.R33_1),
 ("Classification of studies by the Global North/South framework", T.R33_2),
 ("A total of 110 unique sensor tokens were identified", T.R34),
 ("Analytical approaches spanned a continuum", T.R35_1),
 ("Random Forest was the most commonly applied method (n = 160", T.R35_2),
 ("Deep learning methods showed a marked increase in prevalence from 2019 onward. Convolutional", T.R35_3),
 ("Note: Percentage values are calculated relative to the total corpus", T.R35_NOTE),
 ("Spectral indices were extracted or referenced in 460 studies", T.R36),
 ("Climate variables were explicitly mentioned in 592", T.R37),
 ("Phenology constituted the largest single domain (n = 234", T.R38),
 ("Biome classification was inferable for 391 studies", T.R39),
 ("The adoption of open science practices remained limited across the corpus.", T.R310),
 ("Quantitative model performance metrics were explicitly reported", T.R311),
 ("This review synthesised 757 peer-reviewed studies published between 2000 and 2025 to provide", T.D40),
 ("The annual publication trajectory documented in Section 3.2", T.D41_1),
 ("This surge is temporally coherent with three independently documented developments.", T.D41_2),
 ("The rapid growth trajectory also introduces structural concerns.", T.D41_3),
 ("The geographic analysis presented in Section 3.3", T.D42_1),
 ("The mismatch between where research is conducted and where the world", T.D42_2),
 ("Section 3.4 documents 110 unique sensor terms", T.D43_1),
 ("The temporal progression of sensor use reflects", T.D43_2),
 ("The spectral index landscape is equally concentrated.", T.D43_3),
 ("The analytical method distribution documented in Section 3.5", T.D44_1),
 ("Deep learning methods showed a marked increase in prevalence from 2019 onwards. CNNs", T.D44_2),
 ("The broader methodological literature", T.D44_3),
 ("A persistent methodological limitation documented across the corpus", T.D44_4),
 ("Phenology constituted the largest application domain in the corpus", T.D45_1),
 ("The biome distribution documented in Section 3.9", T.D45_2),
 ("The under-representation of drylands is particularly consequential.", T.D45_3),
 ("Peatland under-representation is similarly acute.", T.D45_4_V2),
 ("The open science audit documented in Section 3.10", T.D46_1),
 ("These rates are low by the standards of neighbouring disciplines", T.D46_2),
 ("The temporal trajectory of open science adoption", T.D46_3),
 ("Database coverage. This review searched a single bibliographic database", T.D47_COVERAGE),
 ("The evidence base assembled across 757 studies and the systematic analysis", T.D48_0),
 ("First, the geographic equity deficit demands targeted investment", T.D48_1),
 ("Second, the systematic under-representation of drylands", T.D48_2),
 ("Third, the performance metric inconsistency documented across the corpus", T.D48_3),
 ("Fourth, the under-utilisation of Solar-Induced Fluorescence", T.D48_4),
 ("Fifth, the open science deficit documented here", T.D48_5),
 ("Taken together, the findings of this review affirm", T.D48_6),
 ("This systematic review synthesised evidence from 757 studies to provide", T.C1),
 ("First, the dominance of a limited set of sensors", T.C2),
 ("Additionally, the review identifies major gaps in biome coverage", T.C3),
 ("Future research should prioritise multi-sensor data fusion", T.C4),
]
log = []
for prefix, new in SWAPS:
    set_text(find(prefix), new)
    log.append(('replaced', prefix[:60]))
print('text swaps:', len(log))

# --- Section 2.4, Stage 5: rewrite the retrieval and eligibility narrative
p_s5 = find("Full-text eligibility assessment was performed for all 1,482 records")
set_text(p_s5, T.M24_S5_A)
p_s5b = find("Full-text screening decisions were applied to extracted abstract")
set_text(p_s5b, T.M24_S5_B)
after(p_s5b._p, mk_para(T.M24_S5_C))

# extra limitation paragraph on extraction fidelity, before "Database coverage."
_ef = clone_after(find("Database coverage and full-text availability."), T.D47_EXTRA)
after(_ef._p, mk_para(T.D47_SCREEN))

# ================================================================ 2. section 2.8
p0 = find("All Python scripts used in the screening, extraction, and synthesis pipeline")
set_text(p0, "All Python and shell scripts used in the screening, extraction, re-extraction and "
                   "synthesis pipeline, together with the complete extraction tables, are provided as "
                   "supplementary material to ensure full reproducibility of the review.")
h = clone_after(p0, T.M28_HEAD, style='Heading 2')
el = h._p
for _t in (T.M28_1, T.M28_2, T.M28_3, T.M28_4, T.M28_5):
    el = after(el, mk_para(_t))

# ================================================================ 3. PRISMA table
set_text(find("Table 3. PRISMA 2020 record counts across all screening stages."),
         "Table 3. PRISMA 2020 record counts across all screening stages, including reports "
         "sought for retrieval, reports retrieved, and the evidence base on which each included "
         "study was assessed.")
replace_table_after('Table 3. PRISMA 2020 record counts', xl.parse('T3_PRISMA'), fontsize=8.5)

# ================================================================ 4. replace Tables 5 & 6
sen = xl.parse('T6_sensors').head(16)
sen.columns = ['Sensor / platform', 'n', '% of full-text corpus']
sen['Primary application'] = [
 'Land cover change; 30 m archive since 1972', 'Daily global vegetation products since 2000',
 '10-20 m multispectral; free; 2015-present', 'All-weather; biomass and structure (unattributed)',
 'C-band SAR; free; 2014-present', '3D canopy structure; biomass calibration',
 'Long NDVI archive from 1981', 'Very-high-resolution validation and upscaling',
 'L-band SAR; forest structure and biomass', 'Legacy 1 km-20 m optical record',
 'Sub-metre to 2 m optical; validation', 'Spaceborne LiDAR waveform; canopy height',
 'Imaging spectroscopy; stress and species', '3 m daily optical; phenology and disturbance',
 'MODIS continuity; 375-750 m', 'Spaceborne photon-counting LiDAR']
replace_table_after('Table 5. Top ten remote sensing sensors', sen[['Sensor / platform', 'n', '% of full-text corpus', 'Primary application']])

met = xl.parse('T9_methods').head(18)
met.columns = ['Method', 'n', '% of full-text corpus']
CLS = {'Random Forest': 'Ensemble / tree-based', 'Linear / multiple regression': 'Statistical',
 'SVM / SVR': 'Kernel-based', 'Mann-Kendall / Sen slope': 'Trend statistics',
 'Correlation analysis': 'Statistical', 'Deep learning (generic)': 'Deep learning',
 'Gradient boosting / XGBoost / LightGBM': 'Ensemble / tree-based', 'ANN / MLP': 'Shallow neural network',
 'Decision tree / CART': 'Tree-based', 'CNN (incl. ResNet, VGG, DeepLab)': 'Deep learning',
 'PLS / PLSR': 'Statistical', 'Time-series break detection (BFAST/LandTrendr/CCDC)': 'Time-series',
 'Object-based image analysis': 'Image analysis', 'GAM / GLM': 'Statistical',
 'Explainable AI (SHAP/LIME)': 'Interpretability', 'Spectral unmixing': 'Image analysis',
 'LSTM / GRU / RNN': 'Deep learning', 'Process-based / DGVM model': 'Process-based',
 'Maximum likelihood classifier': 'Classical classifier', 'U-Net': 'Deep learning'}
met['Category'] = met['Method'].map(CLS).fillna('Other')
replace_table_after('Table 6. Frequency of machine learning', met)

# ================================================================ 5. new result tables
p_i = find("At least one spectral vegetation index was identified")._p
idx = xl.parse('T7_indices'); idx.columns = ['Spectral index', 'n', '% of full-text corpus']
last = table_block(p_i, "Table 7. Spectral vegetation indices identified in the full-text corpus (n = 455).",
                   idx)
prod = xl.parse('T8_products'); prod.columns = ['Biophysical variable / product', 'n', '% of full-text corpus']
last = table_block(last, "Table 8. Biophysical variables and higher-level products identified in the "
                         "full-text corpus (n = 455).", prod)
figure_block(last, 'Figure5_indices.png',
             "Figure 5. (a) Spectral vegetation indices and (b) biophysical variables and products "
             "identified in the full-text corpus (n = 455). Counts exceed the corpus size because "
             "studies commonly use several indices.")

p_i = find("Application domains were assigned as multi-label attributes")._p
dom = xl.parse('T11_domains'); dom.columns = ['Application domain', 'Studies (n)', '% of full-text corpus']
prim = xl.parse('T11b_domain_primary').set_index('domain_primary')['n']
dom['Primary domain (n)'] = dom['Application domain'].map(prim).fillna(0).astype(int)
table_block(p_i, "Table 9. Application domains in the full-text corpus (n = 455), as multi-label "
                      "attributes and as the single highest-scoring primary domain.", dom)

p_i = find("A primary biome was assignable for 426")._p
bio = xl.parse('T12_biomes'); bio.columns = ['Biome', 'Studies mentioning (n)', '% of full-text corpus']
bprim = xl.parse('T12b_biome_primary').set_index('biome_primary')['n']
bio['Primary biome (n)'] = bio['Biome'].map(bprim).fillna(0).astype(int)
last = table_block(p_i, "Table 10. Biome coverage in the full-text corpus (n = 455).", bio)
figure_block(last, 'Figure7_evidence_map.png',
             "Figure 7. Evidence map cross-tabulating biome against application domain for the "
             "full-text corpus (n = 455). Empty and near-empty cells identify the structural "
             "evidence gaps discussed in Section 4.5.")

p_i = find("Open science practice was assessed from the full text")._p
os_t = xl.parse('T15_open_science')
last = table_block(p_i, "Table 11. Code and data availability in the full-text corpus (n = 455). "
                             "A study counts as sharing only where a resolvable repository identifier "
                             "is present.", os_t)
figure_block(last, 'Figure8_open_science.png',
             "Figure 8. (a) Code and data availability statements across the full-text corpus "
             "(n = 455). (b) Share of studies providing a resolvable public repository, by "
             "publication period.")

p_i = find("Reporting of quantitative validation statistics")._p
rep = xl.parse('T16_metric_reporting')
last = table_block(p_i, "Table 12. Reporting of model performance metrics in the full-text corpus "
                             "(n = 455). Study-level summaries are within-study medians.", rep,
                   note="Note: RMSE and MAE are not pooled because their units are application-specific. "
                        "Within the above-ground biomass sub-corpus, where units are comparable, 34 "
                        "studies reported 193 RMSE values with a median of 27.2 Mg ha-1 (IQR 14.5-45.5).")
r2d = xl.parse('T17_r2_by_domain')
r2d.columns = ['Primary application domain', 'Studies (n)', 'Median R²', 'Q1', 'Q3']
last = table_block(last, "Table 13. Within-study median R² by primary application domain, for the 186 "
                         "full-text studies reporting R².", r2d)
figure_block(last, 'Figure9_performance.png',
             "Figure 9. (a) Share of full-text studies reporting each validation metric (n = 455). "
             "(b) Distribution of within-study median R² by primary application domain, for domains "
             "with at least eight reporting studies.")

# ================================================================ 6. figures 1-4, 6
cap1 = find("Figure 1. PRISMA 2020 flow diagram")
from docx.text.paragraph import Paragraph as _P
put_figure(_P(cap1._p.getprevious(), cap1._parent), os.path.join(FIG, 'Figure1_PRISMA.png'), 5.6)
set_text(cap1,
         "Figure 1. PRISMA 2020 flow diagram of the systematic literature search and selection "
         "process (n = 757 included studies, of which 455 were assessed on full text).")
cap2 = find("Figure 2. Annual publication trend")
put_figure(_P(cap2._p.getprevious(), cap2._parent), os.path.join(FIG, 'Figure2_publication_trend.png'))
set_text(cap2,
         "Figure 2. Annual publication trend of included vegetation-climate remote sensing studies, "
         "2000-2025 (n = 757), with the subset assessed on full text (n = 455) shown in the "
         "lighter tone.")
cap3 = find("Figure 3. Geographic distribution")
put_figure(_P(cap3._p.getprevious(), cap3._parent), os.path.join(FIG, 'Figure3_geography.png'))
set_text(cap3,
         "Figure 3. (a) Regional distribution of included studies by first-author affiliation "
         "(n = 757). (b) Global North / South classification under the UN M49 definition of "
         "developed regions and under a sensitivity classification that adds the high-income East "
         "Asian economies.")

# Figure 4 after the sensors table (Table 5)
p_t5 = find("Table 5. Top ten remote sensing sensors")
set_text(p_t5, "Table 5. Most frequently used remote sensing sensors and platforms in the "
                   "full-text corpus (n = 455).")
tbl5 = p_t5._p.getnext()          # the table element
while not tbl5.tag.endswith('}tbl'): tbl5 = tbl5.getnext()
_f4 = figure_block(tbl5, 'Figure4_sensors.png',
             "Figure 4. Sensors and platforms used in the full-text corpus (n = 455). Counts exceed "
             "the corpus size because most studies use more than one sensor family.")
_sens = after(_f4, mk_para(T.R34_SENS))
sens_df = xl.parse('T19_review_sensitivity')
table_block(_sens, "Table 14. Sensitivity of headline quantities to the inclusion of review "
                   "articles (20 of 455 full-text studies).", sens_df)

# Figure 6 after Table 6 note
figure_block(find("Note: percentages are calculated relative to the 455-study full-text corpus")._p, 'Figure6_methods.png',
             "Figure 6. (a) Analytical methods across the full-text corpus (n = 455), coloured by "
             "method class. (b) Share of full-text studies in each publication year applying "
             "classical/shallow machine learning and deep learning.")

# ================================================================ 7. appendix tables
set_text(find("Table A1. Model Performance Benchmarks"), "Table A1. Model performance benchmarks: full-text studies reporting R² (n = 186)")
set_text(find("Studies ranked by descending R²"), "Studies ranked by descending within-study median R². All R² values were extracted "
                   "from the reference-stripped body text and validated to the interval 0-1; the "
                   "number of values recovered per study is given so that single-value and "
                   "many-model studies can be distinguished. Dashes indicate fields that could not "
                   "be classified from the available text.")
def short(s, n):
    s = str(s)
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '\u2026'

a1 = xl.parse('A1_r2_studies').copy()
a1['Study'] = a1['Title'].apply(lambda s: short(s, 70))
a1['Median R²'] = a1['Median R²'].round(3); a1['Max R²'] = a1['Max R²'].round(3)
a1['Primary biome'] = a1['Primary biome'].fillna('-').str.replace(' (unspecified)', '', regex=False)
a1 = a1[['Study', 'Year', 'DOI', 'Primary domain', 'Primary biome',
         'R² values reported (n)', 'Median R²', 'Max R²']]
a1 = a1.replace({'Unclassified': '-'})
replace_table_after('Table A1. Model performance benchmarks', a1, fontsize=7,
                    widths=[3.05, 0.4, 1.35, 1.05, 0.85, 0.55, 0.55, 0.5])

set_text(find("Table A2. Open Science Practices"), "Table A2. Open science practice: full-text studies providing a resolvable public "
                   "code repository (n = 40)")
set_text(find("Studies that explicitly reported sharing analysis code"), "Studies for which a resolvable code repository identifier (GitHub, GitLab, "
                   "Bitbucket, Zenodo, Code Ocean, OSF or a Google Earth Engine script link) was "
                   "found in the full text. Data availability is reported separately using the same "
                   "evidence standard.")
a2 = xl.parse('A2_code_studies').copy()
a2['Study'] = a2['Title'].apply(lambda s: short(s, 70))
a2['Code repository'] = a2['Code repository'].fillna('-').astype(str).apply(lambda s: short(s, 55))
a2['Data repository'] = a2['Data repository'].fillna('-').astype(str).apply(lambda s: short(s, 45))
a2 = a2[['Study', 'Year', 'DOI', 'Primary domain', 'Code repository', 'Data status', 'Data repository']]
a2 = a2.replace({'Unclassified': '-'})
replace_table_after('Table A2. Open science practice', a2, fontsize=7,
                    widths=[2.3, 0.4, 1.25, 0.95, 1.85, 0.75, 0.8])

# restore bold lead-ins on the limitation paragraphs
for lead in ("Protocol registration.", "Extraction fidelity.",
             "Database coverage and full-text availability."):
    p = find(lead)
    r0 = p.runs[0]
    rest = r0.text[len(lead):]
    r0.text = lead; r0.bold = True
    nr = p.add_run(rest); nr.bold = False; nr.italic = False

# add the Yu (2012) reference, keeping the list's existing ordering convention
_anchor = find("Zhou, Y., Sachs, T.")
after(_anchor._p, mk_para(T.REF_YU))

# the Table 6 note inherits a coloured run from the template - force body ink
from docx.shared import RGBColor as _RGB
_n = find("Note: percentages are calculated relative to the 455-study full-text corpus")
for _r in _n.runs:
    _r.font.color.rgb = _RGB(0x0b, 0x0b, 0x0b); _r.italic = True; _r.font.size = Pt(9)

# ---- Data Availability Statement, immediately before the reference list
_refs = None
for _p in doc.paragraphs:
    if _p.text.strip() == 'References' and _p.style.name.startswith('Heading'):
        _refs = _p; break
_hel = mk_para(T.DAS_HEAD)
_refs._p.addprevious(_hel)
from docx.text.paragraph import Paragraph as _PP
_PP(_hel, doc).style = doc.styles['Heading 1']
_el = _hel
for _t in (T.DAS_1, T.DAS_2, T.DAS_3):
    _el = after(_el, mk_para(_t))

doc.save(DST)
print('saved', DST)
