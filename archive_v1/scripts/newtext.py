# -*- coding: utf-8 -*-
"""Replacement paragraph text keyed by a unique prefix of the existing paragraph."""

ABSTRACT = (
"This study presents a PRISMA 2020-compliant systematic review of satellite remote sensing "
"approaches used to monitor vegetation responses to climate change over the period 2000-2025. "
"A total of 757 peer-reviewed studies were identified, of which 455 (60.1%) were available as "
"retrievable open-access full text and were re-extracted with a deterministic, fully auditable "
"regular-expression pipeline; the remaining 302 records could be characterised only at the "
"bibliographic level and are therefore excluded from the methodological denominators reported "
"here. Publication output grew steeply after 2019, with the period 2021-2025 accounting for 480 "
"studies (63.4% of the corpus). Landsat (51.4% of full-text studies), MODIS (44.6%) and "
"Sentinel-2 (43.5%) dominated the sensor landscape, 29.9% of studies used synthetic aperture "
"radar, and 62.9% combined two or more sensor families. NDVI remained the reference index "
"(76.9%), ahead of EVI (28.1%), while solar-induced fluorescence appeared in only 4.0% of "
"studies. Random Forest (35.8%) and linear regression (29.5%) were the most frequently applied "
"analytical methods; deep learning was used in 11.4% of studies overall, rising from zero before "
"2020 to 18.0% of studies published in 2023-2025. Research output was approximately evenly split "
"between Global North (52.4%) and Global "
"South (47.6%) first-author institutions - but the Global South share is dominated by a single "
"country, with China alone contributing 208 studies (27.5%) and all other Global South countries "
"combined contributing 152 (20.1%). Drylands, shrublands and peatlands remained markedly "
"under-represented relative to their global extent. Reporting of validation statistics was "
"incomplete: R-squared was reported in 40.9% of "
"full-text studies (within-study median 0.71, IQR 0.57-0.82) and RMSE in 26.6%, although "
"heterogeneous units preclude pooling. Only 8.8% of studies provided a public code repository "
"and 7.5% a public data repository, rising to 12.0% and 9.6% respectively for 2023-2025 "
"publications. The review outlines research gaps and recommendations for multi-sensor "
"integration, methodological standardisation, and equitable and reproducible research in "
"vegetation-climate remote sensing."
)

M25_1 = (
"Structured data extraction was performed in two tiers. Tier 1 (all 757 included studies) drew on "
"Scopus bibliographic metadata: authors, publication year, journal, DOI, first-author country, "
"open access status and citation count. Tier 2 (the 455 studies for which an open-access PDF "
"could be retrieved and parsed) drew on the full text of the article and supplied every "
"methodological variable reported in Sections 3.4 to 3.11. Extraction targeted ten domains "
"(Table 4). The two tiers are reported separately throughout because they support different "
"claims: bibliographic records reliably supply publication year, outlet and author affiliation, "
"but abstracts systematically omit sensor lists, algorithm names, validation statistics and "
"data-availability statements, and cannot support a count of them. All denominators in Sections "
"3.4 to 3.11 are therefore the 455-study full-text corpus, and are labelled as such."
)

M25_2 = (
"Performance metrics (R-squared, RMSE, MAE, overall accuracy, F1 score, and Cohen's kappa) were "
"extracted with explicit unit attribution and application-domain context. For spectral indices, a "
"predefined vocabulary ordered longest-first in the matching algorithm - to prevent partial "
"substring matches - was used to standardise index nomenclature across studies. Country "
"affiliation was extracted from Scopus API metadata and mapped to geographic regions using a "
"validated country-to-region lookup table. Global North and Global South were assigned using the "
"UN M49 classification of developed regions (Europe, Northern America, Japan, Australia and New "
"Zealand); because the treatment of the high-income East Asian economies is contested, a "
"sensitivity classification adding the Republic of Korea, Singapore, Israel, Taiwan and Hong Kong "
"to the Global North is reported alongside the primary classification in Section 3.3."
)

M28_HEAD = "2.8 Full-Text Re-Extraction and Validation Protocol"
M28_1 = (
"The methodological variables reported in this review were extracted from the full text of each "
"article using a deterministic pipeline rather than a generative language model, so that every "
"reported count is reproducible and traceable to the source text. Each PDF was converted to plain "
"text (pdftotext, Poppler 22.x); ligatures and hyphenated line breaks were normalised; and the "
"reference list was removed by locating the last section heading matching 'References', "
"'Bibliography' or 'Literature Cited' in the final two-thirds of the document, so that a platform "
"or algorithm named only in a cited title could not be counted as having been used."
)
M28_2 = (
"Controlled vocabularies were compiled for 26 sensor families, 18 spectral vegetation indices, 12 "
"biophysical variables and products, 30 analytical methods, 12 climate variables, 10 application "
"domains and 13 biomes. Each vocabulary entry is a word-boundary-anchored regular expression. A "
"term was recorded as used by a study when it occurred at least twice in the reference-stripped "
"body text; application domains and biomes required at least three and four occurrences "
"respectively, and the highest-scoring label was additionally recorded as the study's primary "
"domain and primary biome. Two disambiguation rules were applied: a bare mention of 'decision "
"tree' in a study that applied Random Forest was not counted as a separate method, because "
"decision trees are the base learner of Random Forest; and where a specific forest type was "
"identified, the generic forest label was suppressed."
)
M28_3 = (
"Performance metrics were captured with numeric-range and unit validation. R-squared, kappa and "
"F1 values were accepted only in the interval 0 to 1; overall accuracy was normalised to a "
"percentage and accepted only in the interval 20 to 100; and RMSE or MAE values that were "
"unit-less integers in the range 1900-2100 were rejected as probable publication years, since an "
"unqualified four-digit integer in that range is far more often a date than an error magnitude. "
"All values reported by a study were retained (1,408 R-squared values across 186 studies), and "
"study-level summaries are reported as within-study medians so that studies reporting many model "
"variants do not dominate the distribution. RMSE and MAE are not pooled across studies because "
"their units are application-specific; a stratified summary is reported for the above-ground "
"biomass sub-corpus, where units are comparable."
)
M28_4 = (
"Open science practice was assessed from the whole document, including statements printed after "
"the reference list. A study was recorded as sharing code or data only where a resolvable "
"repository identifier was present (GitHub, GitLab, Bitbucket, Zenodo, Code Ocean, the Open "
"Science Framework, figshare, Dryad, PANGAEA, Mendeley Data, or a Google Earth Engine script "
"link). Availability statements without a repository link, statements offering material on "
"request, and explicit refusals were recorded as separate categories rather than being collapsed "
"into a binary shared/not-shared flag. This distinction matters: a substantial share of studies "
"carry a data availability statement that refers only to the third-party satellite products used, "
"which is not a form of research-output sharing."
)
M28_5 = (
"The complete extraction table, the controlled vocabularies, the per-study regular-expression hit "
"counts underlying every value, and the scripts that generate every figure and table in this "
"paper are provided as supplementary material."
)

R31 = (
"The systematic search of Scopus retrieved 4,794 records using the defined title-abstract-keyword "
"query combining remote sensing, vegetation, and climate-related terms, restricted to journal "
"articles and reviews published in English between 2000 and 2025. After removal of six duplicate "
"records, 4,788 unique records remained. Language verification confirmed all retained records were "
"in English, and the time-window filter introduced no further exclusions. Document-type filtering "
"removed 844 non-article records (conference papers, book chapters, editorials), yielding 3,944 "
"candidate articles. Title and abstract screening using a keyword filter excluded a further 2,462 "
"records deemed outside the scope of the review, resulting in 1,482 articles assessed for "
"full-text eligibility. Following full-text assessment, 725 records were excluded because no "
"open-access full text could be retrieved or because the retrieved text did not satisfy all eight "
"eligibility criteria. The final corpus comprised 757 peer-reviewed studies published across 208 "
"journals spanning 2000 to 2025; the three most frequent outlets were Remote Sensing (n = 126), "
"Remote Sensing of Environment (n = 61) and the International Journal of Remote Sensing (n = 28). "
"Of these 757 studies, 455 (60.1%) were available as retrievable full text and form the "
"denominator for all methodological results in Sections 3.4 to 3.11; the remaining 302 studies "
"contribute to the bibliometric analyses in Sections 3.2 and 3.3 only. The complete selection "
"process is illustrated in the PRISMA 2020 flow diagram (Figure 1)."
)

