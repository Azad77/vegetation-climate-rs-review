import pandas as pd, os, re, json, unicodedata
from difflib import SequenceMatcher

TXT='/home/claude/work/src/pdf_text'
d=pd.read_excel('/mnt/user-data/uploads/vegiclimate_review/data/step5_master_clean_19_4_2026.xlsx',sheet_name='Master Clean')
d['doi_n']=d.doi.astype(str).str.strip().str.lower()
doi2idx={}
for i,r in d.iterrows():
    if r.doi_n and r.doi_n!='nan': doi2idx.setdefault(r.doi_n,i)

def norm_title(t):
    t=unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9 ]',' ',t.lower()).split()
titles={i:' '.join(norm_title(t)) for i,t in d.title.items()}

files=sorted(os.listdir(TXT))
link={}   # stem -> row index
# 1. already-linked
for i,fn in d.pdf_filename.dropna().items():
    stem=fn[:-4] if fn.lower().endswith('.pdf') else fn
    if os.path.exists(os.path.join(TXT,stem+'.txt')): link[stem]=i

DOIRE=re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+')
def clean_doi(s):
    s=s.strip().lower().rstrip('.,;)')
    s=re.sub(r'\.(pdf|xml|html)$','',s)
    return s

unmatched=[]
for f in files:
    stem=f[:-4]
    if stem in link: continue
    # from filename: pattern with underscore instead of slash
    cand=None
    m=re.search(r'(10\.\d{4,9})[_/]([-._;()A-Za-z0-9]+)',stem)
    if m:
        cand=clean_doi(m.group(1)+'/'+m.group(2))
        if cand in doi2idx: link[stem]=doi2idx[cand]; continue
    unmatched.append(stem)

print('after filename-DOI:',len(link),'unmatched',len(unmatched))

# 2. DOI found in text
still=[]
for stem in unmatched:
    txt=open(os.path.join(TXT,stem+'.txt'),errors='ignore').read()[:6000]
    hits=[clean_doi(x) for x in DOIRE.findall(txt)]
    got=None
    for h in hits:
        if h in doi2idx and doi2idx[h] not in link.values(): got=doi2idx[h]; break
    if got is None:
        for h in hits:
            if h in doi2idx: got=doi2idx[h]; break
    if got is not None: link[stem]=got
    else: still.append(stem)
print('after text-DOI:',len(link),'unmatched',len(still))

# 3. title match on first 1500 chars
used=set(link.values())
still2=[]
for stem in still:
    head=' '.join(norm_title(open(os.path.join(TXT,stem+'.txt'),errors='ignore').read()[:1500]))
    best=(0,None)
    for i,t in titles.items():
        if len(t)<15: continue
        if t in head: best=(1.0,i); break
        sc=SequenceMatcher(None,t,head[:len(t)+120]).ratio()
        if sc>best[0]: best=(sc,i)
    if best[0]>=0.82: link[stem]=best[1]
    else: still2.append((stem,round(best[0],2)))
print('after title:',len(link),'unmatched',len(still2))
print(still2[:20])
json.dump({k:int(v) for k,v in link.items()},open('/home/claude/work/out/pdf_link.json','w'))
# duplicates: multiple pdfs -> same row
from collections import Counter
c=Counter(link.values())
print('rows with >1 pdf:',sum(1 for v in c.values() if v>1))
print('distinct rows with fulltext:',len(c))
