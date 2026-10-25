"""Plan additive source-arm records without repacking any existing body art."""
from pathlib import Path
import sys,json,re,xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
import build_expanded_assets as a,build_megaman_assets as assets,build_samus_assets as packing
from prepare_crossover import frames
from build_special_art import extract
from build_ordinary_body_layout import source_parts
out=R/'build/verification/new-roster-1-1-nd/bass-arm-plan';out.mkdir(exist_ok=True)
items=list(ET.parse(R/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
for tag in items:
 if tag.get('type')in('SymbolClassTag','ExportAssetsTag')and tag.find('tags')is not None:symbols.update({n.text:i.text for i,n in zip(tag.find('tags'),tag.find('names'))})
sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
timeline=frames(sprites[symbols['MegaMan']])[:17];armtimeline=frames(sprites[symbols['MegaManArm']]);sheet=a.sheet('BASS')
arms=extract(armtimeline,24,sheet);bodies=extract(timeline,24,sheet)
a.ROLE='BASS';a.COLORS=a.targets('BASS');a.BASS_PROJECTILE=False
assets.layers=a.layers;assets.OAM_PRIORITY=True;assets.SCANLINE_PRIORITY=True
source=R/'src/bass_metasprites.inc';code=source.read_text()
def table(n):return [v.strip()for v in re.search(r'^'+n+r':\n\s+\.byte ([^\n]+)',code,re.M)[1].split(',')]
banks=[int(v[1:],16)for v in table('XgBASSBanks')];right=[s.lstrip('<>')for s in table('XgBASSRightLo')]
aliases=dict(re.findall(r'^(\w+) = (\w+)$',code,re.M))
def resolve(s):
 while s in aliases:s=aliases[s]
 return s
used={b:{0}for b in banks};resolved={}
for label,b in zip(right,banks):
 label=resolve(label)
 if label not in resolved:resolved[label]=source_parts(source,label)
 used[b]|={p['tile']//2 for p in resolved[label]}
# Ordinary WALK3 shares bankE1 and retains one extra packed pair.
used[0xe1]|={30}
first=0xd1+len((R/'chr/characters/crossover-roster-high.chr').read_bytes())//1024
raw=(R/'chr/characters/crossover-expanded.chr').read_bytes()
report={'used':{str(b):sorted(v)for b,v in used.items()},'jobs':[]}
for pose,frame,arm in [('STAND',2,1),('ATTACK1',3,4),('JUMPSHOOT',16,4)]:
 original=a.body('BASS',pose,0);body=bodies[frame-1]
 bb=body.getbbox();ob=original.getbbox();shift=(ob[0]-bb[0],ob[1]-bb[1])
 shift=(-7,16)
 placement=next(v for v in timeline[frame-1]['display'].values()if v.get('characterId')==symbols['MegaManArm'])['matrix']
 pos=tuple(round(float(placement[k])/40)+shift[i]for i,k in enumerate(('translateX','translateY')))
 armimage=Image.new('RGBA',original.size);armimage.alpha_composite(arms[arm-1],pos)
 complete=Image.new('RGBA',original.size);complete.alpha_composite(body,shift);complete.alpha_composite(armimage)
 pool=[];parts=packing.parts(complete,(32,32),pool)
 complete.save(out/(pose+'.png'))
 bank=banks[a.POSES.index(pose)];block=raw[(bank-first)*1024:(bank-first+1)*1024]
 fits=[]
 for b in range(224,231):
  blob=raw[(b-first)*1024:(b-first+1)*1024];available={blob[i*32:(i+1)*32]for i in used[b]}
  extra=sum(v not in available for v in pool);fits.append(dict(bank=b,extra=extra,free=32-len(used[b]),fits=extra<=32-len(used[b])))
 report['jobs'].append(dict(pose=pose,frame=frame,arm=arm,placement=pos,bank=bank,parts=parts,patterns=[v.hex()for v in pool],existing=[next((i for i in range(32)if block[i*32:(i+1)*32]==v),None)for v in pool],free=sorted(set(range(32))-used[bank]),fits=fits))
(out/'plan.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