R32 = (
"The annual distribution of included studies revealed a pronounced upward trajectory over the "
"25-year review period (Figure 2). Publication output remained low from 2000 to 2011, with no "
"more than 11 studies in any single year, reflecting the limited availability of freely accessible "
"satellite data archives and the relative immaturity of machine learning applications in remote "
"sensing during this period. A first inflection point is discernible around 2012-2015, reflecting "
"a compound enabling effect: the opening of the Landsat archive to free public access in 2008, the "
"launch of Google Earth Engine in 2010 (Gorelick et al., 2017), and the subsequent proliferation "
"of cloud-based geospatial workflows - each of which required several years to translate into "
"published research output at scale. A second and more pronounced acceleration began after 2019 "
"(n = 47), with annual output reaching 62 studies in 2021, 87 in 2022, 74 in 2023, 120 in 2024, "
"and 137 studies in 2025 - the highest annual count in the corpus. The period 2021-2025 accounts "
"for 480 studies (63.4%) of the total corpus. Full-text availability was itself strongly "
"time-dependent: 250 of the 331 studies published in 2023-2025 (76%) were retrievable as "
"open-access full text, against 27 of the 98 published before 2015 (28%), a gradient that "
"reflects the diffusion of open-access publishing and that must be borne in mind when "
"interpreting the time-stratified results below."
)

R33_1 = (
"First-author institutional affiliation was used as a proxy for the geographic origin of research. "
"East Asia produced the largest share of included studies (n = 244, 32.2%), followed by Europe "
"(n = 208, 27.5%) and North America (n = 147, 19.4%). Together, these three regions account for "
"79.1% of the total output, indicating a pronounced concentration of research capacity in a small "
"number of national research systems. South Asia contributed 31 studies (4.1%), the Middle East "
"and North Africa 30 (4.0%), and Latin America 27 (3.6%), while Sub-Saharan Africa (n = 21, 2.8%), "
"Southeast Asia (n = 15, 2.0%) and Oceania (n = 15, 2.0%) were markedly under-represented relative "
"to their land area and the ecological significance of their vegetation systems (Figure 3a). A "
"further 19 studies (2.5%) could not be assigned to a region from the available affiliation "
"metadata."
)

R33_2 = (
"Classification by the Global North/South framework requires care, and the result is sensitive to "
"how the high-income East Asian economies are treated. Applying the UN M49 definition of developed "
"regions - Europe, Northern America, Japan, Australia and New Zealand - 397 studies (52.4%) "
"originated from Global North institutions and 360 (47.6%) from Global South institutions. Adding "
"the Republic of Korea, Singapore, Israel, Taiwan and Hong Kong to the Global North shifts the "
"split to 421 (55.6%) and 336 (44.4%) respectively (Figure 3b). Neither figure supports the "
"conclusion, common in the bibliometric literature, that the field is overwhelmingly a Global "
"North enterprise. The more consequential finding is that the Global South share rests almost "
"entirely on one country: China "
"alone accounts for 208 first-author studies (27.5% of the corpus), so that every other Global "
"South country combined contributes 152 studies (20.1%). Sub-Saharan Africa, Southeast Asia and "
"Latin America together account for 63 studies (8.3%). Among study areas rather than author "
"affiliations, China was again the most frequently investigated country (n = 84), followed by the "
"United States (n = 37), Canada (n = 18), India (n = 16) and Brazil (n = 15). The mismatch between "
"where research is produced and the geographic distribution of climate-sensitive vegetation - "
"particularly tropical forests, savannas and arid-land vegetation - remains a persistent equity "
"gap in the literature."
)

R34 = (
"Twenty-six distinct sensor families were identified in the full-text corpus after normalisation, "
"reflecting the breadth of remote sensing instruments deployed. The most frequently employed "
"platforms are summarised in Table 5 and Figure 4. Landsat was the most widely used sensor family "
"(n = 234, 51.4% of full-text studies), a position it owes to a free and radiometrically "
"consistent archive extending to 1972 and to 30 m imagery suitable for both land-cover change and "
"biomass work. MODIS ranked second (n = 203, 44.6%), attributable to its continuous daily global "
"coverage since 2000 and its suite of pre-processed vegetation products (MOD13, MOD15, MOD17), and "
"Sentinel-2 third (n = 198, 43.5%), reflecting its 10 m spatial resolution and free data access "
"policy. The near-parity of these three families is itself a finding: a decade ago MODIS would "
"have dominated the field outright, and Sentinel-2 has closed most of that gap within ten years of "
"launch. Radar has a substantial presence across the corpus. Taking the union "
"of Sentinel-1 (n = 90, 19.8%), generic or unattributed SAR (n = 119, 26.2%), ALOS PALSAR (n = 46, "
"10.1%), RADARSAT (n = 6) and TerraSAR-X or TanDEM-X (n = 10), 136 studies (29.9%) used synthetic "
"aperture radar data. LiDAR - airborne, terrestrial or spaceborne - appeared in 81 studies (17.8%) "
"and the spaceborne systems GEDI and ICESat-2 in 26 (5.7%) and 14 (3.1%) respectively, "
"predominantly for canopy structure and biomass. AVHRR and the derived GIMMS record (n = 62, "
"13.6%) remained relevant for long-term greening and browning analyses requiring observations "
"before 2000. Spaceborne hyperspectral instruments (Hyperion, EnMAP, PRISMA, DESIS; n = 23, 5.1%) "
"and the SIF-capable atmospheric sensors (OCO-2/3, GOSAT, GOME-2, TROPOMI; n = 8, 1.8%) remained "
"niche. Multi-sensor working is now the norm rather than the exception: 286 studies (62.9%) used "
"or directly compared two or more sensor families."
)

R35_1 = (
"Analytical approaches spanned a continuum from classical statistical methods to contemporary deep "
"learning architectures. The frequency of machine learning and statistical methods across the "
"full-text corpus is presented in Table 6 and Figure 6."
)

R35_2 = (
"Random Forest was the most commonly applied method (n = 163, 35.8% of full-text studies), "
"consistent with its established robustness for high-dimensional remote sensing classification and "
"regression tasks, its resistance to overfitting, and its ability to rank feature importance - a "
"property particularly valued in vegetation-climate studies seeking to identify dominant drivers. "
"Regression-based approaches (linear, multiple linear, and ordinary least squares variants) were "
"the second most frequent category (n = 134, 29.5%), reflecting their interpretability and "
"continued utility in establishing quantitative relationships between spectral predictors and "
"biophysical variables. Support Vector Machines and Support Vector Regression appeared in 71 "
"studies (15.6%), gradient boosting methods including XGBoost and LightGBM in 35 (7.7%), shallow "
"artificial neural networks and multilayer perceptrons in 33 (7.3%), and Partial Least Squares "
"regression in 17 (3.7%), the latter concentrated in hyperspectral and chemometric applications. "
"Non-parametric trend statistics remained a substantial presence: the Mann-Kendall test and "
"Theil-Sen slope estimator were used in 48 studies (10.5%) and time-series break detection "
"algorithms (BFAST, LandTrendr, CCDC) in 16 (3.5%). Google Earth Engine was used as the analytical "
"platform in 125 studies (27.5%), although it is computing infrastructure rather than an "
"analytical method."
)

