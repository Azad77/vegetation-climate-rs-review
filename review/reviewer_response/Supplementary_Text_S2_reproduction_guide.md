# Supplementary Text S2 — Reproducing the analysis

Repository: https://github.com/Azad77/vegetation-climate-rs-review

All scripts use paths relative to their own location and expect the repository layout:

```
data/                        Scopus export and first-version screening records (inputs, bibliographic fields only)
review/
  scripts/                   all analysis scripts (this guide)
  data_v2/                   revised corpus: master_v2.xlsx (811 included studies), PDF links
  pdf_text/                  plain text of the full-text PDFs (NOT redistributed - see note 1)
  fulltext_extraction.csv    per-study extraction table for the 369 full-text studies
  included_studies.csv       the 811 included studies with DOI and evidence tier
  Revised_Results_Tables.xlsx  every result table
  figures/                   Figures 1-9
  reviewer_response/         Supplementary Tables S1-S14, Texts S1-S3 and intermediate files
  archive_v1/                first-version inputs still read by two scripts
archive_v1/                  the first-version compendium (757 studies), superseded
```

## Inputs

| File | Content | Used by |
|---|---|---|
| `data/step1_scopus_raw.csv` | 4,791 Scopus records after export-stage de-duplication | abstracts_v2, screen_v2_finalize, search_screening_eval |
| `data/step2_exclusion_log.csv` | 2,462 title-screening exclusions with reason | search_screening_eval, openalex_fetch |
| `data/step5_master_clean_19_4_2026.xlsx` | first-version included list (757 studies; bibliographic fields only) | screen_v2_finalize |
| `review/reviewer_response/screening_v2/v2_dec_*.txt` | the title-and-abstract decision for each of the 1,482 records (codes I, E-R, E-V, E-C, U; rules in Supplementary Text S3) | screen_v2_finalize |
| `review/pdf_text/*.txt` | text of the full-text PDFs (note 1) | extract, validation_sample, validation_design, study_area, openalex_fetch |
| RESOLVE Ecoregions 2017 shapefile | biome map (note 2) | compute_biome_areas |

## Run order and outputs

| Step | Script | Output | Manuscript |
|---|---|---|---|
| 1 | `abstracts_v2.py` (network) | `screening_v2/records_with_abstracts.csv` (note 3) | Section 2.4 |
| 2 | `screen_v2_prep.py` | screening sheet; decisions in `screening_v2/v2_dec_*.txt` | Section 2.4 |
| 3 | `screen_v2_finalize.py` (`fetch_oa_pdfs_v2.py` retrieved 19 further open-access PDFs) | `data_v2/master_v2.xlsx`, `data_v2/pdf_link_v2.json`, `screening_v2/screening_v2_log.csv` | Section 2.4 |
| 4 | `prisma_v2.py` | Table 3, Figure 1, Table S1 | Sections 2.4, 3.1 |
| 5 | `screening_agreement_S2.py`, `corpus_change_S3.py` | Table S2 (agreement with the first-version screening), Table S3 (record-level corpus change) | Sections 2.4, 3.1 |
| 6 | `extract.py` | `fulltext_extraction.csv` | Sections 3.4-3.11 |
| 7 | `analyse.py` | `Revised_Results_Tables.xlsx`; Figures 2-8 | Sections 3.2-3.11 |
| 8 | `openalex_fetch.py` (network), `search_screening_eval.py` | Tables S4-S6 | Sections 2.9, 3.1 |
| 9 | `validation_sample.py`, then `score_validation.py` | validation passages; Tables S7-S8 | Sections 2.8, 3.4 |
| 10 | `validation_design.py`, `design_outputs.py` | Table S9, Table 14, Figure 9 | Sections 2.6, 3.11 |
| 11 | `compute_biome_areas.py`, `study_area.py`, `geography_biome.py` | Tables S10-S11 | Sections 2.7, 3.3, 3.9 |
| 12 | `forest_subset.py` | Table S13 | Sections 3.9, 4.5 |
| 13 | `index_bias.py` (uses `query_sim.py`; network on first run) | Table S14 | Section 4.3 |
| 14 | `verify_v2.py` (needs the manuscript, note 4) | Table S12 (computational checks) | Data availability |
| 15 | `consistency_scan.py` (needs the manuscript, note 4) | `consistency_flags.csv` | count/percentage consistency |

`corpus.py` holds the
corpus paths, `vocab.py` the controlled vocabularies and `geo.py` the country-to-region lookup.

Steps 9-11 compare automated labels with **reference labels assigned by reading the source text**
(`reviewer_response/validation/reference_labels.json`, `design/design_reference_labels.json`,
`geography/study_area_reference.json`, `geography/biome_reference.json`). These files are inputs, not outputs: they record
the reference labels and can be edited to re-score the validation.

**Two kinds of check.** `verify_v2.py` (Table S12) is a *computational* check: it recomputes every reported number from the
archived data and compares it with the value stated in the manuscript, so it detects arithmetic and transcription errors only.
The *validation* of the extracted data is done by steps 9-11 against the reference labels.

## Environment
Python 3.10 or later with the packages in `requirements.txt`; pdftotext (Poppler 22.x). Random samples use fixed seeds (2026).

## Notes
1. The full texts are copyright of their publishers and are not redistributed. Every full-text study is identified by DOI
   in `fulltext_extraction.csv`; obtain the PDFs and convert them with `pdftotext -layout` into `review/pdf_text/` using the
   file stem in the `pdf_stem` column. The passages read for validation (`validation/kwic_sample.json`,
   `design/design_kwic.txt`) are regenerated from these texts by steps 9 and 10.
2. Download https://storage.googleapis.com/teow2016/Ecoregions2017.zip and run
   `python compute_biome_areas.py Ecoregions2017.shp`.
3. Abstracts are copyright of their publishers. `records_with_abstracts.csv`, the screening sheet and the OpenAlex caches
   are regenerated by steps 1, 2 and 8 and are not redistributed; Table S1 records the abstract source for every record.
4. `verify_v2.py` and `consistency_scan.py` read the manuscript file (`review/Rasul_VegeClimate Review_R1.docx`), which is not
   part of the repository.
5. Scopus metadata are subject to Elsevier's terms of use; the files in `data/` contain bibliographic fields only.
