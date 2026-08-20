# Vegetation–Climate Remote Sensing Review

Research compendium for **_From NDVI to Neural Networks: A Systematic Review of Satellite Remote
Sensing Methods for Monitoring Vegetation Responses to Climate Change (2000–2025)_**.

This repository contains the screening and extraction pipeline, the derived data tables, and the
figures for a PRISMA 2020 systematic review of 757 peer-reviewed studies, 455 of which were
assessed on full text.

---

## What is here

```
scripts/    the full pipeline, in run order
data/       derived data tables
figures/    Figures 1–9 at 330 dpi
docs/       extraction and validation notes
```

### `scripts/` — run order

| Script | Purpose |
|---|---|
| `link_pdfs.py` | match retrieved PDFs to bibliographic records by DOI and by title |
| `vocab.py` | controlled vocabularies: 26 sensor families, 18 spectral indices, 12 biophysical products, 30 analytical methods, 12 climate variables, 10 application domains, 13 biomes |
| `extract.py` | deterministic regular-expression extraction from the reference-stripped body text |
| `geo.py` | country → region and Global North/South assignment (UN M49) |
| `analyse.py` | all 23 result tables and all 9 figures |
| `newtext.py` | manuscript prose, held as named constants |
| `revise.py` | applies the prose, tables and figures to the manuscript |
| `verify.py` | recomputes 332 quantitative claims from source and reports any mismatch |

### `data/`

| File | Contents |
|---|---|
| `included_studies.csv` | the 757 included studies with DOI, title, authors, year, journal, first-author country, region, and which evidence tier each belongs to |
| `fulltext_extraction.csv` | per-study extraction for the 455 full-text studies, with per-term regular-expression hit counts so any value can be traced to its source |
| `Revised_Results_Tables.xlsx` | 23 sheets — every table in the paper plus the underlying data |
| `verification_checks.csv` | the 332 verification checks, with the stated and recomputed value side by side |

## Method in brief

Extraction is deterministic. No language model is in the loop, so every count is reproducible and
traceable to a span of source text.

- **Reference stripping.** The reference list is removed by locating the last `References` /
  `Bibliography` / `Literature Cited` heading in the final third of the document, so a sensor or
  algorithm named only in a cited title is never counted as having been used.
- **Counting rule.** A term counts as used when it occurs at least twice in the reference-stripped
  body text. Application domains require at least three occurrences and biomes at least four; the
  highest-scoring label is recorded as the study's primary domain and primary biome.
- **Metric validation.** R², κ and F1 are accepted only in [0, 1]; overall accuracy is normalised to
  a percentage and accepted only in [20, 100]; unit-less integers in 1900–2100 are rejected for RMSE
  and MAE as probable publication years. Study-level summaries are within-study medians, so a study
  reporting many model variants does not dominate the distribution. RMSE and MAE are never pooled
  across studies except within the above-ground biomass sub-corpus, where units are comparable.

Full detail is in [`docs/EXTRACTION_AND_VALIDATION_NOTES.md`](docs/EXTRACTION_AND_VALIDATION_NOTES.md).

## Two-tier evidence base

| Tier | Studies | Source | Supports |
|---|---|---|---|
| 1 — record level | 757 | Scopus bibliographic metadata | publication trends, geography |
| 2 — full text | 455 | open-access PDF, retrieved and parsed | all methodological results |

Of 1,482 reports sought for retrieval, an open-access full text was obtained for 572 (38.6%). Every
denominator in the paper states which tier it belongs to.

## Reproducing the analysis

```bash
pip install -r requirements.txt
python scripts/link_pdfs.py     # requires the source PDFs, which are not redistributed here
python scripts/extract.py
python scripts/analyse.py
python scripts/verify.py        # expect: 332 checks, 0 FAIL
```

`analyse.py` and `verify.py` run against the derived tables in `data/` and reproduce every table,
figure and quantitative claim without the source PDFs. `link_pdfs.py` and `extract.py` need the
PDFs themselves — see below.

## Source articles

The PDFs of the reviewed articles, and the plain-text conversions used as extraction input, are
**not** included. They are copyright of their respective publishers and cannot be redistributed.
Every included study is listed with its DOI in `data/included_studies.csv`, so the corpus can be
reassembled by anyone with the appropriate access. The per-term hit counts in
`fulltext_extraction.csv` make each extracted value auditable without the source text.

## Licence

- **Code** (`scripts/`) — MIT, see [`LICENSE`](LICENSE)
- **Data and figures** (`data/`, `figures/`) — CC BY 4.0, see [`LICENSE-data`](LICENSE-data)

## Citation

If you use this compendium, please cite the paper. A `CITATION.cff` file is included and GitHub will
render a formatted citation from it.

---

**Repository:** https://github.com/Azad77/vegetation-climate-rs-review
**Author:** Azad Rasul, Soran University — azad.rasul@soran.edu.iq
