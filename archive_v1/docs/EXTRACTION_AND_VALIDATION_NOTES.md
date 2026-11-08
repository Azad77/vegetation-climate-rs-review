# Extraction and validation notes

Supporting documentation for *From NDVI to Neural Networks: A Systematic Review of Satellite
Remote Sensing Methods for Monitoring Vegetation Responses to Climate Change (2000–2025)*.

This note records how the methodological results were produced and how they were checked. It is
a working document for the author and reviewers; it is not part of the manuscript.

---

## 1. Two-tier evidence base

| Tier | Studies | Source | Supports |
|---|---|---|---|
| 1 — record level | 757 | Scopus bibliographic metadata | Sections 3.2–3.3 (year, outlet, country) |
| 2 — full text | 455 | open-access PDF, retrieved and parsed | Sections 3.4–3.11 (all methodological results) |

Of the 1,482 reports sought for retrieval, an open-access full text was obtained for 572 (38.6%).
455 of those are in the final corpus; 117 were assessed and excluded. For the remaining 910
reports no full text could be retrieved: 302 were retained on the basis of title and abstract and
608 were excluded. Every denominator in the manuscript states which tier it belongs to.

## 2. Extraction pipeline

Deterministic regular-expression extraction, with no language model in the loop, so that every
count is reproducible and traceable to a span of source text.

1. **Text preparation** — `pdftotext` (Poppler); ligature and hyphenation normalisation; the
   reference list removed by locating the last `References` / `Bibliography` / `Literature Cited`
   heading in the final two-thirds of the document, so that a sensor or algorithm named only in a
   cited title cannot be counted as having been used.
2. **Controlled vocabularies** (`vocab.py`) — 26 sensor families, 18 spectral indices, 12
   biophysical products, 30 analytical methods, 12 climate variables, 10 application domains,
   13 biomes. Every entry is a word-boundary-anchored regular expression.
3. **Counting rule** — a term counts as used when it occurs at least twice in the
   reference-stripped body text. Application domains require at least three occurrences and
   biomes at least four; the highest-scoring label is additionally recorded as the study's
   primary domain and primary biome.
4. **Disambiguation** — a bare mention of "decision tree" in a study that applied Random Forest is
   not counted as a separate method, since decision trees are the base learner of Random Forest;
   the generic forest label is suppressed where a specific forest type is identified.
5. **Metric validation** — R², kappa and F1 accepted only in [0, 1]; overall accuracy normalised
   to a percentage and accepted only in [20, 100]; unit-less integers in the range 1900–2100
   rejected for RMSE and MAE as probable publication years. All values reported by a study are
   retained (1,408 R² values across 186 studies) and summarised as within-study medians, so that
   a study reporting many model variants does not dominate the distribution. RMSE and MAE are
   never pooled across studies; a pooled summary is given only for the above-ground biomass
   sub-corpus, where units are comparable.
6. **Open science** — assessed from the whole document, including statements printed after the
   reference list. A study counts as sharing only where a resolvable repository identifier is
   present (GitHub, GitLab, Bitbucket, Zenodo, Code Ocean, OSF, figshare, Dryad, PANGAEA,
   Mendeley Data, or a Google Earth Engine script link). Availability statements without a link,
   offers of material on request, and explicit refusals are recorded as separate categories,
   because a large share of studies carry a data-availability statement that refers only to the
   third-party satellite products used.

Per-study regular-expression hit counts for every vocabulary term are retained in
`fulltext_extraction.csv`, so any single value in the manuscript can be traced to its source.

## 3. Sensitivity and robustness

- **Review articles.** 20 of the 455 full-text studies are reviews. They name more platforms than
  primary studies (6.6 sensor families on average against 2.71). Recomputing every headline
  quantity over the 435 primary studies alone changes no value by more than 1.9 percentage
  points. Reviews are retained, in keeping with the pre-specified eligibility criteria, and the
  full comparison is Table 14.
- **Global North / South.** Reported under the UN M49 definition of developed regions, with a
  sensitivity classification adding the high-income East Asian economies. Both appear in
  Figure 3b.
- **Open-access bias.** The full-text corpus over-represents recent, well-funded and European or
  North American work, because open-access availability correlates with year, journal and funder.
  This is stated as a limitation in Section 4.7.

## 4. Verification

`verify.py` recomputes **332 quantitative claims** in the manuscript directly from the extraction
table, the master spreadsheet and the screening logs — every count, every percentage, every
PRISMA cell, and the review-article sensitivity bounds. All 332 pass. Results are itemised in
`verification_checks.csv` with the stated and recomputed value side by side.

## 5. Open items for the author

1. **Unlogged screening decisions.** 143 of the 725 full-text-stage exclusions carry no logged
   decision and were derived by subtraction; 25 of these are records for which no DOI was
   recorded. A further 85 records that passed full-text screening do not appear in the final
   corpus, having been removed by later cleaning steps without a logged reason. This is reported
   in Section 4.7. Future updates should log every screening and cleaning decision at record
   level.
2. **Prospective registration.** Not completed for this review; noted in Section 4.7. Worth doing
   for any update.

## 6. Files

| File | Contents |
|---|---|
| `VegeClimate Review Paper WithCitations 25_04_2026.docx` | the manuscript |
| `VegeClimate Review Paper WithCitations 25_04_2026.pdf` | rendered PDF |
| `Revised_Results_Tables.xlsx` | 23 sheets — every table in the paper plus the underlying data |
| `fulltext_extraction.csv` | per-study extraction with per-term hit counts |
| `verification_checks.csv` | the 332 verification checks |
| `figures/` | Figures 1–9 at 330 dpi |
| `scripts/` | the full pipeline: `link_pdfs.py`, `vocab.py`, `extract.py`, `geo.py`, `analyse.py`, `newtext.py`, `revise.py`, `verify.py` |
| `pdf_text/` | plain-text conversions of the source PDFs (extraction input) |
