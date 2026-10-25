"""Read-only pinned timeline/body-rectangle inventory for helper implementation."""
from pathlib import Path
import hashlib,json,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/reference'))
from prepare_crossover import frames
OUT=ROOT/'build/player-guide-agent';OUT.mkdir(exist_ok=True)
results={}
for version,folder in [('hosted1x','reference/crossover'),('v202','reference/crossover2')]:
 p=ROOT/folder/'main.xml';tree=ET.parse(p);items=list(tree.getroot().iter('item'));symbols={}
 for t in items:
  if t.get('type') in ('SymbolClassTag','ExportAssetsTag'):
   ids=t.find('tags');names=t.find('names')
   if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
 sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
 shapes={i.get('shapeId'):i for i in items if i.get('shapeId')}
 selected={n:i for n,i in symbols.items() if n.rsplit('.',1)[-1] in ('Platform','HRect','Mario','Luigi','MegaMan','Bass','Samus','Bill','Link','Simon','Ryu','Sophia')}
 rec={'xml_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'symbols':selected,'timelines':{}}
 for name,sid in selected.items():
  if sid not in sprites:continue
  fs=frames(sprites[sid]);body=[];active=''
  for f in fs:
   if f['labels']:active=f['labels'][-1]
   parts=[v for v in f['display'].values() if v.get('name','').lower() in ('hrect','hitrect') or v.get('characterId') in [x for n,x in selected.items() if n.rsplit('.',1)[-1]=='HRect']]
   if parts:body.append({'frame':f['frame'],'labels':f['labels'],'active_label':active,'parts':parts})
  rec['timelines'][name]={'symbol':sid,'frame_count':len(fs),'body_rect_frames':body}
  if name.rsplit('.',1)[-1] in ('Platform','HRect'):
   rec['timelines'][name]['all_frames']=fs
   rec['timelines'][name]['child_shape_bounds']={v['characterId']:dict(shapes[v['characterId']].find('shapeBounds').attrib) for f in fs for v in f['display'].values() if v.get('characterId') in shapes and shapes[v['characterId']].find('shapeBounds') is not None}
 results[version]=rec
(OUT/'platform-timeline-inventory.json').write_text(json.dumps(results,indent=2))
for version,r in results.items():
 print(version,r['symbols'])
 for name,t in r['timelines'].items():
  print(name,'frames',t['frame_count'],'bodyrectframes',len(t['body_rect_frames']))
  if name.rsplit('.',1)[-1] in ('Platform','HRect'):print(json.dumps(t,indent=2)[:12000])
