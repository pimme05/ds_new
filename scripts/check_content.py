from pathlib import Path
import json, ast
root=Path(__file__).resolve().parents[1];d=root/'dist';course=json.loads((d/'data/course.json').read_text())
assert len(course)==12
assert sum(len(s['pages']) for s in course)==220
assert sum(bool(p['code']) for s in course for p in s['pages'])==50
for s in course:
 assert (d/s['pdf']).is_file()
 assert len(s['concepts'])==5 and len(s['quiz'])==2
 assert all(1<=c[2]<=len(s['pages']) for c in s['concepts'])
 for p in s['pages']:
  assert (d/f"slides/{s['id']:02}/{p['page']}.jpg").is_file()
  assert p['text'].strip()
  if p['code']:ast.parse(p['code'])
 nb=json.loads((d/f"notebooks/session-{s['id']:02}.ipynb").read_text())
 for c in nb['cells']:
  if c['cell_type']=='code':ast.parse(c['source'])
 for q in s['quiz']:assert 0<=q['answer']<len(q['options'])
print('PASS: 12 sessions, 220 original slide images/text, 50 syntax-valid code panels, 12 syntax-valid practice notebooks, 24 quiz answers, and source references.')
