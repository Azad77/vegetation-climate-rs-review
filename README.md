# Vegetation–Climate Remote Sensing Review

Research compendium for **_From NDVI to Neural Networks: A Systematic Review of Satellite Remote
Sensing Methods for Monitoring Vegetation Responses to Climate Change (2000–2025)_** (revised version, R1).

The review follows PRISMA 2020. A Scopus search returned 4,794 records; 1,482 were screened on title and
abstract and **811 studies** were included, **369** of them extracted from full text. Every count in the
paper can be recomputed from the files here.

---

## Layout

```
data/          Scopus export and first-version screening records (inputs; bibliographic fields only)
review/        the revised review
  scripts/                 the full pipeline (run order in Supplementary Text S2)
  included_studies.csv     the 811 included studies with DOI and evidence tier
  fulltext_extraction.csv  per-study extraction for the 369 full-text studies, with per-term hit counts
  Revised_Results_Tables.xlsx  every result table
  figures/                 Figures 1–9
  data_v2/                 revised corpus (master_v2.xlsx) and PDF links
  reviewer_response/       Supplementary Tables S1–S14, Supplementary Texts S1–S3 and intermediate files
archive_v1/    the first-version compendium (757 studies, 455 full text), superseded by the revision
```

## Supplementary material

| Item | File (in `review/reviewer_response/`) | Script |
|---|---|---|
| Text S1 — search query as executed | `Supplementary_Text_S1_search_query.txt` | — |
| Text S2 — reproduction guide | `Supplementary_Text_S2_reproduction_guide.md` | — |
| Text S3 — title-and-abstract screening rules | `Supplementary_Text_S3_rescreening_rules.md` | — |
| Table S1 — record-level PRISMA log (1,482 records) | `Table_S1_PRISMA_record_log.*` | `prisma_v2.py` |
| Table S2 — agreement with the first-version screening | `Table_S2_screening_agreement.*` | `screening_agreement_S2.py` |
| Table S3 — corpus change from the first version | `Table_S3_corpus_change.*` | `corpus_change_S3.py` |
| Tables S4–S6 — search recall and screening sensitivity | `Table_S4_*`, `Table_S5_*`, `Table_S6_*` | `search_screening_eval.py` |
| Tables S7–S8 — extraction validation, corrected prevalence | `Table_S7_*`, `Table_S8_*` | `score_validation.py` |
| Table S9 — validation design and reporting quality | `Table_S9_*` | `design_outputs.py` |
| Tables S10–S11 — biome representation, first author vs study area | `Table_S10_*`, `Table_S11_*` | `geography_biome.py` |
| Table S12 — computational checks | `Table_S12_*` | `verify_v2.py` |
| Table S13 — forest vs other studies | `Table_S13_*` | `forest_subset.py` |
| Table S14 — index prominence vs citation benchmark | `Table_S14_*` | `index_bias.py` |

## Method in brief

- **Title-and-abstract screening.** Abstracts were retrieved by DOI from OpenAlex, Crossref and Semantic
  Scholar (available for 1,265 of 1,482 records). Records were screened with Claude Opus 5.5 against the
  written rules in Text S3; every decision is in `screening_v2/v2_dec_*.txt` and Table S1. The decisions
  were not checked against an independent human screening (see Section 4.7 of the paper).
- **Extraction is deterministic.** No language model is used in extraction, so every count is reproducible
  and traceable to a span of source text. The reference list is removed before matching; a term counts as
  used when it occurs at least twice in the body text (domains three times, biomes four).
- **Validation.** The extraction was checked against reference labels for a stratified sample of 40
  studies (92% accuracy, κ = 0.78; Tables S7–S8), and sensor shares are corrected for misclassification.

## Reproducing the analysis

```bash
pip install -r requirements.txt
cd review/scripts
python prisma_v2.py              # Table 3, Figure 1, Table S1
python screening_agreement_S2.py # Table S2
python corpus_change_S3.py       # Table S3
python analyse.py                # result tables and Figures 2-8
python forest_subset.py          # Table S13
python design_outputs.py         # Table S9, Table 14, Figure 9
```

These run from the files in the repository. Steps that read the full texts or call the OpenAlex API
(`extract.py`, `validation_sample.py`, `openalex_fetch.py`, `abstracts_v2.py`) need the source PDFs or network
access; the full run order is in Supplementary Text S2.

## What is not included

The PDFs of the reviewed articles, their text conversions, the retrieved abstracts and the passages read
for validation are copyright of their publishers and are not redistributed (`.gitignore` blocks them).
Every study is identified by DOI, so the corpus can be reassembled by anyone with access, and the per-term
hit counts in `fulltext_extraction.csv` make each extracted value auditable. Scopus metadata are subject to
Elsevier's terms of use.

## Licence

- **Code** (`review/scripts/`, `archive_v1/scripts/`) — MIT, see [`LICENSE`](LICENSE)
- **Data and figures** — CC BY 4.0, see [`LICENSE-data`](LICENSE-data)

## Citation

Please cite the paper. GitHub renders a formatted citation from `CITATION.cff`.

---

**Author:** Azad Rasul, Soran University and Salahaddin University-Erbil — azad.rasul@soran.edu.iq
