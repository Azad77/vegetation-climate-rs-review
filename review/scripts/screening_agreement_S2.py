# Table S2: agreement between the first-version and revised (v2) title-and-abstract screening of the 1,482 records.
import os, pandas as pd
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(REV, 'reviewer_response')
s = pd.read_csv(os.path.join(OUT, 'screening_v2', 'screening_v2_log.csv'))
def kap(a, b):
    po = (a == b).mean(); pe = sum((a == c).mean() * (b == c).mean() for c in set(a) | set(b)); return po, (po - pe) / (1 - pe)
rows = []
for stage, a, b in [('Screening decision (first version: include; revised: code I)',
                     s.screening_decision.str.upper().eq('INCLUDE'), s.screen_v2.eq('I')),
                    ('Final status (included in the corpus)', s.final_status.eq('Included'), s.status_v2.eq('Included'))]:
    po, k = kap(a, b)
    rows.append({'Comparison': stage, 'N': len(s), 'Included by both': int((a & b).sum()), 'First version only': int((a & ~b).sum()),
                 'Revised only': int((~a & b).sum()), 'Excluded by both': int((~a & ~b).sum()),
                 'Agreement (%)': round(po * 100, 1), "Cohen's kappa": round(k, 2)})
T = pd.DataFrame(rows); print(T.to_string(index=False))
T.to_csv(os.path.join(OUT, 'Table_S2_screening_agreement.csv'), index=False, encoding='utf-8-sig')
T.to_excel(os.path.join(OUT, 'Table_S2_screening_agreement.xlsx'), index=False)
