"""validation_design.py - Reviewer 1, comment 5.
(1) Classifies the validation design of every Tier 2 study from its reference-stripped body text (deterministic rules,
    highest-rigour design detected wins): spatially independent test > independent hold-out test > cross-validation
    only (k-fold, leave-one-out, out-of-bag, bootstrap) > none detected (calibration fit or association statistic).
(2) Computes a five-indicator reporting-quality appraisal (0-5) that replaces the unexecuted 'adapted GRADE' score:
    Q1 data/preprocessing documented, Q2 independent (or spatially independent) test, Q3 uncertainty reported,
    Q4 code or data in a resolvable repository, Q5 at least one quantitative performance metric.
(3) Writes passages for the 16 validation-sample studies that report R2, for checking the design classifier.
Outputs -> ../reviewer_response/design/: study_design_quality.csv, design_kwic.txt"""
import os, re, json, pandas as pd
import extract as X
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.dirname(HERE)
OUT = os.path.join(REV, 'reviewer_response', 'design'); os.makedirs(OUT, exist_ok=True)
X.TXT = os.path.join(REV, 'pdf_text')
e = pd.read_csv(os.path.join(REV, 'fulltext_extraction.csv'))
SPATIAL = re.compile(r"spatial(?:ly)?[- ](?:independent|cross[- ]?validat\w*|block\w*|hold[- ]?out|k[- ]?fold)|leave[- ]one[- ](?:site|region|area|plot|location|year|tile|cluster|basin|country)[- ]out|block(?:ed)? cross[- ]?validat|independent (?:sites|regions|areas|test sites|study areas?)", re.I)
TEST = re.compile(r"independent (?:test|validation|data ?set|samples?|testing)|hold[- ]?out|\btest(?:ing)? (?:set|data|dataset|samples?|subset|plots|sites)|validation (?:set|data ?set|samples?|subset|plots|points|sites)|withheld|external validation|(?:training|calibration) (?:and|/) ?(?:test|testing|validation)|randomly (?:split|divided|partitioned|selected)[^.]{0,80}(?:test|validation)|\b\d{2} ?% (?:of (?:the )?)?[^.]{0,40}(?:test|validation)", re.I)
CV = re.compile(r"cross[- ]?validat\w*|\b(?:k|\d{1,2})[- ]fold\b|leave[- ]one[- ]out|\bLOOCV\b|\bLOO\b|out[- ]of[- ]bag|\bOOB\b|bootstrap", re.I)
PREP = re.compile(r"atmospheric(?:ally)? correct|surface reflectance|cloud mask|cloud[- ]free|radiometric(?:ally)? (?:calibrat|correct)|geometric(?:ally)? correct|orthorectif|\bLevel[- ]?2\b|\bL2A\b|quality (?:flag|assessment|band|control)|\bQA\b|maximum value composit|Savitzky", re.I)
RES = re.compile(r"\b\d+(?:\.\d+)?\s?(?:m|km|°)\s?(?:×\s?\d+(?:\.\d+)?\s?(?:m|km)\s?)?(?:spatial )?resolution|resolution of \d|\d+[- ]m (?:pixels?|grid|resolution)", re.I)
UNC = re.compile(r"confidence interval|standard error|uncertaint|prediction interval|credible interval|±", re.I)
rows, kw = [], []
K = json.load(open(os.path.join(REV, 'reviewer_response', 'validation', 'kwic_sample.json')))
for _, x in e.iterrows():
    raw, body = X.load(x.pdf_stem)
    sp, te, cv = SPATIAL.search(body), TEST.search(body), CV.search(body)
    design = ('Spatially independent test' if sp else 'Independent hold-out test' if te else
              'Cross-validation only' if cv else 'None detected')
    metric = any(x[c] > 0 for c in ['r2_n', 'rmse_n', 'mae_n', 'oa_n', 'kappa_n', 'f1_n'])
    q = dict(Q1_data_documented=int(bool(PREP.search(body)) and bool(RES.search(body))),
             Q2_independent_test=int(design in ('Spatially independent test', 'Independent hold-out test')),
             Q3_uncertainty_reported=int(bool(UNC.search(body))),
             Q4_repository=int('Repository link' in (str(x.code_status), str(x.data_status))),
             Q5_metric_reported=int(metric))
    rows.append(dict(doi=x.doi, year=x.year, domain_primary=x.domain_primary, r2_n=x.r2_n, r2_median=x.r2_median,
                     r2_max=x.r2_max, design=design, **q, quality_score=sum(q.values())))
    if x.doi in K and x.r2_n > 0:
        kw.append(f"\n######## {x.doi} ({x.year}) {x.title[:100]}\nPRED DESIGN: {design} | R2 n={x.r2_n} median={x.r2_median}")
        for lab, rx in [('SPATIAL', SPATIAL), ('TEST', TEST), ('CV', CV)]:
            for m in list(rx.finditer(body))[:3]:
                kw.append(f"  [{lab}] ...{body[max(0, m.start()-220):m.end()+180]}...")
        for m in list(re.finditer(r'R\s?2|R²|coefficient of determination', body))[:4]:
            kw.append(f"  [R2] ...{body[max(0, m.start()-200):m.end()+120]}...")
D = pd.DataFrame(rows); D.to_csv(os.path.join(OUT, 'study_design_quality.csv'), index=False, encoding='utf-8-sig')
open(os.path.join(OUT, 'design_kwic.txt'), 'w').write('\n'.join(kw))
print(D.design.value_counts().to_dict()); print(D[D.r2_n > 0].design.value_counts().to_dict())
print(D.quality_score.value_counts().sort_index().to_dict()); print(D[[c for c in D if c.startswith('Q')]].mean().round(3).to_dict())
