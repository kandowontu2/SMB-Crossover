"""Compare immutable crowd benchmark gameplay receipts and timing/visibility."""
from pathlib import Path
import argparse,csv,hashlib,json
p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path,required=True)
p.add_argument('--characters',help='Explicit comma-separated subset present in both manifests')
p.add_argument('--mappers',help='Explicit comma-separated subset present in both manifests')
a=p.parse_args()
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def read(f):return list(csv.DictReader(f.open(newline='')))
bm=json.loads((a.before/'manifest.json').read_text());am=json.loads((a.after/'manifest.json').read_text())
assert bm['script_sha256']==am['script_sha256'],'Use precisely the same frozen benchmark source'
assert all(x['exit']==0 for x in bm['runs']+am['runs']),'Every compared run must complete its bounded arena'
requested_characters=set(map(int,a.characters.split(',')))if a.characters else None
requested_mappers=set(a.mappers.split(','))if a.mappers else None
keys=lambda m:{(x['mapper'],x['character'])for x in m['runs']
 if(requested_characters is None or x['character']in requested_characters)
 and(requested_mappers is None or x['mapper']in requested_mappers)}
assert keys(bm) and keys(am),'A requested comparison must contain actual runs'
assert keys(bm)==keys(am),'Both sides must cover the same mapper/character set'
if requested_characters is not None:assert {c for _,c in keys(bm)}==requested_characters,'Every requested character must be captured'
if requested_mappers is not None:assert {m for m,_ in keys(bm)}==requested_mappers,'Every requested mapper must be captured'
out={'scope':'Explicit native crowd arenas, completed logic-update gameplay state; no route/whole-roster completion claim','before':str(a.before.resolve()),'after':str(a.after.resolve()),'benchmark_source_sha256':bm['script_sha256'],'runs':[],'canonical_mismatch_count':0}
out['requested_subset']={'characters':sorted(requested_characters)if requested_characters is not None else None,'mappers':sorted(requested_mappers)if requested_mappers is not None else None}
for mapper,char in sorted(keys(bm)):
 b=a.before/f'{mapper}-c{char}';d=a.after/f'{mapper}-c{char}'
 bf=next(b.glob('*-canonical.csv'));af=next(d.glob('*-canonical.csv'));bc=read(bf);ac=read(af)
 assert len(bc)==len(ac)==1200,'All20 scenes retain60 completed updates each'
 mismatches=[];count=0
 for i,(x,y)in enumerate(zip(bc,ac)):
  assert x.keys()==y.keys(),'Identical canonical observation columns'
  for k in x:
   if x[k]!=y[k]:
    count+=1
    if len(mismatches)<20:mismatches.append({'row':i,'scene':x['scene'],'update':x['update'],'field':k,'before':x[k],'after':y[k]})
 bs=read(next(b.glob('*-scenes.csv')));ds=read(next(d.glob('*-scenes.csv')));changes=[]
 bdraw={x['scene']:x for x in read(next(b.glob('*-routines.csv')))if x['routine']=='DrawAllMetasprites'}
 adraw={x['scene']:x for x in read(next(d.glob('*-routines.csv')))if x['routine']=='DrawAllMetasprites'}
 br={k:int(v['calls'])for k,v in bdraw.items()};ar={k:int(v['calls'])for k,v in adraw.items()}
 for x,y in zip(bs,ds):
  assert all(x[k]==y[k]for k in ('scene','character','outlinesOff','mode','enemies','updates')),'Identical scene controls'
  changes.append({'scene':int(x['scene']),'mode':x['mode'],'outlinesOff':int(x['outlinesOff']),'enemies':int(x['enemies']),
   'drawAllCalls':{'before':br.get(x['scene'],0),'after':ar.get(y['scene'],0)},
   'skippedRenders':{'before':60-br.get(x['scene'],0),'after':60-ar.get(y['scene'],0)},
   'meanForegroundExcludingDrawCycles':{'before':float(x['meanForegroundCycles'])-float(bdraw.get(x['scene'],{}).get('totalForegroundCycles',0))/60,'after':float(y['meanForegroundCycles'])-float(adraw.get(y['scene'],{}).get('totalForegroundCycles',0))/60},
   **{k:{'before':float(x[k]),'after':float(y[k])}for k in ('physicalFrames','skippedNmis','meanForegroundCycles','drawnEnemyFrames','visibleEnemyFrames','fullyInvisibleEnemyFrames','overloadRowsTotal')+tuple(k for k in('physicalDmas',)if k in x and k in y)}})
 out['canonical_mismatch_count']+=count
 out['runs'].append({'mapper':mapper,'character':char,'canonical_before_sha256':sha(bf),'canonical_after_sha256':sha(af),'canonical_rows':len(bc),'canonical_observation_fields':len(bc[0])-2,'canonical_mismatch_count':count,'first_mismatches':mismatches,'scenes':changes})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
print(len(out['runs']),'runs,',sum(x['canonical_rows']for x in out['runs']),'completed updates,',out['canonical_mismatch_count'],'canonical mismatches')
raise SystemExit(1 if out['canonical_mismatch_count']else 0)
