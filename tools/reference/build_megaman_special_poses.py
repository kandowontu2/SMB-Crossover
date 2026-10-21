"""Compose Mega Man's 2.02 special-weapon arms with his own body sheet."""
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
import build_megaman_assets as a
import build_samus_assets as p
from build_remaining_art import extract
from prepare_crossover import frames
ROOT=a.ROOT

def main():
 items=list(E.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'));sy={}
 for t in items:
  if t.get('type')in('SymbolClassTag','ExportAssetsTag')and t.find('tags')is not None:sy.update({n.text:i.text for i,n in zip(t.find('tags'),t.find('names'))})
 sp={t.get('spriteId'):t for t in items if t.get('type')=='DefineSpriteTag'}
 sheet=Image.open(next((ROOT/'reference/crossover2/images').glob('*_MegaMan000.png'))).convert('RGBA')
 fs=frames(sp[sy['MegaMan']]);bodies=extract(fs[:18],24,sheet);arms=extract(frames(sp[sy['MegaManArm']]),24,sheet)
 rec=[]
 for name,f,arm in [('THROW',3,2),('AIR_THROW',16,5),('FIST',3,6),('AIR_FIST',16,6),('CARRY',2,3),('CARRY_STEP',5,3),('CARRY_WALK1',6,3),('CARRY_WALK2',7,3),('CARRY_WALK3',8,3),('CARRY_JUMP',15,3)]:
  im=bodies[f-1].copy();m=next(v for v in fs[f-1]['display'].values()if v.get('characterId')==sy['MegaManArm'])['matrix'];im.alpha_composite(arms[arm-1],tuple(round(float(m.get(k,0))/40)for k in('translateX','translateY')));rec.append((name,im))
 groups=[];entries=[];lines=['; Mega Man 2.02 separate source arms.','.pushseg','.segment "XG_LUIGI_GFX"'];shared=[];a.SCANLINE_PRIORITY=True
 for name,im in rec:
  raw=shared[:];parts=p.parts(im,(40,16),raw);shared=raw[:];used=[]
  for t,pa,x,y in parts:
   if raw[t//2]not in used:used.append(raw[t//2])
  parts=[(used.index(raw[t//2])*2,pa,x,y)for t,pa,x,y in parts];raw=used
  choices=[(sum(t not in g for t in raw),i)for i,g in enumerate(groups)if len(g)+sum(t not in g for t in raw)<=32]
  if choices:bank=min(choices)[1]
  else:bank=len(groups);groups.append([])
  for t in raw:
   if t not in groups[bank]:groups[bank].append(t)
  parts=[(groups[bank].index(raw[t//2])*2,pa,x,y)for t,pa,x,y in parts];p.raw(lines,'SsMega'+name,parts);entries.append((name,bank));im.save(ROOT/f'build/reference-frames/MM-SPECIAL-{name}.png')
 for suffix,op in [('LeftLo','<'),('LeftHi','>'),('RightLo','<'),('RightHi','>')]:
  side='Left'if suffix.startswith('Left')else'Right';lines +=['SsMega'+suffix+':',' .byte '+','.join(op+'SsMega'+n+side for n,_ in entries)]
 lines +=['SsMegaBanks:',' .byte '+','.join(str(0xaa+b)for _,b in entries),'.popseg']
 (ROOT/'src/megaman_special_poses.inc').write_text('\n'.join(lines)+'\n');(ROOT/'src/megaman_special_pose_ids.inc').write_text('\n'.join('SS_MEGA_'+n+'='+str(i)for i,(n,_)in enumerate(entries))+'\n');(ROOT/'chr/characters/special-megaman-body.chr').write_bytes(b''.join(b''.join(g)+bytes(1024-len(g)*32)for g in groups));print(len(entries),'Mega Man source poses,',len(groups),'CHR banks')
if __name__=='__main__':main()