R35_3 = (
"Deep learning was applied in 52 studies (11.4% of the full-text corpus). Convolutional "
"architectures - including ResNet, VGG and DeepLab variants - were the most common (n = 24, 5.3%), "
"followed by U-Net segmentation models (n = 10, 2.2%) and recurrent architectures, principally "
"LSTM and GRU networks (n = 10, 2.2%). Transformer and attention-based models appeared in four "
"studies (0.9%), and generative adversarial and autoencoder architectures in one each. A further "
"45 studies (9.9%) referred to deep learning generically without naming an architecture. The "
"temporal pattern is the substantive finding: no study published before 2020 in the full-text "
"corpus applied a deep learning architecture, 7 of 128 studies (5.5%) published in 2020-2022 did "
"so, and 45 of 250 studies (18.0%) published in 2023-2025 did so (Figure 6b). Explainable AI "
"methods, principally SHAP, appeared in 10 studies (2.2%), all published from 2022 onwards. Taken "
"together, 208 studies (45.7%) applied at least one machine learning method; the remaining 54.3% "
"relied on statistical, trend-analysis or physically based approaches."
)

R35_NOTE = (
"Note: percentages are calculated relative to the 455-study full-text corpus. Counts sum to more "
"than 455 because individual studies frequently applied several methods; a method was recorded "
"where its name occurred at least twice in the reference-stripped body text."
)

R36 = (
"At least one spectral vegetation index was identified in 386 studies (84.8% of the full-text "
"corpus). The Normalised Difference Vegetation Index dominated the literature (n = 350, 76.9%), "
"reflecting its long-standing status as the standard proxy for vegetation greenness, photosynthetic "
"activity and canopy density (Table 7, Figure 5a). The Enhanced Vegetation Index ranked second "
"(n = 128, 28.1%), preferred in studies requiring reduced atmospheric sensitivity and improved "
"performance in high-biomass tropical environments, with its two-band variant EVI2 in a further 21 "
"studies (4.6%). Soil-adjusted indices (SAVI, MSAVI, OSAVI) appeared in 67 studies (14.7%), "
"predominantly in sparsely vegetated systems where soil background dominates the mixed pixel. "
"Water- and moisture-sensitive indices were widely used - NDWI in 56 studies (12.3%) and "
"NDMI/LSWI in 31 (6.8%) - as were the burn indices NBR and dNBR (n = 29, 6.4%). The kernel NDVI "
"(kNDVI, n = 5) and the near-infrared reflectance of vegetation (NIRv, n = 6), both introduced "
"since 2019 to address NDVI saturation, remain marginal. Drought-focused indices - the Vegetation "
"Condition Index (n = 12, 2.6%), Vegetation Health Index (n = 8) and Temperature Condition Index "
"(n = 9) - collectively appeared in 14 distinct studies, forming a small but coherent "
"methodological cluster."
)

R36B = (
"Biophysical variables and higher-level products were used alongside the reflectance indices "
"(Table 8, Figure 5b). Above-ground biomass was the most frequent target variable (n = 99, 21.8%), "
"followed by leaf area index (n = 85, 18.7%), evapotranspiration (n = 84, 18.5%) and soil moisture "
"(n = 75, 16.5%). Gross primary productivity appeared in 39 studies (8.6%) and net primary "
"productivity in 21 (4.6%). Solar-induced chlorophyll fluorescence was used in 18 studies (4.0%), "
"all published from 2021 onwards, tracking the availability of GOME-2, GOSAT, OCO-2 "
"and TROPOMI products. Its scarcity relative to NDVI is notable given that SIF is coupled directly "
"to photosynthetic electron transport rather than to canopy structure."
)

R37 = (
"Climate variables were identified in 361 of the 455 full-text studies (79.3%). Temperature was "
"the most frequently invoked climate driver (n = 283, 62.2%), encompassing air and surface "
"temperature, warming trends and heat stress. Precipitation, including rainfall and snowfall, "
"ranked second (n = 279, 61.3%). Drought was addressed in 147 studies (32.3%), although formal "
"drought indices - SPI, SPEI, PDSI or their variants - were used in only 25 (5.5%), indicating that "
"most drought-related work relies on unstandardised moisture proxies. Soil moisture appeared in 73 "
"studies (16.0%), solar radiation or photosynthetically active radiation in 48 (10.5%), snow cover "
"in 25 (5.5%) and permafrost in 27 (5.9%). Two variables of increasing importance in the "
"vegetation-climate literature remained scarce: compound extreme events and heatwaves were "
"addressed in 31 studies (6.8%), and vapour pressure deficit - now recognised as a primary control "
"on stomatal conductance and productivity under warming - in only 11 (2.4%). Atmospheric CO2, "
"including CO2 fertilisation effects, was addressed in 19 studies (4.2%)."
)

R38 = (
"Application domains were assigned as multi-label attributes, since most studies address more than "
"one, and additionally as a single primary domain given by the highest-scoring label (Table 9). "
"Phenology was the most common domain (n = 148, 32.5% of full-text studies; primary domain for "
"111, 24.4%), reflecting the sensitivity of plant phenological cycles to inter-annual climate "
"variability and the maturity of long NDVI and EVI time series. Biomass and carbon stock "
"estimation followed (n = 109, 24.0%; primary for 94, 20.7%), then greening and browning trend "
"analysis (n = 103, 22.6%) and land cover or land use change (n = 101, 22.2%). Carbon and water "
"flux studies, including gross and net primary productivity and evapotranspiration, appeared in 87 "
"studies (19.1%). Drought stress and vegetation response (n = 47, 10.3%) and wildfire and "
"post-fire recovery (n = 47, 10.3%) formed smaller but coherent sub-corpora, as did land "
"degradation and restoration (n = 38, 8.4%) and crop yield (n = 32, 7.0%). Species distribution "
"and habitat suitability modelling was rare (n = 7, 1.5%), confirming a persistent gap at the "
"interface of remote sensing and biogeography. Fifty-four studies (11.9%) could not be assigned a "
"primary domain because no domain vocabulary reached the required threshold."
)

R39 = (
"A primary biome was assignable for 426 of the 455 full-text studies (93.6%); Table 10 reports "
"both the primary assignment and the multi-label counts, and Figure 7 cross-tabulates biome "
"against application domain as an evidence map. Forests were by a wide margin the most studied "
"ecosystem: 206 studies (45.3%) had a forest biome as their primary setting, of which 172 did not "
"specify a forest type, 19 were tropical, 10 temperate and 5 boreal. Croplands were the primary "
"setting for 52 studies (11.4%), non-peat wetlands including mangroves and salt marshes for 45 "
"(9.9%), and grasslands and steppe for 43 (9.5%). Tundra and alpine systems (n = 24, 5.3%) were "
"well represented relative to their share of the global land surface, reflecting sustained "
"attention to Arctic and high-elevation warming. By contrast, dryland and desert systems were the "
"primary setting for 26 studies (5.7%) and appeared at all in 78 (17.1%) despite covering "
"approximately 40% of the ice-free land surface; savanna was primary for 11 (2.4%); shrubland for "
"8 (1.8%); and peatland for 6 (1.3%), appearing at all in 12 (2.6%). Urban vegetation was the "
"primary setting for 5 studies (1.1%). The evidence map in Figure 7 shows that the sparsity is "
"structural rather than incidental: peatland-by-biomass, savanna-by-crop-yield and "
"shrubland-by-species-distribution cells are empty or near-empty, whereas forest-by-phenology and "
"forest-by-biomass each contain 78 studies."
)

R310 = (
"Open science practice was assessed from the full text of each study, distinguishing a resolvable "
"repository link from a bare availability statement (Table 11, Figure 8). Of the 455 full-text "
"studies, 40 (8.8%) provided a public repository for analysis code and 34 (7.5%) a public "
"repository for study data. A further 94 studies (20.7%) offered code and 97 (21.3%) offered data "
"on request to the corresponding author, and 173 studies (38.0%) carried a data availability "
"statement with no repository identifier - in the large majority of cases a statement referring to "
"the third-party satellite products used rather than to any research output generated by the "
"authors. No statement of any kind was found in 314 studies (69.0%) for code and 151 (33.2%) for "
"data; five studies (1.1%) stated explicitly that code could not be released. The trajectory is "
"nevertheless clearly positive: the code repository rate rose from 0% for studies published "
"before 2015 to 2.0% in 2015-2019, 7.0% in 2020-2022 and 12.0% in 2023-2025, and the "
"corresponding data repository rate from 3.7% to 4.0%, 5.5% and 9.6% (Figure 8b). Even at the most recent rate, roughly seven in eight "
"studies published in the field do not release the code that produced their results."
)

