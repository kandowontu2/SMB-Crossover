"""Resolve SWF labels and their skin bitmap translations without guessing cells."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from prepare_crossover import frames
tree=ET.parse(ROOT/'reference/crossover2/main.xml')
items=list(tree.getroot().iter('item'))
symbols={}
for tag in items:
    if tag.get('type') in ('SymbolClassTag','ExportAssetsTag'):
        ids=tag.find('tags');names=tag.find('names')
        if ids is not None and names is not None:
            symbols.update({n.text:i.text for i,n in zip(ids,names)})
sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
out={}
for name in ('Mario','Ryu','Sophia','SophiaBullet','MarioFireBall','SophiaBase','SophiaFrontWheel','SophiaBackWheel','SophiaExplosion'):
    sid=symbols[name]
    out[name]={'id':sid,'frames':frames(sprites[sid])}
directory=ROOT/'build/roster-fixes';directory.mkdir(exist_ok=True)
(directory/'atlas-labels.json').write_text(json.dumps(out,indent=2))
atlas={}
for name,info in out.items():
    bitmap={'Mario':'109','Ryu':'36','Sophia':'44','SophiaBullet':'44','MarioFireBall':'109','SophiaBase':'44','SophiaFrontWheel':'44','SophiaBackWheel':'44','SophiaExplosion':'44'}[name]
    atlas[name]={}
    for frame in info['frames']:
        pairs=[]
        entries=sorted(frame['display'].items(),key=lambda item:int(item[0]))
        for i,(depth,v) in enumerate(entries):
            if v.get('characterId')!=bitmap:continue
            mask=next((p for d,p in entries[i+1:] if p.get('characterId')=='18'),None)
            if mask is None:continue
            m=v['matrix'];mm=mask['matrix']
            x,y=(float(mm[k])/40 for k in ('translateX','translateY'))
            w,h=(float(mm[k])/2 for k in ('scaleX','scaleY'))
            left=x-float(m['translateX'])/40;top=y-float(m['translateY'])/40
            pairs.append({'name':v.get('name'),'crop':[round(left),round(top),round(left+w),round(top+h)],'offset':[round(x),round(y)]})
        for label in frame['labels']:
            atlas[name][label]={'frame':frame['frame'],'parts':pairs}
        atlas[name]['#'+str(frame['frame'])]={'frame':frame['frame'],'parts':pairs}
(ROOT/'docs/reference/expanded-atlas.json').write_text(json.dumps(atlas,indent=2)+'\n')
print('Resolved',sum(len(x) for x in atlas.values()),'label/frame mappings from pinned SWF matrices')
