import csv, re
from pathlib import Path

D = Path('data/university')
REQ = ['doc_id','title','source_url','retrieved_at','document_version','audience']
mds = sorted(D.glob('*.md'))

try:
    with open(D/'sources.csv', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
except FileNotFoundError:
    rows = []

ids, auds = [], {}
for p in mds:
    content = p.read_text(encoding='utf-8')
    parts = content.split('---')
    if len(parts) >= 2:
        frontmatter = parts[1]
        fm = dict(re.findall(r'^(\w+):\s*(.+)$', frontmatter, re.M))
    else:
        fm = {}
        
    ids.append(fm.get('doc_id'))
    aud_val = fm.get('audience', 'MISSING')
    auds[aud_val] = auds.get(aud_val, 0) + 1
    
    is_ok = "OK" if all(k in fm for k in REQ) and fm.get("doc_id") == p.stem else "THIEU METADATA"
    print(f'{p.name:40} {is_ok}')

print('so file :', len(mds), '(can 5-10)')
print('csv     :', 'khop' if sorted([r.get('doc_id') for r in rows]) == sorted(ids) else 'LECH')
print('audience:', auds)