R311 = (
"Reporting of quantitative validation statistics was incomplete (Table 12, Figure 9). The "
"coefficient of determination was reported in 186 of the 455 full-text studies (40.9%), which "
"together reported 1,408 individual R-squared values; summarised as within-study medians, the "
"distribution had a median of 0.71 (IQR 0.57-0.82), and the median of the best value reported per "
"study was 0.85. Stratified by primary application domain, median within-study R-squared was "
"highest for crop yield (0.88, n = 4) and land cover change (0.79, n = 8), intermediate for "
"phenology (0.76, n = 39), carbon and water flux (0.72, n = 17) and biomass (0.71, n = 68), and "
"lowest for drought stress (0.57, n = 9) - a gradient consistent with the difficulty of predicting "
"a stress response relative to mapping a structural state. Root mean square error was reported in "
"121 studies (26.6%), but in units that are application-specific and cannot be pooled; restricted "
"to the above-ground biomass sub-corpus, where units are comparable, 34 studies reported 193 RMSE "
"values with a median of 27.2 Mg ha-1 (IQR 14.5-45.5). Overall classification accuracy was "
"reported in 68 studies (14.9%), with a median of 88.0% (IQR 78.0-92.8), and Cohen's kappa in 27 "
"(5.9%, median 0.82). Mean absolute error (n = 27, 5.9%) and F1 score (n = 12, 2.6%) were rare. "
"Because error metrics are frequently reported without units, and because a bare four-digit "
"integer is as often a date as a magnitude, all extracted values were subjected to the range and "
"unit validation described in Section 2.8 before being summarised."
)

# ------------------------------------------------------------------ Discussion
D40 = (
"This review synthesised 757 peer-reviewed studies published between 2000 and 2025, of which 455 "
"were re-extracted from full text, to provide a comprehensive evidence base for satellite remote "
"sensing of vegetation responses to climate change. The findings reported in Sections 3.1 through "
"3.11 reveal a field that has grown rapidly in output, become substantially more analytically "
"sophisticated, and yet remains constrained by an uneven geography of research capacity, "
"incomplete performance reporting, and limited sharing of code and data. The discussion that "
"follows interprets the principal findings across five thematic dimensions: publication growth and "
"its structural drivers; the sensor and spectral index landscape; the machine learning and deep "
"learning transition; thematic and biome coverage patterns; and the open science deficit - before "
"identifying the most critical knowledge gaps and priority research directions that emerge from "
"the evidence."
)

D41_1 = (
"The annual publication trajectory documented in Section 3.2 reveals two distinct phases of "
"acceleration. The period from 2000 to approximately 2011 yielded no more than 11 studies per "
"year, consistent with the operational constraints of that era: satellite data archives were "
"costly or restricted in access, cloud computing infrastructure for large geospatial datasets did "
"not exist at scale, and machine learning methods had not yet been widely adopted in remote "
"sensing contexts. A first inflection point around 2012-2015 coincided with the opening of the "
"Landsat archive in 2008, which made decades of multispectral data freely and programmatically "
"accessible for the first time. The most pronounced acceleration began after 2019, culminating in "
"137 studies in 2025 alone - the highest annual count in the corpus. The period 2021-2025 alone "
"accounts for 480 studies, representing 63.4% of all included publications."
)

D41_2 = (
"This surge is temporally coherent with three independently documented developments. First, the "
"Sentinel-2 constellation, which achieved its full 5-day global revisit capacity from 2017 "
"onwards, provided 10-metre multispectral imagery at no cost, enabling vegetation monitoring at "
"spatial scales that had previously required expensive commercial data. Second, Google Earth "
"Engine - used as the analytical platform in 125 of the 455 full-text studies (27.5%) - lowered "
"the computational barrier to processing planetary-scale time series, allowing researchers without "
"dedicated high-performance computing infrastructure to conduct analyses that would previously "
"have required institutional supercomputing resources. Third, the maturation of deep learning "
"architectures provided new analytical tools for exploiting the temporal and spatial richness of "
"these expanded data archives. The quantitative record of publication growth documented here thus "
"reflects not simply increased scientific interest, but the convergence of three enabling "
"technologies that together democratised large-scale vegetation remote sensing."
)

D41_3 = (
"The rapid growth trajectory also introduces structural concerns. As Section 3.11 documents, 186 "
"full-text studies (40.9%) reported the coefficient of determination and 121 (26.6%) reported root "
"mean square error, leaving a majority of the corpus without either. The concentration of "
"publications in the most recent five years, combined with incomplete and non-standardised "
"performance reporting, suggests that the field is expanding faster than its quality assurance "
"mechanisms are consolidating. Journals, reviewers and authors face a shared challenge: ensuring "
"that the increase in output does not outpace the development of methodological standards capable "
"of benchmarking that output reliably."
)

D42_1 = (
"The geographic analysis presented in Section 3.3 reveals a pronounced concentration of research "
"output in three regions: East Asia (32.2% of studies, n = 244), Europe (27.5%, n = 208) and North "
"America (19.4%, n = 147), which together account for 79.1% of total output. The Global "
"North/South reading of that concentration requires more care than it is usually given, because "
"the result is sensitive to how the high-income and rapidly industrialised East Asian economies "
"are classified. Under the UN M49 definition of developed regions, 52.4% of studies originated "
"from Global North institutions and 47.6% from the Global South; adding the high-income East "
"Asian economies to the Global North moves the split only to 55.6% against 44.4%. Neither figure "
"supports the characterisation, common in the bibliometric literature, of this field as an "
"overwhelmingly Global North enterprise. The more consequential finding is that the Global South "
"share rests almost entirely on one country. China alone accounts for 208 first-author studies "
"(27.5% of the corpus), so that the apparent parity between North and South rests on a single "
"national research system. Excluding China, the entire Global South contributes 152 studies "
"(20.1%), and Sub-Saharan Africa, Southeast Asia and Latin America together contribute 63 (8.3%). "
"The correct characterisation of this field is therefore not North-over-South but a tri-polar "
"concentration in China, Europe and North America, with most of the rest of the world "
"contributing marginally."
)

D42_2 = (
"The mismatch between where research is conducted and where the world's most ecologically "
"significant and climate-sensitive vegetation systems are located is stark. Sub-Saharan Africa "
"contributed only 21 studies (2.8%) despite containing the Congo Basin, the world's second largest "
"tropical forest and a carbon sink of global significance; the studies that do exist from this "
"region demonstrate both the feasibility and the scientific value of remote sensing approaches "
"applied under these conditions (e.g., Bojer et al., 2025; Ikuemonisan et al., 2025; Bihon et al., "
"2025). Southeast Asia contributed 15 studies (2.0%), despite hosting some of the highest rates of "
"deforestation and some of the most biodiverse forest ecosystems on Earth (e.g., Laosuwan et al., "
"2025; Vetrita et al., 2025; Zhou et al., 2025). Latin America contributed 27 studies (3.6%), with "
"Brazil accounting for the majority of these despite the Amazon's outsized role in the global "
"carbon and water cycles (e.g., Souza et al., 2025; Romero-Sanchez et al., 2025). Peatlands, which "
"are the primary setting of only six studies in the corpus (e.g., Habib et al., 2024; Zhou et al., "
"2023), are almost entirely absent despite constituting a disproportionate fraction of terrestrial "
"carbon stocks and being acutely vulnerable to drainage and fire."
)

