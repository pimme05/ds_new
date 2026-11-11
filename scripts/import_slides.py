"""Import all original slides. Requires pypdf; run with --source-dir PATH."""
import argparse, json, re, shutil, ast
from pathlib import Path
from pypdf import PdfReader
parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1]; out=root/'dist';sessions=[]
for i in range(1,13):
 source=args.source_dir/f'Session {i:02} DS Slides.pdf'
 shutil.copy2(source,out/'pdfs'/f'session-{i:02}.pdf')
 reader=PdfReader(source);pages=[]
 for n,p in enumerate(reader.pages,1):
  runs=[];code=[]
  def visit(t,cm,tm,font,size):
   if t.strip():
    runs.append((t.rstrip(),str(font.get('/BaseFont','')) if font else '',size))
    if font and 'Courier' in str(font.get('/BaseFont','')):code.append(t.rstrip())
  text=p.extract_text(visitor_text=visit)
  title=' '.join(t for t,f,z in runs if z>=28) or text.split('\n')[0]
  raw='\n'.join(code)
  fixed=raw
  # A line-wrapped indexing expression in the slide needs parentheses in Python.
  if i==2 and n==18:fixed=fixed.replace("df[df['rank_in_faculty'] == 1]\n   [['name', 'faculty', 'gpa']]", "df.loc[df['rank_in_faculty'] == 1, ['name', 'faculty', 'gpa']]")
  if fixed:
   try:ast.parse(fixed)
   except SyntaxError as e:print('CHECK',i,n,str(e))
  label=next((t for t,f,z in runs if t.startswith('PYTHON')), '')
  pages.append({'page':n,'title':title.strip(),'text':text.strip(),'code':fixed,'originalCode':raw if raw!=fixed else '', 'codeLabel':label.replace('PYTHON  ·  ','').title()})
 sessions.append({'id':i,'pages':pages,'pdf':f'pdfs/session-{i:02}.pdf'})
(out/'data'/'slides.json').write_text(json.dumps(sessions,ensure_ascii=False,indent=2))
print('Imported',sum(len(s['pages']) for s in sessions),'slides;',sum(bool(p['code']) for s in sessions for p in s['pages']),'code panels')
