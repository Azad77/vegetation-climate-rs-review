# Table S3: record-level comparison of the first-version and revised corpus (included in either version).
import os, pandas as pd
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(REV, 'reviewer_response')
s = pd.read_csv(os.path.join(OUT, 'screening_v2', 'screening_v2_log.csv'))
t = s[(s.final_status == 'Included') | (s.status_v2 == 'Included')].copy()
t = t.rename(columns={'final_status': 'status_first_version', 'status_v2': 'status_revised'})
t['change'] = t.apply(lambda r: 'Kept' if r.status_first_version == 'Included' and r.status_revised == 'Included'
                      else ('Removed' if r.status_first_version == 'Included' else 'Added'), axis=1)
t = t[['row_id', 'doi', 'full_title', 'year', 'journal', 'status_first_version', 'status_revised', 'change']]
print(t.change.value_counts().to_string())
t.to_csv(os.path.join(OUT, 'Table_S3_corpus_change.csv'), index=False, encoding='utf-8-sig')
t.to_excel(os.path.join(OUT, 'Table_S3_corpus_change.xlsx'), index=False)