D43_1 = (
"Section 3.4 documents 26 distinct sensor families across the full-text corpus, reflecting genuine "
"methodological pluralism, but the distribution is highly concentrated: Landsat was used in 51.4% "
"of full-text studies (n = 234), MODIS in 44.6% (n = 203) and Sentinel-2 in 43.5% (n = 198). "
"Synthetic aperture radar, taken as the union of Sentinel-1, ALOS PALSAR, RADARSAT, TerraSAR-X and "
"unattributed SAR, appeared in 136 studies (29.9%) - a substantial radar presence, one that reflects the value of all-weather "
"observation for biomass and structure in cloud-affected regions. LiDAR was employed in 81 studies "
"(17.8%), principally for canopy structure and biomass, with GEDI (n = 26) and ICESat-2 (n = 14) "
"establishing spaceborne LiDAR as a routine component of biomass workflows. Perhaps the clearest "
"single indicator of methodological maturation is that 286 studies (62.9%) used or directly "
"compared two or more sensor families: multi-sensor working is now the default."
)

D43_2 = (
"The temporal progression of sensor use reflects broader developments in data availability. MODIS "
"retains its position across the full 25-year period through its uninterrupted daily global "
"coverage since 2000 and the maturity of its pre-processed vegetation products (MOD13, MOD15, "
"MOD17), which dramatically reduce the preprocessing burden for research groups. The rise of "
"Sentinel-2 from 2017 onwards - to within five percentage points of MODIS across the full corpus, "
"despite fifteen fewer years of archive - signals a platform transition that is likely to become "
"more pronounced as that archive deepens. AVHRR and the GIMMS record (n = 62, 13.6%) maintain "
"relevance specifically for long-term trend studies requiring data extending before 2000, a "
"functionality that no currently operational sensor can replace."
)

D43_3 = (
"The spectral index landscape is equally concentrated. NDVI dominated at 76.9% of full-text "
"studies (n = 350), a proportion that reflects both its scientific utility and its status as the "
"de facto standard for vegetation monitoring since Tucker (1979). EVI ranked second (28.1%, "
"n = 128), preferred in high-biomass tropical environments where NDVI saturates, and soil-adjusted "
"indices third (14.7%, n = 67). Leaf area index appeared in 85 studies (18.7%), serving as the "
"primary link between spectral observations and process-based carbon and water flux models. The "
"scarcity of solar-induced fluorescence (n = 18, 4.0%, all published from 2021 onwards) is "
"particularly significant: unlike structural indices such as NDVI and EVI, SIF is directly coupled "
"to photosynthetic electron transport and provides a more mechanistically grounded measure of "
"actual carbon assimilation. Representative applications include SIF-based phenology monitoring "
"(Marsh et al., 2025; Dutra et al., 2025; Meng et al., 2021), carbon flux estimation (Wenyu et "
"al., 2025; Morais Filho et al., 2021), and drought stress detection (Wang et al., 2025; Zhang et "
"al., 2024). Its uptake, enabled by GOME-2, GOSAT, OCO-2 and TROPOMI products, represents the most "
"important spectral innovation of the recent period and warrants substantially greater systematic "
"synthesis than it has yet received. The same holds for the saturation-resistant kernel indices "
"kNDVI (n = 5) and NIRv (n = 6), which despite strong theoretical justification remain almost "
"unused."
)

D44_1 = (
"The analytical method distribution documented in Section 3.5 reveals a field in methodological "
"transition. Random Forest was the most commonly applied method (35.8%, n = 163), consistent with "
"its established robustness for high-dimensional classification and regression tasks, its "
"resistance to overfitting, and its intrinsic feature importance estimation capability. Linear "
"regression methods ranked second (29.5%, n = 134), reflecting their continued interpretability "
"and utility for quantifying relationships between spectral indices and biophysical variables at "
"scales where the linearity assumption holds. Almost half the corpus (208 studies, 45.7%) applied "
"at least one machine learning method, while the remainder relied on statistical, trend-analysis "
"or physically based approaches - a reminder that the field's centre of gravity remains "
"observational and diagnostic rather than predictive."
)

D44_2 = (
"Deep learning was applied in 52 studies (11.4%), and the temporal pattern rather than the "
"aggregate share is what matters. No study published before 2020 in the full-text corpus used a "
"deep learning architecture; 5.5% of 2020-2022 studies did; and 18.0% of 2023-2025 studies did. "
"Convolutional networks and U-Net segmentation models dominate this subset (n = 24 and n = 10), "
"applied principally to land-cover mapping and structure retrieval (e.g., Hanan et al., 2025; "
"D'Amico et al., 2025; Abdelbaki et al., 2025), while recurrent LSTM and GRU networks (n = 10) are "
"deployed for temporal modelling of vegetation time series, exploiting their capacity to capture "
"the lagged dependencies that link antecedent climate conditions to vegetation response (e.g., Sun "
"et al., 2025; Jeong et al., 2022). Transformer and attention-based architectures, which have "
"reshaped adjacent fields, appeared in only four studies (0.9%), indicating that the frontier "
"documented by Reichstein et al. (2019) is being reached with a lag of several years. The "
"appearance of explainable AI methods in 10 studies (2.2%), all from 2022 onwards, suggests the "
"field is beginning to address the interpretability cost that accompanies architectural "
"complexity."
)

D44_3 = (
"The broader methodological literature - synthesised in the introduction of this review - "
"anticipated exactly this evolution. Reichstein et al. (2019) argued in Nature that deep learning "
"architectures, particularly those capable of exploiting spatial and temporal context "
"simultaneously, offered transformative potential for Earth system science. The corpus analysed "
"here provides empirical confirmation of that trajectory while also bounding it: deep learning is "
"now trackable and growing quickly, but remains a minority approach. The continued dominance of "
"Random Forest and linear regression reflects the reality that not all research questions require "
"deep learning's complexity, and that simpler methods often offer superior interpretability at "
"acceptable cost to predictive accuracy."
)

D44_4 = (
"A persistent methodological limitation documented across the corpus is the incompleteness and "
"heterogeneity of performance metric reporting. Within-study median R-squared across the 186 "
"studies reporting it was 0.71 (IQR 0.57-0.82), indicating moderate to good predictive performance "
"on average, with a clear gradient by application domain from crop yield (0.88) and land cover "
"change (0.79) down to drought stress (0.57). RMSE was reported by 121 studies but in units so "
"heterogeneous that pooling is meaningless; only within the above-ground biomass sub-corpus, where "
"34 studies report in Mg ha-1, is a pooled summary defensible (median 27.2 Mg ha-1, IQR "
"14.5-45.5). This experience is itself the argument for standardisation: the field lacks the "
"reporting conventions established in neighbouring disciplines such as computational biology and "
"clinical prediction modelling, and their development represents a priority task for the remote "
"sensing community. A minimal convention - report R-squared or accuracy with the validation "
"design, report error metrics with explicit units and the range of the target variable, and state "
"the spatial structure of the train/test split - would make the great majority of this literature "
"comparable."
)

D45_1 = (
"Phenology was the most common application domain in the corpus (32.5%, n = 148; primary domain "
"for 111 studies), reflecting the sensitivity of plant phenological cycles to inter-annual climate "
"variability and the maturity of NDVI and EVI time series for detecting seasonal transitions. "
"Biomass and carbon stock estimation (24.0%, n = 109), greening and browning trends (22.6%, "
"n = 103) and land cover change (22.2%, n = 101) followed. Carbon and water flux studies appeared "
"in 87 studies (19.1%). Drought stress (10.3%, n = 47) and wildfire and post-fire recovery (10.3%, "
"n = 47) formed coherent but comparatively small sub-corpora - the latter notably small given the "
"escalating global significance of fire as a vegetation disturbance agent - and species "
"distribution modelling was almost absent (1.5%, n = 7)."
)

D45_2 = (
"The biome distribution documented in Section 3.9 reveals systematic under-representation of "
"several ecosystem types. Forests were the primary setting of 45.3% of full-text studies (n = 206), "
"consistent with their prominence in global carbon accounting and the availability of "
"forest-specific remote sensing products; notably, 172 of these did not specify a forest type at "
"all, which is itself a reporting deficiency that limits the transferability of results. Tundra "
"and alpine systems were well represented (5.3%, n = 24) relative to their global land area, "
"reflecting heightened scientific attention to Arctic warming and the potential tipping-point "
"dynamics associated with permafrost degradation. By contrast, dryland and desert ecosystems "
"(5.7% primary, n = 26), savanna (2.4%, n = 11), shrubland (1.8%, n = 8) and peatland (1.3%, "
"n = 6) were all severely under-represented relative to their global extent and ecological "
"importance."
)

