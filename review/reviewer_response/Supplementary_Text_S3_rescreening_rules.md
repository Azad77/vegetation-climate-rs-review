# Supplementary Text S3 - Title-and-abstract screening rules (revision)

Screener: Claude Opus 5.5 (Anthropic), blind to the earlier screening; author check of a random sample (Table S2).
Information: title, journal, year and abstract (OpenAlex, Crossref or Semantic Scholar; opening text of the full text where no
abstract was deposited). 217 of 1,482 records had no abstract and were judged on title and metadata.

Pre-screen (deterministic, tier1_sensitivity_rules.py): abstract with no satellite remote sensing term, no vegetation term, or UAV /
airborne data without satellite data -> flagged; all 64 flagged records were confirmed on reading.

Codes
- I   include: satellite remote sensing (primary or co-primary data) of a vegetation variable, with a climate link:
      (a) a climate variable, climate extreme or climate-related disturbance (drought, heat, frost, fire, storms) is analysed, or
      (b) vegetation carbon, biomass, productivity, phenology or greening is monitored explicitly in a climate-change context.
      Reviews of such work are included (Table 1).
- E-R exclude: satellite remote sensing not the primary data source (UAV, airborne, proximal or leaf spectra only).
- E-V exclude: no vegetation variable (soil, water, land surface temperature, urban heat, floods, atmosphere, hazards).
- E-C exclude: no climate dimension (land-cover, crop or species mapping, yield, disease or pest detection, sensor calibration).
- U   uncertain -> excluded.
Language: records in journals publishing predominantly in a language other than English were excluded (74).
Decision files: reviewer_response/screening_v2/v2_dec_*.txt; combined log: screening_v2_log.csv; Table S1.
