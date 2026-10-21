"""Compare exact physical-frame, DMA and draw receipts from matched light probes."""
from pathlib import Path
import argparse,csv,hashlib,json
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rows(f):return list(csv.DictReader(f.open(newline='')))
bm=json.loads((a.before/'manifest.json').read_text());am=json.loads((a.after/'manifest.json').read_text())
assert bm['metrics_only'] and am['metrics_only'],'This packet covers light physical counters only'
assert bm['script_sha256']==am['script_sha256'],'Precisely matched immutable probe source'
assert all(r['exit']==0 for r in bm['runs']+am['runs']),'Every scene must finish'
keys=lambda m:{(r['mapper'],r['character'])for r in m['runs']}
assert keys(bm)==keys(am),'Matched mapper/character coverage'
out={'scope':'Light actual physical DMA/draw supplement, explicit native crowd arenas. Gameplay canonical traces are a separate packet.','before':str(a.before.resolve()),'after':str(a.after.resolve()),'benchmark_source_sha256':bm['script_sha256'],'before_manifest_sha256':sha(a.before/'manifest.json'),'after_manifest_sha256':sha(a.after/'manifest.json'),'runs':[]}
metrics=('physicalFrames','skippedNmis','physicalDmas','drawCalls','skippedRenders','meanForegroundCycles','meanCycles')
for mapper,char in sorted(keys(bm)):
 b=next((a.before/f'{mapper}-c{char}').glob('*-scenes.csv'));d=next((a.after/f'{mapper}-c{char}').glob('*-scenes.csv'))
 br=rows(b);ar=rows(d);assert len(br)==len(ar)==20
 scenes=[]
 for x,y in zip(br,ar):
  assert all(x[k]==y[k]for k in ('scene','character','outlinesOff','mode','enemies','updates'))
  for row in(x,y):assert int(row['updates'])==60 and int(row['drawCalls'])+int(row['skippedRenders'])==60
  scenes.append({k:int(x[k])if k in('scene','outlinesOff','enemies')else x[k]for k in('scene','mode','outlinesOff','enemies')}|{k:{'before':float(x[k]),'after':float(y[k])}for k in metrics})
 out['runs'].append({'mapper':mapper,'character':char,'before_csv_sha256':sha(b),'after_csv_sha256':sha(d),'scenes':scenes})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
print(len(out['runs']),'runs,',sum(len(r['scenes'])for r in out['runs']),'matched scenes')
for r in out['runs']:
 for s in r['scenes']:
  if s['mode']=='walk'and s['outlinesOff']==1 and s['enemies']in(4,6):
   vals=['%s %g -> %g'%(k,s[k]['before'],s[k]['after'])for k in('physicalFrames','physicalDmas','drawCalls','skippedRenders')]
   print(r['mapper'],r['character'],s['enemies'],'; '.join(vals))