D45_3 = (
"The under-representation of drylands is particularly consequential. Drylands cover approximately "
"40% of the global land surface, and the vegetation dynamics of dryland ecosystems - dominated by "
"the interplay of precipitation variability, vapour pressure deficit and soil moisture - differ "
"fundamentally from those of humid forest systems. That only 11 studies in the entire full-text "
"corpus addressed vapour pressure deficit at all underlines the point. The methodological arsenal "
"developed for humid forest monitoring translates imperfectly to these environments, where "
"vegetation cover is sparse and spectrally mixed, NDVI saturates at the low end rather than the "
"high end, and phenological cycles are driven by episodic rainfall rather than photoperiod. The "
"studies that have addressed dryland systems demonstrate the feasibility of satellite-based "
"monitoring in these challenging environments, including phenological tracking in desert biomes "
"(e.g., Dutra et al., 2025; Qader et al., 2022), above-ground biomass estimation in arid "
"shrublands (Hernandez-Martinez et al., 2025), and greening/browning trend analysis across arid "
"regions (Tang et al., 2025; Chen et al., 2025). The development of dryland-specific remote "
"sensing methods, validated against the growing network of eddy covariance flux towers in these "
"environments, represents a research priority of high ecological and carbon accounting "
"significance."
)

D45_4 = (
"Peatland under-representation is similarly acute. Peatlands store on the order of 500-600 Pg of "
"carbon in organic soils accumulated over millennia - a stock that dwarfs the carbon in "
"above-ground forest biomass. Their vulnerability to drainage, fire and the permafrost degradation "
"associated with Arctic warming makes them a critical system for long-term carbon cycle "
"monitoring. Yet peatland was the primary setting of only six studies in the 455-study full-text "
"corpus, and was mentioned substantively in only twelve. Habib et al. (2024) quantified peatland "
"land use and CO2 emissions in Irish raised bogs using satellite remote sensing, and Zhou et al. "
"(2023) examined the long-term effects of rewetting and drought on gross primary productivity in a "
"temperate peatland. Wetlands more broadly (9.9% primary, n = 45) were better represented, largely "
"through studies of mangroves and salt marshes, but the peat-forming wetlands that constitute the "
"largest terrestrial carbon store remain essentially absent. Figure 7 makes the structure of this "
"gap explicit: the peatland row of the evidence map contains no biomass studies at all."
)

D46_1 = (
"The open science audit documented in Section 3.10 reveals a field in which reproducibility "
"remains substantially constrained, although the picture is more nuanced than a binary "
"shared/not-shared audit conveys. Of the 455 full-text studies, 40 (8.8%) provided a resolvable "
"public repository for analysis code and 34 (7.5%) for study data. A further 94 studies (20.7%) "
"offered code and 97 (21.3%) offered data on request to the corresponding author - a category that "
"the evidence from other fields suggests converts to actual availability in a minority of cases - "
"and 173 (38.0%) carried a data availability statement that pointed only to the third-party "
"satellite products used, which is not a form of research-output sharing. Studies that did deposit "
"both code and data provide replicable templates for the broader community; these are catalogued "
"in Table A2."
)

D46_2 = (
"These rates are low by the standards of neighbouring disciplines that have invested more "
"systematically in reproducibility infrastructure. The consequences are concrete: when methods "
"cannot be inspected, replicated, or applied to new study regions, the cumulative scientific value "
"of individual studies is substantially reduced. Systematic reviews such as the present one must "
"rely on reported results rather than re-analysed data, making it impossible to normalise "
"performance metrics, harmonise variable definitions, or verify the robustness of reported "
"findings - a constraint this review encountered directly in Section 3.11, where heterogeneous "
"RMSE units prevented pooling across all but one application domain. The adoption of platforms "
"such as GitHub, Zenodo and the Open Science Framework for code and data deposition would "
"substantially enhance the scientific return on the investment represented by each published "
"study."
)

D46_3 = (
"The temporal trajectory of open science adoption is clearly positive and can now be quantified "
"directly: the code repository rate rose from 0% before 2015 through 2.0% in 2015-2019 and 7.0% "
"in 2020-2022 to 12.0% in 2023-2025, and the data repository rate from 3.7% through 4.0% and 5.5% "
"to 9.6% over the same periods. Mandatory data availability statements are increasingly required by "
"high-impact journals, and the culture of pre-registration and open materials is diffusing from "
"experimental psychology and ecology into the remote sensing community. The rate of improvement, "
"however, is slow relative to the growth in publication volume: at the 2023-2025 rate, roughly "
"seven of every eight papers published in this field still do not release the code that produced "
"their results."
)

D47_EXTRA = (
"Extraction fidelity. The methodological results in this review rest on regular-expression "
"matching over machine-extracted PDF text, and three limitations of that approach should be "
"stated. First, the requirement that a term occur at least twice in the reference-stripped body "
"text is a compromise: it suppresses passing mentions in an introduction but will miss a sensor or "
"algorithm named only once in a methods section, so the counts reported here are conservative "
"lower bounds. Second, mention is not the same as use - a study that benchmarks Random Forest "
"against its own method is counted as using Random Forest - so the method counts describe the "
"analytical vocabulary of the corpus rather than a census of final models. Third, text extraction "
"from two-column and scanned PDFs is imperfect, and formulae, figure panels and table bodies are "
"unreliably recovered, which particularly affects performance metrics reported only inside tables; "
"the reporting rates in Section 3.11 are therefore also lower bounds. The complete per-study hit "
"counts are supplied as supplementary material so that any individual value can be audited against "
"its source."
)

D47_COVERAGE = (
"Database coverage and full-text availability. This review searched a single bibliographic "
"database (Scopus). Web of Science, PubMed, CAB Abstracts, and grey literature sources - including "
"technical reports, pre-prints and institutional repositories - were not systematically searched. "
"Single-database searches are known to introduce selection bias, as coverage varies substantially "
"across disciplines, journals and publication types (Bramer et al., 2017). Scopus provides broad "
"coverage of peer-reviewed remote sensing literature, and the final corpus of 757 studies "
"represents a substantial evidence base; however, it is likely that a proportion of relevant "
"studies indexed exclusively in Web of Science or published as grey literature were not captured. "
"A second and equally material constraint is that only 455 of the 757 included studies (60.1%) "
"were available as retrievable open-access full text. Because open-access availability is "
"correlated with publication year, journal and funder, the full-text corpus is not a random sample "
"of the included corpus: it over-represents recent, well-funded and European or North American "
"work. The methodological results in Sections 3.4 to 3.11 should therefore be read as describing "
"the open-access segment of the literature, which is the segment a reader can actually obtain and "
"reuse, rather than as unbiased estimates for the field as a whole."
)

D48_0 = (
"The evidence base assembled across 757 studies, of which 455 were re-extracted from full text, "
"and the systematic analysis of their geographic distribution, sensor use, analytical methods, "
"application domains and biome coverage converges on five priority research directions."
)

D48_1 = (
"First, the geographic concentration of research capacity demands targeted investment in "
"under-represented regions, particularly Sub-Saharan Africa, Southeast Asia and tropical Latin "
"America, which together account for 8.3% of the corpus. That the North/South split is close to "
"even does not weaken this conclusion but sharpens it, because the Global South share is almost "
"entirely one country. The barrier is no "
"longer data access, since Sentinel-2, Landsat and MODIS are globally and freely available, but "
"the institutional capacity to process and interpret those data in the context of local ecological "
"knowledge. International collaboration programmes that pair external analytical capacity with "
"local ecological expertise offer a partial solution, but must be structured to build sustainable "
"local capacity rather than extracting intellectual value for external publication."
)

D48_2 = (
"Second, the systematic under-representation of drylands, peatlands, savannas and shrublands - "
"together the primary setting of just 11.2% of full-text studies despite covering a far larger "
"share of the vegetated land surface - requires deliberate community effort to develop and "
"validate remote sensing methods appropriate for these ecosystems. This includes the development "
"of dryland-specific spectral indices that perform robustly at low vegetation cover fractions, the "
"extension of phenological monitoring frameworks to episodically vegetated systems driven by "
"rainfall rather than photoperiod, and the integration of radar and thermal infrared observations "
"to penetrate the cloud cover that limits optical monitoring of tropical peatland systems."
)

D48_3 = (
"Third, the incompleteness and heterogeneity of performance metric reporting - 40.9% of full-text "
"studies reporting R-squared, 26.6% reporting RMSE, and RMSE units so varied that pooling is "
"possible only within a single application domain - constitutes a barrier to cumulative scientific "
"progress that requires a community-level response. The adoption of standardised reporting "
"guidelines, analogous to the EQUATOR network's TRIPOD statement for clinical prediction models, "
"would enable meaningful cross-study benchmarking and facilitate the meta-analytic synthesis that "
"the volume of published studies now warrants."
)

D48_4 = (
"Fourth, the under-utilisation of solar-induced fluorescence as a vegetation monitoring tool - "
"present in only 18 studies (4.0%) across the full-text corpus - represents a missed opportunity "
"given SIF's mechanistic superiority to structural indices for capturing actual photosynthetic "
"activity. The same applies to the saturation-resistant kernel indices kNDVI and NIRv, used in "
"five and six studies respectively. As the OCO-3, TROPOMI and future FLEX mission datasets "
"accumulate, the systematic integration of SIF with structural indices such as NDVI and EVI in "
"multi-index vegetation monitoring frameworks deserves substantially greater research investment "
"than the current literature reflects."
)

D48_5 = (
"Fifth, the open science deficit documented here - 8.8% of full-text studies providing a code "
"repository and 7.5% a data repository, rising to 12.0% and 9.6% for 2023-2025 publications - must "
"be addressed through a combination of journal policy, funder requirements and community norm "
"shifts. The scientific community has demonstrated, in fields from genomics to ecology, that open "
"code and data sharing dramatically accelerate methodological progress and enable the type of "
"cross-study synthesis on which evidence-based policy depends. The vegetation remote sensing "
"community has the infrastructure - GitHub, Zenodo and the Google Earth Engine code sharing "
"environment - to achieve substantially higher adoption rates than the current baseline reflects."
)

D48_6 = (
"Taken together, the findings of this review affirm both the substantial scientific productivity "
"of satellite remote sensing of vegetation responses to climate change over the 25-year study "
"period and the structural constraints that limit the field's capacity to provide the globally "
"consistent, biome-complete, methodologically reproducible evidence base that the urgency of "
"climate change demands. Addressing these constraints - geographic, methodological and "
"institutional - represents the defining challenge for the field in the decade ahead."
)

C1 = (
"This systematic review synthesised evidence from 757 studies, of which 455 were re-extracted from "
"full text using a deterministic and fully auditable pipeline, to provide a comprehensive "
"assessment of how satellite remote sensing has been used to monitor vegetation responses to "
"climate change between 2000 and 2025. The findings demonstrate that the field has expanded "
"rapidly, driven by technological advances in satellite observations, cloud computing and "
"artificial intelligence. Despite this progress, several structural challenges persist."
)

C2 = (
"First, the dominance of three sensor families - Landsat (51.4% of full-text studies), MODIS "
"(44.6%) and Sentinel-2 (43.5%) - and of a single index, NDVI (76.9%), indicates both "
"methodological maturity and path dependency, with mechanistically superior alternatives such as "
"solar-induced fluorescence (4.0%) and saturation-resistant kernel indices remaining marginal. "
"Second, while machine learning is now applied in almost half of all studies (45.7%), led by "
"Random Forest (35.8%), deep learning remains a minority approach (11.4%) even as it grows quickly "
"- from absent before 2020 to 18.0% of studies published in 2023-2025 - and transformer "
"architectures have barely entered the field (0.9%). Third, the geographic imbalance in research "
"output is real but differently shaped than a simple North/South framing implies: the split is "
"approximately even (52.4% against 47.6%), yet the Global South share rests almost entirely on "
"China, leaving Sub-Saharan Africa, Southeast Asia and Latin America with a combined 8.3% of "
"output."
)

C3 = (
"Additionally, the review identifies major gaps in biome coverage, with drylands, savannas, "
"shrublands and peatlands the primary setting of only 11.2% of full-text studies despite their "
"ecological and climatic importance, and with 172 of the 206 forest studies not specifying a forest type at all. "
"Methodological limitations, including incomplete and non-standardised reporting of performance "
"metrics - R-squared reported by 40.9% of studies and RMSE by 26.6%, in units that largely "
"preclude pooling - and low levels of code and data sharing (8.8% and 7.5% respectively), further "
"constrain the reproducibility and comparability of studies."
)

C4 = (
"Future research should prioritise multi-sensor data fusion, which 62.9% of studies already "
"practise and which can be extended systematically; the integration of advanced deep learning "
"models with the physical understanding that process-based approaches supply; and the increased "
"use of emerging indicators such as solar-induced fluorescence. Equally important is the adoption "
"of standardised reporting frameworks and open science practices to enhance transparency and "
"cumulative knowledge building. Addressing these challenges will be essential for developing a "
"robust, globally representative and policy-relevant understanding of vegetation-climate "
"interactions in the face of ongoing environmental change."
)

# ==================================================================== round 2

M24_S5_A = (
"Full-text eligibility assessment was sought for all 1,482 records that passed title and "
"abstract screening. Open-access PDFs were retrieved via the Unpaywall API (Priem et al., 2026) "
"using the registered email address of the corresponding author. Retrieval was conducted in "
"parallel using Python's ThreadPoolExecutor with up to ten concurrent workers. For records where "
"the initial Unpaywall request failed, a cascade of supplementary recovery methods was attempted, "
"including the Semantic Scholar OpenAccess API, CORE API, PubMed Central, the Open Access Button, "
"and direct publisher landing-page parsing. An open-access full text was obtained "
"for 572 of the 1,482 records (38.6%); for the remaining 910 no full text could be retrieved from "
"any of these sources."
)

M24_S5_B = (
"Eligibility was then assessed against all eight criteria in Table 1. For the 572 records with "
"full text, the assessment used the extracted abstract and methods-section text. For the 910 "
"records without full text, the assessment used the title, the Scopus abstract and the "
"bibliographic metadata only. This is a departure from the ideal PRISMA procedure and it is "
"reported here explicitly rather than folded into the exclusion count: a record without full text "
"was retained when the title and abstract satisfied all criteria that are assessable from that "
"evidence, and excluded when they did not or when no abstract was available. Applying this rule, "
"302 of the 910 records without full text were retained and 608 were excluded. Records with "
"uncertain decisions were conservatively assigned EXCLUDE status."
)

M24_S5_C = (
"In total 725 records were excluded at this stage: 458 were assessed against the eligibility "
"criteria and failed at least one; 124 were excluded because no content beyond the title was "
"available to assess; and 143 carry no logged screening decision and were excluded by "
"subtraction, a group that includes 25 records for which no DOI was recorded. Following this "
"assessment, 757 studies were confirmed as eligible and were included in the final synthesis - "
"455 of them assessed on full text and 302 on title and abstract alone. Because this distinction "
"determines which studies can support which claims, it is carried through the whole of Section 3: "
"the bibliometric analyses in Sections 3.2 and 3.3 use all 757 studies, and every methodological "
"result in Sections 3.4 to 3.11 uses only the 455-study full-text corpus. The complete PRISMA "
"2020 record counts are summarised in Table 3 and displayed in the flow diagram (Figure 1)."
)

R31_V2 = (
"The systematic search of Scopus retrieved 4,794 records using the defined title-abstract-keyword "
"query combining remote sensing, vegetation, and climate-related terms, restricted to journal "
"articles and reviews published in English between 2000 and 2025. After removal of six duplicate "
"records, 4,788 unique records remained. Language verification confirmed all retained records were "
"in English, and the time-window filter introduced no further exclusions. Document-type filtering "
"removed 844 non-article records (conference papers, book chapters, editorials), yielding 3,944 "
"candidate articles. Title and abstract screening using a keyword filter excluded a further 2,462 "
"records, leaving 1,482 reports sought for retrieval. An open-access full text was "
"obtained for 572 of these (38.6%); for 910 records no full text could be retrieved. Of the 725 "
"records excluded at this stage, 458 were assessed and failed at least one eligibility criterion, "
"124 could not be assessed because no content beyond the title was available, and 143 carry no "
"logged decision. The final corpus comprised 757 peer-reviewed studies published across 208 "
"journals spanning 2000 to 2025; the three most frequent outlets were Remote Sensing (n = 126), "
"Remote Sensing of Environment (n = 61) and the International Journal of Remote Sensing (n = 28). "
"Of these 757 studies, 455 (60.1%) were assessed and re-extracted from full text and form the "
"denominator for all methodological results in Sections 3.4 to 3.11; the remaining 302 were "
"retained on the basis of title and abstract and contribute to the bibliometric analyses in "
"Sections 3.2 and 3.3 only. The complete selection process is illustrated in the PRISMA 2020 flow "
"diagram (Figure 1)."
)

R34_SENS = (
"Sensitivity to document type. The eligibility criteria admit review articles as well as primary "
"research, and 20 of the 455 full-text studies (4.4%) are reviews. Reviews name more platforms "
"than primary studies - a mean of 6.6 sensor families against 2.71 - and therefore inflate the "
"sensor and method counts slightly. Recomputing every headline quantity over the 435 primary "
"studies alone changes no value by more than 1.9 percentage points (Landsat 51.4% to 50.3%, MODIS "
"44.6% to 44.1%, Sentinel-2 43.5% to 42.5%, NDVI 76.9% to 76.3%, Random Forest 35.8% to 35.2%, "
"any deep learning 11.4% to 10.6%; full comparison in Table 14). Reviews are therefore retained, "
"in keeping with the pre-specified eligibility criteria, and all reported values should be read "
"as carrying an upper bound of roughly two percentage points from this source."
)

D47_SCREEN = (
"Full-text availability and the screening rule. The most consequential limitation of this review "
"concerns what could actually be assessed. An open-access full text was retrieved "
"for only 572 of the 1,482 reports sought (38.6%), and 302 of the 757 included studies were "
"therefore admitted on the basis of their title and abstract rather than their full text. Two "
"consequences follow. First, eligibility criteria that cannot be evaluated from an abstract - "
"minimum spatial extent, the presence of a quantitative outcome metric, and whether satellite data "
"were the primary rather than an ancillary data source - were in effect not applied to those 302 "
"studies, so the corpus is likely to contain some records that a full-text assessment would have "
"excluded. Second, the same evidential limit was resolved inconsistently across the screening "
"stage: 124 records were excluded specifically because no content beyond the title was available, "
"while 302 records with comparably thin evidence were retained. The rule reported in Section 2.4 "
"is the rule that was applied, and the 302 affected studies are identified in the supplementary "
"extraction table so that any reader can reproduce the corpus with or without them. Restricting "
"the entire review to the 455 full-text studies is the more conservative alternative; it was not "
"adopted here because it would discard the bibliographic evidence in Sections 3.2 and 3.3, which "
"rests on Scopus metadata that is complete for all 757 records and is unaffected by full-text "
"availability. A related residual should also be recorded: 85 records that passed full-text "
"screening do not appear in the final corpus, having been removed by the later cleaning steps "
"without a logged reason. Future updates of this review should log every screening and cleaning "
"decision at record level."
)

INTRO_VEG = (
"Vegetation covers the large majority of the ice-free land surface and constitutes the principal "
"interface between the atmosphere and the terrestrial biosphere. Through photosynthesis, "
"transpiration, and surface energy partitioning, plant canopies regulate fluxes of carbon, water "
"vapour, and energy that are critical to the functioning of the Earth system as a whole. The "
"global terrestrial carbon sink, estimated at approximately 3.1 Pg C yr-1 over the 2011-2020 "
"period (IPCC, 2021), is sustained largely by the photosynthetic activity of forests, grasslands, "
"shrublands, and wetlands. Any systematic alteration of vegetation structure or function therefore "
"has first-order consequences for atmospheric CO2 concentrations, regional climate feedbacks, "
"freshwater availability, and biological diversity."
)

D45_4_V2 = (
"Peatland under-representation is similarly acute. Northern peatlands alone most likely store "
"about 500 +/- 100 Pg of carbon in organic soils accumulated since the last deglaciation (Yu, "
"2012) - a stock that exceeds the carbon held in the world's above-ground forest biomass. Their "
"vulnerability to drainage, fire and the permafrost degradation associated with Arctic warming "
"makes them a critical system for long-term carbon cycle monitoring. Yet peatland was the primary "
"setting of only six studies in the 455-study full-text corpus, and was mentioned substantively in "
"only twelve. Habib et al. (2024) quantified peatland land use and CO2 emissions in Irish raised "
"bogs using satellite remote sensing, and Zhou et al. (2023) examined the long-term effects of "
"rewetting and drought on gross primary productivity in a temperate peatland. Wetlands more "
"broadly (9.9% primary, n = 45) were better represented, largely through studies of mangroves and "
"salt marshes, but the peat-forming wetlands that constitute the largest terrestrial carbon store "
"remain essentially absent. Figure 7 makes the structure of this gap explicit: the peatland row of "
"the evidence map contains no biomass studies at all."
)

REF_YU = (
"Yu, Z.C. (2012). Northern peatland carbon stocks and dynamics: A review. Biogeosciences, 9(10), "
"4071-4085. https://doi.org/10.5194/bg-9-4071-2012"
)

# ==================================================================== data availability

DAS_HEAD = "Data Availability Statement"

DAS_1 = (
"All data and code supporting this review are openly available in the GitHub repository "
"vegetation-climate-rs-review at https://github.com/Azad77/vegetation-climate-rs-review. The "
"repository contains the complete screening and extraction pipeline as eight documented Python "
"scripts; the list of all 757 included studies with DOIs, first-author country and evidence tier; "
"the per-study extraction table for the 455 full-text studies, including the per-term hit counts "
"from which every reported figure is derived; the 23 result tables underlying every table and "
"figure in this paper; the 332 automated verification checks with stated and recomputed values "
"side by side; and all nine figures at publication resolution."
)

DAS_2 = (
"Extraction is deterministic and involves no language model, so every count reported in Sections "
"3.4 to 3.11 is reproducible from the archived scripts and traceable to a span of source text. "
"Running verify.py against the archived tables reproduces all 332 quantitative claims made in this "
"paper."
)

DAS_3 = (
"The bibliographic records were retrieved from Scopus (Elsevier) on 11 April 2026; the search "
"query is reproduced in full in Table 2, and reuse of the underlying Scopus metadata is subject to "
"Elsevier's terms. The full texts of the reviewed articles are copyright of their respective "
"publishers and are not redistributed; every included study is identified by DOI so that the "
"corpus can be reassembled by any reader with the appropriate access. Code is released under the "
"MIT licence and the derived data and figures under CC BY 4.0. No new primary data were generated "
"in this study."
)

M21_FIX = (
"The review protocol was designed and documented prior to data collection in accordance with "
"PRISMA 2020 reporting guidelines (Page et al., 2021) and supplemented by the ROSES reporting "
"standards for environmental systematic reviews. Formal registration on a prospective registry "
"(PROSPERO or OSF) was not completed, and this is noted as a limitation in Section 4.7. All "
"protocol elements - search strategy, eligibility criteria, screening procedure and data "
"extraction framework - were specified before the search was executed, and are archived in full "
"in the public repository cited in the Data Availability Statement. A single database, Scopus, was "
"used as the sole source to maintain a reproducible and capped query volume consistent with Scopus "
"export limits (5,000 records). The PRISMA 2020 flow diagram documenting all screening decisions "
"and record counts is presented in Figure 1."
)
